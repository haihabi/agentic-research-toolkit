"""The git layer. All git usage in the server goes through this module.

Design points:
  * The token is supplied to git via GIT_ASKPASS (an env-fed helper script), so it
    never appears in argv (visible to `ps`) and never in `.git/config` on disk.
    The clone remote is stored as `https://git@git.overleaf.com/<id>` — username
    only, no secret.
  * Every git invocation carries an explicit `user.name` / `user.email` so commits
    work on a machine with no global git identity.
  * stderr/stdout is token-redacted before it can reach an exception message.
  * Two sync paths:
      - fast_forward(): read path. fetch + `merge --ff-only`. Never merges, never
        conflicts, never creates a commit.
      - sync(): mutation path. fetch + merge. On a real conflict the merge is
        aborted and MergeConflictError is raised — nothing is left half-merged.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .errors import GitCommandError, MergeConflictError, TokenMissingError

# `git status --porcelain` two-letter codes that indicate an unresolved conflict.
_CONFLICT_CODES = {"DD", "AU", "UD", "UA", "DU", "AA", "UU"}

_ASKPASS_POSIX = """\
#!/bin/sh
# git calls this with the prompt string as $1. Answer the username prompt with a
# constant and every other prompt (the password) with the token from the env.
case "$1" in
  Username*) printf '%s' 'git' ;;
  *) printf '%s' "$OVERLEAF_GIT_TOKEN" ;;
esac
"""

_ASKPASS_WINDOWS = """\
@echo off
setlocal enabledelayedexpansion
set "prompt=%~1"
if /i "!prompt:~0,8!"=="Username" (echo git) else (echo !OVERLEAF_GIT_TOKEN!)
endlocal
"""


class Git:
    """Thin, security-aware wrapper around the `git` CLI."""

    def __init__(self, token: str | None, name: str, email: str, helper_dir: Path):
        self._token = token
        self._name = name
        self._email = email
        self._helper_dir = helper_dir
        self._askpass: Path | None = None

    # -- internals ---------------------------------------------------------

    def _redact(self, text: str) -> str:
        if self._token and text:
            return text.replace(self._token, "***")
        return text

    def _ensure_askpass(self) -> Path:
        if self._askpass and self._askpass.is_file():
            return self._askpass
        self._helper_dir.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            path = self._helper_dir / "askpass.cmd"
            path.write_text(_ASKPASS_WINDOWS, encoding="utf-8")
        else:
            path = self._helper_dir / "askpass.sh"
            path.write_text(_ASKPASS_POSIX, encoding="utf-8")
            path.chmod(0o700)
        self._askpass = path
        return path

    def _env(self, needs_auth: bool) -> dict[str, str]:
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"  # never block on an interactive prompt
        if needs_auth:
            if not self._token:
                raise TokenMissingError(
                    "OVERLEAF_GIT_TOKEN is not set. Export it in the environment "
                    "that launches this server (see the README)."
                )
            env["OVERLEAF_GIT_TOKEN"] = self._token
            env["GIT_ASKPASS"] = str(self._ensure_askpass())
        return env

    def run(
        self,
        args: list[str],
        cwd: Path | None = None,
        *,
        check: bool = True,
        needs_auth: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        cmd = [
            "git",
            "-c",
            f"user.name={self._name}",
            "-c",
            f"user.email={self._email}",
            *args,
        ]
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            env=self._env(needs_auth),
            check=False,
        )
        if check and result.returncode != 0:
            detail = self._redact(result.stderr).strip() or self._redact(result.stdout).strip()
            raise GitCommandError(f"git {args[0]} failed: {detail}")
        return result

    # -- high-level operations ------------------------------------------------

    def clone(self, url: str, dest: Path) -> None:
        self.run(["clone", url, str(dest)], needs_auth=True)

    def remote_url(self, repo: Path) -> str:
        r = self.run(["remote", "get-url", "origin"], cwd=repo, check=False)
        return r.stdout.strip() if r.returncode == 0 else ""

    def current_branch(self, repo: Path) -> str:
        return self.run(["symbolic-ref", "--short", "HEAD"], cwd=repo).stdout.strip()

    def fetch(self, repo: Path) -> None:
        self.run(["fetch", "origin"], cwd=repo, needs_auth=True)

    def conflicted_files(self, repo: Path) -> list[str]:
        out = self.run(["status", "--porcelain"], cwd=repo).stdout
        return [line[3:] for line in out.splitlines() if line[:2] in _CONFLICT_CODES]

    def fast_forward(self, repo: Path) -> None:
        """Read path: pull remote changes only if they fast-forward cleanly.

        If local history has diverged, this is a no-op and the caller sees the
        local state; the next mutation goes through sync() and surfaces the
        conflict properly.
        """
        self.fetch(repo)
        branch = self.current_branch(repo)
        self.run(["merge", "--ff-only", f"origin/{branch}"], cwd=repo, check=False)

    def sync(self, repo: Path) -> None:
        """Mutation path: fetch + merge. Abort and raise on a real conflict."""
        self.fetch(repo)
        branch = self.current_branch(repo)
        merge = self.run(["merge", "--no-edit", f"origin/{branch}"], cwd=repo, check=False)
        if merge.returncode != 0:
            files = self.conflicted_files(repo)
            self.run(["merge", "--abort"], cwd=repo, check=False)
            raise MergeConflictError(files)

    def commit(self, repo: Path, message: str) -> None:
        # Under the per-project lock and after a clean sync, the only worktree
        # change is the one apply_fn just made, so staging everything is safe and
        # correctly handles renames (git mv) and deletions of now-missing paths.
        self.run(["add", "-A"], cwd=repo)
        self.run(["commit", "-m", message], cwd=repo)

    def has_pending_changes(self, repo: Path, paths: list[str]) -> bool:
        out = self.run(["status", "--porcelain", "--", *paths], cwd=repo).stdout
        return bool(out.strip())

    def push_with_retry(self, repo: Path) -> str:
        r = self.run(["push", "origin", "HEAD"], cwd=repo, check=False, needs_auth=True)
        if r.returncode == 0:
            return (r.stdout or r.stderr).strip() or "Pushed."
        # The remote likely advanced between our sync and our push. Re-sync once
        # (which will raise if that introduced a conflict) and try again.
        self.sync(repo)
        r2 = self.run(["push", "origin", "HEAD"], cwd=repo, check=False, needs_auth=True)
        if r2.returncode != 0:
            raise GitCommandError(
                f"Push failed after retry: {self._redact(r2.stderr).strip()}"
            )
        return (r2.stdout or r2.stderr).strip() or "Pushed."
