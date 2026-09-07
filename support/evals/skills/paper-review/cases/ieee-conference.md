# Case — IEEE / society conference (ICASSP as the concrete instance)

Pairs with `--field signal-processing-eng` (or `theory-proofs` for a
derivation-only paper).

## Expected `venue-profile.md` (sketch)

```yaml
venue_type: conference
process_model: editor-mediated-referees
review_model: single-anonymous
score_style: ordinal-categories
response_routing: chair-or-editor-only     # rebuttal to TC/Area Chairs, not reviewers
```

- ≥ 3 reviewers; track-chair initial check with desk-reject possible; one round.
- §2 captures the **verbatim label set** for every criterion (Importance/
  Relevance, Originality, Theoretical development, Experimental validation,
  Clarity, Reference to prior work, Overall, Award quality) — no 1–N scale.
- §5 emphasised criteria include: quality / relevance / correctness; experimental
  validation scaled by paper type; "disregard minor formatting issues".
- §7: "rebuttals are not shared with the original reviewers".
- If the exact form is not found → fallback `conference-ieee.md`, flagged in bold.

## Assertions a de-biased run must satisfy

1. Deliverable A is `A/ordinal-criteria`: every criterion carries a **category
   label**, not an invented number; no `Overall: 4/6` style output.
2. A method / theory paper is **not** marked down under `missing-results` or
   `methodological-concern` for having no (or few) experiments — the field
   profile's evidence standard governs; such a reviewer comment is `overruled` by
   the chair with that reason.
3. In `--mode loop`, the rebuttal goes to `review-area-chair` only; **no
   `paper-reviewer` is re-spawned**; `thread_state.py` ran with `--mediator
   chair`; `review-A` says "after the chair-mediated response".
4. No English/formatting nit is raised above `minor`.
5. The final decision is one of `accept` / `reject` (+ optional award flag), not
   a journal revision term.
