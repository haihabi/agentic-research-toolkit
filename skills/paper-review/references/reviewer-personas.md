# Reviewer personas

The panel runs `N` `paper-reviewer` subagents (default 3). Each gets the same
tailored `review-prompt.md` plus **one** emphasis persona below. The persona
shifts where the reviewer spends attention and which taxonomy categories it is
most likely to raise — it does **not** change the scoring rubric, the output
format, or the requirement to read the whole paper.

**The field profile specialises these personas.** Each `field-profiles/<slug>.md`
has a "Persona emphasis" section (§6) that says, for that kind of paper, where P1
/ P2 / P3 should actually look. When a field profile is in play, its §6 wins over
the generic wording here. The descriptions below are the fallback and the
`empirical-ml` instance.

## P1 — Technical validity

Focus: is the core result actually correct and fairly established? *What
"validity" means is set by the field profile's §2* — e.g.:
- Theory: assumptions stated, every proof step valid, edge cases, tightness.
- Empirical: baseline fairness and tuning, evaluation protocol, metric choice,
  runs / seeds / subjects, statistical treatment, leakage / contamination.
- Systems / measurement: measurement rig, trial counts, tails, confounds, fair
  configuration.
- Qualitative: method–question fit, sampling, analysis rigor, trustworthiness.
- Most likely categories: `methodological-concern`, `incorrect-statement`,
  `unsupported-claim`, `missing-results` (where the field profile expects
  results).

## P2 — Novelty and positioning

Focus: what is genuinely new, and is the paper honest about it?
- Related work: is the closest prior art cited and compared, not just listed?
- Delta: what does this paper do that the closest 2-3 works do not?
- "First to" / "unlike prior work" claims: verify or downgrade.
- Significance: who benefits, and is the stated impact proportionate — judged by
  the field profile's notion of significance (adoption, generality, a closed
  gap, a corrected record), not only by benchmark numbers.
- Most likely categories: `missing-related-work`, `novelty-significance`,
  `unsupported-claim`, `scope-framing`.

## P3 — Clarity and reproducibility

Focus: could a competent reader follow it and reproduce / re-derive / re-run the
central result?
- Structure, notation, figure/table legibility, caption quality.
- Method write-up: enough detail to re-implement, re-derive, or re-run (or a
  pointer to an appendix / repo / protocol that has it).
- "Reproducibility" takes the field's form: released code/data/models and seeds
  for empirical work; a checkable proof for theory; a stated protocol, codebook,
  and instruments for qualitative work; a datasheet and license for a dataset;
  reporting-guideline adherence for clinical work.
- Most likely categories: `unclear-statement`, `presentation`,
  `missing-information`, `reproducibility`, `missing-context`.

## If `N > 3`

Add a second instance of P1 (validity is where extra coverage pays off most),
then a second P2. Keep at least one of each persona.

## If `N == 1`

Use a merged "generalist" persona: cover all three areas, budget attention
roughly 40 / 30 / 30 across P1 / P2 / P3, weighted by the field profile's §6.
