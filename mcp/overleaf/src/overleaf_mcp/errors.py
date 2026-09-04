"""Expected, user-facing error types.

Anything that subclasses OverleafMCPError is a clean, explained failure that the
MCP client should show to the user as-is. Everything else is a bug.
"""

from __future__ import annotations


class OverleafMCPError(RuntimeError):
    """Base class for expected, user-facing errors."""


class TokenMissingError(OverleafMCPError):
    """OVERLEAF_GIT_TOKEN was needed for a network operation but is not set."""


class ProjectNotFoundError(OverleafMCPError):
    """No locally registered project with the given name."""


class ProjectExistsError(OverleafMCPError):
    """A project with the given local name is already registered."""


class PathEscapeError(OverleafMCPError):
    """A file path or project name would escape its allowed directory."""


class FileTooLargeError(OverleafMCPError):
    """A binary read/write exceeds the configured size limit."""


class GitCommandError(OverleafMCPError):
    """A git subprocess exited non-zero. The message is token-redacted."""


class CompileError(OverleafMCPError):
    """latexmk is unavailable, misconfigured, or timed out."""


class MergeConflictError(OverleafMCPError):
    """Syncing hit a real conflict; the merge was aborted and nothing applied."""

    def __init__(self, files: list[str]):
        self.files = files
        listed = ", ".join(files) if files else "unknown files"
        super().__init__(
            f"Couldn't sync automatically — changes on Overleaf conflict with local "
            f"edits in: {listed}. Nothing was applied. Call get_conflicts for the "
            f"base/mine/theirs of each file, then resolve_conflict with all of them."
        )
