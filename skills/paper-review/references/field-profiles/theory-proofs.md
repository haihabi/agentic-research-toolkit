# Field profile — Theory and proofs (`theory-proofs`)

`last_reviewed: 2026-09-06`

## 1. What this profile covers

Papers whose central contribution is a mathematical result: a theorem, an
algorithm with proved guarantees (approximation, regret, sample complexity,
convergence), a hardness / lower-bound result, or a new analysis technique.
Covers STOC / FOCS / SODA / COLT / ITCS and the theory tracks of ML venues.
**Do not** use for: an empirical method with a bit of hand-wavy analysis
(`empirical-ml`), a systems paper with a performance model (`systems-measurement`).

## 2. What "validity" means here

- **Are the assumptions stated precisely** — and are they reasonable, or do they
  quietly trivialise the problem?
- **Are the proofs correct and complete** — every non-trivial step justified, no
  gap hidden behind "it is easy to see", constants / dependencies tracked,
  edge cases (base cases, boundary regimes) handled. Check the key lemmas
  yourself; spot-check the rest.
- **Do the theorem statements match what is proved** — no stronger claim in the
  abstract/intro than the formal statement supports; quantifier order correct;
  the result is not vacuous in the stated regime.
- **Tightness / optimality claims** — is a matching lower bound given or cited,
  or is "tight" overstated?
- **Definitions** — standard, or if new, well-motivated and used consistently.

## 3. Evidence standard

The proof **is** the evidence. Experiments are usually **not expected**; their
absence is not a weakness and must not be raised as `missing-results` unless the
paper itself makes an empirical claim. A clean proof of a modest result can be a
strong paper if the technique or the statement matters. Illustrative simulations,
if present, are a courtesy, not a requirement, and are not held to
`empirical-ml` standards.

**`work_spec` for `needs-new-work` here**: `kind` is `proof` or `derivation`;
required fields `goal` (the statement to establish), `proof_obligation` (the
exact gap in the current argument — which step, which lemma, which case), and
`acceptance` (what a complete argument must show). `conditions` / `metrics` /
`statistics` do not apply.

## 4. What "novelty" and "significance" look like here

A new theorem; a new or substantially simpler proof of a known result; a new
technique/framework reusable beyond this paper; closing (or meaningfully
narrowing) a known gap; a surprising impossibility. Significance is argued by the
importance of the problem, the reach of the technique, or the size of the gap
closed — not by adoption numbers.

## 5. Taxonomy categories: load-bearing vs. rarely applicable

Load-bearing: `incorrect-statement` (broken proof step, false lemma, wrong
constant), `methodological-concern` (invalid derivation, unstated assumption
doing the work), `unsupported-claim` (abstract > theorem), `missing-context`
(undefined notation, missing prerequisite), `novelty-significance`,
`missing-related-work` (prior/parallel results). Usually **not applicable**:
`missing-results`, `reproducibility` (no artifacts), `presentation` beyond
notation.

## 6. Persona emphasis

- **P1 (validity)** — read the main proofs line by line; hunt for the gap, the
  unstated assumption, the quantifier slip.
- **P2 (novelty/positioning)** — is this already known / implied by a cited or
  well-known result? Is the technique genuinely new?
- **P3 (clarity)** — is the argument followable: proof structure, notation,
  where the difficulty actually lies, intuition before formalism.

## 7. Common failure modes

Abstract claims stronger than the formal theorem; a load-bearing assumption that
removes the hard case; a "simple" step that is actually the crux and is wrong or
unproven; ignoring a known matching bound; reinventing a result under new
notation; constants/log factors swept under O(·) when the paper's point is
quantitative.

## 8. Do-not-import

- `missing-results` / benchmark comparisons / ablations / seeds from
  `empirical-ml` — irrelevant unless the paper claims an empirical contribution.
- Wall-clock measurement from `systems-measurement`.
- "Release code and data" reproducibility asks — there is nothing to release;
  reproducibility here = the proof is checkable.
