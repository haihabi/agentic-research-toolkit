# Case — society / engineering journal (IEEE Transactions, ACM journal)

Pairs with the field profile matching the paper (`signal-processing-eng`,
`systems-measurement`, `theory-proofs`, …).

## Expected `venue-profile.md` (sketch)

```yaml
venue_type: journal
process_model: rolling-revision          # or editor-mediated-referees
review_model: single-anonymous           # (journal-dependent)
score_style: none
response_routing: chair-or-editor-only
```

- Referee-report structure (prose, numbered major/minor points) + confidential
  comments to the editor + a recommendation from a revision ladder
  (`accept` / `minor` / `major` / `reject & resubmit` / `reject`).
- Required statements: data & code availability, competing interests, funding,
  ethics where applicable.
- If the form is not found → fallback `journal-referee-report.md`.

## Assertions

1. Deliverable A is `A/editor-mediated`: an **editor summary** marking each
   referee point binding / advisory / overruled, then each referee report intact.
   There is **no merged unified comment list** and no meta-review that fuses the
   referees.
2. `review-B` is the de-duplicated **union** of referee comments, each keeping
   its `raised_by`.
3. No author-facing numeric score is invented; the decision uses the venue's
   revision-ladder wording.
4. `--mode loop` runs one editor-mediated round (response letter + revision
   plan + this round's decision); `--K` is ignored.
