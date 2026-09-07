# paper-review — system diagram

How the `paper-review` skill is wired, in both modes. This file is the source of
record; Panels A and B are also published as an interactive Artifact.

The review prompt is always `paper-review-base.md` (venue- and field-agnostic) +
a **field profile** (`--field`: what validity/evidence/novelty mean for this
paper type) + the per-run **venue profile** (form, scales, decision set, and
`process_model`). `process_model` selects the synthesis step and the loop shape
(Panel D).

- **`static` mode** (Panel A) — one review pass: reviewer panel →
  `review-area-chair` synthesis (merge for `panel-plus-metareviewer`; editor
  summary for `editor-mediated-referees`; light note for a workshop) →
  deliverables A + B → `todonotes`.
- **`loop` mode** (Panel B) — adds the author-response stage, an end-of-loop
  decision, the Group 1 / Group 2 split, a human curation gate, and then real
  paper corrections + an action list. The stage is a reviewer-visible K-round
  rebuttal, a single chair-mediated pass, or an editor-mediated revision round —
  see Panel D.

Both modes also publish a per-run **review-report Artifact** (from
`skills/paper-review/assets/review-report-template.html`) — a browsable dashboard
of reviewers and comments; in loop mode it carries the rebuttal threads, the
decision, and a live per-comment Accept / Reject curation control backed by the
artifact `db`.

---

## Panel A — `static` mode (single pass)

```mermaid
flowchart TB
  INa[/"paper PDF · venue+year · optional LaTeX"/] --> VRa[venue-researcher]
  VRa --> RPa[review-prompt.md]
  RPa --> Pa["N paper-reviewers (uniform)"]
  Pa --> ACMa["review-area-chair — merge"]
  ACMa --> Aa["deliverable A<br/>scores + recommendation"]
  ACMa --> Ba["deliverable B<br/>every comment, unverified"]
  Ba --> TEXa["LaTeX todonotes<br/>(all comments)"]
```

Nothing tests whether a comment is right, fixable, or already answerable — every
comment lands in deliverable B and every one gets a `\todo`.

---

## Panel B — `loop` mode

```mermaid
flowchart TB
  IN[/"paper PDF · venue+year · optional LaTeX<br/>· optional code / results / refs · K"/]
  IN --> VR[venue-researcher] --> RP[review-prompt.md]
  RP --> P1["paper-reviewer R1<br/>deep thinking"]
  RP --> P2["paper-reviewer R2<br/>medium"]
  RP --> P3["paper-reviewer R3<br/>light"]

  P1 --> LOOP
  P2 --> LOOP
  P3 --> LOOP

  subgraph LOOP ["Author-response loop — K rounds, early-stop · NO area chair · NO todonotes"]
    direction LR
    RS["response-researcher<br/>(authors' side) · reads ALL reviews"] -->|targeted questions| EV["evidence-gatherer<br/>code · results · refs — read-only"]
    EV -->|finding + citations + confidence| RS
    RS -->|"rebuttal round k<br/>stance + fix / argument + evidence"| RVW["reviewers R1..RN — rebuttal-eval<br/>paper + web + each other's reviews"]
    RVW -->|"reply: resolved / partial / unconvinced"| ST{{"thread_state.py<br/>state machine + oscillation guard"}}
    ST -->|not converged| RS
  end

  LOOP --> POST["reviewers: post-rebuttal score updates"]
  POST --> AC2["review-area-chair — END, single invocation<br/>discussion (pros/cons) → adjudicate contested<br/>→ FINAL DECISION accept / reject + why"]
  AC2 --> DA["review-A (post-discussion)<br/>decision + rationale + score deltas"]
  AC2 --> A2[response-to-reviewers.md]
  AC2 --> PART{{partition}}
  PART --> G1["Group 1 — accepted<br/>review-B1 + JSON"]
  PART --> G2["Group 2 — unresolved<br/>review-B2 + JSON"]
  G1 --> ANN["annotate paper — todonotes<br/>local copy or Overleaf (once)"]
  G2 -.->|--annotate-unresolved| ANN
  ANN --> RPT["review-report Artifact<br/>threads · G1/G2 · decision · curation control (db)"]
  RPT --> MC{{"back to MAIN CHAT<br/>user accepts / rejects each comment (on the report or in chat)<br/>→ curation/decisions.json"}}
  MC -->|accepted G1| FIX["apply_corrections.py<br/>correct the paper → corrected/ + diff"]
  MC -->|accepted G2| ACT["action-list.md<br/>experiments / clarifications to do"]
```

---

## Panel C1 — comment lifecycle (state machine)

```mermaid
stateDiagram-v2
  [*] --> open
  open --> accepted: concede-and-fix + reviewer resolved
  open --> rebutted: dispute + reviewer withdraw/resolved  //  or concede-cannot-fix + withdraw
  open --> in_debate: partial agreement / unconvinced / need-more
  open --> unresolved_insufficient_info: concede-cannot-fix + reviewer still presses
  in_debate --> accepted
  in_debate --> rebutted
  in_debate --> unresolved_insufficient_info
  in_debate --> unresolved_disagreement: K rounds reached, or state oscillated twice
  accepted --> [*]
  rebutted --> [*]
  unresolved_disagreement --> [*]
  unresolved_insufficient_info --> [*]
```

