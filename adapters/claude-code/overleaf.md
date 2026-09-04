# overleaf → Claude Code

Add to the project's `.mcp.json` (or `~/.claude.json`). Replace the directory
with your absolute path to `mcp/overleaf`, and supply the token via the
environment rather than committing it.

```json
{
  "mcpServers": {
    "overleaf": {
      "command": "uv",
      "args": ["run", "--directory", "/abs/path/to/agentic-research-toolkit/mcp/overleaf", "overleaf-mcp"],
      "env": { "OVERLEAF_GIT_TOKEN": "${OVERLEAF_GIT_TOKEN}" }
    }
  }
}
```

First-time setup:

```bash
cd mcp/overleaf && uv venv && uv pip install -e .
```
