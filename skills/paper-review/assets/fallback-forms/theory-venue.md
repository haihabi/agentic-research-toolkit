# Fallback form — theory venue (STOC / FOCS / SODA / CCC / ITCS family)

> **Fallback in use.** The real review form for this venue+year could not be
> found. This is a generic theory-conference structure. Deliverable A must state
> this in bold. Pair with field profile `theory-proofs`.

`last_reviewed: 2026-09-06`

`process_model: panel-plus-metareviewer` (no merged comment list) ·
`score_style: none` (an accept/reject lean + confidence) ·
`response_routing: not found` (some theory venues have a rebuttal, some do not —
check; default `none`)

## Report to the PC (prose)

1. **Summary** — the model, the result(s), and the techniques, in your own words.
   State the theorem informally and note the key parameters/assumptions.
2. **Correctness** — did you check the main proofs? Which lemmas did you verify,
   which did you spot-check, where are the gaps or unstated assumptions? Are
   constants / dependencies as claimed?
3. **Significance** — importance of the problem; size of the gap closed; whether
   the technique is likely reusable. Is the result already known or implied by
   prior work?
4. **Relation to prior work** — closest results, cited and compared; any
   concurrent work.
5. **Presentation** — is the argument followable; is the hard part identified;
   notation.
6. **Detailed comments** — numbered; each a discrete taxonomy-tagged item.

## Overall

| Field | Value |
|---|---|
| Recommendation | `accept` · `weak accept` · `borderline` · `weak reject` · `reject` |
| Reviewer confidence | `expert` · `knowledgeable` · `some familiarity` · `educated guess` |
| Did you check the proofs? | `in full` · `the main ones` · `spot-checked` · `no` |

## Notes

- **Experiments are not expected.** Do not raise `missing-results` unless the
  paper itself claims an empirical contribution.
- A clean proof of a modest result, or a simpler proof of a known one, can be a
  strong paper if the statement or technique matters.
- Reproducibility here = the proof is checkable from what is written (plus a
  full-proofs appendix).
