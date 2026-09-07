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
depends on `venue_type`, `score_style`, and `process_model`: `A/conference`
(numeric), `A/ordinal-criteria` (per-criterion category labels), `A/journal`, or
`A/editor-mediated` (editor summary, no merged list).

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

### A/ordinal-criteria

For venues that score each criterion with a **named category, not a number**
(many IEEE / society conferences; `score_style: ordinal-categories`). Same
overall shape as `A/conference`, but the per-reviewer `### Scores` block becomes
a `### Criteria` block:

```
## Reviewer 1
### Summary
### Strengths
### Weaknesses
### Detailed comments
### Criteria
<criterion name>: <verbatim category label chosen> — <1–2 sentence justification>
  (repeat for every criterion on the venue's form, e.g. Importance/Relevance,
   Originality/Novelty, Theoretical development, Experimental validation,
   Clarity, Reference to prior work, Overall, Award quality)
### Confidence: <verbatim label>
```

Do not emit a numeric value for any criterion the venue expresses as a category.
The meta-review / summary section is titled per the venue (e.g. "TC-chair
summary").

### A/editor-mediated

For `process_model` `editor-mediated-referees` and `rolling-revision`. There is
**no merged comment list** and no meta-review that fuses the referees.

```
# <venue> <year> — referee reports for "<paper title>"

## Editor summary
- Decision: <one value from venue-profile.md decision set>
- What the authors must address (binding): <bulleted, each → referee id(s)>
- Recommended but not binding (advisory): <bulleted>
- Referee points not carried forward (overruled): <bulleted, each with the reason>
- For rolling-revision: what round this is, and what the next round will check.

## Referee 1
<the venue's referee-report structure, intact, in its own fields/scales>
### Confidential remarks to the editor
### Recommendation: <value from the decision set>

## Referee 2
…
```

`review-B` in this layout is the **union** of referee comments, de-duplicated
only for exact repeats, each keeping its `raised_by`; it is an index for the
authors, not a merged adjudication.

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

### B-01 · missing-results · major · needs-new-work
**Where:** §5.2 Ablations — p7 — `sections/experiments.tex:142`
**Quote:** "we observe consistent gains across all settings"
**Raised by:** R2, R4
**Problem:** …
**Evidence:** …
**Fix (`work_spec` · experiment):**
- Goal: support "we observe consistent gains across all settings"
- Design: run method + baseline on settings C, D, E with the Section-4 protocol
- Conditions: C · D · E · baseline on C/D/E   ·   Metrics: primary metric, mean ± std, 5 seeds
- Acceptance: Table 3 gains a C/D/E block, gain positive and > 1 std each — OR the
  claim is rewritten to "on A and B" (edit below)
- Effort: ~1 day, same compute as the existing Table 3 runs

### B-02 · unsupported-claim · major · needs-reframing
**Where:** Abstract — p1 — `sections/abstract.tex:3`
**Quote:** "the first method to jointly optimise both objectives"
**Fix (`edit`):**
- `sections/abstract.tex:3` — replace
  `the first method to jointly optimise both objectives`
  with
  `among the first methods to jointly optimise both objectives`
  — *why: the "first" claim is not established (Smith 2023)*

### B-03 · …
```

Items are ordered by severity (`blocking` first), then by document position.
Merged items keep every contributing reviewer in **Raised by** and the union of
the strongest severity / actionability. **Every item carries a typed `fix`**
(`prompts/review-comment-taxonomy.md` → "The `fix` object"): a `kind: edit` with
verbatim `find` / `replace`, a `kind: work_spec` with an `acceptance` test, exact
`kind: response_text`, or a `kind: question` with per-answer branches. Free-text
advice ("consider revising") is not an acceptable fix and `check_fixes.py` fails
the run.

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
      "actionability": "needs-new-work",
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
      "fix": {
        "kind": "work_spec",
        "work": {
          "kind": "experiment",
          "goal": "we observe consistent gains across all settings",
          "design": "run method + baseline on C, D, E with the Section-4 protocol",
          "conditions": ["C", "D", "E", "baseline on C/D/E"],
          "metrics": ["primary metric, mean ± std"],
          "data": "existing benchmark; no new data",
          "statistics": "5 seeds per cell",
          "acceptance": "Table 3 gains a C/D/E block with positive gain > 1 std each, OR the claim is rewritten to 'on A and B'",
          "effort": "~1 day, same compute as Table 3"
        }
      }
    },
    {
      "id": "B-02",
      "category": "unsupported-claim",
      "severity": "major",
      "actionability": "needs-reframing",
      "raised_by": ["R1"],
      "location": { "section": "Abstract", "page": 1, "file": "sections/abstract.tex", "line": 3,
                    "quote": "the first method to jointly optimise both objectives" },
      "problem": "…",
      "evidence": "…",
      "fix": {
        "kind": "edit",
        "edits": [
          { "file": "sections/abstract.tex", "line": 3,
            "find": "the first method to jointly optimise both objectives",
            "replace": "among the first methods to jointly optimise both objectives",
            "why": "the 'first' claim is not established (Smith 2023)" }
        ]
      }
    }
  ]
}
```

`location.file` / `location.line` are present only when LaTeX source was
available; otherwise `page` alone anchors the item and the LaTeX pass is skipped.
**`fix` is required on every item** — schema and the per-`actionability` shape are
in `prompts/review-comment-taxonomy.md`. `scripts/check_fixes.py` validates it
(right shape for the `actionability`; every `edit.find` occurs in the source).

---

## Run folder layout

```
paper-review-<venue><year>-<UTC-timestamp>/
  README.md                     # run summary (skill step 9)
  field-profile.md              # the chosen references/field-profiles/<slug>.md
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
**Proposed final_fix:** <a typed `fix` object (taxonomy schema) — `kind: edit` with
  verbatim find/replace, or `kind: work_spec` with an `acceptance` test — or the
  literal `none` if the comment genuinely cannot be actioned>

### R1-03  ·  stance: dispute
…
```

`final_fix` everywhere in loop mode is a **typed `fix` object** (same schema as
`fix` in `review-comment-taxonomy.md`), or `null` / `none`. It is the
**post-rebuttal agreed** version; the reviewer's original `fix` stays in
`reviews/reviewer-<i>.md`.

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

Same layout as static mode for this venue (`A/conference`, `A/ordinal-criteria`,
`A/journal`, or `A/editor-mediated`), with:

- the document opens with **`Final decision: <value>`** (venue vocabulary) and
  the AC / editor rationale;
- the synthesis is the post-discussion one ("after N response rounds + AC
  discussion", or "after the chair-mediated response" for chair-only venues);
- each reviewer block shows `Scores: <name> <initial> -> <final>` only if the
  loop was reviewer-visible; for the chair-mediated variant, scores are the
  originals and the chair's rulings are summarised instead.

## Deliverable A2 — `response-to-reviewers.md`

A clean author response letter, one entry per original comment, drawn from the
final thread state:

```
# Response to reviewers — "<paper title>"

We thank the reviewers. Below we respond to each point; [R#-##] tags cross-
reference the reviews.

## Reviewer 1
**[R1-01] (accepted)** We agree; applied the change (`fix.kind`). See §X.
**[R1-03] (disagreement)** We respectfully disagree: <argument>. <what the AC ruled>.
**[R1-05] (insufficient info)** This would require <work_spec.design>; we note it
as a limitation and future work.
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
  "category": "…", "severity": "…", "actionability": "…",
  "location": { "section": "...", "page": 7, "file": "...", "line": 142, "quote": "..." },
  "problem": "…", "evidence": "…",
  "fix": { "kind": "edit", "edits": [ { "file": "...", "line": 142,
           "find": "<verbatim current text>", "replace": "<verbatim new text>",
           "why": "<agreed rationale>" } ] }
}
```

`fix` here is the **post-rebuttal agreed** version (was `final_fix`). Only
`kind: edit` items can be auto-applied by `apply_corrections.py`; `kind: work_spec`
/ `response_text` / `question` items are listed for manual action.

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

`corrected/` is a copy of the `.tex` tree with every user-accepted B1 item whose
`fix.kind == edit` applied (each `edits[]` entry as a `find` → `replace`) and that
item's `% paper-review` `\todo` line removed. `corrections.diff` is the unified
diff. Local mode compiles it; Overleaf mode records the commits in
`overleaf-commits.md`. Accepted items whose `fix.kind` is `work_spec` /
`response_text` / `question` are listed (not applied) under "needs manual edit"
and, for `work_spec`, also go to `action-list.md`.

## Action list — `action-list.md`

From user-accepted B2 items **and** accepted B1 items with `fix.kind: work_spec`:

```
# Action list — "<paper title>"

Ordered by severity, then group_reason.

## 1. [B2-01 ← R1-03] experiment — support "consistent gains across all settings"   (major · insufficient-info)
Design: run method + baseline on C, D, E with the Section-4 protocol.
Conditions: C · D · E · baseline on C/D/E.   Metrics: primary metric, mean ± std, 5 seeds.
Acceptance: C/D/E block added to Table 3 with gain > 1 std each, OR the claim is scoped to {A, B}.
Effort: ~1 day, same compute as Table 3.

## 2. …
```

Each entry is the item's `fix.work_spec` fields laid out in full — never a
one-line paraphrase.

## Run folder layout (loop mode)

```
paper-review-<venue><year>-<UTC-timestamp>/
  README.md                     # run summary (step 13)
  field-profile.md
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

# Challenge & re-review outputs

Everything a run produces lives under `cycle-<n>/`; `cycle-1/` is the original
review. The three stages (challenge / apply / re-review) are each user-triggered
and never chain automatically.

## `cycle-<n>/challenge/requests.json`

What the user disputed, from chat.

```json
{
  "generated": "YYYY-MM-DDThh:mm:ssZ",
  "requests": [
    { "id": "R2-07", "argument": "the signal model is the standard narrowband one, §3.1",
      "counter_fix": null },
    { "id": "R1-03", "argument": "…",
      "counter_fix": { "kind": "edit", "edits": [ { "find": "…", "replace": "…", "why": "…" } ] } }
  ]
}
```

## `cycle-<n>/challenge/round-<j>/` (j = 1..J, J = 2)

`rebuttal.md` (one per round, `response-researcher` in challenge mode — same
shape as the loop-mode `rebuttal.md`, but every entry opens with
`**User argument:** <verbatim from requests.json>` before the researcher's
stance) and `reviewer-<i>-reply.md` for the one reviewer that owns each
challenged comment.

## `cycle-<n>/challenge/outcomes.json`

```json
{
  "requests_seen": ["R2-07", "R1-03"],
  "outcomes": [
    { "id": "R2-07", "old_state": "open", "new_state": "accepted",
      "old_severity": "major", "new_severity": "minor",
      "revised_fix": { "kind": "edit", "edits": [ { "find": "…", "replace": "…", "why": "…" } ] },
      "transcript_ref": "cycle-1/challenge/round-1/" },
    { "id": "R1-03", "old_state": "open", "new_state": "challenged-upheld",
      "revised_fix": null, "what_would_settle_it": "…",
      "transcript_ref": "cycle-1/challenge/round-2/" }
  ]
}
```

The challenged rows of `review-B` / `review-B1` are rewritten in place with the
`revised_fix` / `new_severity` / `new_state`, and a `## Post-challenge changes`
section is prepended listing what moved and what did not.

## `cycle-<n+1>/reconciliation.{md,json}` (written by `review-area-chair` on re-review)

Produced only when the user runs `re-review` and `corrections.diff` was
non-empty. Compares the prior `cycle-<n>/review-B.json` against the fresh review
of `corrected/paper_v<n>/`.

```json
{
  "prior_cycle": 1, "cycle": 2,
  "applied_diff": "cycle-1/corrected/corrections.diff",
  "items": [
    { "prior_id": "B-01", "status": "resolved", "evidence": "C/D/E block now in Table 3 (§5.2)" },
    { "prior_id": "B-04", "status": "persists", "new_id": "B-02", "note": "edit applied but the claim in §1 still overreaches" },
    { "prior_id": null,   "status": "new", "new_id": "B-05", "note": "the added Table 3 rows use a different metric" }
  ]
}
```

`reconciliation.md` is the same three groups (resolved / persists / new) in prose,
and opens the new `cycle-<n+1>/review-A-venue-style.md`.

## Run folder layout (with challenge / re-review)

```
paper-review-<venue><year>-<UTC-timestamp>/
  cycle-1/
    venue-profile.md  field-profile.md  review-prompt.md
    reviews/  reviewer-*.md  area-chair.md
    review-A-venue-style.md  review-B*.md  review-B*.json
    rebuttal/  …                         # loop mode only
    challenge/  requests.json  round-*/  outcomes.json
    curation/decisions.json
    corrected/  paper_v1/  corrections.diff
    annotated/  …  annotations.diff
  cycle-2/
    reviews/  reviewer-*.md  area-chair.md
    review-A-venue-style.md  review-B*.md  review-B*.json
    reconciliation.md  reconciliation.json
    challenge/  …                        # if the user challenges cycle-2
    …
  review-report.html
  README.md            # per-cycle summary + convergence status
```

For a plain `--mode static` run with no challenge, `cycle-1/` is the whole run
(the pre-existing flat layout is equivalent to `cycle-1/` contents at the run
root; a run only grows the `cycle-<n>/` nesting once `challenge` or `re-review`
is used).

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
      "problem": "…",
      "fix": { "kind": "edit", "edits": [
        { "find": "the first method to jointly optimise both objectives",
          "replace": "among the first methods to jointly optimise both objectives",
          "why": "the 'first' claim is not established" } ] },

      // loop mode only:
      "group": 1, "group_reason": "agreed",
      "state": "accepted",
      "final_fix": { "kind": "edit", "edits": [ /* post-rebuttal agreed version */ ] },
      "challenge": { "state": "challenged-upheld", "rounds": 2,
                     "outcome": "…", "transcript_ref": "cycle-1/challenge/round-2/…" },
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

`fix` (and `final_fix`) are the typed `fix` objects from
`review-comment-taxonomy.md`. Static-mode comments omit `group` / `state` /
`thread` / `final_fix` / `challenge`; the page then shows no curation control and
no threads. `challenge` is present only on comments the user challenged.

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
