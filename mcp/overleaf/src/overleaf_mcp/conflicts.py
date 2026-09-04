"""Conflict inspection: attempt a merge, and if it conflicts, pull out the
common-ancestor / local / remote version of every conflicted file, then abort
so the working tree is left exactly as it was.
"""

from __future__ import annotations

from pathlib import Path

from .git_sync import Git


def three_way_versions(git: Git, repo: Path, file_path: str) -> dict[str, str | None]:
    """base = common ancestor, mine = local, theirs = remote.

    A side is None when the file did not exist there (e.g. added on one side only).
    """

    def show(stage: int) -> str | None:
        r = git.run(["show", f":{stage}:{file_path}"], cwd=repo, check=False)
        return r.stdout if r.returncode == 0 else None

    return {"base": show(1), "mine": show(2), "theirs": show(3)}


def attempt_merge(git: Git, repo: Path) -> dict:
    """Fetch + merge.

    Clean  -> {"conflicted": False}. The merge commit is kept: it is just a
              normal sync from Overleaf.
    Conflict -> the merge is aborted (working tree untouched) and this returns
              {"conflicted": True, "files": {path: {base, mine, theirs}}}.
    """
    git.fetch(repo)
    branch = git.current_branch(repo)
    merge = git.run(["merge", "--no-edit", f"origin/{branch}"], cwd=repo, check=False)
    if merge.returncode == 0:
        return {"conflicted": False}
    files = git.conflicted_files(repo)
    details = {f: three_way_versions(git, repo, f) for f in files}
    git.run(["merge", "--abort"], cwd=repo, check=False)
    return {"conflicted": True, "files": details}
