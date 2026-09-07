---
name: paper-review
description: >
  Produce a venue- and field-accurate peer review of an academic paper — for an
  ML conference, an IEEE conference, a society or multidisciplinary journal, a
  security venue, a theory venue, or a workshop. Given a paper (PDF, or PDF plus
  LaTeX source), a target venue and year, and a paper-type (`--field`), it
  researches that venue's actual review process and `process_model`, composes a
  review prompt from a frozen base + a field profile + the per-run venue profile,
  and runs the review in one of two modes: `static` (a reviewer panel, then an
  area-chair / editor synthesis appropriate to the process model → a venue-style
  review package + a taxonomy-tagged point-by-point list), or `loop` (adds an
  author-response stage routed the way the venue routes it — reviewer-visible
  rebuttal, chair-only response, or an editor-mediated revision round — an
  end-of-loop decision, a split into agreed vs. unresolved comments, a human
  curation gate, and then real paper corrections plus an action list). When LaTeX
  source is available it injects the corrections as todonotes and checks the
  paper still compiles — local copy or Overleaf project.
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

## Three layers

- **Frozen base (do not regenerate per run):** `prompts/paper-review-base.md`
  (venue- and field-agnostic conduct + substance), `prompts/review-comment-taxonomy.md`,
  `prompts/paper-review-output-spec.md`, `prompts/field-profile-spec.md`, and
  `references/*.md` (including `references/field-profiles/*.md`). Authored once
  from `references/prior-art.md`. Refresh deliberately (yearly, or when a cited
  guideline changes) and bump the `last_reviewed` dates.
- **Field profile (frozen, one chosen per run):** exactly one
  `references/field-profiles/<slug>.md`, selected by `--field`. Defines what
  validity, evidence, and novelty mean for *this kind of paper* (see
  `prompts/field-profile-spec.md`).
- **Per run:** everything else. Only the target submission's venue specifics are
  researched, into a thin `venue-profile.md` — including the venue's
  `process_model`, which drives the synthesis step and the loop.

## Procedure

### 1. Collect inputs and set up the run folder

- Required: paper PDF path; `venue`; `year`.
- **`--field <slug>`** — the paper type, one of the slugs in
  `prompts/field-profile-spec.md` (`empirical-ml`, `theory-proofs`,
  `systems-measurement`, `signal-processing-eng`, `hci-qualitative`,
  `dataset-benchmark`, `applied-clinical`, `position-survey`). If not given,
  read the title + abstract, propose the best-fit slug **and one sentence of
  why**, and ask the user to confirm or override before proceeding. Never
  silently default to `empirical-ml`. Copy the chosen
  `references/field-profiles/<slug>.md` into the run folder as `field-profile.md`.
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
folder. It must cite a URL per line and list gaps honestly. Required fields it
must resolve (or record as `not found` with the fallback consequence):

- **`process_model`** — one of `panel-plus-metareviewer` (ML-conference style:
  independent reviewers, then a meta-reviewer merges), `editor-mediated-referees`
  (journal / IEEE-conference style: an editor or TC chair synthesises; referees
  are not merged into one list), `light-single-pass` (workshop), or
  `rolling-revision` (revision rounds with a per-round editor decision).
- **Response routing** (§7): does the author response reach the reviewers, or
  only the chair / editor, or is there no response stage?
- For ordinal-category forms (many IEEE / society venues): the **verbatim label
  set for every criterion**, not an invented numeric scale.

If the review form could not be found, it names the matching
`assets/fallback-forms/` file (`conference-ml`, `conference-ieee`,
`journal-referee-report`, `journal-medical`, or `theory-venue`); copy that into
the profile and flag it.

### 4. Compose the tailored prompt

Concatenate, in this order, into `review-prompt.md` in the run folder:

