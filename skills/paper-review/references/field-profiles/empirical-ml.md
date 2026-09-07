# Field profile — Empirical machine learning (`empirical-ml`)

`last_reviewed: 2026-09-06`

## 1. What this profile covers

Papers whose central claim is that a learning method, architecture, training
procedure, or prompting/agent scheme works better (or reveals something) when
evaluated on datasets, benchmarks, or tasks. Includes most NeurIPS / ICLR / ICML
/ CVPR / ACL-style submissions. **Do not** use for: a new benchmark itself
(`dataset-benchmark`), a learning-theory paper with proofs (`theory-proofs`), an
ML systems / serving / efficiency-measurement paper (`systems-measurement`).

## 2. What "validity" means here

- **Baseline fairness** — are the baselines strong, current, and tuned with
  comparable budget to the proposed method? Is the comparison apples-to-apples
  (same data, same compute, same evaluation)?
- **Evaluation protocol** — held-out/test discipline, no tuning on test, no
  benchmark contamination / train–test leakage, correct metric for the task,
  dataset splits reported.
- **Statistical treatment** — more than one seed/run where variance matters;
  means with spread (std / CI / error bars); is the reported gain outside the
  noise? Multiple-comparison awareness when many configs are tried.
- **Ablations** — is each claimed-important component isolated? Are gains
  attributed to the stated cause rather than a confound (more compute, more data,
  longer training, a better tokenizer)?
- **Generalisation of the claim** — do results hold across the datasets/models/
  settings the abstract implies, or only the ones in the main table?

## 3. Evidence standard

Empirical support is expected and is the load-bearing artifact. A claim of
improvement needs a controlled comparison with variance. **Not** required:
topping every leaderboard (a well-scoped insight, analysis, or negative result
counts); results on tasks the paper never claimed; SOTA on compute the authors
plainly did not have — hold the paper to its stated scope. A method that is
simpler / cheaper / more robust at equal accuracy is a contribution.

**`work_spec` for `needs-new-work` here** (`review-comment-taxonomy.md` schema):
`kind` is usually `experiment` or `ablation`; required fields `goal`, `design`,
`conditions`, `metrics`, `statistics` (seeds/trials + test), `acceptance`
(the numeric bar that resolves the comment), `effort`.

## 4. What "novelty" and "significance" look like here

New method or a new combination with a demonstrated reason it helps; a new
empirical phenomenon or a careful analysis that changes how people act; a
negative or contradictory result that corrects a common practice. Significance is
argued through generality (holds across settings), practical impact (adoption,
cost), or insight (explains a mechanism).

## 5. Taxonomy categories: load-bearing vs. rarely applicable

Load-bearing: `methodological-concern`, `missing-results`, `unsupported-claim`,
`missing-related-work`, `reproducibility`, `novelty-significance`. Rarely the
crux (but usable): `incorrect-statement` for proofs (few here),
`ethics-and-compliance` unless human data / released models / dual-use.

## 6. Persona emphasis

- **P1 (validity)** — baseline fairness, leakage/contamination, seed count and
  variance, ablation attribution.
- **P2 (novelty/positioning)** — delta over the closest 2–3 methods; "first to"
  claims; whether the gain is the interesting part or a known trick.
- **P3 (clarity/repro)** — enough to re-run: hyperparameters, data prep, compute,
  code/model release, exact prompts.

## 7. Common failure modes

Weak or under-tuned baselines; single-seed tables with small gaps; tuning on the
test set or reusing a contaminated benchmark; ablations that change two things at
once; abstract claims broader than the experiments; "SOTA" against a stale
number; released code that does not reproduce the headline.

## 8. Do-not-import

- Proof-completeness demands from `theory-proofs` — an empirical paper may state
  intuitions without theorems.
- Wall-clock / throughput measurement rigor from `systems-measurement` unless the
  paper makes an efficiency claim.
- Dataset-documentation completeness from `dataset-benchmark` unless the paper
  ships a dataset.
