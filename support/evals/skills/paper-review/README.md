# support/evals/skills/paper-review/

Sanity checks for the `paper-review` skill. Not a scored benchmark — the goal is
to catch regressions in structure, grounding, and the venue-generality of the
output.

## Phase 0 checks (static artifacts)

- **P0a genericness** — `grep -nE 'NeurIPS|ICLR|ICML|CVPR' prompts/paper-review-base.md`
  returns only "e.g." example mentions, never a hard-coded default venue, and no
  ML-only rubric term (`ablation`, `seed`, `leaderboard`, `benchmark`) appears as
  a requirement — only as a field-profile example. `paper-review-base.md` has a
  `last_reviewed` line and its "What this file is and is not" section disclaims
  structure/scores/decision-vocabulary.
- **P0b traceability** — every concrete claim in `references/prior-art.md` and
  `references/venue-guidance-generic.md` carries a URL; `prior-art.md` section A
  has a subsection for each venue family (ML conf, IEEE conf, IEEE Transactions,
  security, ACM journal, clinical, theory, social science).
- **P0c taxonomy mapping** — every Axis-1 slug in
  `prompts/review-comment-taxonomy.md` appears in the mapping table; Axis-3 slugs
  are the revision-cycle-neutral set (`resolve-in-response-text`,
  `defer-to-final-version`, `needs-new-work`, `needs-reframing`,
  `needs-author-clarification`) — the old rebuttal/camera-ready slugs appear
  nowhere in `prompts/` or `skills/`.
- **P0d field profiles** — every slug in `prompts/field-profile-spec.md` "The
  set" has a file in `references/field-profiles/`, each with sections 1–8 and a
  `last_reviewed` line and a non-empty §8 "do-not-import".
- **P0e process model** — `prompts/venue-profile-template.md` defines
  `process_model`, `score_style`, `response_routing`; `agents/review-area-chair.md`
  has a role variant for each `process_model` value; `agents/venue-researcher.md`
  is required to output all three header fields.
- **P0f fallback coverage** — `assets/fallback-forms/` has `conference-ml`,
  `conference-ieee` (ordinal-category, `chair-or-editor-only`),
  `journal-referee-report`, `journal-medical`, `theory-venue`;
  `venue-guidance-generic.md` and `venue-research-checklist.md` list all five.
- **P0g typed fix** — `prompts/review-comment-taxonomy.md` defines the `fix`
  object with per-`actionability` kinds and the `work_spec` schema; no
  `suggested_fix` / `patch` (as an optional free field) remains in `prompts/` or
  `skills/`. `scripts/check_fixes.py` compiles and self-tests (below).

## Fix-specificity checks (script-level, no model)

- **F1 valid pass** — `check_fixes.py` on a `review-B.json` where every item has a
  well-formed `fix` (kind matches `actionability`; `edit.find` present) exits 0.
- **F2 catches vague** — an item whose `fix.kind: edit` has `replace: "consider
  rewording"` is reported; exit 1.
- **F3 catches unanchored** — with `--source`, an `edit.find` string absent from
  the LaTeX is reported.
- **F4 catches wrong kind** — `actionability: needs-new-work` with `fix.kind:
  edit`, or `resolve-in-response-text` with `kind: work_spec`, is reported.
- **F5 work_spec completeness** — a `work_spec` missing `acceptance` (or, for
  `kind: proof`, `proof_obligation`) is reported.
- **F6 apply** — `apply_corrections.py` applies every accepted `fix.kind: edit`
  (each `edits[]` entry) and lists `work_spec` items under `to_action_list`;
  `build_annotations.py` renders a per-kind one-line summary in each `\todo`.

## Acceptance cases (`cases/`)

One expected `venue-profile.md` sketch + assertions per venue family:
`cases/ieee-conference.md` (ICASSP as the concrete instance),
`cases/ml-conference.md` (regression guard), `cases/society-journal.md`,
`cases/multidisciplinary-journal.md`, `cases/theory-venue.md`, `cases/workshop.md`.
Each names the `--field` it pairs with and the 2–3 things a de-biased run must
get right.

