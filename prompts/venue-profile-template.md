# Venue profile template

`venue-researcher` fills one copy of this per run and writes it to the run
folder as `venue-profile.md`. It captures **only what is specific to this venue,
year, and track** — it must not restate the generic reviewing guidance in
`paper-review-base.md`. Every non-obvious line carries a source URL. Anything not
found after a genuine search is recorded as `not found`; anything that does not
apply to this venue type is `not applicable`.

---

```yaml
venue: ""                    # e.g. "NeurIPS", "ICASSP", "IEEE Transactions on Signal Processing"
year: ""
track: ""                    # main / findings / workshop name / journal section; "" if single-track
venue_type: ""               # conference | journal | workshop
review_model: ""             # single-blind | double-blind | open | not found
retrieved: "YYYY-MM-DD"
```

## 1. Review / referee-report form

List the exact fields the reviewer must fill, in order, with any per-field
instructions quoted from the source.

| Field | Required? | Instructions (quoted) |
|---|---|---|
| … | | |

## 2. Rating scheme

For each numeric or ordinal score the form asks for, give the scale **with its
label text verbatim**. If the venue uses no numeric scores (common for
journals), write `not applicable` and describe any confidential
recommendation-to-editor scale instead.

| Score name | Scale (verbatim labels) |
|---|---|
| Overall / recommendation | e.g. `1: Strong Reject … 6: Strong Accept` |
| Confidence | e.g. `1: educated guess … 5: absolutely certain` |
| … | |

## 3. Decision set

The exact set of outcomes the handling AC / editor chooses from.

- Conference example: `accept (oral)`, `accept (poster)`, `borderline`, `reject`.
- Journal example: `accept`, `minor revision`, `major revision`,
  `reject & resubmit`, `reject`.

## 4. Scope / subject areas

From the call for papers or the journal's aims & scope: what is in scope, what is
explicitly out of scope, named subject areas or subject-editor categories
relevant to this submission.

## 5. Criteria emphasised by this venue

Points the venue's reviewer/AC guide stresses that go **beyond** the generic
criteria — e.g. "reproducibility is weighted heavily", "significance to the
signal-processing community specifically", "broad general interest", "theoretical
novelty not required for the applications track".

## 6. Ethics / compliance / checklist deltas

Venue-specific required statements or checklists beyond the generic ethics check:
reproducibility checklist, broader-impact statement, data-availability statement,
reporting summary, dual-use policy, competing-interests statement, funding
disclosure, use-of-LLM disclosure. Note which are mandatory vs. recommended.

## 7. Author interaction

- Rebuttal / response: allowed? length limit? window?
- Number of review rounds expected.
- Whether reviewers see each other's reviews / discuss.

## 8. Sample recent reviews (3–5)

For each: source URL, venue+year, and 2–4 sentences on its structure and register
(how long, how many weaknesses, how blunt, whether it quotes the paper, whether
scores are justified inline). Do **not** paste full third-party reviews; summarise
structure. Prefer the same venue; fall back to the immediately prior year or a
sibling venue and say so.

## 9. Sources

Flat list of every URL used, each with a one-line note on what it provided.

## 10. Gaps

Explicit list of everything that could not be found, so the reviewer and AC know
what the profile does not cover and the skill knows when to fall back to
`assets/fallback-forms/`.
