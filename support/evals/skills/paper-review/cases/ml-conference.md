# Case — ML/CS conference (regression guard)

Pairs with `--field empirical-ml`. This case exists to prove the de-bias work
did **not** change behaviour for the venue family the skill already handled.

## Expected `venue-profile.md` (sketch)

```yaml
venue_type: conference
process_model: panel-plus-metareviewer
review_model: double-blind          # (venue-dependent)
score_style: numeric
response_routing: reviewer-visible
```

- Form fields ≈ Summary / Strengths & Weaknesses / Quality / Clarity /
  Significance / Originality / Questions / Limitations / Overall / Confidence /
  Ethics, with verbatim scale labels.
- Decision set: accept (oral/spotlight/poster) / borderline / reject.

## Assertions

1. Static mode: `review-area-chair` does the **full merge** — one meta-review,
   de-duplicated unified `review-B` with `raised_by`, renumbered `B-01…`.
2. Deliverable A is `A/conference` with numeric scores and one-to-two-sentence
   justifications.
3. Loop mode: reviewer-visible K-round rebuttal; `thread_state.py` default mode;
   post-rebuttal score deltas; `review-area-chair` spawned once at the end.
4. The empirical-ML validity checks (baseline fairness, leakage, seeds/variance,
   ablation attribution) appear in the `Required checks for this review` block.
5. Output is materially identical to a pre-change run on the same fixture
   (structure, sections, scale handling).
