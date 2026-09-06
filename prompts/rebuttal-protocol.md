# Rebuttal protocol (loop mode)

Rules of the author-response loop that runs in `--mode loop` of the
`paper-review` skill. Shared by `response-researcher` and `paper-reviewer`
(rebuttal-eval mode). The skill and `scripts/thread_state.py` enforce the
bookkeeping; this file defines the vocabulary and the conduct.

`last_reviewed: 2026-09-06`

---

## Participants and information sets

- **`response-researcher`** — acts for the authors. Sees: the paper, all N raw
  reviews (no merge), every prior round's exchange, and — when the user supplied
  them — the codebase / experiment results / reference set (through
  `evidence-gatherer`, read-only).
- **`paper-reviewer` (rebuttal-eval)** — the same reviewers who wrote the
  reviews, now at their assigned thinking level. Sees: the paper, the public
  web, **the other reviewers' reviews and replies** (open discussion), and the
  researcher's rebuttal. **Never** the codebase, result files, or any internal
  author document.
- **`review-area-chair`** — not present during the loop. Enters once, after it.

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
| `concede-and-fix` | The comment is right; here is the concrete correction. | The exact text/structure change (`final_fix`), and where it goes. |
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
