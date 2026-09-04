# overleaf → Codex CLI

Add to `~/.codex/config.toml`. Replace the directory with your absolute path to
`mcp/overleaf`. Codex reads the token from the process environment; export
`OVERLEAF_GIT_TOKEN` in the shell that launches Codex, or set it under `env`.

```toml
[mcp_servers.overleaf]
command = "uv"
args = ["run", "--directory", "/abs/path/to/agentic-research-toolkit/mcp/overleaf", "overleaf-mcp"]

[mcp_servers.overleaf.env]
OVERLEAF_GIT_TOKEN = "..."
```

First-time setup:

```bash
cd mcp/overleaf && uv venv && uv pip install -e .
```
