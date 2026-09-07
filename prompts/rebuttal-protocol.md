# Rebuttal protocol (loop mode)

Rules of the author-response loop that runs in `--mode loop` of the
`paper-review` skill. Shared by `response-researcher` and `paper-reviewer`
(rebuttal-eval mode). The skill and `scripts/thread_state.py` enforce the
bookkeeping; this file defines the vocabulary and the conduct.

`last_reviewed: 2026-09-06`

---

## Which variant runs

Set by `venue-profile.md` `response_routing`:

- **`reviewer-visible`** — the K-round loop below: `response-researcher` ↔
  reviewers, `thread_state.py` default mode. Most ML conferences.
- **`chair-or-editor-only`** — the **chair-mediated variant** (section at the
  end): one rebuttal, adjudicated by `review-area-chair`; the reviewers never
  see it and are not re-spawned. IEEE / SPS conferences ("rebuttals are not
  shared with the original reviewers").
- **`none`** — no response stage; the skill goes straight to the decision.

## Participants and information sets

- **`response-researcher`** — acts for the authors. Sees: the paper, all N raw
  reviews (no merge), every prior round's exchange, and — when the user supplied
  them — the codebase / experiment results / reference set (through
  `evidence-gatherer`, read-only).
- **`paper-reviewer` (rebuttal-eval)** — the same reviewers who wrote the
  reviews, now at their assigned thinking level. Sees: the paper, the public
  web, **the other reviewers' reviews and replies** (open discussion), and the
  researcher's rebuttal. **Never** the codebase, result files, or any internal
  author document. *Absent in the chair-mediated variant.*
- **`review-area-chair`** — not present during the reviewer-visible loop; enters
  once, after it. In the chair-mediated variant it is the **only** evaluator of
  the rebuttal.

## One round

1. `response-researcher` writes a single `rebuttal/round-<k>/rebuttal.md`
   addressing every still-`open` / `in_debate` comment (ids `R<i>-<nn>`), each as
   one entry: `stance` + either a concrete correction or a rebuttal argument +
   the evidence it rests on.
2. Each reviewer writes `rebuttal/round-<k>/reviewer-<i>-reply.md` responding to
   **its own** comments (it may briefly note agreement/disagreement with another
   reviewer's point, but only its own comments change state).
3. `thread_state.py` updates every thread's state and reports
   `{changed, terminal, remaining}`.

## Researcher stance vocabulary (one per comment, per round)

| Stance | Meaning | Must include |
|---|---|---|
| `concede-and-fix` | The comment is right; here is the concrete correction. | A typed `fix` object as `final_fix` (`review-comment-taxonomy.md` schema): `kind: edit` with verbatim find/replace, or `kind: work_spec` with an `acceptance` test. |
| `concede-cannot-fix` | The comment is right, but it cannot be addressed with what exists (needs new experiments / data / knowledge the authors do not have here). | What specifically is missing and what would be required. |
| `partially-accept` | Part is right; part is not. | Which part is conceded (+ fix) and which is disputed (+ argument). |
| `dispute` | The comment is mistaken or rests on a misreading. | A specific, evidence-backed argument; a pointer to the paper text or an `evidence-gatherer` finding. |
| `need-clarification` | The researcher cannot respond until the reviewer clarifies what they are asking. | The specific question back to the reviewer. |

**A stance without evidence is not a stance.** `dispute` and `concede-cannot-fix`
must cite something — a line of the paper, a web source, or an
`evidence-gatherer` finding with its `supports` value and confidence. A bare
assertion is treated by `thread_state.py` as `no-response` for that comment.

## Reviewer reply vocabulary (one per own comment, per round)

| Reply | Meaning |
|---|---|
| `resolved` | The researcher's response (fix or argument) fully settles it. |
| `partially-resolved` | Some of it is settled; a named part remains. |
| `unconvinced` | Not settled; the reviewer states specifically why and what would convince them. |
| `need-more` | The reviewer needs another round / more detail before deciding. |
| `withdraw` | The reviewer accepts the rebuttal argument and withdraws the comment. |

A reviewer may also submit `severity: <new>` for one of its comments.

## State transitions (applied by `thread_state.py`)

See `prompts/comment-resolution-states.md` for the full state machine. Summary of
the per-round mapping:

| Researcher stance | Reviewer reply | New state |
|---|---|---|
| `concede-and-fix` | `resolved` | `accepted` |
| `concede-and-fix` | `partially-resolved` / `unconvinced` / `need-more` | `in_debate` |
| `concede-cannot-fix` | `resolved` / `withdraw` | `rebutted` *(agreed not actionable — recorded, not fixed)* |
| `concede-cannot-fix` | anything else | `unresolved_insufficient_info` |
| `dispute` | `withdraw` / `resolved` | `rebutted` |
| `dispute` | `unconvinced` / `partially-resolved` / `need-more` | `in_debate` |
| `partially-accept` | `resolved` | `accepted` (fix = the conceded part) |
| `partially-accept` | otherwise | `in_debate` |
| `need-clarification` | (reviewer answers) | back to `open` with the answer attached |
| any | no reply this round | unchanged |

## Termination

- **Terminal states:** `accepted`, `rebutted`, `unresolved_disagreement`,
  `unresolved_insufficient_info`. Once terminal, a comment is not revisited.
- **Stop the loop** when: every comment is terminal, **or** a full round produced
  zero state changes, **or** `k == K` (`K` default 2).
- **At `k == K`,** every still-`open` / `in_debate` comment becomes
  `unresolved_disagreement` (if the dispute is substantive) or
  `unresolved_insufficient_info` (if the blocker is missing information) — the
  researcher's last stance decides which.
- **Oscillation guard:** if a comment's state has changed direction twice
  (e.g. `open → in_debate → open → in_debate`), force it to
  `unresolved_disagreement` immediately and mark `oscillated: true`.

## `comment-threads.json` schema

```json
{
  "run": "paper-review-<venue><year>-<ts>",
  "K": 2,
  "rounds_run": 2,
  "stopped_because": "converged | no-change | K-reached",
  "threads": [
    {
      "id": "R2-07",
      "reviewer": "R2",
      "category": "missing-results",
      "severity_initial": "major",
      "severity_final": "major",
      "state": "unresolved_insufficient_info",
      "oscillated": false,
      "group": 2,
      "group_reason": "insufficient-info",
      "final_fix": null,
      "rounds": [
        {
          "k": 1,
          "stance": "concede-cannot-fix",
          "researcher_note": "C-E runs were never executed; no logs exist.",
          "evidence": [{"source": "results", "supports": "cannot-tell", "confidence": 2}],
          "replies": {"R2": {"reply": "unconvinced", "why": "then the claim must be cut"}}
        }
      ]
    }
  ]
}
```

## Conduct (both sides)

- Stay evidence-bound. Concede when the evidence is against you.
- No fabricated results, references, or quotes. "We could run X" is not "we ran X".
- Attack the argument, not the participant.
- Keep each entry short: stance, the point, the evidence, done.

## Chair-mediated variant (`response_routing: chair-or-editor-only`)

One pass, no reviewer replies.

1. `response-researcher` writes a single `rebuttal/round-1/rebuttal.md` against
   every `open` comment, same stance vocabulary and evidence rule as above.
2. `review-area-chair` (chair-mediated response mode) rules on **each addressed
   comment** with one line of reasoning, using the chair vocabulary:

   | Chair ruling | Meaning |
   |---|---|
   | `addressed` | the response settles it |
   | `partly` | part settled, a named part remains |
   | `upheld` | the response does not settle it; the weakness stands |
   | `moot` | no longer relevant given other conceded changes |

3. The skill builds `replies.json` from the chair's rulings with
   `reviewer: "AC"` and runs
   `thread_state.py --mediator chair --round 1 --K 1`. State mapping
   (`CHAIR_TABLE` in the script):

   | Researcher stance | Chair ruling | New state |
   |---|---|---|
   | `concede-and-fix` / `partially-accept` | `addressed` | `accepted` (with `final_fix`) |
   | `dispute` / `concede-cannot-fix` / `need-clarification` | `addressed` | `rebutted` |
   | any | `partly` | `in_debate` → forced terminal at round end |
   | any | `moot` | `rebutted` |
   | `dispute` / `partially-accept` / `concede-and-fix` | `upheld` | `unresolved_disagreement` |
   | `concede-cannot-fix` / `need-clarification` | `upheld` | `unresolved_insufficient_info` |
   | (comment not addressed by the rebuttal) | — | forced terminal at round end |

Terminal states and the mapping to output groups are unchanged
(`comment-resolution-states.md`).

## User-seeded challenge (post-review, `challenge/`)

Runs after a completed review (static or loop), when the user disputes specific
comments. It is **not** part of the venue simulation — it always goes
author ↔ reviewer regardless of `response_routing` (the user is pressure-testing
the review's correctness). `--via-chair` optionally routes it through
`review-area-chair` instead.

- Input: `challenge/requests.json` — per comment, the user's `argument` and an
  optional `counter_fix` (a typed `fix` object).
- `response-researcher` runs in **challenge mode**: it argues the user's point on
  evidence, and reports honestly if the evidence is against the user.
- Per challenged comment, for `j = 1..J` (`J = 2`): researcher stance → the one
  reviewer that owns the comment replies → `thread_state.py` (default mediator).
  Same oscillation guard and forced resolution at `j = J`.
- Terminal outcomes: `accepted` (revised typed `fix` recorded), reviewer
  `withdraw` → `rebutted`, or still-disputed after `J` → **`challenged-upheld`**.
- The challenged rows of `review-B` / `review-B1` are rewritten with the revised
  `fix` / severity / state; `challenge/outcomes.json` records every transition.
- No paper edits here — applying still goes through the curation gate.
