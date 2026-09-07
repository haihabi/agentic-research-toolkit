# paper-review

Produce a venue- and field-accurate peer review of an academic paper — ML
conference, IEEE / society conference, journal, security venue, theory venue, or
workshop — plus an actionable point-by-point correction list, plus (when LaTeX
source is available) `todonotes` annotations injected into the paper.

## Inputs

| Input | Required | Notes |
|---|---|---|
| Paper PDF | yes | Read natively. |
| `venue`, `year` | yes | e.g. `NeurIPS 2025`, `ICASSP 2025`, `IEEE Transactions on Signal Processing 2025`. |
| `--field` | yes* | Paper type: `empirical-ml`, `theory-proofs`, `systems-measurement`, `signal-processing-eng`, `hci-qualitative`, `dataset-benchmark`, `applied-clinical`, `position-survey`. *If omitted, the skill proposes one from the title/abstract and asks — it never defaults to `empirical-ml`. Schema: `prompts/field-profile-spec.md`. |
| `--mode` | no | `static` (default) or `loop` — see Modes. |
| `track` / subject area | no | Main / findings / workshop name / journal section. |
| LaTeX source | no | Local root/dir, **or** an Overleaf project (via the `overleaf` MCP server). Enables the annotation pass. |
| `N` reviewers | no | Default 3. In loop mode they run at mixed thinking levels. |
| `--code` / `--results` / `--refs` | no | **loop mode only.** Read-only evidence for the author-side `response-researcher`; never shown to reviewers. |
| `--K` | no | loop mode: max author-response rounds (default 2, early-stop on convergence). |
| `--annotate-unresolved` | no | loop mode: also annotate Group 2 comments as greyed `[UNRESOLVED]` notes. |
| `--dry-run` | no | Overleaf mode: compute and show edits, make no commits. |

## Concrete fixes

Every review comment carries a **typed `fix`** (`prompts/review-comment-taxonomy.md`):
`kind: edit` with the **verbatim** current text and its replacement;
`kind: work_spec` with a concrete design and an `acceptance` test (the specific
result that resolves the comment); `kind: response_text`; or `kind: question`
with per-answer branches. `scripts/check_fixes.py` fails the run on vague or
unanchored fixes.

## Challenge & re-review (post-run, user-triggered)

- **`challenge <id>: <argument>`** — dispute a comment; `response-researcher`
  argues your point with the owning reviewer for up to `--J` (default 2) rounds;
  the comment ends `accepted` (revised `fix`), `rebutted`, or `challenged-upheld`.
- **`re-review`** — after you apply edits, re-run steps 5–10 on the revised paper
  (reusing the venue/field profiles); produces `cycle-<n+1>/` with a
  `reconciliation.md` (prior comments `resolved` / `persists` / `new`). Runs only
  when you ask; a re-review never auto-follows an apply.

## Modes

- **`static`** — one pass: reviewer panel → `review-area-chair` **synthesis**
  (full merge for `panel-plus-metareviewer`; editor summary with binding/advisory
  tags for `editor-mediated-referees`; light note for a workshop; per-round
  decision for `rolling-revision`) → deliverable A (venue-style review) +
  deliverable B (point-by-point) → todonotes.
- **`loop`** — adds an author-response stage, routed by the venue's
  `response_routing`: a reviewer-visible K-round rebuttal
  (`response-researcher` + `evidence-gatherer` vs. the reviewers), **or** a
  single chair-mediated pass for venues that don't share the response with
  reviewers (IEEE / SPS), **or** an editor-mediated revision round. Then an
  end-of-loop **decision** in the venue's own vocabulary, a split into **Group 1**
  (agreed & applicable → `review-B1`) and **Group 2** (unresolved →
  `review-B2`), a **human curation gate**, and then real paper **corrections**
  for accepted Group 1 items plus an **`action-list.md`** for accepted Group 2
  items. Diagram: [`docs/paper-review-system.md`](../../docs/paper-review-system.md).

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
| `scripts/thread_state.py` | Loop / challenge: apply the rebuttal state machine for one round (`--mediator chair` for chair-only venues). |
| `scripts/check_fixes.py` | Validate that every comment carries a well-formed typed `fix`; `edit.find` strings occur in the source. Gate before deliverable B is finalised. |
| `scripts/apply_corrections.py` | Apply user-accepted `fix.kind: edit` items → `corrected/paper_v<n>/` + `corrections.diff`; route `work_spec` items to `action-list.md`. |
| `references/prior-art.md` | Phase-0 sources for the base prompt (balanced across venue families). **Read only when refreshing.** |
| `references/field-profiles/*.md` | Per-paper-type profiles: what validity / evidence / novelty mean. One is chosen per run by `--field`. |
| `references/venue-guidance-generic.md` | The map `venue-researcher` fills in, incl. `process_model`. |
| `references/venue-research-checklist.md` | Per-venue-family research checklist. |
| `references/reviewer-personas.md` | Panel emphasis personas (specialised by the field profile). |
| `references/latex-annotation-notes.md` | `todonotes` edge cases. |
| `assets/todonotes-preamble.tex` | Preamble block. |
| `assets/fallback-forms/` | Generic forms when the real one can't be found. |
| `assets/review-report-template.html` | Per-run review dashboard; skill substitutes the run JSON and publishes it as an Artifact (loop mode: with the `db` curation control). |

## Related units

- Prompts: `prompts/paper-review-base.md`, `prompts/field-profile-spec.md`,
  `prompts/review-comment-taxonomy.md`, `prompts/venue-profile-template.md`,
  `prompts/paper-review-output-spec.md`, `prompts/rebuttal-protocol.md`,
  `prompts/comment-resolution-states.md`.
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

Re-fetch the URLs in `references/prior-art.md` (kept balanced across venue
families — ML conf, IEEE conf, journals, security, theory, social science),
update `prompts/paper-review-base.md`, `references/field-profiles/*.md`, and
`references/venue-guidance-generic.md`, and bump their `last_reviewed` dates. Do
this yearly or when a cited guideline changes. A normal run never touches these.
