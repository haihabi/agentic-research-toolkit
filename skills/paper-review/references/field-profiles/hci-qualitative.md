# Field profile — HCI, qualitative, and mixed-methods (`hci-qualitative`)

`last_reviewed: 2026-09-06`

## 1. What this profile covers

Papers whose contribution rests on studying people: user studies, interviews,
ethnography, diary studies, surveys, participatory / design research, and
mixed-methods work. Covers CHI / CSCW / UIST (study papers) / DIS and HCI tracks
elsewhere. **Do not** use for: a UI *system* paper evaluated on task performance
with no qualitative claim (`systems-measurement` or `empirical-ml`), a pure
benchmark (`dataset-benchmark`).

## 2. What "validity" means here

- **Fit of method to question** — is the chosen method (qualitative,
  quantitative, mixed) appropriate for what the paper asks? Quant claims need
  quant rigor; interpretive claims need interpretive rigor. Neither substitutes.
- **Sampling and recruitment** — who was studied, how recruited, how many, why
  that number is adequate for the claim (saturation for qualitative; power for
  quantitative); who is excluded and what that does to the claims.
- **Data collection and analysis** — protocol described; analysis method named
  (thematic analysis, grounded theory, statistical tests) and applied
  consistently; coding process and (where relevant) inter-rater reliability or a
  reflexive account of why it is not used.
- **Trustworthiness** — for qualitative work: reflexivity / positionality,
  member checking or triangulation where claimed, quotes that actually support
  the themes. For quantitative: assumptions, effect sizes with CIs, not just
  p-values; no HARKing.
- **Claim scope** — findings framed as transferable insight, not
  over-generalised to "users" from a small specific sample.

## 3. Evidence standard

Depth, transparency, and coherence of interpretation are the evidence for
qualitative work — **not** sample size alone and **not** a benchmark. A study of
12 participants can be a strong paper. For quantitative/mixed work, standard
statistical reporting applies. Reproducibility here means transparency of process
(protocol, instruments, codebook, analysis steps), not a re-runnable script.
"Not generalisable" is not by itself a valid criticism of a qualitative study
that does not claim generalisability.

**`work_spec` for `needs-new-work` here**: `kind` is `user-study` or `analysis`;
required fields `goal`, `design` (method, protocol, recruitment), `data`
(participants + N + why N adequate — saturation or power), `statistics` (for
quantitative arms: test + effect sizes), `acceptance` (what the added data /
analysis must show). Often the fix is instead `kind: edit` scoping the claim to
the sample studied.

## 4. What "novelty" and "significance" look like here

A new empirical understanding of a practice or population; a design implication
or framework grounded in the data; a method contribution for studying something;
a concept that reframes a problem. Significance is argued by relevance to design
/ theory / practice and by what the community can now do or see differently.

## 5. Taxonomy categories: load-bearing vs. rarely applicable

Load-bearing: `methodological-concern` (method–question mismatch, sampling,
analysis rigor, over-claiming), `unsupported-claim` (theme not backed by data;
"users" from n=8), `missing-context` (unstated researcher stance, unexplained
setting), `novelty-significance`, `ethics-and-compliance` (consent, IRB,
vulnerable participants, data handling — often `blocking` here),
`missing-related-work`. Usually recast: `reproducibility` → process transparency;
`missing-results` → missing analysis step or missing participant detail, not
"run more experiments".

## 6. Persona emphasis

- **P1 (validity)** — method fit, sampling, analysis rigor, ethics.
- **P2 (novelty/positioning)** — contribution over prior qualitative/HCI work;
  is the framing new or a relabelling.
- **P3 (clarity)** — is the study reported transparently enough to assess:
  protocol, participant table, codebook, quote–claim linkage.

## 7. Common failure modes

Method that cannot answer the question asked; tiny or unmotivated sample with
universal claims; analysis method named but not evident in the results; quotes
that illustrate rather than evidence the themes; no positionality/reflexivity for
interpretive work; p-values without effect sizes; ethics of recruitment or data
skipped; "implications for design" that do not follow from the findings.

## 8. Do-not-import

- Benchmark comparisons, leaderboard framing, and "n is too small / not
  generalisable" reflexes from `empirical-ml` — apply the qualitative standard
  instead.
- Re-runnable-artifact reproducibility from `systems-measurement`.
- Proof demands from `theory-proofs`.
