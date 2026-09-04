"""Test scaffolding: a local bare git repo stands in for git.overleaf.com.

No network, no real token. `file://` remotes never trigger the askpass helper, so
a dummy token is enough to satisfy the auth guard.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from overleaf_mcp.git_sync import Git
from overleaf_mcp.service import OverleafService
from overleaf_mcp.workspace import Workspace

SEED_MAIN_TEX = (
    "\\documentclass{article}\n"
    "\\begin{document}\n"
    "Hello world.\n"
    "\\end{document}\n"
)


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-c", "user.name=seed", "-c", "user.email=seed@example.com", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.fixture
def fake_overleaf(tmp_path: Path) -> Path:
    """A bare repo with one commit (main.tex) on branch `main`. Returns its path."""
    bare = tmp_path / "remote" / "project.git"
    bare.parent.mkdir(parents=True)
    subprocess.run(
        ["git", "init", "--bare", "--initial-branch=main", str(bare)],
        check=True,
        capture_output=True,
    )
    seed = tmp_path / "seed"
    subprocess.run(["git", "clone", str(bare), str(seed)], check=True, capture_output=True)
    (seed / "main.tex").write_text(SEED_MAIN_TEX, encoding="utf-8")
    _git("add", "-A", cwd=seed)
    _git("commit", "-m", "seed", cwd=seed)
    _git("push", "origin", "main", cwd=seed)
    return bare


@pytest.fixture
def service(tmp_path: Path, fake_overleaf: Path) -> OverleafService:
    ws_root = tmp_path / "workspace"
    workspace = Workspace(ws_root)
    git = Git(
        token="dummy-token",
        name="overleaf-mcp",
        email="overleaf-mcp@localhost",
        helper_dir=workspace.helper_dir,
    )
    return OverleafService(
        git,
        workspace,
        max_binary_bytes=1 * 1024 * 1024,  # 1 MB, small enough to test the limit
        compile_timeout=120,
        remote_template=f"file://{fake_overleaf}",
    )


@pytest.fixture
def other_clone(tmp_path: Path, fake_overleaf: Path):
    """A second working clone of the fake remote, for simulating web-editor edits."""
    path = tmp_path / "other"
    subprocess.run(["git", "clone", str(fake_overleaf), str(path)], check=True, capture_output=True)

    def commit_push(rel_path: str, content: str, message: str = "web edit") -> None:
        _git("pull", "--ff-only", cwd=path)
        (path / rel_path).write_text(content, encoding="utf-8")
        _git("add", "-A", cwd=path)
        _git("commit", "-m", message, cwd=path)
        _git("push", "origin", "main", cwd=path)

    commit_push.path = path  # type: ignore[attr-defined]
    return commit_push


def read_remote_file(bare: Path, rel_path: str) -> str:
    """Read a file's content from the bare repo's main branch."""
    return subprocess.run(
        ["git", "show", f"main:{rel_path}"],
        cwd=bare,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
