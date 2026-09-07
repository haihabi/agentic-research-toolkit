# Venue research checklist

Working checklist for `venue-researcher` during a run. Goal: fill every slot of
`prompts/venue-profile-template.md` for **this venue + year + track**, with a
source URL per line, in a bounded amount of searching. Do not re-summarise the
generic reviewing guidance — that already lives in `paper-review-base.md`.

## 0. Classify

- Determine `venue_type` (conference / journal / workshop) and publisher
  (IEEE / ACM / a specific journal publisher / independent / OpenReview-hosted).
- Determine the review model (single / double blind / open).

## 1. ML / CS conferences (NeurIPS, ICLR, ICML, CVPR, ICCV, ACL, EMNLP, AAAI, …)

- `<venue-site>/<year>/CallForPapers` — scope, tracks, page limit, dual
  submission and LLM-use policy.
- `<venue-site>/<year>/ReviewerGuidelines` or `ReviewerInstructions` — form
  fields, per-field instructions.
- `<venue-site>/<year>/AreaChairGuidelines` / `ACGuide` / `SACGuidelines` —
  decision set, how meta-reviews are written, calibration norms.
- `<venue-site>/<year>/EthicsGuidelines` + the reproducibility / paper checklist
  the authors submitted.
- OpenReview: the venue group page → an accepted paper and a rejected paper →
  copy the review form structure and note register/length of the reviews. Prefer
  the same year; else the previous year (say so).

## 2. IEEE / society conferences (ICASSP, ICIP, ICME, ICC, INFOCOM, …)

- `<year>.<conf>.org/editorial-procedures/` (SPS venues) or `/reviewer-guidelines/`
  — capture, **verbatim**: every review-form criterion and its **ordinal label
  set** (Confidence, Importance/Relevance, Paper type, Originality/Novelty,
  Theoretical development, Experimental validation, Clarity, Reference to prior
  work, Overall, Award quality). Set `score_style: ordinal-categories`. Do **not**
  invent a 1–N scale.
- From the same page: number of reviewers (usually "at least three"); the
  **rebuttal** rule — window, and critically **who receives it** (SPS: TC / Area
  Chairs, *not shared with the original reviewers* → `response_routing:
  chair-or-editor-only`, `process_model: editor-mediated-referees`); desk-reject
  / initial-check stage; single-anonymous vs. double.
- `signalprocessingsociety.org/publications-resources/guidelines-reviewers` — what
  a good review contains; "use the whole score range"; "disregard minor
  formatting issues".
- `<year>.<conf>.org/author-kit-instructions/` — page limit, anonymity, template.
- IEEE publication ethics & plagiarism policy, no-manuscript-to-LLM rule (`ieee.org`).
- Sample reviews: IEEE conference reviews are private; note that and rely on the
  editorial-procedures description.

## 3. IEEE Transactions and other engineering journals

- The specific journal's "Information for Authors" and "Information for
  Reviewers" pages on IEEE Xplore / the society site.
- Recommendation set (accept / author revision "R1", "R2" / reject; some use
  "revise and resubmit as new").
- Any structured review questions the ScholarOne form asks (sometimes listed in
  the info-for-reviewers page).
- Reproducibility / data policy if the society has one (e.g. reproducible
  research initiatives in signal processing).

## 4. Multidisciplinary and life-science journals (Nature portfolio, Science, PNAS, PLOS, Cell, eLife, …)

- Publisher "For Referees" / "Guide to Referees" / "Reviewer instructions".
- "Editorial policies": authorship, competing interests, data availability, code
  availability, reporting standards / reporting summary, ethics & consent, dual
  use, preprint policy.
- Whether the journal operates transparent peer review — if so, published
  referee reports on recent articles are the sample-review source.
- Decision set and whether referees give a recommendation to the editor only.
- Broad-significance bar: does this venue require general interest beyond the
  subfield?

## 5. Workshops

- The workshop's own CFP page: archival or not, review depth, page limit,
  acceptance model.
- Inherit ethics / formatting norms from the parent conference; note that.
- Usually `process_model: light-single-pass`, `response_routing: none`.

## 6. Theory venues (STOC, FOCS, SODA, CCC, COLT, ITCS)

- Venue CFP + PC / reviewer instructions: is there a rebuttal? a numeric rubric,
  or just an accept/reject lean + confidence? page limit for the main body vs.
  a full-proofs appendix.
- Expect `score_style: none` or a minimal lean; `process_model:
  panel-plus-metareviewer` without a merged comment list, or `light-single-pass`.
- Note in §5 (emphasised criteria): correctness/completeness of proofs,
  significance of the result and the technique — **experiments are not
  expected**; pair with field profile `theory-proofs`.

## 7. Social-science / humanities / medical venues

- **Medical / clinical** (per ICMJE): journal "Instructions for Reviewers";
  which reporting guideline applies (CONSORT / STROBE / TRIPOD / PRISMA /
  STARD); trial-registration, ethics-approval, data-sharing, competing-interest
  requirements; open vs. closed peer review (source of sample reports). Pair
  with field profile `applied-clinical`; fallback `journal-medical`.
- **Social science / humanities** (APSA, ASA, disciplinary journals): reviewer
  guidelines emphasising theoretical framing, method–question fit, and
  engagement with the literature; whether the venue expects quantitative,
  qualitative, or interpretive rigor. Pair with `hci-qualitative` or
  `position-survey`.

## 8. Always

- Record every URL in section 9 of the profile with a one-line note.
- Put everything not found in section 10 (Gaps).
- Always resolve `process_model` and `response_routing` — if unsure, infer from
  the closest match in section 0 / `venue-guidance-generic.md` and say so.
- If the form itself cannot be found, tell the skill which
  `assets/fallback-forms/` file matches: `conference-ml`, `conference-ieee`,
  `journal-referee-report`, `journal-medical`, or `theory-venue`.

## Future hook — OpenReview API

Much of section 1 (live review form JSON, large samples of past reviews with
ratings) is available structured through the OpenReview API. A dedicated
`mcp/openreview` server is out of scope for now; when it exists, steps 1's manual
page-fetching collapses into a couple of API calls. Leave this note here so the
follow-up is discoverable.
