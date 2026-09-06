# support/evals/skills/paper-review/

Sanity checks for the `paper-review` skill. Not a scored benchmark — the goal is
to catch regressions in structure, grounding, and the venue-generality of the
output.

## Phase 0 checks (static artifacts)

- **P0a genericness** — `grep -nE 'NeurIPS|ICLR|ICML|CVPR' prompts/paper-review-base.md
  skills/paper-review/references/venue-guidance-generic.md` returns only "e.g."
  example mentions, never a hard-coded default venue. `paper-review-base.md` has a
  `last_reviewed` line.
- **P0b traceability** — every concrete claim in `references/prior-art.md` and
  `references/venue-guidance-generic.md` carries a URL.
- **P0c taxonomy mapping** — every Axis-1 slug in
  `prompts/review-comment-taxonomy.md` appears in the mapping table with a
  PeerRead aspect and a generic rubric dimension.

## Phase 1 checks (per-run, on fixtures)

Use 1-2 open-access papers from `support/datasets/` (arXiv PDF; and one with an
arXiv source tarball for the LaTeX path).

1. **Conference run** (`ICLR 2025`): `venue-profile.md` has
   `venue_type: conference`, real form fields, verbatim scale labels, a non-empty
   Sources section, an honest Gaps section.
2. **Journal run** (`IEEE Transactions on Signal Processing`, and a Nature-portfolio
   journal): `venue_type: journal`, prose referee-report layout in deliverable A,
   decision set includes revision options, no invented numeric author-facing
   scale, data-availability / reporting checks present.
3. **IEEE conference run** (`ICASSP 2025`): short IEEE form, not the ML template.
4. **Delta-only** — `venue-researcher`'s fetch log hits venue/year pages only,
   not the generic reviewer-guide corpus; `venue-profile.md` restates no generic
   advice.
5. **Deliverable A** — fields/scales/decision words match `venue-profile.md`;
   one meta-review/editor recommendation + N reviews; fallback use flagged.
6. **Deliverable B** — every item has category + severity + actionability +
   location + quote + suggested_fix; `review-B.json` parses; no exact-duplicate
   items across reviewers.
7. **LaTeX local** — `annotated/` compiles; `\listoftodos` present; note colours
   match severity; original tree byte-identical.
8. **LaTeX Overleaf** (test project) — `--dry-run` makes zero commits; real run
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
  citing comment ids.
- **L9 no mid-loop todonotes** — no `\todo` string is written anywhere before
  step 10L.
- **L10 regression** — `--mode static` (default) reproduces the pre-loop A + B.
- **L11 report Artifact** — `review-report.html` is produced in both modes and
  parses (valid JSON in `#report-data`); loop mode publishes it with
  `capabilities: {db: {}}`; the page renders with `db` absent (read-only banner,
  no thrown errors) and, when `db` is present, a curation click writes
  `curation/<id>` and `read_db` on that collection returns it.

## Known evaluation pitfalls (from arXiv:2501.10326)

Position bias (order of reviewers/comments), verbosity bias, decision leakage
(the model stating accept/reject before reasoning), and prompt injection from
text inside the PDF. Spot-check outputs for these.
