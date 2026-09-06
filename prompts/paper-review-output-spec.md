# Paper-review output specification

Defines the exact shape of the deliverables the `paper-review` skill produces.
The reviewer subagents and the area chair / editor all write to this spec so the
skill can assemble the run folder mechanically.

`last_reviewed: 2026-09-07`

- **`--mode static`** (default): sections "Per-reviewer output" through
  "Run folder layout" below. One pass; deliverables A and B.
- **`--mode loop`**: the section "Loop mode outputs" at the end. Adds the
  author-response loop artifacts, the two comment groups (B1 / B2), the curation
  gate, and the applied corrections / action list. In loop mode there is **no
  pre-loop merge** and reviews are kept per-reviewer.

---

## Per-reviewer output (intermediate, one per `paper-reviewer`)

A single Markdown document:

```
## THOUGHT
<free-form reasoning for the area chair; not shown to authors>

## REVIEW
<the venue form from venue-profile.md section 1, every field filled,
 every score from section 2 with a one-to-two sentence justification>

## COMMENTS
<YAML list; each entry is the metadata block from review-comment-taxonomy.md>
```

Reviewer ids are `R1`, `R2`, … assigned by the skill. Comment ids are
`<reviewer-id>-<nn>`.

---

## Deliverable A — `review-A-venue-style.md`

The package a submitter would receive back, in the venue's own vocabulary. Layout
depends on `venue_type`.

### A/conference

```
# <venue> <year> — review package for "<paper title>"

## Meta-review (area chair)
- Recommendation: <one value from venue-profile.md section 3>
- Summary of the discussion: <2-4 paragraphs reconciling the reviews:
  points of agreement, unresolved disagreements, what would change the outcome>
- Key factors in the recommendation: <bullet list, each tied to reviewer items>

## Reviewer 1
<the venue form, all fields + scores, exactly as the form defines them>
### Strengths
### Weaknesses
### Questions
### Additional feedback
### Ethics flags
### Scores
<name: value — justification>

## Reviewer 2
…

## Reviewer 3
…
```

### A/journal

```
# <venue> <year> — referee reports for "<paper title>"

## Editor recommendation
- Decision: <one value from venue-profile.md section 3, e.g. "major revision">
- Editor summary: <2-4 paragraphs: what must be addressed for the next round,
  which referee points are binding, which are advisory>

## Referee 1
### Summary of the manuscript
### Is the work novel and (if the venue requires it) of broad significance?
### Are the claims fully supported by the data / analysis?
### Statistics and reporting standards
### Major points
### Minor points
### Confidential remarks to the editor
### Recommendation: <value from the decision set>

## Referee 2
…
```

If a fallback form from `assets/fallback-forms/` was used because the real form
could not be found, deliverable A must say so at the top, in bold, naming which
fallback.

---

## Deliverable B — `review-B-point-by-point.md` + `review-B.json`

The merged, de-duplicated correction list. This is the authors' actionable
to-do list and the input to the LaTeX annotation pass.

### `review-B-point-by-point.md`

```
# Point-by-point corrections — "<paper title>"

Counts: blocking N · major N · minor N · nit N        (total N)
By category: missing-results N · methodological-concern N · …

---

### B-01 · missing-results · major · needs-new-experiments
**Where:** §5.2 Ablations — p7 — `sections/experiments.tex:142`
**Quote:** "we observe consistent gains across all settings"
**Raised by:** R2, R4
**Problem:** …
**Evidence:** …
**Suggested fix:** …

### B-02 · …
```

Items are ordered by severity (`blocking` first), then by document position.
Merged items keep every contributing reviewer in **Raised by** and the union of
the strongest severity / actionability.

### `review-B.json`

Machine-readable sidecar for `scripts/build_annotations.py`. One object:

```json
{
  "paper_title": "…",
  "venue": "…",
  "generated": "YYYY-MM-DDThh:mm:ssZ",
  "source_mode": "pdf-only | latex-local | latex-overleaf",
  "items": [
    {
      "id": "B-01",
      "category": "missing-results",
      "severity": "major",
      "actionability": "needs-new-experiments",
      "raised_by": ["R2", "R4"],
      "location": {
        "section": "5.2 Ablations",
        "page": 7,
        "file": "sections/experiments.tex",
        "line": 142,
        "quote": "we observe consistent gains across all settings"
      },
      "problem": "…",
      "evidence": "…",
      "suggested_fix": "…"
    }
  ]
}
```

`location.file` / `location.line` are present only when LaTeX source was
available; otherwise `page` alone anchors the item and the LaTeX pass is skipped.

---

## Run folder layout

```
paper-review-<venue><year>-<UTC-timestamp>/
  README.md                     # run summary (skill step 9)
  venue-profile.md
  review-prompt.md              # the composed tailored prompt
  reviews/
    reviewer-1.md
    reviewer-2.md
    reviewer-3.md
    area-chair.md
  review-A-venue-style.md
  review-B-point-by-point.md
  review-B.json
  annotated/                    # latex-local mode only: annotated copy + PDF + log
  annotations.diff              # latex mode: the unified diff that was applied
  overleaf-commits.md           # latex-overleaf mode only: commits made + how to revert
```

