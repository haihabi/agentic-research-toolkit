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
process_model: ""            # panel-plus-metareviewer | editor-mediated-referees | light-single-pass | rolling-revision
review_model: ""             # single-blind | double-blind | open | not found
score_style: ""              # numeric | ordinal-categories | none | mixed
response_routing: ""         # reviewer-visible | chair-or-editor-only | none | not found
retrieved: "YYYY-MM-DD"
```

### `process_model` — pick one, with a source

| Value | Fits | Tell-tale |
|---|---|---|
| `panel-plus-metareviewer` | most ML/CS conferences | independent reviewers, then an AC/SAC writes a meta-review that merges them; numeric scores; rebuttal usually reviewer-visible |
| `editor-mediated-referees` | most journals; IEEE / society conferences (ICASSP family) | a handling editor / TC chair synthesises; referee reports are **not** merged into one list; author response (if any) goes to the editor/chair, not the referees |
| `light-single-pass` | workshops | one light round, short form, often no author response, non-archival common |
| `rolling-revision` | journals with revision rounds; security venues with major-revision | a per-round decision (minor / major / reject); the same referees see the revised version next round |

## 1. Review / referee-report form

List the exact fields the reviewer must fill, in order, with any per-field
instructions quoted from the source.

| Field | Required? | Instructions (quoted) |
|---|---|---|
| … | | |

## 2. Rating scheme

For each score the form asks for, give the scale **with its label text
verbatim**. Set `score_style` in the header accordingly:

- `numeric` — an integer scale (`1: Strong Reject … 6: Strong Accept`).
- `ordinal-categories` — named categories, **not** numbers, per criterion. Common
  at IEEE / society venues. Capture the full label set for **every** criterion,
  e.g. Importance = `Of broad interest | Of sufficient interest | Of limited
  interest | Irrelevant`. **Do not** convert these to a 1–N scale.
- `none` — no author-facing score (common for journals). Write `not applicable`
  and describe any confidential recommendation-to-editor scale instead.
- `mixed` — some criteria scored, some categorical / prose.

| Score / criterion name | Style | Scale (verbatim labels) |
|---|---|---|
| Overall / recommendation | numeric | e.g. `1: Strong Reject … 6: Strong Accept` |
| Confidence | numeric | e.g. `1: educated guess … 5: absolutely certain` |
| … | | |

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
- **Response routing** (sets `response_routing` in the header): do the original
  reviewers read the author response and re-evaluate (`reviewer-visible`), or
  does it go only to the AC / TC chair / handling editor (`chair-or-editor-only`
  — e.g. ICASSP: "rebuttals are not shared with the original reviewers"), or is
  there no response stage (`none`)?
- Number of review rounds expected; is there a per-round decision
  (`rolling-revision`) or a single decision?
- Whether reviewers see each other's reviews / discuss.
- Desk-reject / initial-check stage before peer review?

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
