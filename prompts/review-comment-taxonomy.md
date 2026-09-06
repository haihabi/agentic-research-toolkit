# Review comment taxonomy

A fixed vocabulary for classifying every point raised in a paper review. It is
domain-neutral: it applies equally to an ML conference paper, a signal-processing
paper full of derivations, and a life-sciences journal submission. Reviewers and
the area chair / editor tag **every** correction item on three axes and attach
the metadata block. Deliverable B (the point-by-point list) and the LaTeX
`todonotes` annotations are built directly from these tags.

`last_reviewed: 2026-09-06`

In `--mode loop`, each tagged comment also carries a `resolution` state that
evolves through the author-response loop and ends up in one of two output groups
— see `prompts/comment-resolution-states.md` and `prompts/rebuttal-protocol.md`.

---

## Axis 1 — Category (what kind of issue it is)

Exactly one category per item. Pick the most specific one that fits; if two apply
equally, pick the one that implies the larger fix.

| Slug | Use it when… | Typical fix |
|---|---|---|
| `missing-context` | A term, symbol, prerequisite, or assumption the reader needs is not given before it is used. | Add a sentence / definition / forward reference. |
| `missing-information` | The method or setup is under-specified — a competent reader could not re-implement or re-derive it (hyperparameters, data splits, hardware, solver settings, measurement conditions, prompt text, statistical test used). | Add the detail to the paper or an appendix. |
| `missing-results` | A claim is made but the experiment, ablation, baseline, dataset, proof, or measurement that would support it is absent. | Run/add the missing evidence. |
| `missing-related-work` | Relevant prior art is uncited, or cited but not compared against / positioned relative to. | Add citation + one or two sentences of positioning, or an empirical comparison. |
| `unsupported-claim` | A statement in the abstract, intro, or conclusion is stronger than what the evidence in the paper actually shows (overgeneralisation, causal language for correlational results, "first to" without a check). | Soften the claim, or add support, or scope it. |
| `methodological-concern` | There is a flaw or risk in the design itself: data leakage, train/test contamination, unfair baseline tuning, wrong or missing statistics, confound, non-reproducible randomness, invalid derivation step, inappropriate metric. | Redesign / re-run / add controls / correct the analysis. |
| `incorrect-statement` | Something is simply wrong: a false factual claim, a broken equation, a mislabeled axis/figure/table, a wrong citation, an internal contradiction. | Correct it. |
| `unclear-statement` | The content may be fine but the wording is ambiguous, contradictory, imprecise, or the notation is undefined / overloaded. | Rewrite the sentence; fix notation. |
| `presentation` | Structure, figure/table legibility, notation consistency, caption quality, typos, grammar, formatting, length/page-limit, equation rendering. | Editorial fix, usually camera-ready. |
| `reproducibility` | Code, data, models, or an environment specification are not available or not sufficient; missing seeds; missing data-availability / artifact / licensing statement expected by the venue. | Release artifacts; add the statement. |
| `ethics-and-compliance` | Missing or inadequate ethics review, consent, IRB, dual-use / safety discussion, broader-impact statement, competing-interests statement, or a venue checklist item; potential policy violation. | Add the statement / obtain approval / flag for an ethics review. |
| `novelty-significance` | The contribution is incremental, the delta over prior work is small or unclear, or the significance / likely impact is over- or under-stated. | Sharpen the contribution statement; add what is genuinely new; or reframe. |
| `scope-framing` | Title / abstract / body mismatch; the paper is a poor fit for the venue or track; the framing promises more than the paper delivers. | Retitle / reframe / move claims. |

## Axis 2 — Severity (how much it matters for the decision)

Exactly one.

| Slug | Meaning |
|---|---|
| `blocking` | On its own this would change the recommendation. Must be resolved for acceptance. |
| `major` | Materially weakens the paper; the authors are expected to address it in the rebuttal / revision, and the score depends on their response. |
| `minor` | Should be fixed and improves the paper, but does not move the score. |
| `nit` | Cosmetic or optional. Typos, wording preferences, small polish. |

## Axis 3 — Actionability (what the authors have to do)

Exactly one.

| Slug | Meaning |
|---|---|
| `fix-in-rebuttal-text` | Can be resolved by explanation or clarification in the response, no new work. |
| `fix-camera-ready` | A wording / figure / citation change that can wait for the final version. |
| `needs-new-experiments` | Requires running something that does not exist yet. |
| `needs-reframing` | Requires rewriting claims, scope, or positioning (not new results). |
| `needs-clarification-from-authors` | The reviewer cannot judge severity until the authors answer a question. |

## Metadata block (attached to every item)

```yaml
id: R2-07                      # <reviewer-id>-<running number>; the AC keeps merged ids
category: missing-results
severity: major
actionability: needs-new-experiments
location:
  section: "5.2 Ablations"
  page: 7                      # for PDF-only review
  file_line: "sections/experiments.tex:142"   # when LaTeX source is present
  quote: "we observe consistent gains across all settings"   # verbatim anchor, <= 20 words
raised_by: [R2, R4]           # filled by the AC after merge
confidence: 3                  # reviewer self-rating, venue's confidence scale (here 1-5)
problem: >
  The "consistent gains across all settings" claim is supported only by the two
  settings in Table 3; the three settings named in Section 3 are not reported.
evidence: >
  Table 3 covers {A, B}. Section 3 also defines {C, D, E}. No results for C-E appear
  anywhere in the paper or appendix.
suggested_fix: >
  Add the C/D/E runs to Table 3, or restrict the claim to {A, B} and say so explicitly.
```

`quote` is mandatory whenever the item refers to specific text — it is what makes
the point traceable and what anchors the `\todo` note in the LaTeX pass.

## Severity → `todonotes` colour (LaTeX pass)

| Severity | `\todo` colour |
|---|---|
| `blocking` | `red!70` |
| `major` | `orange!80` |
| `minor` | `blue!40` |
| `nit` | `gray!30` |

## Mapping table — taxonomy slug → PeerRead aspect → generic rubric dimension

Used by the area chair to roll individual comments up into the venue's numeric
rubric (deliverable A) and to keep the taxonomy anchored to the peer-review
literature (PeerRead, Kang et al. 2018; *Identifying Aspects in Peer Reviews*,
2025).

| Taxonomy slug | PeerRead aspect | Generic rubric dimension |
|---|---|---|
| `missing-context` | Clarity / Substance | Clarity |
| `missing-information` | Substance | Reproducibility / Rigour |
| `missing-results` | Substance / Soundness | Rigour (support for claims) |
| `missing-related-work` | Meaningful Comparison | Positioning |
| `unsupported-claim` | Soundness/Correctness | Rigour (support for claims) |
| `methodological-concern` | Soundness/Correctness | Rigour (validity) |
| `incorrect-statement` | Soundness/Correctness | Rigour (validity) |
| `unclear-statement` | Clarity | Clarity |
| `presentation` | Clarity | Clarity |
| `reproducibility` | Substance / Replicability | Reproducibility |
| `ethics-and-compliance` | (venue policy) | Ethics & compliance |
| `novelty-significance` | Originality / Impact | Novelty & significance |
| `scope-framing` | Appropriateness | Scope / venue fit |

The "too general" labels that the *Identifying Aspects in Peer Reviews* taxonomy
explicitly drops — bare **Strength**, **Weakness**, **Question**, **Comment** —
are deliberately not categories here. A strength is recorded in deliverable A's
narrative; a question is an item with `actionability: needs-clarification-from-authors`.
