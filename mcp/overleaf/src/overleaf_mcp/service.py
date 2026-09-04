"""The actual behaviour behind every tool, as plain Python with no MCP imports.

server.py wires these methods to FastMCP; the tests drive them directly against a
local bare repo standing in for git.overleaf.com.
"""

from __future__ import annotations

import base64
import binascii
from collections.abc import Callable
from pathlib import Path

from .conflicts import attempt_merge
from .errors import FileTooLargeError, OverleafMCPError
from .git_sync import Git
from .latex_compile import compile_project as _compile_project
from .workspace import BUILD_DIRNAME, Workspace

_DEFAULT_TEMPLATE = "https://git@git.overleaf.com/{id}"


class OverleafService:
    def __init__(
        self,
        git: Git,
        workspace: Workspace,
        *,
        max_binary_bytes: int,
        compile_timeout: int,
        remote_template: str = _DEFAULT_TEMPLATE,
    ):
        self._git = git
        self._ws = workspace
        self._max_binary_bytes = max_binary_bytes
        self._compile_timeout = compile_timeout
        self._remote_template = remote_template

    # -- helpers ---------------------------------------------------------

    def _remote_url(self, project_id: str) -> str:
        pid = project_id.strip()
        if not pid or any(c.isspace() for c in pid) or ".." in pid:
            raise OverleafMCPError("Invalid Overleaf project ID.")
        if "{id}" in self._remote_template:
            return self._remote_template.format(id=pid)
        return self._remote_template

    def _mutate(
        self,
        local_name: str,
        paths: list[str],
        message: str,
        apply_fn: Callable[[Path], None],
    ) -> str:
        repo = self._ws.project_dir(local_name)
        with self._ws.lock(local_name):
            self._git.sync(repo)  # raises MergeConflictError on a real conflict
            apply_fn(repo)
            if not self._git.has_pending_changes(repo, paths):
                return "No change — the project already matches this content."
            self._git.commit(repo, message)
            push = self._git.push_with_retry(repo)
        return f"{message} — synced to Overleaf. {push}"

    def _read_synced(self, local_name: str) -> Path:
        repo = self._ws.project_dir(local_name)
        with self._ws.lock(local_name):
            self._git.fast_forward(repo)
        return repo

    # -- project registry ------------------------------------------------

    def add_project(self, overleaf_project_id: str, local_name: str) -> str:
        dest = self._ws.project_dir(local_name, must_exist=False)
        self._git.clone(self._remote_url(overleaf_project_id), dest)
        exclude = dest / ".git" / "info" / "exclude"
        exclude.parent.mkdir(parents=True, exist_ok=True)
        existing = exclude.read_text(encoding="utf-8") if exclude.is_file() else ""
        exclude.write_text(existing.rstrip("\n") + f"\n{BUILD_DIRNAME}/\n", encoding="utf-8")
        return f"Added project '{local_name}' (Overleaf ID {overleaf_project_id})."

    def list_projects(self) -> list[dict]:
        out = []
        for name in self._ws.list_project_names():
            url = self._git.remote_url(self._ws.root / name)
            pid = url.rstrip("/").rsplit("/", 1)[-1] if url else ""
            out.append({"local_name": name, "overleaf_project_id": pid})
        return out

    def sync_project(self, local_name: str) -> str:
        repo = self._ws.project_dir(local_name)
        with self._ws.lock(local_name):
            self._git.sync(repo)
        return f"'{local_name}' is in sync with Overleaf."

    # -- reads ---------------------------------------------------------------

    def list_files(self, local_name: str, subdir: str = "") -> list[str]:
        repo = self._read_synced(local_name)
        base = self._ws.resolve_in_project(repo, subdir) if subdir else repo
        files = []
        for path in base.rglob("*"):
            parts = path.relative_to(repo).parts
            if ".git" in parts or BUILD_DIRNAME in parts:
                continue
            if path.is_file():
                files.append(path.relative_to(repo).as_posix())
        return sorted(files)

    def read_file(self, local_name: str, file_path: str) -> str:
        repo = self._read_synced(local_name)
        target = self._ws.resolve_in_project(repo, file_path)
        if not target.is_file():
            raise OverleafMCPError(f"{file_path} not found in '{local_name}'.")
        try:
            return target.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise OverleafMCPError(
                f"{file_path} is not UTF-8 text — use read_binary_file."
            ) from exc

    def read_binary_file(self, local_name: str, file_path: str) -> dict:
        repo = self._read_synced(local_name)
        target = self._ws.resolve_in_project(repo, file_path)
        if not target.is_file():
            raise OverleafMCPError(f"{file_path} not found in '{local_name}'.")
        size = target.stat().st_size
        self._check_binary_size(size)
        return {
            "file_path": file_path,
            "size_bytes": size,
            "content_base64": base64.b64encode(target.read_bytes()).decode("ascii"),
        }

    # -- writes ------------------------------------------------------------

    def edit_file(
        self, local_name: str, file_path: str, content: str, message: str | None = None
    ) -> str:
        def apply(repo: Path) -> None:
            target = self._ws.resolve_in_project(repo, file_path)
            if not target.is_file():
                raise OverleafMCPError(
                    f"{file_path} not found in '{local_name}'. Use add_file to create it."
                )
            target.write_text(content, encoding="utf-8")

        return self._mutate(local_name, [file_path], message or f"Edit {file_path}", apply)

    def add_file(
        self, local_name: str, file_path: str, content: str, message: str | None = None
    ) -> str:
        def apply(repo: Path) -> None:
            target = self._ws.resolve_in_project(repo, file_path)
            if target.exists():
                raise OverleafMCPError(
                    f"{file_path} already exists in '{local_name}'. Use edit_file instead."
                )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        return self._mutate(local_name, [file_path], message or f"Add {file_path}", apply)

    def add_binary_file(
        self,
        local_name: str,
        file_path: str,
        content_base64: str,
        message: str | None = None,
    ) -> str:
        try:
            raw = base64.b64decode(content_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise OverleafMCPError("content_base64 is not valid base64.") from exc
        self._check_binary_size(len(raw))

        def apply(repo: Path) -> None:
            target = self._ws.resolve_in_project(repo, file_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)

        return self._mutate(
            local_name, [file_path], message or f"Add binary {file_path}", apply
        )

    def delete_file(
        self, local_name: str, file_path: str, message: str | None = None
    ) -> str:
        def apply(repo: Path) -> None:
            target = self._ws.resolve_in_project(repo, file_path)
            if not target.is_file():
                raise OverleafMCPError(f"{file_path} not found in '{local_name}'.")
            target.unlink()

        return self._mutate(local_name, [file_path], message or f"Delete {file_path}", apply)

    def move_file(
        self,
        local_name: str,
        src_path: str,
        dst_path: str,
        message: str | None = None,
    ) -> str:
        def apply(repo: Path) -> None:
            src = self._ws.resolve_in_project(repo, src_path)
            dst = self._ws.resolve_in_project(repo, dst_path)
            if not src.is_file():
                raise OverleafMCPError(f"{src_path} not found in '{local_name}'.")
            if dst.exists():
                raise OverleafMCPError(f"{dst_path} already exists in '{local_name}'.")
            dst.parent.mkdir(parents=True, exist_ok=True)
            self._git.run(["mv", src_path, dst_path], cwd=repo)

        return self._mutate(
            local_name,
            [src_path, dst_path],
            message or f"Move {src_path} -> {dst_path}",
            apply,
        )

    # -- conflicts -------------------------------------------------------

    def get_conflicts(self, local_name: str) -> dict:
        repo = self._ws.project_dir(local_name)
        with self._ws.lock(local_name):
            result = attempt_merge(self._git, repo)
        if not result["conflicted"]:
            return {"conflicted": False, "message": "No conflicts — in sync with Overleaf."}
        return {"conflicted": True, "files": result["files"]}

    def resolve_conflict(
        self,
        local_name: str,
        resolutions: dict[str, str],
        message: str | None = None,
    ) -> str:
        repo = self._ws.project_dir(local_name)
        with self._ws.lock(local_name):
            self._git.fetch(repo)
            branch = self._git.current_branch(repo)
            merge = self._git.run(
                ["merge", "--no-edit", f"origin/{branch}"], cwd=repo, check=False
            )
            if merge.returncode == 0:
                return "No conflicts to resolve — already in sync with Overleaf."

            conflicted = self._git.conflicted_files(repo)
            missing = [f for f in conflicted if f not in resolutions]
            if missing:
                self._git.run(["merge", "--abort"], cwd=repo, check=False)
                raise OverleafMCPError(
                    f"Missing resolved content for: {', '.join(missing)}. Call "
                    "get_conflicts for base/mine/theirs, then retry with every "
                    "conflicted file covered."
                )

            for name in conflicted:
                self._ws.resolve_in_project(repo, name).write_text(
                    resolutions[name], encoding="utf-8"
                )
                self._git.run(["add", "--", name], cwd=repo)

            self._git.run(
                ["commit", "-m", message or f"Resolve conflict in {', '.join(conflicted)}"],
                cwd=repo,
            )
            push = self._git.push_with_retry(repo)
        return f"Resolved {', '.join(conflicted)} — synced to Overleaf. {push}"

    # -- compile ---------------------------------------------------------

    def compile_project(
        self,
        local_name: str,
        root_file: str | None = None,
        engine: str | None = None,
    ) -> dict:
        repo = self._ws.project_dir(local_name)
        with self._ws.lock(local_name):
            self._git.fast_forward(repo)
            return _compile_project(repo, root_file, engine, self._compile_timeout)

    # -- internal ------------------------------------------------------------

    def _check_binary_size(self, size: int) -> None:
        if size > self._max_binary_bytes:
            limit_mb = self._max_binary_bytes // (1024 * 1024)
            raise FileTooLargeError(
                f"{size} bytes exceeds the {limit_mb} MB limit "
                "(raise OVERLEAF_MCP_MAX_BINARY_MB to change)."
            )
