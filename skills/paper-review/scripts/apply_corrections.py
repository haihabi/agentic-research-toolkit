#!/usr/bin/env python3
"""apply_corrections.py — apply the user-accepted Group 1 corrections.

Runs after the curation gate. Copies the .tex tree to <out-dir>/corrected/,
applies each accepted Group 1 item whose `fix.kind == "edit"` (every entry in
`fix.edits[]` as a find -> replace), removes that item's `% paper-review <id>`
todo line, writes corrections.diff, and (local mode) compiles. Accepted items
whose `fix.kind` is `work_spec` / `response_text` / `question` cannot be applied
mechanically — they are reported under "needs_manual_edit" (and `work_spec`
items are also listed under "to_action_list").

    apply_corrections.py --b1 review-B1.json --decisions curation/decisions.json \
        --source SRC --out-dir DIR [--engine pdflatex] [--no-compile]

Each `fix.edits[]` entry is {file, line?, find, replace, why?}. An entry may also
carry an explicit op for anchored inserts:
  {"op": "insert_after",  "file": "sec/x.tex", "anchor": "...", "text": "..."}
  {"op": "insert_before", "file": "sec/x.tex", "anchor": "...", "text": "..."}
The default op is "replace" (find -> replace, first occurrence).

For Overleaf mode pass --emit-plan to print the edit list as JSON instead of
touching a local tree; the skill then applies it via the overleaf MCP.
"""
from __future__ import annotations
import argparse, difflib, json, os, shutil, subprocess, sys


def read(path):
    return open(path, encoding="utf-8", errors="replace").read()


def apply_patch(text: str, patch: dict) -> tuple[str, bool]:
    op = patch.get("op")
    if op == "replace":
        find, repl = patch["find"], patch.get("replace", "")
        if find in text:
            return text.replace(find, repl, 1), True
        return text, False
    if op in ("insert_after", "insert_before"):
        anchor, ins = patch["anchor"], patch["text"]
        lines = text.splitlines(keepends=True)
        for i, ln in enumerate(lines):
            if anchor in ln:
                block = ins if ins.endswith("\n") else ins + "\n"
                at = i + 1 if op == "insert_after" else i
                lines.insert(at, block)
                return "".join(lines), True
        return text, False
    return text, False


def strip_todo(text: str, cid: str) -> str:
    keep = [ln for ln in text.splitlines(keepends=True)
            if f"% paper-review {cid}" not in ln]
    return "".join(keep)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--b1", required=True)
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--engine", default=None)
    ap.add_argument("--no-compile", action="store_true")
    ap.add_argument("--emit-plan", action="store_true")
    args = ap.parse_args()

    items = {it["id"]: it for it in json.load(open(args.b1, encoding="utf-8")).get("items", [])}
    decisions = json.load(open(args.decisions, encoding="utf-8")).get("decisions", [])
    accepted = [d["id"] for d in decisions
                if d.get("group") == 1 and d.get("user") == "accept"]

    def edit_to_patch(e: dict) -> dict:
        op = e.get("op", "replace")
        if op in ("insert_after", "insert_before"):
            return {"op": op, "file": e["file"], "anchor": e["anchor"],
                    "text": e["text"]}
        return {"op": "replace", "file": e["file"], "find": e["find"],
                "replace": e.get("replace", "")}

    plan, manual, to_action_list = [], [], []
    for cid in accepted:
        it = items.get(cid)
        if not it:
            manual.append({"id": cid, "reason": "not found in review-B1.json"})
            continue
        fix = it.get("fix") or it.get("final_fix")
        if not isinstance(fix, dict):
            manual.append({"id": cid, "reason": "no typed fix object"})
            continue
        kind = fix.get("kind")
        if kind != "edit":
            manual.append({"id": cid, "reason": f"fix.kind={kind} — not mechanically applyable"})
            if kind == "work_spec":
                to_action_list.append({"id": cid, "work": fix.get("work", {})})
            continue
        edits = fix.get("edits") or []
        if not edits:
            manual.append({"id": cid, "reason": "fix.kind=edit but edits[] empty"})
            continue
        for e in edits:
            if not e.get("file"):
                manual.append({"id": cid, "reason": "edit missing `file` (PDF-only review?)"})
                continue
            plan.append({"id": cid, "file": e["file"], "patch": edit_to_patch(e)})

    if args.emit_plan:
        json.dump({"apply": plan, "needs_manual_edit": manual,
                   "to_action_list": to_action_list,
                   "strip_todos": sorted({p["id"] for p in plan})},
                  sys.stdout, indent=2)
        print()
        return 0

    corrected = os.path.join(args.out_dir, "corrected")
    if os.path.exists(corrected):
        shutil.rmtree(corrected)
    if os.path.isdir(args.source):
        shutil.copytree(args.source, corrected)
    else:
        os.makedirs(corrected)
        shutil.copy(args.source, corrected)

    applied, failed = [], []
    touched: dict[str, str] = {}
    for p in plan:
        fp = os.path.join(corrected, p["file"])
        if not os.path.isfile(fp):
            failed.append({**p, "reason": "file missing"})
            continue
        text = touched.get(fp, read(fp))
        text, ok = apply_patch(text, p["patch"])
        if not ok:
            failed.append({**p, "reason": "anchor/find not matched"})
            continue
        text = strip_todo(text, p["id"])
        touched[fp] = text
        applied.append(p["id"])

    for fp, text in touched.items():
        open(fp, "w", encoding="utf-8").write(text)

    # diff
    diff_lines = []
    for fp, text in touched.items():
        rel = os.path.relpath(fp, corrected)
        old = read(os.path.join(args.source, rel)) if os.path.isdir(args.source) else read(args.source)
        diff_lines += list(difflib.unified_diff(
            old.splitlines(keepends=True), text.splitlines(keepends=True),
            fromfile=f"a/{rel}", tofile=f"b/{rel}"))
    open(os.path.join(args.out_dir, "corrections.diff"), "w", encoding="utf-8").write(
        "".join(diff_lines))

    result = {"applied": applied, "failed": failed, "needs_manual_edit": manual,
              "to_action_list": to_action_list, "corrected_dir": corrected}

    if not args.no_compile and touched:
        # find the root file
        root = None
        for dp, _, fs in os.walk(corrected):
            for f in fs:
                if f.endswith(".tex") and "\\documentclass" in read(os.path.join(dp, f)):
                    root = os.path.join(dp, f)
                    break
            if root:
                break
        if root:
            engine = args.engine or "pdflatex"
            r = subprocess.run(["latexmk", f"-{engine}", "-interaction=nonstopmode",
                                "-halt-on-error", os.path.basename(root)],
                               cwd=os.path.dirname(root), capture_output=True, text=True)
            log = os.path.join(args.out_dir, "corrected-compile.log")
            open(log, "w", encoding="utf-8").write(r.stdout + "\n---STDERR---\n" + r.stderr)
            result["compiled"] = r.returncode == 0
            result["compile_log"] = log

    json.dump(result, sys.stdout, indent=2)
    print()
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
