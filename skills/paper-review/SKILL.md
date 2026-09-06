---
name: paper-review
description: >
  Produce a conference- or journal-accurate peer review of an academic paper.
  Given a paper (PDF, or PDF plus LaTeX source) and a target venue and year, it
  researches that venue's actual review process, composes a venue-specific review
  prompt from a frozen base, and runs the review in one of two modes: `static`
  (a reviewer panel + area-chair merge → a venue-style review package + a
  taxonomy-tagged point-by-point list), or `loop` (adds an author-response
  rebuttal loop, an end-of-loop area-chair decision, a split into agreed vs.
  unresolved comments, a human curation gate, and then real paper corrections
  plus an action list). When LaTeX source is available it injects the
  corrections as todonotes and checks the paper still compiles — local copy or
  Overleaf project.
---

# Paper review

## When to use

The user wants a paper reviewed the way a program committee or journal would
review it, and/or wants an actionable list of fixes. Inputs: a paper PDF; the
target venue and year; optionally the LaTeX source (local directory or an
Overleaf project); optionally a track / subject area.

## Modes

`--mode {static | loop}` (default `static`).

- **`static`** — steps 1–9 below. One pass: panel → `review-area-chair` **merge**
  → deliverables A + B → todonotes from `review-B.json`.
- **`loop`** — steps 1–5, then the "Loop mode" section. Adds the author-response
  loop, the end-of-loop AC decision, the Group 1 / Group 2 split, a curation
  gate, and applied corrections + an action list. **No pre-loop merge**; reviews
  stay per-reviewer; the AC is invoked once, at the end.

## Two layers

- **Frozen base (do not regenerate per run):** `prompts/paper-review-base.md`,
  `prompts/review-comment-taxonomy.md`, `prompts/paper-review-output-spec.md`,
  and `references/*.md`. Authored once from `references/prior-art.md`. Refresh
  deliberately (yearly, or when a cited guideline changes) and bump the
  `last_reviewed` dates.
- **Per run:** everything else. Only the target submission's venue specifics are
  researched, into a thin `venue-profile.md`.

## Procedure

### 1. Collect inputs and set up the run folder

- Required: paper PDF path; `venue`; `year`.
- Optional: `track`; LaTeX source as either a local root/dir or an Overleaf
  project (`local_name` already registered with the `overleaf` MCP server, or an
  Overleaf project id — call `add_project` once); `N` reviewers (default 3);
  `--dry-run` (Overleaf mode: compute and show edits, make no commits).
- Create `paper-review-<venue><year>-<UTC-timestamp>/` (see the run-folder
  layout in `prompts/paper-review-output-spec.md`).

### 2. Ingest the paper

- Read the PDF.
- If LaTeX source is **local**: run `scripts/flatten_latex.sh <root.tex>` to get
  a flattened file and a `section → file:line` map.
- If LaTeX source is on **Overleaf**: `sync_project`, then `list_files` +
  `read_file` for each `.tex`; build the same `section → file:line` map from the
  fetched contents.
- If no LaTeX: work from the PDF; comment locations use section + page only and
  the annotation pass (step 8) is skipped.

### 3. Research the venue delta

Spawn the `venue-researcher` agent with: `venue`, `year`, `track`, the paper's
title/abstract, `references/venue-guidance-generic.md`, and
`references/venue-research-checklist.md`. It returns a filled
`prompts/venue-profile-template.md` → save as `venue-profile.md` in the run
folder. It must cite a URL per line and list gaps honestly. If the review form
could not be found, it names the matching `assets/fallback-forms/` file; copy
that into the profile and flag it.

### 4. Compose the tailored prompt

Concatenate, in this order, into `review-prompt.md` in the run folder:

1. `prompts/paper-review-base.md`
2. `venue-profile.md` (this run's)
3. `prompts/review-comment-taxonomy.md`
4. `prompts/paper-review-output-spec.md` (the "Per-reviewer output" section)

Add a one-paragraph header naming the paper, venue, year, track, and `venue_type`.

### 5. Run the reviewer panel

Spawn `N` `paper-reviewer` agents (strong model, high/max thinking). Each gets
`review-prompt.md`, the paper (PDF and, if available, the flattened LaTeX), and
one emphasis persona from `references/reviewer-personas.md` (P1, P2, P3, then
repeat P1, P2 …). Each does a reflection pass and returns per-reviewer output per
the spec. Save as `reviews/reviewer-<i>.md`. For a paper too long for one
context, instruct the agent to read it in section chunks.

### 6. Area chair / editor merge  *(static mode only)*

Spawn `review-area-chair` with: `review-prompt.md`, all `reviews/reviewer-*.md`,
the paper, and `venue-profile.md`. It (a) does its own independent full read
(the holistic "single strong reviewer" pass), (b) merges: de-duplicates
overlapping comments, reconciles contradictions, unions severities/actionability,
records all contributing reviewers in `raised_by`, (c) produces a recommendation
in the venue's decision vocabulary (rating band for a conference; editorial
decision for a journal). Save as `reviews/area-chair.md`.

