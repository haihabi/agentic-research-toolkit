# Field profile — Systems and measurement (`systems-measurement`)

`last_reviewed: 2026-09-06`

## 1. What this profile covers

Papers whose contribution is a built system (its design and what building it
taught us) or a measurement study of a real system, network, or population.
Covers OSDI / SOSP / NSDI / USENIX ATC / IMC / SIGCOMM / EuroSys and the systems
tracks of ML venues (serving, training infra, efficiency). **Do not** use for: a
learning method that happens to report latency (`empirical-ml` unless the
efficiency claim is central), a purely analytical performance-model paper
(`theory-proofs`).

## 2. What "validity" means here

- **Measurement methodology** — what exactly was measured, with what tool, at
  what point in the stack; clock/counter accuracy; warm-up and steady-state;
  enough trials; tail (p95/p99) not just mean; load generator not the
  bottleneck.
- **Baseline and configuration fairness** — compared against a real, tuned
  alternative on the same hardware/workload; apples-to-apples; the proposed
  system not given a quiet advantage (bigger cache, disabled safety check).
- **Workload realism** — representative traces / benchmarks / request mixes;
  stated and justified; not cherry-picked to the system's strengths.
- **Confounds** — noisy-neighbour effects, thermal throttling, background jobs,
  network variance, dataset size vs. memory; are results isolated from these?
- **Generality** — does it hold across hardware, scale, and workloads the
  abstract implies, or one setup?

## 3. Evidence standard

Quantitative evaluation on a real implementation is expected. Ablations of design
choices and an honest overhead/limitations section carry weight. A negative
result ("we built X and it did not help, here is why") is publishable. **Not**
required: beating every system on every metric; results at hyperscale if the
paper scopes itself smaller; formal proofs (a performance model is a bonus).

**`work_spec` for `needs-new-work` here**: `kind` is `measurement`,
`experiment`, or `analysis`; required fields `goal`, `design` (the rig and what
is measured where), `conditions` (workloads / configs / baselines), `metrics`
(incl. tail latency / overhead as relevant), `statistics` (trials to bound
noise), `acceptance`, `effort` (+ hardware).

## 4. What "novelty" and "significance" look like here

A new design point or mechanism; a non-obvious lesson from building/operating at
scale; the first measurement of some real phenomenon; a result that overturns a
common assumption. Significance is argued by generality, by magnitude of
improvement on a metric people care about, or by the system being real and used.

## 5. Taxonomy categories: load-bearing vs. rarely applicable

Load-bearing: `methodological-concern` (measurement flaws, unfair setup),
`missing-results` (missing baseline, missing tail latency, missing overhead),
`unsupported-claim` (abstract > eval), `reproducibility` (artifact availability,
environment spec), `missing-related-work`. Sometimes: `ethics-and-compliance` for
measurement of humans / live networks.

## 6. Persona emphasis

- **P1 (validity)** — the measurement rig, trial counts, tails, confounds,
  baseline tuning.
- **P2 (novelty/positioning)** — design delta over the closest systems; is the
  lesson new or folklore.
- **P3 (clarity/repro)** — enough to rebuild and re-measure: configs, hardware,
  workloads, artifact.

## 7. Common failure modes

Mean-only latency; one run; load generator saturated; unfair or stale baseline;
workload chosen to flatter the system; overhead reported vaguely or not at all;
"scales" claim shown at two points; artifact that needs unavailable hardware and
no fallback.

## 8. Do-not-import

- Seed-count / statistical-significance framing from `empirical-ml` applies to
  variance across runs but not to a demand for "5 seeds" on a deterministic
  systems benchmark — ask for enough trials to bound noise, not a ritual number.
- Proof completeness from `theory-proofs`.
- Leaderboard framing — systems papers are rarely a single-number contest.
