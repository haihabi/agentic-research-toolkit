# paper-review → Claude Code

Wires the portable `paper-review` skill + its agent specs into Claude Code.

## Skill

Symlink for native auto-discovery:

```bash
ln -s ../../skills/paper-review .claude/skills/paper-review
```

## Agents

Render the specs in `agents/` into `.claude/agents/*.md`. Suggested mapping of
the neutral `model` / `thinking` fields:

| Spec | model | Thinking | Tools |
|---|---|---|---|
| `venue-researcher` | `sonnet` | default | `WebSearch`, `WebFetch`, `Read`, `Write` |
| `paper-reviewer` | see below | see below | `Read`, `WebSearch`, `WebFetch` |
| `review-area-chair` | `opus` | high (ultrathink) | `Read`, `Write` |
| `response-researcher` | `opus` | high (ultrathink) | `Read`, `Write`, `WebSearch`, `WebFetch` — **no `Bash`** |
| `evidence-gatherer` | `sonnet` | default | `Read`, `Grep`, `Glob` (+ `WebSearch`, `WebFetch` in `references` mode) — read-only |

### `paper-reviewer` panel — mixed thinking levels

The N instances run at **different** budgets so the panel behaves like a real
committee. Default N = 3:

| Instance | model | thinking |
|---|---|---|
| R1 (deep) | `opus` | high / ultrathink |
| R2 (medium) | `sonnet` | medium |
| R3 (light) | `sonnet` | low |

For N > 3, cycle deep → medium → light. Reviewers are **never** passed the
`--code` / `--results` / `--refs` paths or the `evidence/` outputs (loop mode) —
their inputs are the paper, the web, and (in rebuttal-eval) the other reviews.

The skill runs in the main session and spawns agents with the `Agent` tool
(`subagent_type` = the rendered agent name). The panel's N reviewers run in
parallel; in loop mode so do their rebuttal-eval calls each round. In loop mode
`review-area-chair` is spawned **once**, after the loop; in static mode it does
the pre-deliverable merge.

## MCP

The `overleaf` MCP server is **required only for Overleaf annotation mode**. Wire
it per `adapters/claude-code/overleaf.md`. Local LaTeX mode and PDF-only mode do
not need it (they need `latexmk` / `latexpand` on `PATH`).

Tools the skill calls in Overleaf mode: `add_project` (once), `sync_project`,
`list_files`, `read_file`, `edit_file`, `get_conflicts`, `resolve_conflict`,
`compile_project`.

## Confirmations

Overleaf mode writes to a live shared project. The skill must show
`annotations.diff` (and, in loop mode, `corrections.diff`) and get an explicit
user "yes" before any `edit_file`, every run. `--dry-run` bypasses all writes.

## Review report Artifact

Both modes: the skill fills `skills/paper-review/assets/review-report-template.html`
with the run's report object and publishes it with the **`Artifact` tool**
(`action: "publish"`). Loop mode passes `capabilities: {db: {}}` so the report's
per-comment Accept / Reject control is live.

## Loop mode curation gate

Step 11L hands control back to the main chat. The user curates on the published
report page; the skill then reads their choices with the `Artifact` tool
(`action: "read_db"`, `db_op: "list"`, `collection: "curation"`) and derives
`curation/decisions.json`. If the report's `db` is unavailable, the user states
choices in chat and the skill writes the file. It must not run step 12L (apply
corrections / build action list) until `curation/decisions.json` exists.
