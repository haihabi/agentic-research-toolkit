# paper-review — concrete fixes + challenge/re-review cycle

Status: **implemented** on branch `debias-paper-review` (2026-09-06), on top of
the venue/field de-bias work (`paper-review-debias-plan.md`).

Two changes, composed: every review comment must carry a **concrete, typed
`fix`** (Part 1); a user can then **challenge** specific comments and, when the
challenge changes the paper text, **re-review** on demand (Part 2).

---

## Part 1 — every fix is concrete and applyable

### Problem

`suggested_fix` was free prose ("add the runs, or scope the claim") — not an
edit, not applyable, no detail for new-work items.

### The typed `fix` object

Replaces `suggested_fix` (and the old optional `patch`) in the taxonomy metadata
block. Shape keyed to `actionability`:

| `actionability` | `fix.kind` | payload |
|---|---|---|
| `defer-to-final-version`, most `incorrect-statement` / `unclear-statement` / `presentation` / `missing-context` | `edit` | `edits: [{file, line, find, replace, why}]` — `find` verbatim from the paper, `replace` the full new text |
| `needs-reframing` | `edit` | one edit per sentence/claim, may span locations |
| `resolve-in-response-text` | `response_text` | `text:` the exact paragraph for the authors' response |
| `needs-new-work` | `work_spec` | `work: {...}` (schema below) |
| `needs-author-clarification` | `question` | `question:` + `answers: [{if, then_severity, then_fix}]` |

`work_spec`:

```yaml
work:
  kind: experiment | ablation | proof | derivation | measurement | user-study | analysis | dataset-addition
  goal: "<claim this must support — quoted from the paper>"
  design: "<what to run / build / prove>"
  conditions: [...]          # empirical kinds
  metrics: [...]             # incl. the comparison / bound
  data: "<dataset / instrument / participants + N and why>"
  statistics: "<trials or seeds, test, effect sizes>"
  proof_obligation: "<proof/derivation: exact statement + the gap>"
  acceptance: "<the specific result that resolves the comment>"
  effort: "<hours | days | weeks; + compute>"
```

Field profiles (§3) state which `work_spec` fields are mandatory per `kind`.

### Enforcement

- `paper-reviewer` / `review-area-chair` rules: a comment without a well-formed
  `fix` for its `actionability` is incomplete; the reflection pass fills it; the
  AC unions `edits` / takes the strongest `work_spec`, never collapses to prose.
- New `scripts/check_fixes.py` — asserts every `review-B*.json` item has a
  well-formed `fix`, and every `edit.find` occurs in the source. Runs in the
  skill before deliverable B is finalised, and in evals.
- `apply_corrections.py` consumes `fix.edits[]` (every `kind: edit` is a real
  patch → far more auto-applies); `build_annotations.py` renders `work_spec` as a
  full `\todo` block and a detailed `action-list.md` entry.

### Files

`prompts/review-comment-taxonomy.md`, `prompts/paper-review-base.md`,
`prompts/paper-review-output-spec.md`, `agents/paper-reviewer.md`,
`agents/review-area-chair.md`, `agents/response-researcher.md`,
`skills/paper-review/references/field-profiles/*.md`,
`skills/paper-review/scripts/{check_fixes.py (new),apply_corrections.py,build_annotations.py}`,
`skills/paper-review/SKILL.md`, `support/evals/skills/paper-review/README.md`.

---

## Part 2 — challenge & re-review (all three stages user-triggered)

After any `cycle-1` review (static or loop). Nothing chains automatically.

### Stage A — challenge (`challenge <id>: <argument>` in chat; `--J` = 2)

Per disputed comment, for `j = 1..2`:

1. `response-researcher` (**challenge mode**) argues the user's point,
   evidence-bound (may call `evidence-gatherer` if `--code/--results/--refs`
   given); writes a stance. If the evidence is against the user, it says so.
2. That comment's reviewer (`paper-reviewer`, rebuttal-eval) replies.
3. `thread_state.py` (default mediator) updates just those threads; oscillation
   guard + forced resolution at `j = 2`.
4. Concession → the conceding party authors the revised `fix` (Part 1 shape).
   Still upheld after 2 rounds → `challenged-upheld` (Group 2 / disagreement),
   transcript kept.

Writes `cycle-<n>/challenge/{requests.json,round-*/,outcomes.json}` and rewrites
the challenged rows of `review-B` / `review-B1`, prepending `## Post-challenge
changes`.

### Stage B — curate & apply (existing curation gate)

User picks which agreed/revised fixes to apply. `kind: edit` fixes auto-apply
(`apply_corrections.py`) → `cycle-<n>/corrected/paper_v<n>/` + `corrections.diff`.
`work_spec` items go to `action-list.md`, never the paper.

### Stage C — re-review (user-triggered only)

The skill records that the text changed and stops. On an explicit `re-review`
(or `paper-review re-review <run-folder>`):

- re-run **steps 5–10 only** on the latest `paper_v<n>/`, reusing
  `venue-profile.md` / `field-profile.md` / `review-prompt.md`;
- the panel gets the prior `review-B` + `corrections.diff` as prior-round
  context and marks each prior point **resolved / persists / new**;
- output → `cycle-<n+1>/` with `reconciliation.md`.
- If `corrections.diff` is empty, `re-review` is a no-op and says so.

No `--max-cycles`: the user decides how many times to go around.

### Run folder

```
paper-review-<venue><year>-<ts>/
  cycle-1/  venue-profile.md field-profile.md review-prompt.md
            reviews/  review-A-*.md  review-B*.{md,json}
            challenge/  requests.json round-*/  outcomes.json
            curation/decisions.json
            corrected/  paper_v1/  corrections.diff
  cycle-2/  reviews/ review-A-*.md review-B*.{md,json}  reconciliation.md
            challenge/ …
  README.md  # per-cycle summary + convergence status
```

### Files

`skills/paper-review/SKILL.md` (new "## Challenge & re-review" section — A/B/C as
separate entry points), `agents/response-researcher.md` (challenge mode),
`agents/paper-reviewer.md` (re-review mode), `agents/review-area-chair.md`
(`reconciliation.md`), `prompts/rebuttal-protocol.md` (user-seeded subsection),
`prompts/comment-resolution-states.md` (`challenged-upheld`),
`prompts/paper-review-output-spec.md` (`cycle-<n>/` layout, `outcomes.json`,
`reconciliation.{md,json}`), `docs/paper-review-system.md` (Panel E),
`skills/paper-review/README.md`, `adapters/claude-code/paper-review.md`,
`support/evals/skills/paper-review/README.md`.

## Build order

Part 1 (fix schema + `check_fixes.py`) → Part 2 (challenge/re-review).
