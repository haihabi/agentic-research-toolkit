# agents/

Agent specs in a host-neutral schema. One Markdown file per agent:
`agents/<agent-name>.md`.

Frontmatter fields: `name`, `description`, `tools`, `model`, `skills`, `mcp`.
Adapters translate a spec into `.claude/agents/*.md`, a Codex prompt, or a Gemini
command.

| Agent | When to use | Skills / MCP assumed |
|-------|-------------|----------------------|
| [venue-researcher](venue-researcher.md) | Fill a venue profile for a target conference/journal/workshop before a review. | `paper-review` |
| [paper-reviewer](paper-reviewer.md) | Produce one reviewer's structured review + tagged comments; in loop mode also evaluate the authors' rebuttal per comment. | `paper-review` |
| [review-area-chair](review-area-chair.md) | Static: independent read + merge a panel into deliverables A and B. Loop: end-of-loop discussion + final accept/reject + Group 1/2 partition. | `paper-review` |
| [response-researcher](response-researcher.md) | Author-side responder in the loop: per-comment stance + concrete fix or evidence-backed argument each round. | `paper-review` |
| [evidence-gatherer](evidence-gatherer.md) | Read-only fact-check of a review comment against the authors' code / results / references. | `paper-review` |
