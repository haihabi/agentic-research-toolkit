"""The local workspace: the directory of cloned projects, name/path validation,
and per-project locks so concurrent tool calls don't race on one working tree.
"""

from __future__ import annotations

import re
import threading
from pathlib import Path

from .errors import PathEscapeError, ProjectExistsError, ProjectNotFoundError

# Name of the per-project directory latexmk writes into. Excluded from git and
# from list_files so build artifacts are never committed or surfaced.
BUILD_DIRNAME = ".build"

_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class Workspace:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.helper_dir = self.root / ".helpers"
        self.helper_dir.mkdir(exist_ok=True)
        self._locks: dict[str, threading.Lock] = {}
        self._locks_guard = threading.Lock()

    def lock(self, name: str) -> threading.Lock:
        with self._locks_guard:
            return self._locks.setdefault(name, threading.Lock())

    def project_dir(self, name: str, *, must_exist: bool = True) -> Path:
        if not _NAME_RE.match(name or ""):
            raise PathEscapeError(
                "Project name must be non-empty and use only letters, digits, "
                "'-' and '_'."
            )
        path = (self.root / name).resolve()
        if path.parent != self.root:
            raise PathEscapeError("Invalid project name.")
        is_repo = (path / ".git").is_dir()
        if must_exist and not is_repo:
            raise ProjectNotFoundError(
                f"No project named '{name}'. Use add_project first."
            )
        if not must_exist and is_repo:
            raise ProjectExistsError(f"'{name}' is already registered.")
        return path

    def resolve_in_project(self, project_dir: Path, rel_path: str) -> Path:
        if not rel_path or rel_path.startswith(("/", "\\")):
            raise PathEscapeError("file_path must be a relative path inside the project.")
        pd = project_dir.resolve()
        target = (pd / rel_path).resolve()
        if target != pd and pd not in target.parents:
            raise PathEscapeError("Path escapes the project directory.")
        rel_parts = target.relative_to(pd).parts
        if ".git" in rel_parts:
            raise PathEscapeError("Refusing to touch the .git directory.")
        if rel_parts and rel_parts[0] == BUILD_DIRNAME:
            raise PathEscapeError(f"'{BUILD_DIRNAME}/' is the local build directory, not a project file.")
        return target

    def list_project_names(self) -> list[str]:
        return sorted(
            entry.name
            for entry in self.root.iterdir()
            if entry.is_dir() and (entry / ".git").is_dir()
        )
