"""Startup configuration, read once from the environment.

The git token is read here and nowhere else. It is never accepted as a tool
argument and never echoed in a tool result.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_data_dir

_APP = "overleaf-mcp"


@dataclass(frozen=True)
class Config:
    git_token: str | None
    workspace_dir: Path
    git_name: str
    git_email: str
    max_binary_bytes: int
    compile_timeout: int


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}.") from exc
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}.")
    return value


def load_config() -> Config:
    ws_env = os.environ.get("OVERLEAF_MCP_WORKSPACE")
    workspace = (
        Path(ws_env).expanduser().resolve()
        if ws_env
        else Path(user_data_dir(_APP, _APP)).resolve()
    )
    return Config(
        git_token=(os.environ.get("OVERLEAF_GIT_TOKEN") or None),
        workspace_dir=workspace,
        git_name=os.environ.get("OVERLEAF_MCP_GIT_NAME", "overleaf-mcp"),
        git_email=os.environ.get("OVERLEAF_MCP_GIT_EMAIL", "overleaf-mcp@localhost"),
        max_binary_bytes=_int_env("OVERLEAF_MCP_MAX_BINARY_MB", 25) * 1024 * 1024,
        compile_timeout=_int_env("OVERLEAF_MCP_COMPILE_TIMEOUT", 120),
    )