1. `prompts/paper-review-base.md`
2. `field-profile.md` (this run's, from step 1)
3. `venue-profile.md` (this run's)
4. `prompts/review-comment-taxonomy.md`
5. `prompts/paper-review-output-spec.md` (the "Per-reviewer output" section)

Add a one-paragraph header naming the paper, venue, year, track, `venue_type`,
`process_model`, and `--field`.

Then append a **`## Required checks for this review`** block, built by the skill:

- every bullet from `venue-profile.md` §5 ("criteria emphasised by this venue"),
  verbatim;
- the field profile's §3 evidence standard, condensed to 1–2 lines (especially
  any "X is not required / not a weakness here" clause);
- the field profile's §8 "do-not-import" list.

`paper-review-base.md`'s reflection pass requires the reviewer to confirm the
review addresses every item in this block. This is what makes the venue and
field profiles **binding** rather than background reading.

### 5. Run the reviewer panel

Spawn `N` `paper-reviewer` agents (strong model, high/max thinking). Each gets
`review-prompt.md`, the paper (PDF and, if available, the flattened LaTeX), and
one emphasis persona from `references/reviewer-personas.md` (P1, P2, P3, then
repeat P1, P2 …), **as specialised by the field profile's §6**. Each does a
reflection pass and returns per-reviewer output per the spec. Save as
`reviews/reviewer-<i>.md`. For a paper too long for one context, instruct the
agent to read it in section chunks.

### 6. Area chair / editor synthesis  *(static mode only)*

Spawn `review-area-chair`, passing `process_model` from `venue-profile.md`; it
runs the matching role variant (see `agents/review-area-chair.md`). Inputs:
`review-prompt.md`, all `reviews/reviewer-*.md`, the paper, `venue-profile.md`,
`field-profile.md`.

- **`panel-plus-metareviewer`** — the full merge: independent read, then
  de-duplicate overlapping comments, reconcile contradictions, union
  severities/actionability, record all contributing reviewers in `raised_by`,
  renumber `B-01…`. Recommendation in the venue's rating band + accept/reject.
- **`editor-mediated-referees`** — **no merged unified list.** The editor does an
  independent read, writes an editor summary that marks each referee point
  binding / advisory / overruled (with reasons), and issues a decision in the
  venue's revision-ladder vocabulary. Deliverable B is the union of referee
  comments, de-duplicated only for exact repeats, each keeping its `raised_by`.
- **`light-single-pass`** — organiser pass: a short summary reconciling the
  reviews and an accept/reject (or non-archival note). Minimal B.
- **`rolling-revision`** — treat this static run as one round: editor decision
  for this round (`minor` / `major` / `reject`) + the point list the authors
  must address next round.

Save as `reviews/area-chair.md`.

### 7. Write deliverables A and B

Per `prompts/paper-review-output-spec.md`:

- `review-A-venue-style.md` — layout chosen by the venue form and `process_model`:
  `A/conference` (numeric scales), `A/ordinal-criteria` (per-criterion label
  sets, e.g. IEEE / society venues), `A/journal`, or `A/editor-mediated`
  (editor summary with binding/advisory tags, revision-ladder decision).
  Synthesis (meta-review or editor summary) first, then each reviewer's review /
  referee report in the venue's own fields and scales. Flag fallback-form use in
  bold. Never emit a numeric score or a decision term the venue profile does not
  list.
- `review-B-point-by-point.md` + `review-B.json` — the correction list, ordered
  by severity then document position, with the count summary header. Merged for
  `panel-plus-metareviewer`; de-duplicated-only for `editor-mediated-referees`.
  **Every item carries a typed `fix`** (`prompts/review-comment-taxonomy.md` →
  "The `fix` object"): a `kind: edit` with verbatim `find` / `replace`, a
  `kind: work_spec` with an `acceptance` test, exact `kind: response_text`, or a
  `kind: question`.

### 7b. Validate the fixes

`python scripts/check_fixes.py review-B.json [--source <root-or-map>]`. It fails
the run if any item lacks a well-formed `fix` for its `actionability`, if a
`replace` reads like advice, or if an `edit.find` string does not occur in the
source. Fix the offenders (send them back to `review-area-chair` / the panel) and
re-run before finalising deliverable B. Same gate in loop mode on `review-B1.json`.

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

Run steps 1–5, then the author-response stage. **Its shape depends on
`venue-profile.md`'s `process_model` and response routing (§7)** — do not run a
reviewer-visible rebuttal for a venue that does not have one.

### Loop shape by process model

| Routing (venue profile §7) | What 7L does |
|---|---|
| Response is **reviewer-visible** (most ML conferences; some security venues) | Full rebuttal loop: `response-researcher` ↔ reviewers in rebuttal-eval mode, `thread_state.py` in its default mode. |
| Response goes to **chair / editor only** (IEEE / SPS conferences: rebuttal to TC chairs, *not shared with reviewers*) | **Chair-mediated:** `response-researcher` writes one rebuttal; it goes to `review-area-chair`, **never to the `paper-reviewer` agents**. `thread_state.py --mediator chair` records the chair's per-comment ruling as terminal. Reviewers are not re-spawned. |
| **No response stage** (`light-single-pass`, and conferences without a rebuttal) | Skip 7L entirely; go straight to 8L with the reviews as-is. |
| **`rolling-revision`** (journals; revision-cycle security venues) | One round only per skill run: `response-researcher` writes a response-to-reviewers + revision plan; `review-area-chair` (editor variant) issues this round's decision. `--K` is ignored (real rounds happen across separate runs). |

### Extra inputs (step 1)

`--code <repo>`, `--results <dir>`, `--refs <bib | dir of PDFs>` (all optional,
**read-only**, never shown to reviewers); `--K <n>` (default 2, used only for the
reviewer-visible loop); `--annotate-unresolved`. Step 5 keeps the N reviews
**separate** (`reviews/reviewer-<i>.md`), comment ids `R<i>-<nn>`. Step 6 is
skipped.

### 7L. Author-response stage

Read `prompts/rebuttal-protocol.md` and `prompts/comment-resolution-states.md`.

**Reviewer-visible loop** — for `k = 1..K`:

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

**Chair-mediated response** — single pass:

1. Spawn `response-researcher` as above; it writes `rebuttal/round-1/rebuttal.md`.
2. **Do not spawn reviewers.** Spawn `review-area-chair` in **chair-mediated
   response** mode with all `reviews/reviewer-*.md`, `rebuttal/round-1/rebuttal.md`,
   the paper, `venue-profile.md`, `field-profile.md`. It rules on each addressed
   comment (`upheld` / `addressed` / `partly` / `moot`) with a one-line reason.
3. Build `stances.json` from the rebuttal and `replies.json` from the chair's
   rulings (`reviewer` = `"AC"`), then
   `python scripts/thread_state.py --mediator chair --threads … --round 1 --K 1 …`.

`rolling-revision` — see the table above; produce the response letter + revision
plan and hand to 8L's editor variant. No `thread_state.py` loop.

**No todonotes are written in this step.**

### 8L. Area chair / editor: discussion + final decision (single invocation)

Spawn `review-area-chair` in **end-of-loop decision mode** with all reviews, the
full `rebuttal/` tree, `comment-threads.json`, the post-rebuttal updates (if the
reviewer-visible loop ran), `venue-profile.md`, and `field-profile.md`. Its role
variant follows `process_model` (metareviewer vs. handling editor). It writes
`rebuttal/discussion-log.md`, adjudicates every contested comment, issues the
**final decision in the venue's exact vocabulary** (accept/reject + tier for a
conference; a revision-ladder term for a journal / `rolling-revision`) with a
rationale citing comment ids, and sets each thread's `group` / `group_reason`
(grouping near-duplicates).

