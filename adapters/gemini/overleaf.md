# overleaf → Gemini CLI

Add to `.gemini/settings.json` (project) or `~/.gemini/settings.json` (global).
Replace the directory with your absolute path to `mcp/overleaf`. `$OVERLEAF_GIT_TOKEN`
is expanded from the environment.

```json
{
  "mcpServers": {
    "overleaf": {
      "command": "uv",
      "args": ["run", "--directory", "/abs/path/to/agentic-research-toolkit/mcp/overleaf", "overleaf-mcp"],
      "env": { "OVERLEAF_GIT_TOKEN": "$OVERLEAF_GIT_TOKEN" }
    }
  }
}
```

First-time setup:

```bash
cd mcp/overleaf && uv venv && uv pip install -e .
```