## Phase 1 checks (per-run, on fixtures)

Use 1-2 open-access papers from `support/datasets/` (arXiv PDF; and one with an
arXiv source tarball for the LaTeX path).

1. **Conference run** (`ICLR 2025`, `--field empirical-ml`): `venue-profile.md`
   has `venue_type: conference`, `process_model: panel-plus-metareviewer`,
   `score_style: numeric`, real form fields, verbatim scale labels, a non-empty
   Sources section, an honest Gaps section.
2. **Journal run** (`IEEE Transactions on Signal Processing`, and a Nature-portfolio
   journal): `venue_type: journal`, `process_model: rolling-revision` or
   `editor-mediated-referees`, `score_style: none`, `A/editor-mediated` layout in
   deliverable A (no merged comment list), decision set includes revision
   options, no invented numeric author-facing scale, data-availability /
   reporting checks present.
3. **IEEE conference run** (`ICASSP 2025`, `--field signal-processing-eng`):
   `process_model: editor-mediated-referees`, `response_routing:
   chair-or-editor-only`, `score_style: ordinal-categories`; deliverable A is
   `A/ordinal-criteria` with verbatim category labels and **no invented 1–N
   scale**; the review does not raise `missing-results` for absent experiments in
   a method paper.
4. **Venue conditioning** — run the *same paper* as `ICLR 2025` and as `ICASSP
   2025`: the two `review-A` files differ in form, scale style, decision
   vocabulary, and which criteria are emphasised — not just the header.
5. **Field conditioning** — run the *same paper* with `--field empirical-ml` and
   `--field theory-proofs` (or `signal-processing-eng`): the validity comments
   and the `Required checks for this review` block differ; the non-ML run does
   not import ablation/seed/leaderboard demands.
6. **Delta-only** — `venue-researcher`'s fetch log hits venue/year pages only,
   not the generic reviewer-guide corpus; `venue-profile.md` restates no generic
   advice but does resolve `process_model` / `response_routing`.
7. **Deliverable A** — fields/scales/decision words match `venue-profile.md`
   (ordinal labels stay labels, not numbers); synthesis section matches
   `process_model` (meta-review vs. editor summary vs. light note); N reviews;
   fallback use flagged in bold.
8. **Deliverable B** — every item has category + severity + actionability +
   location + quote + suggested_fix; `review-B.json` parses; merged for
   `panel-plus-metareviewer`, de-duplicated-only union for
   `editor-mediated-referees`.
9. **LaTeX local** — `annotated/` compiles; `\listoftodos` present; note colours
   match severity; original tree byte-identical.
10. **LaTeX Overleaf** (test project) — `--dry-run` makes zero commits; real run
   shows the diff, waits for confirmation, then one commit per file + preamble;
   `compile_project` succeeds; `overleaf-commits.md` lists commits + revert
   recipe; a simulated mid-run edit is recovered via `get_conflicts` /
   `resolve_conflict`.

## Loop mode checks (`--mode loop`)

Script-level (no model, fast) — fixtures under a scratch dir:

- **L1 state machine** — `thread_state.py` on a 3-comment fixture
  (concede-and-fix + resolved; concede-cannot-fix + unconvinced; dispute +
  unconvinced → concede-and-fix + resolved) yields
  `accepted / unresolved_insufficient_info / accepted` and
  `stopped_because = converged` before `K`.
- **L1b chair-mediated** — `thread_state.py --mediator chair --round 1 --K 1` on
  a fixture with replies `reviewer: "AC"` and rulings
  `addressed / upheld / partly` yields
  `accepted / unresolved_* / <forced terminal>` in one round,
  `stopped_because = converged` when nothing is left `in_debate`. Default
  (`--mediator reviewers`) behaviour is unchanged (regression).
