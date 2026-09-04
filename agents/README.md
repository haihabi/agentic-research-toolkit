# agents/

Agent specs in a host-neutral schema. One Markdown file per agent:
`agents/<agent-name>.md`.

Frontmatter fields: `name`, `description`, `tools`, `model`, `skills`, `mcp`.
Adapters translate a spec into `.claude/agents/*.md`, a Codex prompt, or a Gemini
command.

| Agent | When to use | Skills / MCP assumed |
|-------|-------------|----------------------|
| _(none yet)_ | | |
