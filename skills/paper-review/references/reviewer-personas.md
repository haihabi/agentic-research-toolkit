# Reviewer personas

The panel runs `N` `paper-reviewer` subagents (default 3). Each gets the same
tailored `review-prompt.md` plus **one** emphasis persona below. The persona
shifts where the reviewer spends attention and which taxonomy categories it is
most likely to raise — it does **not** change the scoring rubric, the output
format, or the requirement to read the whole paper.

Personas are domain-neutral. They work for an ML paper, a signal-processing
paper, or a biology paper.

## P1 — Technical validity

Focus: is the core result actually correct and fairly established?
- Derivations / proofs: assumptions stated, steps valid, edge cases.
- Experiments: baseline fairness and tuning, evaluation protocol, metric choice,
  number of runs / seeds / subjects, statistical treatment, error bars.
- Threats: data leakage, train/test contamination, confounds, selection effects,
  cherry-picked settings.
- Most likely categories: `methodological-concern`, `incorrect-statement`,
  `unsupported-claim`, `missing-results`.

## P2 — Novelty and positioning

Focus: what is genuinely new, and is the paper honest about it?
- Related work: is the closest prior art cited and compared, not just listed?
- Delta: what does this paper do that the closest 2-3 works do not?
- "First to" / "unlike prior work" claims: verify or downgrade.
- Significance: who benefits, and is the stated impact proportionate?
- Most likely categories: `missing-related-work`, `novelty-significance`,
  `unsupported-claim`, `scope-framing`.

## P3 — Clarity and reproducibility

Focus: could a competent reader follow it and reproduce the central result?
- Structure, notation, figure/table legibility, caption quality.
- Method write-up: enough detail to re-implement or re-derive (or a pointer to
  an appendix / repo that has it).
- Artifacts: code / data / models availability and sufficiency; seeds;
  environment; licensing; the venue's required availability statements.
- Most likely categories: `unclear-statement`, `presentation`,
  `missing-information`, `reproducibility`, `missing-context`.

## If `N > 3`

Add a second instance of P1 (validity is where extra coverage pays off most),
then a second P2. Keep at least one of each persona.

## If `N == 1`

Use a merged "generalist" persona: cover all three areas, budget attention
roughly 40 / 30 / 30 across P1 / P2 / P3.