Group 1 = `accepted`. Group 2 = `unresolved_disagreement` ∪
`unresolved_insufficient_info`. `rebutted` is recorded in the discussion log only.

---

## Panel C2 — one loop round (sequence; area chair absent until the end)

```mermaid
sequenceDiagram
  participant SK as skill (orchestrator)
  participant RS as response-researcher
  participant EV as evidence-gatherer
  participant RV as reviewers R1..RN
  participant ST as thread_state.py

  Note over SK,ST: input = all N raw reviews, comments R&lt;i&gt;-&lt;nn&gt;, state = open
  loop each round k = 1..K  (SK stops early when a round changes nothing)
    RS->>EV: per-comment questions (code / results / refs)
    EV-->>RS: finding + supports(yes/no/partial/cannot-tell) + citations + confidence
    RS->>RV: rebuttal round k — one doc, per comment: stance + fix-or-argument + evidence
    Note over RV: each reviewer also sees the other reviews and replies
    RV-->>RS: reply per own comment — resolved / partial / unconvinced / need-more (+ severity change)
    RS->>ST: round-k stances + reviewer replies
    ST-->>SK: {changed, terminal, remaining} + oscillation flags
  end
  RV->>SK: post-rebuttal score updates (original -> revised)
```

The area chair, the curation gate, and the apply step happen after this loop —
see Panel B.

---

## Panel D — loop shape by `process_model` / response routing

```mermaid
flowchart TB
  RUN[/"reviews R1..RN (raw) + venue-profile.process_model"/] --> Q{response routing?}

  Q -->|reviewer-visible<br/>ML confs| RV["K-round rebuttal loop<br/>response-researcher ↔ reviewers<br/>thread_state.py (default)"]
  Q -->|chair-or-editor-only<br/>IEEE / SPS confs| CM["chair-mediated (1 pass)<br/>response-researcher → review-area-chair<br/>reviewers NOT re-spawned<br/>thread_state.py --mediator chair"]
  Q -->|none<br/>workshops / no rebuttal| NO["skip response stage"]
  Q -->|rolling-revision<br/>journals / security| RR["response letter + revision plan<br/>editor issues this round's decision<br/>K ignored (rounds = separate runs)"]

  RV --> DEC["review-area-chair — end-of-loop decision<br/>(metareviewer or handling-editor variant)"]
  CM --> DEC
  NO --> DEC
  RR --> DEC
  DEC --> OUT["decision (venue vocabulary) · G1/G2 split · deliverables"]
```

`review-area-chair` never merges referee reports into one list unless
`process_model` is `panel-plus-metareviewer`. For `editor-mediated-referees` it
writes an editor summary that tags each referee point binding / advisory /
overruled, and `review-B` is the de-duplicated union of referee comments.

---

## Panel E — challenge & re-review (post-run, every stage user-triggered)

Every comment carries a typed `fix` (`kind: edit` with verbatim find/replace,
`kind: work_spec` with an `acceptance` test, `response_text`, or `question`);
`check_fixes.py` gates deliverable B. After the run the user may:

```mermaid
flowchart TB
  R["cycle-1 review (static or loop)<br/>review-B* with typed fixes"] --> C{{"user: challenge <id>: <argument>"}}
  C -->|per comment, j=1..J (2)| RS["response-researcher (challenge mode)<br/>argues the USER's point, evidence-bound"]
  RS --> RV["the one owning reviewer (rebuttal-eval)<br/>or review-area-chair if --via-chair"]
  RV --> TS{{"thread_state.py"}}
  TS -->|accepted| RF["revised typed fix written into review-B*"]
  TS -->|withdraw| RB["rebutted"]
  TS -->|upheld after J| CU["challenged-upheld → Group 2"]

  RF --> B{{"user: curation gate + apply_corrections.py"}}
  B -->|fix.kind = edit| COR["corrected/paper_v&lt;n&gt;/ + corrections.diff"]
  B -->|fix.kind = work_spec| AL["action-list.md (full spec)"]

  COR --> STOP["skill records 'text changed — re-review available' and STOPS"]
  STOP --> RR{{"user: re-review  (explicit; never automatic)"}}
  RR -->|corrections.diff non-empty| PANEL["re-run steps 5–10 on paper_v&lt;n&gt;<br/>reuse venue-profile / field-profile / review-prompt<br/>panel in re-review mode: prior review-B + diff"]
  PANEL --> REC["review-area-chair (reconciliation)<br/>cycle-&lt;n+1&gt;/ + reconciliation.md<br/>(resolved / persists / new)"]
  REC --> C
```

The user decides how many cycles to run; `re-review` re-issues the decision only
with `--rescore`.
