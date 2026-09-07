# paper-review — de-bias plan (C + A + B)

Status: **implemented** on branch `debias-paper-review` (2026-09-06). WP1–WP5 +
WP0 landed; see the commit. Remaining: a live dry run on real papers across
venue families (needs fixture PDFs).

## Problem

The `paper-review` skill's "venue-neutral" core is really an ML-conference core.
A review produced for a non-ML-conference venue comes out conference-ML-shaped no
matter what `venue-researcher` discovered. Three defects, each breaking a
different venue family:

| Defect | Breaks for | Concrete example |
|---|---|---|
| Assumes numeric score scales | Venues with ordinal per-criterion labels, or no author-facing scores | IEEE conferences (ICASSP-family); most journals |
| Rebuttal loop = reviewers read & re-evaluate the author response | Venues where the response goes only to the chair/editor; venues with no response; multi-month revision cycles | IEEE conferences; Nature-family; workshops |
| "Weak/absent experiments" is a weakness; ablations/seeds/baselines are *the* validity check | Theory, systems-measurement, HCI-qualitative, dataset, clinical, position papers | STOC/FOCS; CHI; TOMS |
| Panel → area-chair **merge into one unified list** | Editor-mediated referee models (referees don't merge, often don't see each other) | Most journals |

## Fix — three layers

- **C — rebalance the foundation.** Re-weight `references/prior-art.md` away from
  ~80% ML-conference sources; re-distil `prompts/paper-review-base.md` down to
  genuinely venue-independent principles; push venue-shaped structure entirely
  into the profile layers; make the comment taxonomy's actionability axis
  revision-cycle-neutral.
- **A — field / paper-type profile layer.** A second thin frozen artifact,
  chosen per run, parallel to the venue profile. The venue profile answers "what
  form / scale / process does this venue use"; the field profile answers "what
  does rigor, novelty, and evidence mean for *this kind of paper*." Also: make
  the venue profile **binding** (its emphasised criteria become explicit required
  checks the reflection pass verifies), not advisory.
- **B — process-model abstraction.** `process_model` becomes a first-class
  `venue-researcher` output. The orchestration branches on it: whether there is a
  merge step, whether reviewers see each other, whether "loop" means a
  rebuttal-window or an editor-mediated revision round or nothing, and which
  synthesis role the chair agent plays.

## Work packages

### WP0 — acceptance-test matrix (`support/evals/skills/paper-review/cases/`)

One expected `venue-profile.md` sketch + assertions per venue family:
`ieee-conference.md` (ICASSP as the concrete instance), `ml-conference.md`
(regression guard), `society-journal.md`, `multidisciplinary-journal.md`,
`theory-venue.md`, `workshop.md`.

### WP1 — C

- `references/prior-art.md` — add equal-weight sections: IEEE conference
  editorial procedures; a security venue with a major-revision cycle; an ACM
  journal; a clinical venue (ICMJE); a theory venue; one social-science /
  humanities venue.
- `prompts/paper-review-base.md` — re-distil to principles only; add the clause
  that structure/fields/scores/decision-vocabulary/author-interaction all come
  from the venue + field profiles; move ablations/leaderboard norms out.
- `prompts/review-comment-taxonomy.md` — Axis 3 → `resolve-in-response-text`,
  `defer-to-final-version`, `needs-new-work`, `needs-reframing`,
  `needs-author-clarification`.

### WP2 — A

- new `skills/paper-review/references/field-profiles/*.md` (8 types) +
  `prompts/field-profile-spec.md`.
- `skills/paper-review/SKILL.md` — `--field` input; prompt assembly
  `base → field-profile → venue-profile → taxonomy → output-spec`; the
  "Required checks for this review" block.
- `skills/paper-review/references/reviewer-personas.md` — personas reference the
  field profile's validity checklist instead of hard-coding ablations/seeds.

### WP3 — B

- `prompts/venue-profile-template.md` — `process_model` field; §7 expansion
  (does the response reach the reviewers or only the chair/editor; rounds;
  desk-reject stage).
- `references/venue-guidance-generic.md` — `process_model` row; IEEE-conference
  specifics.
- `references/venue-research-checklist.md` — flesh out the IEEE-conference path;
  add theory and medical/social-science paths.
- `agents/venue-researcher.md` — output `process_model`; capture ordinal label
  sets verbatim; record rebuttal visibility.
- `agents/review-area-chair.md` — role variants keyed on `process_model`.
- `agents/paper-reviewer.md` — rebuttal-eval mode is skipped when the response
  is chair-only.
- `skills/paper-review/SKILL.md` — step 6 merge conditional; loop mode branch
  (chair-mediated vs reviewer-visible vs revision-round).
- `skills/paper-review/scripts/thread_state.py` — `--mediator chair` mode.
- `prompts/rebuttal-protocol.md`, `prompts/comment-resolution-states.md` — the
  chair-mediated variant.
- `prompts/paper-review-output-spec.md` — `A/ordinal-criteria` and
  `A/editor-mediated` deliverable layouts.
- `docs/paper-review-system.md` — Panel for the editor-/chair-mediated flow.

### WP4 — fallback forms

- rewrite `assets/fallback-forms/conference-ieee.md` to the real IEEE-conference
  form (ordinal per-criterion labels, Award-quality, Paper-type, single-anon,
  "disregard minor formatting", rebuttal-to-chairs, one round + desk reject).
- new `assets/fallback-forms/theory-venue.md`, `assets/fallback-forms/journal-medical.md`.
- `adapters/claude-code/paper-review.md` — note `--field`.

### WP5 — evals

- `support/evals/skills/paper-review/README.md` — venue-conditioning test,
  field-conditioning test, the WP0 assertions.

## Build order

WP1 → WP2 → WP3 → WP4 → (WP0 + WP5 together, since the cases exercise the new
concepts). Then a dry run on one IEEE conference, one journal, one theory venue.