### 9L. Draft deliverables

Per the "Loop mode outputs" section of `prompts/paper-review-output-spec.md`:
`review-A-venue-style.md` (opens with the decision + rationale),
`response-to-reviewers.md`, `review-B1-agreed-corrections.md` + `review-B1.json`
(only `accepted`; each with its agreed typed `fix` — `kind: edit` items are the
ones `apply_corrections.py` can apply), `review-B2-unresolved.md` +
`review-B2.json`. Then run `python scripts/check_fixes.py review-B1.json
[--source <root-or-map>]` and resolve any offender before continuing.

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
  curation/decisions.json --source <src> --out-dir <run>` → `corrected/paper_v1/`
  + `corrections.diff`, compiled (local). Applies every accepted item with
  `fix.kind == edit` (each `edits[]` entry as `find` → `replace`). Overleaf: run
  with `--emit-plan`, show the diff, confirm, apply via `edit_file`,
  `compile_project`, write `overleaf-commits.md`.
- Accepted items with `fix.kind` `work_spec` / `response_text` / `question` are
  listed as "needs manual edit"; `work_spec` ones also go to `action-list.md`
  (with the full spec — `apply_corrections.py`'s `to_action_list`).
- Build `action-list.md` from those plus the user-accepted Group 2 items.

### 13L. Run summary

`README.md`: `--mode loop`, `K`, rounds run, `stopped_because`, oscillation
count, the AC decision, the comment × state × group × user-decision table, links
to `corrected/` and `action-list.md`, any "needs manual edit" items, and — if the
text changed — a note that `re-review` is available (see "Challenge & re-review").

## Challenge & re-review (post-run, all user-triggered)

After a completed run, the user can dispute comments and — separately — ask for a
re-review of a revised paper. Nothing here chains automatically. Everything lands
under `cycle-<n>/` in the run folder (`cycle-1/` is the original run); see
`prompts/paper-review-output-spec.md` → "Challenge & re-review outputs".

### Stage A — challenge (`challenge <id>: <argument>` in chat)

1. Collect the user's disputes into `cycle-<n>/challenge/requests.json` — per
   comment an `argument` and an optional `counter_fix` (a typed `fix` object).
2. Read `prompts/rebuttal-protocol.md` → "User-seeded challenge". For each
   challenged comment, for `j = 1..J` (`--J`, default 2):
   - Spawn `response-researcher` in **challenge mode** with the paper, that
     comment's review, the user's `argument`/`counter_fix`, and (if given) the
     evidence paths. It writes `cycle-<n>/challenge/round-<j>/rebuttal.md`, each
     entry opening with `**User argument:** …`.
   - Spawn the **one** `paper-reviewer` that owns the comment (rebuttal-eval
     mode) → `cycle-<n>/challenge/round-<j>/reviewer-<i>-reply.md`.
   - Build `stances.json` / `replies.json`, run
     `python scripts/thread_state.py --threads cycle-<n>/challenge/threads.json
     --round <j> --K <J> [--init …] --stances … --replies …`.
   - `--via-chair`: route to `review-area-chair` (chair-mediated) instead of the
     reviewer, using `thread_state.py --mediator chair`.
3. Terminal outcomes → `cycle-<n>/challenge/outcomes.json`: `accepted` (revised
   typed `fix` recorded), reviewer `withdraw` → `rebutted`, or still-disputed
   after `J` → `challenged-upheld` (Group 2, `group_reason: challenge-failed`).
4. Rewrite the challenged rows of `review-B` / `review-B1` in place with the
   revised `fix` / severity / state; prepend a `## Post-challenge changes`
   section. Re-run `check_fixes.py`. Rebuild annotations for changed items.

