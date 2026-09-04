# agentic-research-toolkit

Host-neutral utilities for doing research with agents — MCP servers, skills,
agent specs, and prompts — plus per-host adapters for **Claude Code**,
**Codex CLI**, and **Gemini CLI**.

## Design

Two layers:

1. **Portable content** — authored once, no reference to any specific host:
   `mcp/`, `skills/`, `agents/`, `prompts/`.
2. **Adapters** — the only host-specific code: `adapters/<host>/` wires the
   portable content into one CLI (MCP registration, context files, command
   definitions, symlinks).

Rule: nothing under the portable layer may name a host. All host knowledge lives
in `adapters/`.

## Layout

| Path              | Contents |
|-------------------|----------|
| `AGENTS.md`       | Canonical agent instructions (host-neutral). Per-host pointers live in adapters. |
| `mcp/`            | MCP servers, one self-contained directory per server. Portable across all hosts. |
| `skills/`         | Capabilities: a host-neutral `SKILL.md` body plus `scripts/` and `references/`. |
| `agents/`         | Agent specs in a neutral schema, one Markdown file per agent. |
| `prompts/`        | Reusable prompt fragments and templates. |
| `adapters/`       | Per-host wiring: `claude-code/`, `codex/`, `gemini/`. |
| `support/`        | Scaffolding, not deliverables: `shared/`, `evals/`, `datasets/`, `scripts/`. |
| `docs/`           | Design notes, architecture, decisions. |

## Host support matrix

| Unit         | Claude Code            | Codex CLI                   | Gemini CLI                  |
|--------------|------------------------|-----------------------------|----------------------------|
| MCP servers  | `.mcp.json`            | `config.toml [mcp_servers]` | `settings.json mcpServers` |
| Skills       | native auto-discovery  | consumed as a playbook      | consumed as a playbook / command |
| Agent specs  | `.claude/agents/*.md`  | inlined into a prompt       | custom command / prompt    |
| Context file | `CLAUDE.md` / `AGENTS.md` | `AGENTS.md`               | `GEMINI.md`                |

See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions.

## License

[Apache-2.0](LICENSE).
