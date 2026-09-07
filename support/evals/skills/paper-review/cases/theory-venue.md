# Case — theory venue (STOC / FOCS / SODA / COLT)

Pairs with `--field theory-proofs`.

## Expected `venue-profile.md` (sketch)

```yaml
venue_type: conference
process_model: panel-plus-metareviewer   # no merged comment list; or light-single-pass
review_model: double-blind               # (venue-dependent)
score_style: none                        # accept/reject lean + confidence
response_routing: reviewer-visible       # or none — check the venue
```

- Report is prose: summary of the model/result/techniques, correctness (which
  proofs were checked), significance, relation to prior work.
- If the form is not found → fallback `theory-venue.md`.

## Assertions

1. `missing-results` / benchmark / ablation / seed comments are **absent** unless
   the paper itself claims an empirical contribution; if a reviewer raises one it
   is `overruled` with the field-profile reason.
2. The `Required checks for this review` block is about proof correctness,
   assumptions, tightness, and relation to prior work — not experiments.
3. Validity comments engage with specific lemmas / steps and quote them.
4. `reproducibility` is interpreted as "the proof is checkable", not
   "release code and data".
5. Decision vocabulary is an accept/reject lean + confidence, not a 1–10 scale.
