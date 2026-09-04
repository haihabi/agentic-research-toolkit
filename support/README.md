# support/

Scaffolding, not deliverables. Nothing here is a unit the toolkit ships; it
exists to build, test, and feed the units in `mcp/`, `skills/`, `agents/`, and
`prompts/`.

| Path         | Contents |
|--------------|----------|
| `shared/`    | Code reused across servers, skills, and scripts (clients, schemas, prompt fragments). |
| `evals/`     | Eval suites for the units in this repo. |
| `datasets/`  | Fixtures and research corpora. |
| `scripts/`   | Setup, run, and sync/generate helpers. |

Dependency direction: `agents/` → `skills/` → `mcp/` / `support/shared/`. Never
the reverse.