### 7. Write deliverables A and B

Per `prompts/paper-review-output-spec.md`:

- `review-A-venue-style.md` — A/conference or A/journal layout by `venue_type`;
  meta-review / editor recommendation first, then each reviewer's review /
  referee report in the venue's own fields and scales. Flag fallback-form use.
- `review-B-point-by-point.md` + `review-B.json` — the merged correction list,
  ordered by severity then document position, with the count summary header.

### 8. LaTeX annotation (only if LaTeX source is available)

- `python scripts/build_annotations.py review-B.json --source <root-or-map>` →
  an ordered edit list + the preamble edit + `annotations.diff` (the unified
  diff). With `--dry-run` it stops here.
- **Local mode:** `python scripts/inject_todonotes.py` copies the tree to
  `annotated/`, applies the edits, runs `latexmk -pdf -interaction=nonstopmode`.
  Record pass/fail, log path, PDF path.
- **Overleaf mode:** show `annotations.diff` and **ask the user to confirm**
  (writes push to the live shared project). On confirm, apply via the `overleaf`
  MCP: one `edit_file` per annotated `.tex` (commit message
  `paper-review: todonotes (<n> notes) [run <timestamp>]`) and one `edit_file`
  for the preamble line. If a call fails with a conflict, run `get_conflicts` /
  `resolve_conflict` and retry. Then `compile_project`. Write
  `overleaf-commits.md` with the commit list and the revert recipe.
- Consult `references/latex-annotation-notes.md` for class-specific handling
  (IEEEtran/llncs → inline-only; beamer → skip annotation, deliverable B only).

### 9. Run summary

Write `README.md` in the run folder: links to every artifact; the count table
(category × severity); the recommendation / decision; unanchored items;
(Overleaf mode) commits made and how to undo them; anything the venue profile
could not resolve.

### 10. Review report Artifact  *(both modes)*

Author a per-run HTML report from `skills/paper-review/assets/review-report-template.html`:
build the report object (schema in `prompts/paper-review-output-spec.md` →
"Review report Artifact") from the run's JSON, substitute it into
`<script id="report-data">`, save the result as `review-report.html` in the run
folder, and **publish it as an Artifact**.

- Static mode: publish with no capabilities.
- Loop mode: publish with `capabilities: {db: {}}` so the per-comment
  Accept / Reject curation control is live (see step 11L).

Put the published URL in the run `README.md`.

---

## Loop mode (`--mode loop`)

Run steps 1–5, then:

### Extra inputs (step 1)

`--code <repo>`, `--results <dir>`, `--refs <bib | dir of PDFs>` (all optional,
**read-only**, never shown to reviewers); `--K <n>` (default 2);
`--annotate-unresolved`. Step 5 keeps the N reviews **separate**
(`reviews/reviewer-<i>.md`), comment ids `R<i>-<nn>`. Step 6 (merge) is skipped.

### 7L. Author-response loop (K rounds, early-stop, no area chair)

Read `prompts/rebuttal-protocol.md` and `prompts/comment-resolution-states.md`.
For `k = 1..K`:

1. Spawn `response-researcher` with all `reviews/reviewer-*.md`, the paper, every
   prior `rebuttal/round-*/`, and the evidence source paths. It spawns
   `evidence-gatherer` (read-only) as needed — save each result to
   `evidence/<type>-<nn>.md`. It writes `rebuttal/round-<k>/rebuttal.md`.
2. Spawn the same N `paper-reviewer` instances in **rebuttal-eval mode** (same
   assigned thinking levels; inputs = paper + web + **all** reviews and replies;
   never the evidence paths). Each writes
   `rebuttal/round-<k>/reviewer-<i>-reply.md`. Parallel.
