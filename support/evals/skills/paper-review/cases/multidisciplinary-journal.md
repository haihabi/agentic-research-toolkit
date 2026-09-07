# Case — multidisciplinary / life-science journal (Nature-family, PLOS, clinical)

Pairs with `--field applied-clinical` for a health study, else the matching
field profile.

## Expected `venue-profile.md` (sketch)

```yaml
venue_type: journal
process_model: rolling-revision
review_model: single-anonymous          # or open peer review
score_style: none
response_routing: chair-or-editor-only
```

- Free-form referee report addressing: novelty and **broad significance**,
  whether conclusions are fully supported, statistics & reporting standards,
  numbered major points, minor points.
- Split: comments to the authors vs. **confidential comments to the editor**.
- Required around submission: reporting summary / reporting-guideline checklist
  (CONSORT / STROBE / PRISMA / TRIPOD as applicable), data-availability,
  code-availability, competing-interests, ethics/IRB, trial registration.
- If the form is not found → fallback `journal-medical.md` (clinical) or
  `journal-referee-report.md`.

## Assertions

1. Deliverable A is `A/editor-mediated`; includes a **broad-significance**
   assessment distinct from domain significance where the venue requires it.
2. A confidential-to-editor section exists and is kept separate from the
   author-facing report.
3. For a clinical paper: reporting-guideline adherence is a first-class validity
   axis; missing items are concrete `missing-information` findings; ethics /
   registration gaps can be `blocking`.
4. No invented numeric author-facing score; decision in the venue's wording.
5. The review is not framed around beating a benchmark.
