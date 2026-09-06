#!/usr/bin/env python3
"""inject_todonotes.py — local-mode LaTeX annotation.

Copies a .tex project to <out-dir>/annotated/, applies the edit plan from
build_annotations.py, adds the todonotes preamble + \\listoftodos, and compiles
with latexmk.

    inject_todonotes.py --source SRC --plan annotations.json --out-dir DIR
                        [--engine pdflatex] [--no-compile]

Original tree is never modified. Prints the annotated PDF path on success.
"""
from __future__ import annotations
import argparse, json, os, re, shutil, subprocess, sys

PREAMBLE = (
    "% paper-review: begin\n"
    "\\usepackage[colorinlistoftodos,textsize=small,prependcaption]{todonotes}\n"
    "% paper-review: end\n"
)


def apply_inserts(path: str, inserts: list[dict]):
    """inserts: [{line, insert}] — insert AFTER the given 1-based line.

    A line of 0 (or one that would land in the preamble) is moved to just after
    \\begin{document} so a \\todo never precedes it.
    """
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines(keepends=True)
    begin = next((i for i, l in enumerate(lines) if "\\begin{document}" in l), None)
    for ins in sorted(inserts, key=lambda x: x["line"], reverse=True):
        at = ins["line"]
        if begin is not None and at <= begin + 1:
            at = begin + 1
        text = ins["insert"]
        if not text.endswith("\n"):
            text += "\n"
        lines.insert(min(at, len(lines)), text)
    open(path, "w", encoding="utf-8").write("".join(lines))


def add_preamble(root: str):
    text = open(root, encoding="utf-8", errors="replace").read()
    if re.search(r'\\usepackage(\[[^\]]*\])?\{todonotes\}', text):
        # already loaded — strip a `disable` option if present
        text = re.sub(r'(\\usepackage\[[^\]]*?)\bdisable\b,?\s*(\][^\n]*\{todonotes\})',
                      r'\1\2', text)
    else:
        text = text.replace("\\begin{document}", PREAMBLE + "\\begin{document}", 1)
    open(root, "w", encoding="utf-8").write(text)


def add_listoftodos(root: str):
    text = open(root, encoding="utf-8", errors="replace").read()
    if "\\listoftodos" in text:
        return
    if "\\maketitle" in text:
        text = text.replace("\\maketitle", "\\maketitle\n\\listoftodos  % paper-review", 1)
    else:
        text = re.sub(r'(\\begin\{document\})', r'\1\n\\listoftodos  % paper-review',
                      text, count=1)
    open(root, "w", encoding="utf-8").write(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="source .tex dir (or single file)")
    ap.add_argument("--plan", required=True, help="annotations.json from build_annotations.py")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--engine", default=None)
    ap.add_argument("--no-compile", action="store_true")
    args = ap.parse_args()

    plan = json.load(open(args.plan, encoding="utf-8"))
    if plan.get("skipped"):
        print(f"inject_todonotes.py: skipped ({plan['skipped']})", file=sys.stderr)
        return 0

    ann = os.path.join(args.out_dir, "annotated")
    if os.path.exists(ann):
        shutil.rmtree(ann)
    if os.path.isdir(args.source):
        shutil.copytree(args.source, ann)
    else:
        os.makedirs(ann)
        shutil.copy(args.source, ann)

    root_rel = os.path.relpath(plan["root"], args.source) if os.path.isdir(args.source) \
        else os.path.basename(plan["root"])
    root_path = os.path.join(ann, root_rel)

    # group text inserts by file
    by_file: dict[str, list[dict]] = {}
    for e in plan["edits"]:
        if e.get("preamble") or e.get("listoftodos"):
            continue
        by_file.setdefault(e["file"], []).append(e)
    for rel, inserts in by_file.items():
        fp = os.path.join(ann, rel)
        if os.path.isfile(fp):
            apply_inserts(fp, inserts)
        else:
            print(f"inject_todonotes.py: WARN missing {rel}, {len(inserts)} notes dropped",
                  file=sys.stderr)

    add_preamble(root_path)
    add_listoftodos(root_path)

    if args.no_compile:
        print(root_path)
        return 0

    engine = args.engine or plan.get("engine") or "pdflatex"
    cmd = ["latexmk", f"-{engine}", "-interaction=nonstopmode", "-halt-on-error",
           os.path.basename(root_path)]
    r = subprocess.run(cmd, cwd=os.path.dirname(root_path),
                       capture_output=True, text=True)
    log = os.path.join(args.out_dir, "annotated-compile.log")
    open(log, "w", encoding="utf-8").write(r.stdout + "\n---STDERR---\n" + r.stderr)
    pdf = os.path.splitext(root_path)[0] + ".pdf"
    if r.returncode == 0 and os.path.isfile(pdf):
        print(pdf)
        return 0
    print(f"inject_todonotes.py: compile FAILED (rc={r.returncode}), see {log}",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