---

# Loop mode outputs (`--mode loop`)

## Reviews are kept per-reviewer

`reviews/reviewer-<i>.md` (same per-reviewer shape as above), **not merged**.
Comment ids stay `R<i>-<nn>` all the way through. After the loop each reviewer
also writes `reviews/reviewer-<i>-post-rebuttal.md`:

```
## POST-REBUTTAL UPDATE — R<i>
Scores: <name>: <old> -> <new> (— one-line reason) ; …
Overall stance change: <e.g. "leaning reject -> borderline">
```

## Round artifacts — `rebuttal/round-<k>/`

`rebuttal.md` (one per round, written by `response-researcher`):

```
# Rebuttal — round <k>

### R2-07  ·  stance: concede-cannot-fix
**Point:** <the reviewer's comment, one line>
**Response:** <correction text, or the argument>
**Evidence:** <source: code|results|references|paper|web> — supports: yes|no|partial|cannot-tell — confidence 1-5 — <1 line>
**Proposed final_fix:** <exact text/structure change, or "none — needs new experiments">

### R1-03  ·  stance: dispute
…
```

`reviewer-<i>-reply.md` (one per reviewer per round):

```
# R<i> reply — round <k>

### R<i>-03  ·  reply: unconvinced
**Why:** <specific, what would convince me>
**Severity:** major   (unchanged | -> minor)

### R<i>-05  ·  reply: resolved
```

## `rebuttal/comment-threads.json`

Exactly the schema in `prompts/rebuttal-protocol.md` (`run`, `K`, `rounds_run`,
`stopped_because`, `threads[]` with per-round entries and the final `state`,
`group`, `group_reason`, `final_fix`).

## `rebuttal/discussion-log.md` (area chair, single pass)

```
# Area-chair discussion & decision — "<paper title>"

## Final decision: <accept | reject | … venue vocabulary>
<2-4 paragraph rationale citing specific comment ids and their rebuttal outcomes>

## Contested comments
### R1-03 — <one-line topic>   [→ Group 2 / disagreement]
- R1 position: …
- Author position: …
- Pros of the author's view: …
- Cons: …
- AC call: <the adjudication> — because …

### R2-07 — …

## Withdrawn after rebuttal
- R3-02 — reviewer withdrew because <argument that settled it>
```

## Deliverable A — `review-A-venue-style.md`

Same A/conference or A/journal layout as static mode, with:

