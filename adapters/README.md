# adapters/

Per-host wiring. Each subdirectory takes the portable content (`mcp/`, `skills/`,
`agents/`, `prompts/`) and makes it usable inside one agent CLI. This is the
**only** place host-specific names, paths, and config formats may appear.

| Adapter          | Host        | Wires up |
|------------------|-------------|----------|
| `claude-code/`   | Claude Code | `.mcp.json`, symlinks into `skills/` & `agents/`, `CLAUDE.md` → `AGENTS.md` |
| `codex/`         | Codex CLI   | `config.toml [mcp_servers]`, `AGENTS.md` usage, prompt exports |
| `gemini/`        | Gemini CLI  | `settings.json mcpServers`, `GEMINI.md`, `commands/*.toml` |

Each adapter has its own `README.md` with install steps and a sync script (in
`scripts/`) that regenerates its artifacts from the portable content.
