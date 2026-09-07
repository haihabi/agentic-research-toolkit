# Field profile — Applied clinical and biomedical (`applied-clinical`)

`last_reviewed: 2026-09-06`

## 1. What this profile covers

Papers reporting clinical, epidemiological, or biomedical studies where results
bear on health: trials, observational studies, diagnostic/prognostic model
studies, digital-health interventions, secondary analyses of health data. Covers
medical journals (per ICMJE) and health tracks of ML venues (clinical ML).
**Do not** use for: a pure ML method benchmarked on a medical dataset with no
clinical claim (`empirical-ml`), a biology theory/method paper with no health
outcome.

## 2. What "validity" means here

- **Study design vs. question** — is the design (RCT, cohort, case-control,
  cross-sectional, retrospective model study) able to support the causal or
  predictive claim made? Prospective vs. retrospective stated.
- **Reporting-guideline adherence** — CONSORT (trials), STROBE (observational),
  TRIPOD / TRIPOD-AI (prediction models), PRISMA (reviews), STARD (diagnostic
  accuracy). Missing items are concrete `missing-information` findings.
- **Bias and confounding** — selection bias, measurement bias, missing-data
  handling, confounder adjustment, immortal-time bias; for models: data leakage,
  outcome definition, calibration not just discrimination, external validation.
- **Statistics** — pre-specified primary outcome and analysis; sample-size /
  power justification; effect sizes with CIs; multiplicity; subgroup claims
  flagged as exploratory.
- **Ethics and governance** — IRB / ethics approval, informed consent, trial
  registration (with date vs. enrolment), data-sharing statement, conflicts,
  funding role.
- **Clinical relevance** — is the effect size meaningful to patients, not just
  statistically significant? Generalisability of the population.

## 3. Evidence standard

The load-bearing artifact is a **well-designed, fully reported study** meeting the
relevant reporting guideline. A null or negative result from a sound trial is
publishable and valuable. Not required: a new method or algorithm; SOTA on a
benchmark; large n if the design and analysis are appropriate and the paper is
scoped accordingly. Prospective registration and protocol adherence carry
significant weight.

**`work_spec` for `needs-new-work` here**: `kind` is `analysis`, `experiment`
(e.g. external validation), or `measurement`; required fields `goal`, `design`
(the specific analysis: e.g. calibration + external validation, confounder
adjustment, sensitivity analysis), `data` (cohort + N), `statistics`
(pre-specified test, effect size + CI, multiplicity), `acceptance`. Missing
reporting-guideline items are `kind: edit` adding the required text.

## 4. What "novelty" and "significance" look like here

New evidence on a clinical question; a rigorously validated model ready for a
defined use; a well-powered replication or refutation; a methodological advance
for health research. Significance is argued by impact on practice, policy, or
patient outcomes and by the strength of the design.

## 5. Taxonomy categories: load-bearing vs. rarely applicable

Load-bearing: `methodological-concern` (design–claim mismatch, bias, confounding,
leakage), `ethics-and-compliance` (approval, consent, registration —
frequently `blocking`), `missing-information` (unreported guideline items),
`unsupported-claim` (causal language from observational data; overstated clinical
benefit), `missing-results` (missing primary-outcome analysis, missing external
validation), `reproducibility` (data/code/protocol availability). Rarely central:
`presentation` beyond figure/table reporting standards.

## 6. Persona emphasis

- **P1 (validity)** — design vs. claim, reporting-guideline checklist, bias and
  confounding, statistics, model validation.
- **P2 (novelty/positioning)** — what this adds to existing clinical evidence;
  registered protocol vs. reported analysis.
- **P3 (clarity/ethics)** — ethics/registration/consent/data statements; clear,
  unspun reporting of outcomes and harms.

## 7. Common failure modes

Causal claims from observational data; outcome switching vs. the registration;
no power/sample-size justification; missing STROBE/CONSORT items; model reported
with AUROC only, no calibration, no external validation; data leakage via
preprocessing; significant p-value with a clinically trivial effect; spin in the
abstract; ethics approval or registration not stated.

## 8. Do-not-import

- Benchmark-leaderboard framing from `empirical-ml`; "beat SOTA" is not the bar.
- Demands for a novel algorithm — a sound study of an existing tool is the
  contribution.
- Re-runnable-artifact reproducibility as the only lens — protocol and reporting
  transparency matter as much, and data may be legitimately restricted.