- the document opens with **`Final decision: <value>`** and the AC rationale;
- the meta-review is the post-discussion one ("after N response rounds + AC
  discussion");
- each reviewer block shows `Scores: <name> <initial> -> <final>`.

## Deliverable A2 — `response-to-reviewers.md`

A clean author response letter, one entry per original comment, drawn from the
final thread state:

```
# Response to reviewers — "<paper title>"

We thank the reviewers. Below we respond to each point; [R#-##] tags cross-
reference the reviews.

## Reviewer 1
**[R1-01] (accepted)** We agree. We have <final_fix>. See §X.
**[R1-03] (disagreement)** We respectfully disagree: <argument>. <what the AC ruled>.
**[R1-05] (insufficient info)** This would require <new experiment>; we note it as
a limitation and future work.
```

## Deliverable B1 — `review-B1-agreed-corrections.md` + `review-B1.json`

Group 1 only (`state == accepted`). Markdown as in static deliverable B. JSON is
the static `review-B.json` schema per item plus:

```json
{
  "id": "B1-01",
  "source_ids": ["R2-07", "R4-03"],
  "resolution": "accepted",
  "group_reason": "agreed",
  "thread_ref": "rebuttal/comment-threads.json#R2-07",
  "final_fix": "<the exact agreed text/structure change>",
  "category": "…", "severity": "…", "actionability": "…",
  "location": { "section": "...", "page": 7, "file": "...", "line": 142, "quote": "..." },
  "problem": "…", "evidence": "…", "suggested_fix": "…"
}
```

## Deliverable B2 — `review-B2-unresolved.md` + `review-B2.json`

Group 2 (`unresolved_disagreement` ∪ `unresolved_insufficient_info`). Per item:

```json
{
  "id": "B2-01",
  "source_ids": ["R1-03"],
  "resolution": "unresolved_disagreement",
  "group_reason": "disagreement",
  "thread_ref": "rebuttal/comment-threads.json#R1-03",
  "thread_summary": "<2-3 sentences: what each side held, where it stuck>",
  "what_would_settle_it": "<the missing experiment / data / decision>",
  "category": "…", "severity": "…",
  "location": { "...": "..." }
}
```

## Curation gate — `curation/decisions.json`

Written from the user's accept/reject choices in the main chat. The skill blocks
until this file exists.

```json
{
  "generated": "YYYY-MM-DDThh:mm:ssZ",
  "decisions": [
    { "id": "B1-01", "group": 1, "user": "accept", "note": "" },
    { "id": "B1-04", "group": 1, "user": "reject", "note": "reviewer misread; leave as is" },
    { "id": "B2-01", "group": 2, "user": "accept", "note": "add to camera-ready plan" }
  ]
}
```

## Applied corrections — `corrected/` + `corrections.diff`

`corrected/` is a copy of the `.tex` tree with every user-accepted B1 `final_fix`
applied and that item's `% paper-review` `\todo` line removed. `corrections.diff`
is the unified diff. Local mode compiles it; Overleaf mode records the commits in
`overleaf-commits.md`. Items whose `final_fix` is not a self-contained text edit
are listed (not applied) under "needs manual edit" in the run summary.

## Action list — `action-list.md`

From user-accepted B2 items:

```
# Action list — "<paper title>"

Ordered by severity, then group_reason.

## 1. [B2-01 ← R1-03] Run the C–E ablation settings   (major · insufficient-info)
Why: reviewer R1 holds the "consistent gains" claim is unsupported for C–E.
What settles it: results for settings C, D, E added to Table 3, or the claim scoped to {A,B}.

## 2. …
```

## Run folder layout (loop mode)

```
paper-review-<venue><year>-<UTC-timestamp>/
  README.md                     # run summary (step 13)
  venue-profile.md
  review-prompt.md
  reviews/
    reviewer-1.md  reviewer-2.md  reviewer-3.md
    reviewer-1-post-rebuttal.md  …
  rebuttal/
    round-1/  rebuttal.md  reviewer-1-reply.md  reviewer-2-reply.md  reviewer-3-reply.md
    round-2/  …
    comment-threads.json
    discussion-log.md
  evidence/  code-*.md  results-*.md  refs-*.md
  response-to-reviewers.md
  review-A-venue-style.md
  review-B1-agreed-corrections.md  review-B1.json
  review-B2-unresolved.md          review-B2.json
  annotated/  …  annotations.diff  (or overleaf-commits.md)
  curation/  decisions.json
  corrected/  …  corrections.diff
  action-list.md
```

## Run summary additions (step 13)

- `--mode loop`, `K`, rounds run, `stopped_because`.
- Oscillation count.
- AC final decision + one-line rationale.
- Table: comment id × final state × group × user decision.
- Links to `corrected/`, `action-list.md`; list of "needs manual edit" items.
- The published `review-report` Artifact URL.

---

# Review report Artifact (both modes)

Authored from `skills/paper-review/assets/review-report-template.html` by
substituting a **report object** into `<script id="report-data">`, saved as
`review-report.html` in the run folder, and published as an Artifact (loop mode:
with `capabilities: {db: {}}`). The template renders the page and, in loop mode,
the curation control.

## Report object

```json
{
  "meta": {
    "paper": "…", "venue": "…", "year": "2026",
    "mode": "static | loop", "K": 2,
    "generated": "YYYY-MM-DD",
    "example": false,
    "run_folder": "paper-review-…/",
    "annotated_pdf": "annotated/main.pdf"
  },

  "decision":       { "value": "reject", "rationale": "…" },     // loop mode
  "recommendation": { "value": "Borderline reject (3/6)", "rationale": "…" },  // static mode

  "reviewers": [
    { "id": "R1", "level": "deep",
      "scores": [ { "name": "Overall", "initial": 3, "final": 3, "scale": "1-6" },
                  { "name": "Confidence", "value": 4 } ],   // static: use "value"; loop: "initial"/"final"
      "summary": "…" }
  ],

  "comments": [
    { "id": "R1-02", "reviewer": "R1",
      "category": "unsupported-claim", "severity": "blocking",
      "actionability": "needs-reframing",
      "location": "Abstract - p1 - sections/abstract.tex:3",
      "quote": "the first method to …",
      "problem": "…", "suggested_fix": "…",

      // loop mode only:
      "group": 1, "group_reason": "agreed",
      "state": "accepted",
      "final_fix": "…",
      "thread": [
        { "k": 1, "stance": "concede-and-fix", "note": "…",
          "evidence": "paper S3 - supports:no - conf 4",
          "replies": [ { "reviewer": "R1", "reply": "resolved", "why": "" } ] }
      ]
    }
  ],

  "response_letter": "…"     // loop mode only
}
```

Static-mode comments omit `group` / `state` / `thread` / `final_fix`; the page
then shows no curation control and no threads.

## Curation store (loop mode)

The page writes each choice to the artifact `db` at:

```
collection: "curation"
doc id:     "<comment-id>"          e.g. "R1-02"
document:   { "id": "R1-02", "group": 1,
              "decision": "accept" | "reject" | null,
              "note": "", "at": "ISO-8601" }
```

The skill reads this collection back (`Artifact` `action: "read_db"`,
`db_op: "list"`, `collection: "curation"`) and derives
`curation/decisions.json` — one `{id, group, user, note}` per curated comment.

## Run-folder addition

`review-report.html` (the data-substituted template) is saved alongside the
other deliverables in both modes; the published URL goes in the run `README.md`.
