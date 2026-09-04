"""FastMCP transport layer: one thin tool wrapper per OverleafService method.

All behaviour lives in service.py. Tool docstrings are what the MCP client shows
the model, so they carry the usage guidance.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .config import load_config
from .git_sync import Git
from .service import OverleafService
from .workspace import Workspace

_cfg = load_config()
_ws = Workspace(_cfg.workspace_dir)
_git = Git(_cfg.git_token, _cfg.git_name, _cfg.git_email, _ws.helper_dir)
_svc = OverleafService(
    _git,
    _ws,
    max_binary_bytes=_cfg.max_binary_bytes,
    compile_timeout=_cfg.compile_timeout,
)

mcp = FastMCP("overleaf")


@mcp.tool()
def add_project(overleaf_project_id: str, local_name: str) -> str:
    """Register and clone an Overleaf project so it appears in list_projects.

    Needed once per project. Overleaf's git bridge cannot enumerate your
    projects, so you supply the ID the first time (Overleaf project Menu -> Git,
    or Account Settings -> Git integration).

    overleaf_project_id: the Overleaf project ID.
    local_name: short alias (letters, digits, '-', '_') used by every other tool.
    """
    return _svc.add_project(overleaf_project_id, local_name)


@mcp.tool()
def list_projects() -> list[dict]:
    """List every project currently registered locally."""
    return _svc.list_projects()


@mcp.tool()
def sync_project(local_name: str) -> str:
    """Pull the latest Overleaf changes into the local copy.

    Fails without changing anything if there is a real merge conflict; use
    get_conflicts / resolve_conflict in that case.
    """
    return _svc.sync_project(local_name)


@mcp.tool()
def list_files(local_name: str, subdir: str = "") -> list[str]:
    """List files in the project (optionally under a subdirectory), syncing first."""
    return _svc.list_files(local_name, subdir)


@mcp.tool()
def read_file(local_name: str, file_path: str) -> str:
    """Read a UTF-8 text file, syncing the latest Overleaf changes first."""
    return _svc.read_file(local_name, file_path)


@mcp.tool()
def read_binary_file(local_name: str, file_path: str) -> dict:
    """Read a binary file (figure, PDF, ...), returned base64-encoded.

    Fails if the file is larger than the configured limit
    (OVERLEAF_MCP_MAX_BINARY_MB, default 25).
    """
    return _svc.read_binary_file(local_name, file_path)


@mcp.tool()
def edit_file(
    local_name: str, file_path: str, content: str, message: str | None = None
) -> str:
    """Overwrite an existing text file, then sync to Overleaf.

    Pulls remote changes first, commits, and pushes. If a real merge conflict is
    found, nothing is applied and the call fails.
    """
    return _svc.edit_file(local_name, file_path, content, message)


@mcp.tool()
def add_file(
    local_name: str, file_path: str, content: str, message: str | None = None
) -> str:
    """Create a new text file (and any parent directories), then sync to Overleaf."""
    return _svc.add_file(local_name, file_path, content, message)


@mcp.tool()
def add_binary_file(
    local_name: str, file_path: str, content_base64: str, message: str | None = None
) -> str:
    """Create or replace a binary file from base64 content, then sync to Overleaf.

    Fails if the decoded size exceeds OVERLEAF_MCP_MAX_BINARY_MB (default 25).
    """
    return _svc.add_binary_file(local_name, file_path, content_base64, message)


@mcp.tool()
def delete_file(local_name: str, file_path: str, message: str | None = None) -> str:
    """Delete a file from the project, then sync to Overleaf."""
    return _svc.delete_file(local_name, file_path, message)


@mcp.tool()
def move_file(
    local_name: str, src_path: str, dst_path: str, message: str | None = None
) -> str:
    """Rename/move a file, preserving history in a single commit, then sync."""
    return _svc.move_file(local_name, src_path, dst_path, message)


@mcp.tool()
def get_conflicts(local_name: str) -> dict:
    """Check whether syncing would conflict, without leaving a half-merged state.

    If clean, applies the sync and reports no conflicts. If it conflicts, aborts
    and returns, per file, the common-ancestor ("base"), local ("mine"), and
    Overleaf ("theirs") versions. Build a resolved version of each, then call
    resolve_conflict with all of them.
    """
    return _svc.get_conflicts(local_name)


@mcp.tool()
def resolve_conflict(
    local_name: str, resolutions: dict[str, str], message: str | None = None
) -> str:
    """Apply resolved content for every conflicted file and sync to Overleaf.

    resolutions maps file_path -> final content and must cover EVERY file
    get_conflicts reported; otherwise nothing is applied and the missing names
    are returned.
    """
    return _svc.resolve_conflict(local_name, resolutions, message)


@mcp.tool()
def compile_project(
    local_name: str, root_file: str | None = None, engine: str | None = None
) -> dict:
    """Build the project to PDF locally with latexmk and return the result.

    Syncs first, then compiles into a git-excluded .build/ directory. Returns
    success, pdf_path, duration_s, parsed errors, and the tail of the log.
    root_file/engine are auto-detected when omitted. Requires a TeX distribution
    with latexmk on the host; its toolchain may differ from Overleaf's.
    """
    return _svc.compile_project(local_name, root_file, engine)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
