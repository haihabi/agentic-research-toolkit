# Field profile — Datasets and benchmarks (`dataset-benchmark`)

`last_reviewed: 2026-09-06`

## 1. What this profile covers

Papers whose contribution is a new dataset, benchmark, evaluation suite, or
challenge — the resource itself, plus baseline results that characterise it.
Covers NeurIPS Datasets & Benchmarks track and equivalents. **Do not** use for: a
method paper that also introduces a small eval set as a side artifact
(`empirical-ml`), a measurement study that produces data but claims a finding
(`systems-measurement`).

## 2. What "validity" means here

- **Construction methodology** — how were items collected/generated/annotated;
  annotator pool, guidelines, training, pay; inter-annotator agreement; quality
  control and its results; how errors and disagreements were handled.
- **Representativeness and bias** — what population/phenomenon is the dataset
  meant to represent, and does the construction actually cover it? Known biases,
  demographic skew, domain gaps stated honestly.
- **Contamination and leakage** — is there a real train/val/test split? Any
  overlap with common pretraining corpora? Can the test set be gamed by
  memorisation or a shortcut feature?
- **Metric and protocol** — does the proposed metric measure the intended
  capability? Is the evaluation protocol precise enough to be reproduced
  identically? Is there a leaderboard-gaming risk?
- **Baselines** — enough baselines (including trivial / majority / human) to show
  the benchmark is neither saturated nor impossible, and to characterise
  headroom.
- **Legal / ethical basis** — licensing of source material, consent, PII, opt-out,
  takedown process; datasheet / croissant-style documentation.

## 3. Evidence standard

The load-bearing artifact is the **resource and its documentation** (datasheet /
data card, collection code, hosting plan, license), not a SOTA number. Baseline
results are needed only to characterise difficulty and headroom, not to win.
A benchmark that is hard, well-documented, and legally clean is a strong paper
even if every baseline is weak. Long-term maintenance/hosting plan matters.

**`work_spec` for `needs-new-work` here**: `kind` is `analysis`,
`dataset-addition`, or `measurement`; required fields `goal`, `design` (e.g. the
IAA study, the contamination check, the missing baseline), `data`, `metrics` /
`statistics` as relevant, `acceptance` (the number or artifact that resolves the
comment — e.g. "IAA κ reported per split; κ ≥ 0.6 or the disagreement handling
is documented"). Documentation gaps are usually `kind: edit` to the datasheet.

## 4. What "novelty" and "significance" look like here

A capability or domain not previously measurable; a harder or cleaner version of
an existing benchmark; a benchmark that exposes a failure mode; better evaluation
methodology. Significance is argued by what the community can now measure and by
likely adoption.

## 5. Taxonomy categories: load-bearing vs. rarely applicable

Load-bearing: `methodological-concern` (annotation quality, bias, contamination,
metric validity), `reproducibility` (can the eval be run identically; is the data
actually available under a usable license), `ethics-and-compliance` (consent,
PII, licensing — often `blocking`), `missing-information` (undocumented
construction detail), `missing-related-work` (existing similar resources),
`novelty-significance`. Recast: `missing-results` → missing baseline needed to
characterise the benchmark, not "improve the method".

## 6. Persona emphasis

- **P1 (validity)** — annotation process and agreement, contamination, metric
  validity, bias.
- **P2 (novelty/positioning)** — what this measures that existing benchmarks do
  not; overlap with prior resources.
- **P3 (clarity/repro)** — datasheet completeness, license, availability,
  protocol precision, maintenance plan.

## 7. Common failure modes

No inter-annotator agreement or quality audit; unclear or unpaid annotation;
test set overlaps pretraining data; metric that rewards a shortcut; only one
strong-model baseline (no human / trivial); vague licensing or unaddressed PII;
no datasheet; no hosting/maintenance commitment; "diverse" claimed without
evidence.

## 8. Do-not-import

- "Beat SOTA" / leaderboard framing from `empirical-ml` — baselines here exist to
  characterise, not to win.
- Ablation grids for a method — there is no method.
- Proofs from `theory-proofs`.
