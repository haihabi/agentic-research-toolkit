# adapters/gemini/

Wires the portable content into **Gemini CLI**.

- MCP: emit `mcpServers` entries for `.gemini/settings.json` from `mcp/*/`.
- Skills: expose each as a custom command (`.gemini/commands/<name>.toml`) or a
  referenced playbook.
- Agents: render `agents/*.md` specs into commands / prompts.
- Context: generate `GEMINI.md` from `AGENTS.md`.

## Servers

- [overleaf](overleaf.md)

<!-- Add: sync script, generated settings.json snippet, commands/, notes. -->
