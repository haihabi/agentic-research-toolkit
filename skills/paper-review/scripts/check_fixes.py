#!/usr/bin/env python3
"""check_fixes.py — validate that every review comment carries a concrete fix.

Runs after deliverable B / B1 is written and before it is finalised (and in
evals). It enforces the `fix` object contract from
prompts/review-comment-taxonomy.md: the right `kind` for the item's
`actionability`, the required sub-fields present, and every `edit.find` string
actually occurring in the LaTeX source (when source is available).

    check_fixes.py review-B.json [review-B1.json ...] [--source SRC] [--strict]

Exit 0 = all items OK. Exit 1 = at least one offender (printed as JSON lines).
--strict also fails on soft warnings (short/again-non-unique find strings).

`fix` may also appear as `final_fix` (loop mode agreed version); both are checked.
"""
from __future__ import annotations
import argparse, json, os, re, sys

# actionability -> allowed fix.kind(s)
ALLOWED = {
    "defer-to-final-version": {"edit"},
    "needs-reframing": {"edit"},
    "resolve-in-response-text": {"response_text"},
    "needs-new-work": {"work_spec"},
    "needs-author-clarification": {"question"},
    # these commonly resolve by an edit but may legitimately need work
    "": {"edit", "work_spec", "response_text", "question"},
}
# categories that almost always take an edit regardless of actionability
EDIT_CATEGORIES = {"incorrect-statement", "unclear-statement", "presentation",
                   "missing-context"}
VAGUE = re.compile(r"\b(consider|might want|could|should probably|try to|"
                   r"strengthen|improve|clarify|revise|rework|more detail|"
                   r"as needed|etc\.)\b", re.I)


def load_source_text(src: str | None) -> str | None:
    if not src:
        return None
    if os.path.isfile(src):
        return open(src, encoding="utf-8", errors="replace").read()
    if os.path.isdir(src):
        buf = []
        for dp, _, fs in os.walk(src):
            for f in fs:
                if f.endswith((".tex", ".bib")):
                    buf.append(open(os.path.join(dp, f), encoding="utf-8",
                                   errors="replace").read())
        return "\n".join(buf)
    return None


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def check_item(it: dict, src_text: str | None, strict: bool) -> list[str]:
    errs: list[str] = []
    cid = it.get("id", "?")
    act = it.get("actionability", "")
    cat = it.get("category", "")
    for key in ("fix", "final_fix"):
        fix = it.get(key)
        if fix in (None, "none"):
            if key == "fix":
                errs.append(f"{cid}: no `fix` object")
            continue
        if not isinstance(fix, dict):
            errs.append(f"{cid}: `{key}` is not an object (got {type(fix).__name__})")
            continue
        kind = fix.get("kind")
        allowed = ALLOWED.get(act, ALLOWED[""])
        if cat in EDIT_CATEGORIES:
            allowed = allowed | {"edit"}
        if kind not in allowed:
            errs.append(f"{cid}: fix.kind={kind!r} not allowed for "
                        f"actionability={act!r} (allowed: {sorted(allowed)})")
        if kind == "edit":
            edits = fix.get("edits")
            if not isinstance(edits, list) or not edits:
                errs.append(f"{cid}: fix.edits missing or empty")
                continue
            for j, e in enumerate(edits):
                if not e.get("find") or not str(e.get("find")).strip():
                    errs.append(f"{cid}: edit[{j}] has empty `find`")
                    continue
                if "replace" not in e:
                    errs.append(f"{cid}: edit[{j}] missing `replace` "
                                f"(use \"\" for a deletion)")
                if VAGUE.search(str(e.get("replace", ""))):
                    errs.append(f"{cid}: edit[{j}] `replace` reads like advice, "
                                f"not final text: {e['replace'][:60]!r}")
                if src_text is not None:
                    f = norm(str(e["find"]))
                    if f and norm(src_text).count(f) == 0:
                        errs.append(f"{cid}: edit[{j}] `find` not found in source: "
                                    f"{e['find'][:70]!r}")
                    elif strict and f and norm(src_text).count(f) > 1:
                        errs.append(f"{cid}: edit[{j}] `find` matches "
                                    f"{norm(src_text).count(f)}x (not unique)")
                elif strict and len(norm(str(e["find"]))) < 12:
                    errs.append(f"{cid}: edit[{j}] `find` very short, may not "
                                f"anchor uniquely: {e['find']!r}")
        elif kind == "work_spec":
            w = fix.get("work") or {}
            if not w.get("kind"):
                errs.append(f"{cid}: work_spec missing work.kind")
            if not norm(w.get("goal", "")):
                errs.append(f"{cid}: work_spec missing `goal`")
            if not norm(w.get("acceptance", "")):
                errs.append(f"{cid}: work_spec missing `acceptance` "
                            f"(the result that resolves the comment)")
            if not norm(w.get("design", "")):
                errs.append(f"{cid}: work_spec missing `design`")
            if w.get("kind") in ("proof", "derivation") and not norm(
                    w.get("proof_obligation", "")):
                errs.append(f"{cid}: work_spec kind={w.get('kind')} needs "
                            f"`proof_obligation`")
        elif kind == "response_text":
            if not norm(fix.get("text", "")):
                errs.append(f"{cid}: response_text has empty `text`")
            elif len(norm(fix["text"])) < 40:
                errs.append(f"{cid}: response_text `text` too short to be the "
                            f"actual paragraph: {fix['text']!r}")
        elif kind == "question":
            if not norm(fix.get("question", "")):
                errs.append(f"{cid}: question has empty `question`")
            ans = fix.get("answers")
            if not isinstance(ans, list) or not ans:
                errs.append(f"{cid}: question missing `answers` branches")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--source")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    src_text = load_source_text(args.source)
    all_errs: list[str] = []
    total = 0
    for path in args.files:
        data = json.load(open(path, encoding="utf-8"))
        items = data.get("items", [])
        total += len(items)
        for it in items:
            all_errs += [f"{os.path.basename(path)}: {e}"
                         for e in check_item(it, src_text, args.strict)]

    for e in all_errs:
        print(json.dumps({"offender": e}))
    print(json.dumps({"checked_items": total, "offenders": len(all_errs),
                      "source_checked": src_text is not None}), file=sys.stderr)
    return 1 if all_errs else 0


if __name__ == "__main__":
    raise SystemExit(main())
