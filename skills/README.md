# skills/

Capabilities. One directory per skill: `skills/<skill-name>/` with a `SKILL.md`
at its root.

The `SKILL.md` **body is host-neutral** — Claude Code auto-discovers it, other
hosts consume the same folder as a playbook via their adapter. `scripts/` are
plain executables any host can call directly.

| Skill | Description | Depends on |
|-------|-------------|------------|
| [paper-review](paper-review/) | Venue-accurate peer review of a paper: research the venue, run a reviewer panel + area-chair merge, emit a venue-style review + point-by-point corrections, and inject `todonotes` into the LaTeX. | `prompts/paper-review-*`, `prompts/review-comment-taxonomy`, `agents/venue-researcher`, `agents/paper-reviewer`, `agents/review-area-chair`, `mcp/overleaf` (Overleaf mode) |
