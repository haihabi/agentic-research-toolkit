# Fallback form — clinical / biomedical journal (ICMJE-aligned)

> **Fallback in use.** The real reviewer instructions for this journal could not
> be found. This structure follows the ICMJE Recommendations and common
> medical-journal referee forms. Deliverable A must state this in bold. Pair with
> field profile `applied-clinical`.

`last_reviewed: 2026-09-06`

`process_model: rolling-revision` · `score_style: none` (recommendation to editor
only) · `response_routing: chair-or-editor-only` (handling editor mediates each
round) · `review_model: check — often single-anonymous or open`

## Report to the authors (prose, numbered points)

1. **Summary** — the question, design, population, main findings, in your words.
2. **Importance and originality** — is the question important; what does this add
   to existing evidence?
3. **Study design vs. claim** — can the design (RCT / cohort / case-control /
   cross-sectional / diagnostic-accuracy / prediction-model) support the causal
   or predictive claim made? Prospective vs. retrospective.
4. **Reporting-guideline adherence** — CONSORT / STROBE / TRIPOD(-AI) / PRISMA /
   STARD as applicable; list missing items as discrete points.
5. **Bias and confounding** — selection, measurement, attrition, missing data,
   confounder adjustment; for models: leakage, outcome definition, calibration,
   external validation.
6. **Statistics** — pre-specified primary outcome and analysis; sample-size /
   power justification; effect sizes with CIs; multiplicity; subgroup analyses
   flagged as exploratory.
7. **Clinical relevance** — is the effect meaningful to patients, not only
   statistically significant? Generalisability of the population.
8. **Major points** — numbered; each a discrete taxonomy-tagged item.
9. **Minor points** — numbered.

## Checks that required statements are present

Ethics / IRB approval · informed consent · **trial registration** (number + date
vs. enrolment) · data-sharing statement · code availability (for model studies) ·
competing interests · funding source and its role · reporting-guideline checklist.

## Confidential recommendation to the editor

| Field | Value |
|---|---|
| Recommendation | `accept` · `minor revision` · `major revision` · `reject & resubmit` · `reject` |
| Your expertise on this manuscript | `high` · `medium` · `low` |
| Any concern not for the authors | suspected misconduct, competing interests, priority, ethics |

## Notes

- A well-designed, fully reported study with a **null result** is publishable.
- Do not require a novel algorithm or method — a sound study of an existing tool
  is a contribution.
- Ethics/registration/consent gaps are frequently `blocking`.
