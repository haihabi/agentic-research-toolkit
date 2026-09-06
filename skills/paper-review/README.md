# paper-review

Produce a conference- or journal-accurate peer review of an academic paper, plus
an actionable point-by-point correction list, plus (when LaTeX source is
available) `todonotes` annotations injected into the paper.

## Inputs

| Input | Required | Notes |
|---|---|---|
| Paper PDF | yes | Read natively. |
| `venue`, `year` | yes | e.g. `NeurIPS 2025`, `ICASSP 2025`, `IEEE Transactions on Signal Processing 2025`. |
| `--mode` | no | `static` (default) or `loop` — see Modes. |
| `track` / subject area | no | Main / findings / workshop name / journal section. |
| LaTeX source | no | Local root/dir, **or** an Overleaf project (via the `overleaf` MCP server). Enables the annotation pass. |
| `N` reviewers | no | Default 3. In loop mode they run at mixed thinking levels. |
| `--code` / `--results` / `--refs` | no | **loop mode only.** Read-only evidence for the author-side `response-researcher`; never shown to reviewers. |
| `--K` | no | loop mode: max author-response rounds (default 2, early-stop on convergence). |
| `--annotate-unresolved` | no | loop mode: also annotate Group 2 comments as greyed `[UNRESOLVED]` notes. |
| `--dry-run` | no | Overleaf mode: compute and show edits, make no commits. |

## Modes

- **`static`** — one pass: reviewer panel → `review-area-chair` merge →
  deliverable A (venue-style review) + deliverable B (point-by-point) → todonotes.
- **`loop`** — adds an author-response rebuttal loop (`response-researcher` +
  `evidence-gatherer` vs. the reviewers, K rounds), an end-of-loop area-chair
  **decision** (accept/reject + why), a split into **Group 1** (agreed &
  applicable → `review-B1`) and **Group 2** (unresolved → `review-B2`), a
  **human curation gate** (you accept/reject each comment), and then real paper
  **corrections** for accepted Group 1 items plus an **`action-list.md`** for
  accepted Group 2 items. Diagram: [`docs/paper-review-system.md`](../../docs/paper-review-system.md).

## Outputs (in `paper-review-<venue><year>-<timestamp>/`)

- `venue-profile.md` — the per-run venue delta (form, scales, decision set,
  checklists, sample-review notes, sources, gaps).
- `review-prompt.md` — the composed tailored prompt.
- `reviews/reviewer-*.md`, `reviews/area-chair.md` — intermediate.
- **`review-A-venue-style.md`** — the review package in the venue's own form
  (meta-review / editor recommendation + individual reviews / referee reports).
- **`review-B-point-by-point.md`** + `review-B.json` — merged, de-duplicated,
  taxonomy-tagged corrections.
- `annotated/` (+ PDF, log) or `overleaf-commits.md` — the LaTeX annotation
  result.
- `review-report.html` + a **published Artifact** — a browsable review dashboard
  (reviewers, comments, and in loop mode the rebuttal threads, Group 1/2 split,
  AC decision, and a live per-comment Accept/Reject curation control).
- `README.md` — run summary with a category × severity count table + the report URL.

## How to run

Portable content only; a per-host adapter drives it (see
`adapters/<host>/paper-review.md` for agent-model wiring and the `overleaf` MCP
requirement). The procedure is in `SKILL.md`.

## Structure

| Path | Purpose |
|---|---|
| `SKILL.md` | The procedure (both modes). |
| `scripts/flatten_latex.sh` | `latexpand` wrapper + section→line map. |
| `scripts/build_annotations.py` | `review-B.json` / `review-B1.json` → LaTeX edit plan + unified diff (`--unresolved` adds greyed `[UNRESOLVED]` notes). |
| `scripts/inject_todonotes.py` | Local mode: annotated copy + `latexmk`. |
| `scripts/thread_state.py` | Loop mode: apply the rebuttal state machine for one round; update `comment-threads.json`. |
| `scripts/apply_corrections.py` | Loop mode: apply user-accepted Group 1 fixes → `corrected/` + `corrections.diff`. |
| `references/prior-art.md` | Phase-0 sources for the base prompt. **Read only when refreshing.** |
| `references/venue-guidance-generic.md` | The map `venue-researcher` fills in. |
| `references/venue-research-checklist.md` | Per-venue-family research checklist. |
| `references/reviewer-personas.md` | Panel emphasis personas. |
| `references/latex-annotation-notes.md` | `todonotes` edge cases. |
| `assets/todonotes-preamble.tex` | Preamble block. |
| `assets/fallback-forms/` | Generic forms when the real one can't be found. |
| `assets/review-report-template.html` | Per-run review dashboard; skill substitutes the run JSON and publishes it as an Artifact (loop mode: with the `db` curation control). |

## Related units

- Prompts: `prompts/paper-review-base.md`, `prompts/review-comment-taxonomy.md`,
  `prompts/venue-profile-template.md`, `prompts/paper-review-output-spec.md`,
  `prompts/rebuttal-protocol.md`, `prompts/comment-resolution-states.md`.
- Agents: `agents/venue-researcher.md`, `agents/paper-reviewer.md`,
  `agents/review-area-chair.md`, `agents/response-researcher.md`,
  `agents/evidence-gatherer.md`.
- Docs: `docs/paper-review-system.md` (system diagram).
- MCP: `mcp/overleaf` (Overleaf annotation mode only).

## Dependencies

- Local LaTeX mode: `latexmk` + a TeX distribution; `latexpand` for flattening.
- Overleaf mode: the `overleaf` MCP server configured with a git token.
- Web access for `venue-researcher`.

## Refreshing the frozen base (Phase 0)

Re-fetch the URLs in `references/prior-art.md`, update `prompts/paper-review-base.md`
and `references/venue-guidance-generic.md`, and bump their `last_reviewed` dates.
Do this yearly or when a cited guideline changes. A normal run never touches these.
