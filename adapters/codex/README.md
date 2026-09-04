# adapters/codex/

Wires the portable content into **Codex CLI**.

- MCP: emit `[mcp_servers.<name>]` blocks for `~/.codex/config.toml` from `mcp/*/`.
- Skills: no native discovery — export each `SKILL.md` body as a reference doc or
  prompt the agent can be pointed at.
- Agents: inline `agents/*.md` specs into a prompt (no first-class subagents).
- Context: `AGENTS.md` at repo root is read natively.

## Servers

- [overleaf](overleaf.md)

<!-- Add: sync script, generated config.toml snippet, notes. -->
