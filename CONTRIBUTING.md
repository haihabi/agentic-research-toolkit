# Contributing

## Core rule: portable content vs. adapters

- **Portable layer** — `mcp/`, `skills/`, `agents/`, `prompts/` — must never name
  a specific host (no "Claude", "Codex", "Gemini", no host-specific paths or
  config keys).
- **Adapter layer** — `adapters/<host>/` — holds every host-specific detail:
  MCP registration snippets, context files, command definitions, symlinks,
  generator scripts.

## Conventions

- **Naming:** kebab-case for directories and for skill / server / agent names.
  The directory (or file) name is the canonical identifier.
- **Every unit has its own `README.md`** stating purpose, inputs/outputs, how to
  run, and dependencies.
- **Each `mcp/<server>` pins its own dependencies.** No repo-wide lockfile.
- **Dependency direction:** `agents/` → `skills/` → `mcp/` / `support/shared/`.
  Never the reverse. Adapters may depend on anything; nothing depends on adapters.
- **Each top-level directory's `README.md` is an index** (a table of its units).
- **`support/`** holds scaffolding, not deliverables: `shared/` (code reused
  across units), `evals/`, `datasets/`, `scripts/`.

## Adding a unit

### MCP server (`mcp/<server-name>/`)

```
README.md            # tools exposed, env vars, run command
pyproject.toml        # or package.json — pinned deps
src/<server_name>/server.py
tests/
```

Then add a registration snippet to each `adapters/<host>/`.

### Skill (`skills/<skill-name>/`)

```
SKILL.md             # frontmatter (name, description) + host-neutral instructions
scripts/             # executable helpers, callable directly by any host
references/           # docs loaded on demand
assets/               # templates, boilerplate
```

Keep the `SKILL.md` body host-neutral prose. Claude Code reads it natively; other
hosts consume it as a playbook via their adapter.

### Agent spec (`agents/<agent-name>.md`)

Neutral frontmatter: `name`, `description`, `tools`, `model`, `skills`, `mcp`.
Adapters translate this into `.claude/agents/*.md`, a Codex prompt, or a Gemini
command.

### Prompt (`prompts/<name>.md`)

Plain Markdown fragment or template. No host-specific syntax.
