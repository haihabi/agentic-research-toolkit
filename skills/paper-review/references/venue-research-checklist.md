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

## 2. IEEE conferences (ICASSP, ICIP, ICME, ICC, INFOCOM, …)

- `<year>.<conf>.org/editorial-procedures/` or `/reviewer-guidelines/` — scoring
  criteria (often quality / relevance / correctness / novelty), score scale,
  recommendation categories.
- `<year>.<conf>.org/author-kit-instructions/` — page limit, anonymity, template.
- IEEE publication ethics & plagiarism policy (`ieee.org`).
- Sample reviews: IEEE conference reviews are private; note that and rely on the
  editorial-procedures description of what a good review contains.

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

## 6. Always

- Record every URL in section 9 of the profile with a one-line note.
- Put everything not found in section 10 (Gaps).
- If the form itself cannot be found, tell the skill which
  `assets/fallback-forms/` file matches (`conference-ml`, `conference-ieee`,
  `journal-referee-report`).

## Future hook — OpenReview API

Much of section 1 (live review form JSON, large samples of past reviews with
ratings) is available structured through the OpenReview API. A dedicated
`mcp/openreview` server is out of scope for now; when it exists, steps 1's manual
page-fetching collapses into a couple of API calls. Leave this note here so the
follow-up is discoverable.
