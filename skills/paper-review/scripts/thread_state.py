#!/usr/bin/env python3
"""thread_state.py — apply the rebuttal state machine for one round.

Keeps the loop bookkeeping out of the model. Reads the current
comment-threads.json (or initialises it from a comment list), applies one
round's researcher stances + reviewer replies, handles oscillation and the
forced resolution at k == K, writes the file back, and prints a JSON status the
skill uses to decide whether to continue.

    thread_state.py --threads comment-threads.json --round K --K 2 \
        --stances stances.json --replies replies.json [--init comments.json]

stances.json : [{"id","stance","researcher_note","evidence":[...],"final_fix"}]
replies.json : [{"id","reviewer","reply","why","severity"}]
comments.json (only with --init): [{"id","reviewer","category","severity"}]

Vocabulary and the transition table are defined in
prompts/rebuttal-protocol.md and prompts/comment-resolution-states.md.
"""
from __future__ import annotations
import argparse, json, sys

TERMINAL = {"accepted", "rebutted", "unresolved_disagreement",
            "unresolved_insufficient_info"}
NONTERMINAL = {"open", "in_debate"}

# (stance, reply) -> new state.  reply None == no reply this round.
TABLE = {
    ("concede-and-fix", "resolved"): "accepted",
    ("concede-and-fix", "partially-resolved"): "in_debate",
    ("concede-and-fix", "unconvinced"): "in_debate",
    ("concede-and-fix", "need-more"): "in_debate",
    ("concede-cannot-fix", "resolved"): "rebutted",
    ("concede-cannot-fix", "withdraw"): "rebutted",
    ("concede-cannot-fix", "partially-resolved"): "unresolved_insufficient_info",
    ("concede-cannot-fix", "unconvinced"): "unresolved_insufficient_info",
    ("concede-cannot-fix", "need-more"): "unresolved_insufficient_info",
    ("concede-cannot-fix", None): "unresolved_insufficient_info",
    ("dispute", "withdraw"): "rebutted",
    ("dispute", "resolved"): "rebutted",
    ("dispute", "unconvinced"): "in_debate",
    ("dispute", "partially-resolved"): "in_debate",
    ("dispute", "need-more"): "in_debate",
    ("partially-accept", "resolved"): "accepted",
    ("partially-accept", "partially-resolved"): "in_debate",
    ("partially-accept", "unconvinced"): "in_debate",
    ("partially-accept", "need-more"): "in_debate",
    ("need-clarification", "resolved"): "open",
    ("need-clarification", "withdraw"): "rebutted",
}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", required=True)
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--K", type=int, default=2)
    ap.add_argument("--stances", required=True)
    ap.add_argument("--replies", required=True)
    ap.add_argument("--init")
    args = ap.parse_args()

    if args.init:
        comments = load(args.init)
        doc = {"K": args.K, "rounds_run": 0, "stopped_because": None,
               "threads": [{
                   "id": c["id"], "reviewer": c.get("reviewer", c["id"].split("-")[0]),
                   "category": c.get("category"), "severity_initial": c.get("severity"),
                   "severity_final": c.get("severity"), "state": "open",
                   "state_history": ["open"], "oscillated": False,
                   "group": None, "group_reason": None, "final_fix": None, "rounds": [],
               } for c in comments]}
    else:
        doc = load(args.threads)

    stances = {s["id"]: s for s in load(args.stances)}
    replies_by_id: dict[str, list] = {}
    for r in load(args.replies):
        replies_by_id.setdefault(r["id"], []).append(r)

    by_id = {t["id"]: t for t in doc["threads"]}
    changed = 0

    for tid, t in by_id.items():
        if t["state"] in TERMINAL:
            continue
        st = stances.get(tid)
        reps = replies_by_id.get(tid, [])
        # the raising reviewer's reply is the one that moves state
        own = next((r for r in reps if r.get("reviewer") == t["reviewer"]), None)
        reply = own["reply"] if own else (reps[0]["reply"] if reps else None)
        if own and own.get("severity"):
            t["severity_final"] = own["severity"]

        prev = t["state"]
        if st is None:
            new = prev                      # comment not addressed this round
        else:
            new = TABLE.get((st["stance"], reply), "in_debate")
            if st.get("final_fix") and st["final_fix"] != "none":
                t["final_fix"] = st["final_fix"]

        t["rounds"].append({
            "k": args.round,
            "stance": st["stance"] if st else None,
            "researcher_note": (st or {}).get("researcher_note"),
            "evidence": (st or {}).get("evidence", []),
            "replies": {r.get("reviewer", "?"): {k: r[k] for k in ("reply", "why")
                                                 if k in r} for r in reps},
        })

        if new != prev:
            t["state_history"].append(new)
            changed += 1

        # oscillation: 3+ toggles among {open, in_debate}
        toggles = sum(1 for a, b in zip(t["state_history"], t["state_history"][1:])
                      if a in NONTERMINAL and b in NONTERMINAL and a != b)
        if toggles >= 3 and new not in TERMINAL:
            new = "unresolved_disagreement"
            t["oscillated"] = True
            t["state_history"].append(new)

        t["state"] = new

    # forced resolution at the last round
    if args.round >= args.K:
        for t in by_id.values():
            if t["state"] in NONTERMINAL:
                last = t["rounds"][-1]["stance"] if t["rounds"] else None
                t["state"] = ("unresolved_insufficient_info"
                              if last in ("concede-cannot-fix", "need-clarification")
                              else "unresolved_disagreement")
                t["state_history"].append(t["state"])
                changed += 1

    doc["rounds_run"] = args.round
    remaining = sum(1 for t in by_id.values() if t["state"] in NONTERMINAL)
    terminal = sum(1 for t in by_id.values() if t["state"] in TERMINAL)

    if remaining == 0:
        doc["stopped_because"] = "converged"
    elif changed == 0:
        doc["stopped_because"] = "no-change"
    elif args.round >= args.K:
        doc["stopped_because"] = "K-reached"
    else:
        doc["stopped_because"] = None

    with open(args.threads, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)

    status = {"round": args.round, "changed": changed, "terminal": terminal,
              "remaining": remaining, "stopped": doc["stopped_because"] is not None,
              "stopped_because": doc["stopped_because"]}
    print(json.dumps(status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
