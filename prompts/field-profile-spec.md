# Field profile specification

A **field profile** says what rigor, evidence, novelty, and the common failure
modes look like for **one kind of research paper** — independent of the venue.
Where the venue profile is discovered per run by `venue-researcher`, field
profiles are a small frozen set in
`skills/paper-review/references/field-profiles/`, authored once from
`references/prior-art.md` and refreshed on the same schedule as
`paper-review-base.md`.

The skill picks exactly one per run (`--field`, auto-suggested from the paper's
title/abstract + venue, user-confirmed) and concatenates it into the review
prompt **between the base and the venue profile**:

```
paper-review-base.md  →  field-profile.md  →  venue-profile.md  →  taxonomy  →  output-spec
```

Precedence: the base governs conduct; the field profile governs what counts as
sound/novel/sufficient *for this kind of paper*; the venue profile governs form,
scales, decision vocabulary, process, and emphasis, and overrides the field
profile where they touch the same point (e.g. an applications track that waives
the theory bar).

---

## File shape

Each `field-profiles/<slug>.md` has this structure. Keep every section short and
concrete; a profile is guidance a reviewer reads once, not a manual.

```markdown
# Field profile — <human name> (`<slug>`)

`last_reviewed: YYYY-MM-DD`

## 1. What this profile covers
2–4 sentences: the kind of paper, with examples, and the nearest neighbours it
should NOT be used for (point to the right slug instead).

## 2. What "validity" means here
The specific questions that replace the generic "Validity" sub-bullets in
`paper-review-base.md`. This is the heart of the profile — what a competent
reviewer actually checks to decide the core result is correct and fairly
established.

## 3. Evidence standard
What counts as adequate support for a claim in this kind of work, and — crucially
— what does NOT count against a paper. State plainly when experiments /
benchmarks / ablations / seeds are not expected, or when a proof / a measurement
/ a user study / a dataset card is the load-bearing artifact instead.

## 4. What "novelty" and "significance" look like here
The forms a genuine contribution takes in this field (new method, first
measurement, framework, dataset, negative result, replication, theory), and how
significance is argued (adoption, generality, a settled open problem, a corrected
record).

## 5. Taxonomy categories: load-bearing vs. rarely applicable
Which `review-comment-taxonomy.md` Axis-1 categories carry most weight for this
field, and which are usually `not applicable` (say why). Never removes a category
— a reviewer can still use any — just sets expectations.

## 6. Persona emphasis
One line each for P1 / P2 / P3 (`reviewer-personas.md`) specialising where that
persona spends attention for this kind of paper.

## 7. Common failure modes
A short list of the recurring real weaknesses in this kind of submission, phrased
so a reviewer can look for them. These are the things a field-blind reviewer
misses or misjudges.

## 8. Do-not-import
Explicit list of criteria from *other* fields (usually empirical-ML) that must
not be applied here, with the one-line reason.
```

## The set

| slug | for |
|---|---|
| `empirical-ml` | learning systems evaluated on benchmarks / tasks |
| `theory-proofs` | theorems, algorithms with proved guarantees, complexity |
| `systems-measurement` | built systems, measurement studies, performance evaluation |
| `signal-processing-eng` | signal/communications/control methods with analysis + simulation |
| `hci-qualitative` | user studies, qualitative and mixed-methods, design research |
| `dataset-benchmark` | new datasets, benchmarks, evaluation suites |
| `applied-clinical` | clinical / biomedical / health studies |
| `position-survey` | position papers, surveys, reproducibility / meta-science reports |

If a paper genuinely spans two (e.g. a signal-processing method with a large
empirical study), pick the profile matching its **primary claimed
contribution** and note the secondary lens in the run README.