### Stage B — apply

The existing curation gate + `python scripts/apply_corrections.py` (step 12L),
writing `cycle-<n>/corrected/paper_v<n>/` + `corrections.diff`. Only
`fix.kind == edit` items apply; `work_spec` items go to `action-list.md`.

### Stage C — re-review (only on explicit `re-review`)

After Stage B the skill just records in `README.md` that the text changed and
`re-review` is available, then stops. When the user runs `re-review` (or
`paper-review re-review <run-folder>`):

1. If the latest `corrected/corrections.diff` is empty → no-op; say so.
2. Re-run **steps 5–10 only** on the latest `corrected/paper_v<n>/`, reusing
   `venue-profile.md`, `field-profile.md`, `review-prompt.md`. Pass each
   `paper-reviewer` the prior `cycle-<n>/review-B.json` + `corrections.diff`;
   they run in **re-review mode** and each leave a `reviewer-<i>-reconcile.md`.
3. Spawn `review-area-chair` in **reconciliation mode** → `cycle-<n+1>/` with
   `review-A-venue-style.md`, `review-B*.{md,json}` (typed fixes), and
   `reconciliation.{md,json}` (every prior comment `resolved` / `persists` /
   `new`; regressions flagged).
4. Only re-issue the decision if the user also passed `--rescore`.
5. The user may then challenge `cycle-<n+1>` (Stage A again). The user decides
   how many cycles to run.

## Guardrails

- Never fabricate references, results, quotes, or venue facts. Unfound venue
  details are "not found" in the profile, not guessed.
- The reviewer agents must not receive a bias instruction.
- **Every comment ships a typed `fix`; `check_fixes.py` must pass** before
  deliverable B / B1 is finalised and after a challenge rewrites rows.
- The challenge and re-review stages are **only** run on an explicit user
  request. A re-review never starts as a continuation of "apply".
- The reviewer agents must not receive a bias instruction.
- **Never invent a numeric score or a decision term the venue profile does not
  list.** If the venue uses ordinal category labels, use those labels; if it has
  no author-facing score, do not add one.
- **Pick the field profile explicitly** (step 1). Do not review a
  theory / qualitative / systems / dataset / clinical / position paper against an
  empirical-ML rubric; honour the field profile's §8 "do-not-import" list.
- **Route the author response the way the venue routes it.** If
  `venue-profile.md` §7 says the response is not shared with reviewers, the
  `paper-reviewer` agents are never given the rebuttal — the chair adjudicates.
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
