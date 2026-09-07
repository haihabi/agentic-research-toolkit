# Field profile — Signal processing and engineering methods (`signal-processing-eng`)

`last_reviewed: 2026-09-06`

## 1. What this profile covers

Papers proposing a method in signal processing, communications, control,
information theory (applied), audio/speech, image processing, or radar/array
processing, where the contribution is an algorithm or estimator backed by
**analysis plus simulation** (and sometimes real data). Covers ICASSP / EUSIPCO /
ICIP / ICC / GLOBECOM and the IEEE Transactions in these areas. **Do not** use
for: a pure learning-on-benchmarks paper (`empirical-ml`), a pure theorem paper
with no method (`theory-proofs`), a hardware/measurement study
(`systems-measurement`).

## 2. What "validity" means here

- **Problem formulation and model** — signal/system/noise model stated; are the
  assumptions (stationarity, Gaussianity, linearity, known order, SNR regime)
  realistic for the stated application, and is the method's behaviour outside
  them discussed?
- **Derivation correctness** — the estimator/algorithm/bound is derived, not
  asserted; approximations named and their regime of validity stated;
  optimality/consistency/unbiasedness claims actually established or cited.
- **Simulation methodology** — enough Monte-Carlo trials; comparison against the
  right classical baselines (matched filter, MUSIC/ESPRIT, MMSE, CRLB, the
  standard codec, the obvious prior method), not a strawman; metrics standard for
  the subfield (MSE vs. CRLB, BER vs. SNR, PESQ/STOI, ROC); parameter ranges
  (SNR, snapshots, array size) swept, not a single point.
- **Complexity** — computational cost stated and compared; real-time / resource
  claims supported.
- **Reproducibility of the claim** — the model + parameters are enough for
  another group to re-simulate.

## 3. Evidence standard

Analysis + simulation is the norm; a Cramér–Rao or other bound comparison is
strong evidence. Real-data or hardware validation strengthens a paper but its
**absence is not disqualifying** when the paper is a method paper and says so —
per IEEE SPS guidance, experimental validation is scaled by paper type and
"theoretical papers may need none". Do **not** demand deep-learning baselines
unless the paper positions itself against them. Minor formatting / English issues
are not grounds for rejection (they are `presentation` nits).

**`work_spec` for `needs-new-work` here**: `kind` is `experiment` (simulation),
`derivation`, or `analysis`; required fields `goal`, `design` (signal model +
what is swept), `conditions` (SNR / snapshots / array size / baselines incl. the
CRLB or the standard method), `metrics` (MSE vs bound, BER vs SNR, complexity),
`statistics` (Monte-Carlo trial count), `acceptance`. For a `derivation`,
`proof_obligation` instead of `conditions`.

## 4. What "novelty" and "significance" look like here

A new estimator/algorithm with better MSE–complexity trade-off, a new bound, a
relaxed assumption, a method that works in a regime prior art could not, or a
unifying analysis. Significance is argued by relevance to a real
signal-processing problem and by improvement over the established baseline —
"of broad interest" vs. "of limited interest" in the ICASSP sense.

## 5. Taxonomy categories: load-bearing vs. rarely applicable

Load-bearing: `methodological-concern` (invalid derivation step, unrealistic
model, unfair/strawman baseline, too few trials), `incorrect-statement` (broken
equation, wrong bound), `unsupported-claim` (optimality/robustness asserted not
shown), `missing-related-work` (uncited classical or IEEE prior art),
`missing-results` (missing SNR/snapshot sweep, missing complexity comparison,
missing CRLB). Often `not applicable`: heavy `reproducibility` artifact demands
(code release is encouraged, not mandatory at most of these venues) — judge
against the venue profile.

## 6. Persona emphasis

- **P1 (validity)** — the derivation, the signal model's realism, trial counts,
  baseline fairness, bound comparison.
- **P2 (novelty/positioning)** — delta over the standard method; is the
  assumption relaxation real; uncited classical work.
- **P3 (clarity)** — notation, equation correctness, figure axes (dB scales,
  units), enough parameters to reproduce the plots.

## 7. Common failure modes

Signal model that assumes away the hard part; approximation with no stated regime
of validity; baseline that is a weakened version of the real competitor;
single-SNR-point results; no CRLB / no complexity comparison; "robust" claimed
from one mismatch scenario; optimality claimed from a special case; over-reliance
on one dataset of real recordings.

## 8. Do-not-import

- Benchmark-leaderboard framing, learned-baseline requirements, and large
  ablation grids from `empirical-ml` — unless the paper is itself an ML paper.
- Full proof completeness from `theory-proofs` — derivations should be correct
  and gap-free, but a method paper is not held to a theory venue's standard.
- Artifact/repo-release gating from `dataset-benchmark` / heavy
  `reproducibility`.
- Rejecting for English/formatting — that is explicitly not a reason at IEEE SPS
  venues.