3. Convert this round's `rebuttal.md` + replies to `stances.json` / `replies.json`
   and run
   `python scripts/thread_state.py --threads rebuttal/comment-threads.json
   --round <k> --K <K> [--init round0-comments.json] --stances … --replies …`.
   It prints `{changed, terminal, remaining, stopped_because}`.
4. Stop when `stopped` is true (`converged` / `no-change` / `K-reached`).
5. After the last round, spawn each `paper-reviewer` once more for its
   `reviews/reviewer-<i>-post-rebuttal.md` (score deltas).

**No todonotes are written in this step.**

### 8L. Area chair: discussion + final decision (single invocation)

Spawn `review-area-chair` in **end-of-loop decision mode** with all reviews, the
full `rebuttal/` tree, `comment-threads.json`, the post-rebuttal updates,
`venue-profile.md`. It writes `rebuttal/discussion-log.md`, adjudicates every
contested comment, issues the **final decision (accept / reject** in the venue's
vocabulary**)** with a rationale citing comment ids, and sets each thread's
`group` / `group_reason` (grouping near-duplicates).

### 9L. Draft deliverables

Per the "Loop mode outputs" section of `prompts/paper-review-output-spec.md`:
`review-A-venue-style.md` (opens with the decision + rationale),
`response-to-reviewers.md`, `review-B1-agreed-corrections.md` + `review-B1.json`
(only `accepted`; each with its `final_fix`, and a `patch` when the fix is a
self-contained text change), `review-B2-unresolved.md` + `review-B2.json`.

### 10L. Annotate the paper for review (once)

`python scripts/build_annotations.py review-B1.json --source <root-or-map>
[--unresolved review-B2.json]`, then `inject_todonotes.py` (local) or the
`overleaf` MCP edits (as in static step 8, with the same confirmation).

### 10.5L. Publish the review report Artifact

As in step 10 (both modes) but with `capabilities: {db: {}}`, so the report page
carries a live per-comment Accept / Reject curation control. The report includes
the rebuttal threads, the Group 1 / Group 2 split, the AC decision, and the draft
`response-to-reviewers` letter.

### 11L. Curation gate — hand back to the main chat

Show the user the published report URL and the annotated PDF, and ask them to
mark each Group 1 / Group 2 comment **accept** / **reject**.

- Preferred: they curate on the report page; the skill then reads it back with
  `Artifact` `action: "read_db"` (`db_op: "list"`, `collection: "curation"`) and
  writes `curation/decisions.json`.
- Fallback (report `db` unavailable, or user prefers chat): the user states
  their choices in chat and the skill writes `curation/decisions.json` directly.

**Do not proceed to 12L without `curation/decisions.json`.**

### 12L. Apply

- `python scripts/apply_corrections.py --b1 review-B1.json --decisions
  curation/decisions.json --source <src> --out-dir <run>` → `corrected/` +
  `corrections.diff`, compiled (local). Overleaf: run with `--emit-plan`, show
  the diff, confirm, apply via `edit_file`, `compile_project`, write
  `overleaf-commits.md`. Items with no `patch` are listed as "needs manual edit".
- Build `action-list.md` from the user-accepted Group 2 items.

### 13L. Run summary

`README.md`: `--mode loop`, `K`, rounds run, `stopped_because`, oscillation
count, the AC decision, the comment × state × group × user-decision table, links
to `corrected/` and `action-list.md`, and any "needs manual edit" items.

## Guardrails

- Never fabricate references, results, quotes, or venue facts. Unfound venue
  details are "not found" in the profile, not guessed.
- The reviewer agents must not receive a bias instruction.
- Overleaf writes require explicit user confirmation every run; `--dry-run`
  never writes.
- Keep author identity out of the review even if the venue is single-blind and
  the authors are guessable.
- **Loop mode:** reviewers never receive `--code` / `--results` / `--refs` or the
  `evidence/` outputs — only `response-researcher` and `evidence-gatherer` do,
  read-only. No `todonotes` before step 10L. The curation gate (11L) is a hard
  stop — no corrections are applied without `curation/decisions.json`. `apply_corrections.py`
  and the Overleaf edits only touch items the user accepted.

## Host notes

Model/thinking-budget assignments and MCP wiring are host-specific and live in
the per-host adapter (`adapters/<host>/paper-review.md`). The `overleaf` MCP
server is required only for Overleaf mode; local mode needs a TeX installation
with `latexmk` and (for flattening) `latexpand`.
