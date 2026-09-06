# Generic venue guidance — the map `venue-researcher` fills in

Frozen Phase-0 synthesis. It describes the **shape** of academic review across
venue types so the researcher knows what to look for and where the per-run venue
profile's slots come from. It contains no venue-specific values — those are
discovered per run.

`last_reviewed: 2026-09-06`

---

## The three venue types

| | Conference | Journal | Workshop |
|---|---|---|---|
| Cycle | one round, fixed deadlines | multiple rounds until accept/reject | one light round |
| Reviewer output | structured form + scores | referee report (mostly prose) + confidential note to editor | short form / free comments |
| Synthesis role | area chair / senior program committee / meta-reviewer | handling editor / associate editor | organiser |
| Author interaction | rebuttal in a fixed window, sometimes discussion | response-to-reviewers letter each round | often none |
| Decision set | accept / (oral/poster/spotlight) / borderline / reject | accept / minor revision / major revision / reject & resubmit / reject | accept / reject (non-archival common) |
| Rating | almost always numeric | often none to authors; sometimes a confidential 1–N to the editor | light or none |
| Extra requirements | reproducibility checklist, broader-impact / ethics statement, anonymity | data & code availability, reporting standards, competing interests, funding, ethics/IRB | usually minimal |

## What varies venue to venue (the profile's slots)

1. **Form fields and their order.** From a handful (ICASSP-style: summary,
   strengths, weaknesses, detailed comments, scores) to a dozen (NeurIPS-style:
   separate quality / clarity / significance / originality / limitations /
   questions / ethics fields).

2. **Score names and scale text.** The *numbers* are meaningless without the
   label text: a `4` is "excellent" on a 1-4 quality scale but "borderline
   accept" on a 1-6 overall scale. Always capture the verbatim labels. Common
   shapes: 1-4 ordinal quality dimensions; 1-6 or 1-10 overall; 1-5 confidence.
   Journals frequently have **no** author-facing score.

3. **Decision vocabulary.** Conferences decide once (accept/reject, sometimes
   with a presentation tier). Journals iterate: "minor revision" (editor decides
   next round), "major revision" (back to reviewers), "reject & resubmit" (treated
   as a new submission), "reject". Use the venue's exact words in deliverable A.

4. **Emphasis.** Some venues weight reproducibility heavily; some require broad
   general significance (Nature-family) rather than domain significance; some
   have an applications track where theoretical novelty is not required; IEEE
   venues care about correctness and relation to prior IEEE work; ML venues care
   about baselines and ablations.

5. **Mandatory statements / checklists.** Reproducibility checklist,
   broader-impact statement, limitations section, data-availability statement,
   code-availability statement, reporting summary, competing-interests
   declaration, funding disclosure, use-of-LLM disclosure, ethics/IRB approval.
   Which exist and which are mandatory is venue- and year-specific.

6. **Review model.** Single-blind, double-blind, or open. Affects whether the
   reviewer should avoid guessing authors and whether anonymity slips are a
   reportable issue.

7. **Author interaction rules.** Whether a rebuttal exists, its length and
   window, whether reviewers discuss, how many rounds.

## Where to find each (search order)

- **Conferences:** the year's site → "Call for Papers", "Reviewer Guidelines" /
  "Reviewer Instructions", "Area Chair Guidelines", "Ethics Guidelines",
  "Author Guidelines" (for the checklist the authors had to fill). OpenReview
  venue page for the live review form and for sample reviews of accepted/rejected
  papers.
- **Journals:** publisher site → "For Referees" / "Guide to Referees" /
  "Information for Reviewers", "Editorial Policies", "Submission Guidelines"
  (for the required statements). Society editorial-procedures page for IEEE.
  Transparent-peer-review / published-peer-review files for sample reports.
- **Workshops:** the workshop's own page; falls back to its parent conference's
  norms.
- **Always:** record the URL for every value; mark `not found` honestly; mark
  `not applicable` where a slot does not exist for this venue type.

## Fallbacks

If the real form cannot be found, the skill uses `assets/fallback-forms/`:
`conference-ml.md`, `conference-ieee.md`, or `journal-referee-report.md`, chosen
by `venue_type` and publisher. Deliverable A must then state, in bold, that a
generic fallback form was used.
