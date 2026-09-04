# adapters/claude-code/

Wires the portable content into **Claude Code**.

- MCP: generate/append `.mcp.json` entries from `mcp/*/`.
- Skills: symlink `.claude/skills/<name>` → `../../skills/<name>` (native
  auto-discovery).
- Agents: render `agents/*.md` specs into `.claude/agents/*.md`.
- Context: symlink `CLAUDE.md` → `AGENTS.md`.

## Servers

- [overleaf](overleaf.md)

<!-- Add: install.sh / sync script, generated .mcp.json snippet, notes. -->
