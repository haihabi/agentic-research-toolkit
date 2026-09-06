# prompts/

Reusable prompt fragments and templates as plain Markdown — no host-specific
syntax. Skills, agent specs, and adapters compose these.

| Prompt | Purpose |
|--------|---------|
| [paper-review-base.md](paper-review-base.md) | Frozen venue-agnostic reviewer guidance + prompt (Phase 0). |
| [review-comment-taxonomy.md](review-comment-taxonomy.md) | Three-axis taxonomy (category / severity / actionability) + metadata schema for review comments. |
| [venue-profile-template.md](venue-profile-template.md) | Structure `venue-researcher` fills per run with the target venue's specifics. |
| [paper-review-output-spec.md](paper-review-output-spec.md) | Exact shape of deliverables A (venue-style review) and B (point-by-point corrections) + run-folder layout, for both `static` and `loop` modes. |
| [rebuttal-protocol.md](rebuttal-protocol.md) | Rules of the loop-mode author-response loop: stance / reply vocabularies, the transition table, termination, `comment-threads.json` schema. |
| [comment-resolution-states.md](comment-resolution-states.md) | The comment lifecycle state machine and the Group 1 / Group 2 mapping. |