- **L2 forced resolution** — a comment left `in_debate` at `k == K` becomes
  `unresolved_disagreement` (or `unresolved_insufficient_info` if the last stance
  was `concede-cannot-fix`).
- **L3 oscillation** — a thread toggling open↔in_debate three times is forced to
  `unresolved_disagreement`, `oscillated: true`.
- **L4 annotation split** — `build_annotations.py review-B1.json --unresolved
  review-B2.json`: B1 items get severity-coloured `\todo`s, B2 items get
  `black!12` `[UNRESOLVED …]` inline notes; `inject_todonotes.py` output compiles.
- **L5 curation + apply** — with `curation/decisions.json` accepting a subset,
  `apply_corrections.py` edits only the accepted B1 items that carry a `patch`,
  writes `corrected/` + `corrections.diff`, compiles; unpatched items are listed
  as "needs manual edit"; rejected items are untouched.

Run-level (with agents):

- **L6 no merge** — `comment-threads.json` ids are `R<i>-<nn>`; there is no
  `reviews/area-chair.md` before the loop; `rebuttal.md` addresses all reviewers.
- **L7 reviewer boundary** — with `--code`, no `paper-reviewer` call receives the
  repo path or `evidence/`; the three panel calls use three thinking levels.
- **L8 AC once, decision** — `review-area-chair` is spawned exactly once, after
  the loop; `review-A-venue-style.md` opens with `Final decision:` + a rationale
  citing comment ids, in the venue's exact decision vocabulary.
- **L8b routing** — for a `chair-or-editor-only` venue, no `paper-reviewer` agent
  is spawned in rebuttal-eval mode; the rebuttal appears only in the
  `review-area-chair` inputs; `thread_state.py` was run with `--mediator chair`.
  For a `none`-routing venue, step 7L is skipped entirely.
- **L9 no mid-loop todonotes** — no `\todo` string is written anywhere before
  step 10L.
- **L10 regression** — `--mode static` (default) reproduces the pre-loop A + B.
- **L11 report Artifact** — `review-report.html` is produced in both modes and
  parses (valid JSON in `#report-data`); loop mode publishes it with
  `capabilities: {db: {}}`; the page renders with `db` absent (read-only banner,
  no thrown errors) and, when `db` is present, a curation click writes
  `curation/<id>` and `read_db` on that collection returns it.

## Challenge & re-review checks

Script-level:

- **X1 challenge state** — `thread_state.py` on a challenge fixture
  (`--K 2`, replies from the owning reviewer): a `dispute` + reviewer
  `unconvinced` twice ends `unresolved_disagreement`; the skill maps it to
  `challenged-upheld` / Group 2 / `group_reason: challenge-failed`.
- **X2 no text change ⇒ no re-review** — with an empty `corrections.diff`,
  `re-review` is a no-op and says so; no `cycle-2/` is created.
- **X3 work_spec never edits the paper** — an accepted B1 item with `fix.kind:
  work_spec` produces an `action-list.md` entry and **no** hunk in
  `corrections.diff`.

Run-level (with agents):

- **X4 challenge routing** — a `challenge` engages `response-researcher`
  (challenge mode, entry opens `**User argument:**`) and the **one** owning
  `paper-reviewer`; other reviewers are not spawned. `--via-chair` swaps in
  `review-area-chair` + `thread_state.py --mediator chair`.
- **X5 challenge is user-triggered** — no `challenge/` folder appears unless the
  user asked; `re-review` never runs as a continuation of `apply`.
- **X6 reconciliation** — after `re-review`, `cycle-2/reconciliation.json` tags
  every `cycle-1` comment `resolved` / `persists` / `new`; a `resolved` comment
  does not reappear under a new id; regressions carry `regression: true`.
- **X7 rescore opt-in** — the decision changes only when `--rescore` was passed.

## Known evaluation pitfalls (from arXiv:2501.10326)

Position bias (order of reviewers/comments), verbosity bias, decision leakage
(the model stating accept/reject before reasoning), and prompt injection from
text inside the PDF. Spot-check outputs for these.
