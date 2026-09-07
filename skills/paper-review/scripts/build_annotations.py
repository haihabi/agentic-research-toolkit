#!/usr/bin/env python3
"""build_annotations.py — turn review-B.json into a concrete LaTeX edit plan.

Shared by both LaTeX annotation modes (local copy + latexmk, and Overleaf via
the overleaf MCP). It does no writing of its own: it emits an edit plan and a
unified diff for review.

    build_annotations.py review-B.json --source SRC [--out-dir DIR]

SRC is either:
  * a directory containing the .tex project (local mode), or
  * a flattened flat.tex file produced by flatten_latex.sh (either mode).

Outputs in --out-dir (default: cwd):
  annotations.json   ordered list of edits: {file, line, insert, id, unanchored}
                     plus one {preamble: true, ...} entry and one {listoftodos}
  annotations.diff   unified diff of the planned inserts (context only, for humans)

Anchoring: for each item with location.file+line, insert after that line. Else
try to match location.quote in the section named by location.section, then
anywhere. Unmatched -> section-start inline note, flagged unanchored.

See references/latex-annotation-notes.md for the markup and edge cases.
"""
from __future__ import annotations
import argparse, difflib, json, os, re, sys

SEV_COLOR = {"blocking": "red!70", "major": "orange!80",
             "minor": "blue!40", "nit": "gray!30"}
INLINE_ONLY_CLASSES = ("IEEEtran", "llncs", "acmart")
TEX_SPECIAL = {'#': r'\#', '%': r'\%', '&': r'\&', '_': r'\_',
               '$': r'\$', '^': r'\^{}', '~': r'\~{}'}


def tex_escape(s: str) -> str:
    out = []
    for ch in s:
        if ch == '\\':
            out.append(r'\textbackslash{}')
        elif ch in TEX_SPECIAL:
            out.append(TEX_SPECIAL[ch])
        else:
            out.append(ch)
    return ''.join(out).replace('->', r'$\rightarrow$')


def fix_summary(item: dict) -> str:
    """One-line, human summary of the typed `fix` object for a \\todo note."""
    fix = item.get("fix") or item.get("final_fix")
    if not isinstance(fix, dict):
        # legacy / free-text fallback
        return str(item.get("suggested_fix", "")).strip().replace("\n", " ")
    kind = fix.get("kind")
    if kind == "edit":
        parts = []
        for e in fix.get("edits", []):
            f = (e.get("find") or "").strip().replace("\n", " ")
            r = (e.get("replace") or "").strip().replace("\n", " ")
            f = (f[:60] + "…") if len(f) > 60 else f
            r = (r[:60] + "…") if len(r) > 60 else r
            parts.append(f'replace "{f}" -> "{r}"' if r else f'delete "{f}"')
        return "; ".join(parts)
    if kind == "work_spec":
        w = fix.get("work", {})
        return (f"{w.get('kind', 'new work')}: {w.get('design', '')} "
                f"[done when: {w.get('acceptance', '')}]").strip().replace("\n", " ")
    if kind == "response_text":
        t = (fix.get("text") or "").strip().replace("\n", " ")
        return "respond: " + ((t[:120] + "…") if len(t) > 120 else t)
    if kind == "question":
        return "ask authors: " + (fix.get("question") or "").strip().replace("\n", " ")
    return ""


def note_text(item: dict) -> str:
    i = item["id"]
    cat = item["category"]
    sev = item["severity"]
    problem = item.get("problem", "").strip().replace("\n", " ")
    fix = fix_summary(item)
    body = f"[{i}][{cat}/{sev}] {problem}"
    if fix:
        body += f" -> {fix}"
    return tex_escape(body)


def find_root_and_class(source: str):
    """Return (root_path, documentclass or None)."""
    if os.path.isfile(source):
        text = open(source, encoding="utf-8", errors="replace").read()
        m = re.search(r'\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}', text)
        return source, (m.group(1) if m else None)
    for dirpath, _, files in os.walk(source):
        for f in files:
            if not f.endswith(".tex"):
                continue
            p = os.path.join(dirpath, f)
            text = open(p, encoding="utf-8", errors="replace").read()
            m = re.search(r'\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}', text)
            if m:
                return p, m.group(1)
    return None, None


def load_lines(source: str, rel: str | None):
    if os.path.isfile(source):
        path = source
    elif rel:
        path = os.path.join(source, rel)
    else:
        return None, None
    if not os.path.isfile(path):
        return None, None
    return path, open(path, encoding="utf-8", errors="replace").read().splitlines()


def section_line(lines, section):
    """1-based line of the \\section whose title contains the section words."""
    if not section:
        return None
    words = [w.lower() for w in re.findall(r'[A-Za-z]+', section)]
    for idx, ln in enumerate(lines):
        low = ln.lower()
        if '\\section' in low and any(w in low for w in words):
            return idx + 1
    return None


def quote_line(lines, quote, section=None):
    if not quote:
        return None
    q = re.sub(r'\s+', ' ', quote.strip().lower())[:60]
    sect_start = (section_line(lines, section) or 1) - 1
    for idx in range(sect_start, len(lines)):
        if q and q[:30] in re.sub(r'\s+', ' ', lines[idx].lower()):
            return idx + 1
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("review_b", help="review-B.json (static) or review-B1.json (loop)")
    ap.add_argument("--source", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--unresolved", help="review-B2.json — also emit greyed "
                    "[UNRESOLVED] inline notes")
    args = ap.parse_args()

    data = json.load(open(args.review_b, encoding="utf-8"))
    items = [dict(it, _unresolved=False) for it in data.get("items", [])]
    if args.unresolved and os.path.isfile(args.unresolved):
        u = json.load(open(args.unresolved, encoding="utf-8")).get("items", [])
        items += [dict(it, _unresolved=True) for it in u]
    root, klass = find_root_and_class(args.source)
    inline_only = bool(klass and klass.split(',')[0].strip() in INLINE_ONLY_CLASSES)
    if klass and klass.split(',')[0].strip() == "beamer":
        print("build_annotations.py: beamer detected — annotation skipped, "
              "deliverable B only.", file=sys.stderr)
        json.dump({"skipped": "beamer", "edits": []},
                  open(os.path.join(args.out_dir, "annotations.json"), "w"), indent=2)
        return 0

    edits = []
    if root:
        edits.append({"preamble": True, "file": os.path.relpath(root, args.source)
                      if os.path.isdir(args.source) else root})
        edits.append({"listoftodos": True, "file": os.path.relpath(root, args.source)
                      if os.path.isdir(args.source) else root})

    root_rel = (os.path.relpath(root, args.source)
                if root and os.path.isdir(args.source) else
                (os.path.basename(root) if root else "flat.tex"))
    _, root_lines = load_lines(args.source, root_rel if os.path.isdir(args.source) else None)
    if root_lines is None and root and os.path.isfile(root):
        root_lines = open(root, encoding="utf-8", errors="replace").read().splitlines()

    diff_blocks = []
    for it in items:
        loc = it.get("location", {})
        rel = loc.get("file")
        line = loc.get("line")
        path, lines = load_lines(args.source, rel)
        anchored = False
        target_file = rel
        if lines and isinstance(line, int) and 1 <= line <= len(lines):
            at = line
            anchored = True
        elif lines and quote_line(lines, loc.get("quote"), loc.get("section")):
            at = quote_line(lines, loc.get("quote"), loc.get("section"))
            anchored = True
        else:
            # unanchored: place inline at the section start in the root file,
            # or just after \begin{document} as a last resort.
            at = 0
            if root_lines is not None:
                target_file = root_rel
                sl = section_line(root_lines, loc.get("section"))
                if sl is None:
                    for idx, ln in enumerate(root_lines):
                        if '\\begin{document}' in ln:
                            sl = idx + 1
                            break
                at = sl or 1

        if it.get("_unresolved"):
            color = "black!12"
            body = tex_escape(f"[UNRESOLVED {it['id']}] "
                              f"{it.get('thread_summary', it.get('problem', ''))}")
            insert = (f"\\todo[inline, color={color}]{{{body}}}"
                      f"  % paper-review {it['id']}")
            anchored_for_diff = False
        else:
            color = SEV_COLOR.get(it["severity"], "gray!30")
            if anchored and not inline_only:
                insert = f"\\todo[color={color}]{{{note_text(it)}}}  % paper-review {it['id']}"
            else:
                insert = (f"\\todo[inline, color={color}]{{{note_text(it)}}}"
                          f"  % paper-review {it['id']}")
            anchored_for_diff = anchored
        edits.append({"file": target_file or root_rel,
                      "line": at, "insert": insert, "id": it["id"],
                      "unanchored": not anchored, "unresolved": it.get("_unresolved", False)})
        anchored = anchored_for_diff
        if lines and anchored:
            ctx_lo = max(0, at - 2)
            before = lines[ctx_lo:at]
            after = before + [insert] + lines[at:at + 1]
            diff_blocks.append("\n".join(difflib.unified_diff(
                before + lines[at:at + 1], after,
                fromfile=f"{rel}:{at}", tofile=f"{rel}:{at} (annotated)", lineterm="")))

    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "annotations.json"), "w", encoding="utf-8") as fh:
        json.dump({"root": root, "documentclass": klass, "inline_only": inline_only,
                   "edits": edits}, fh, indent=2)
    with open(os.path.join(args.out_dir, "annotations.diff"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(diff_blocks) + "\n")

    n_un = sum(1 for e in edits if e.get("unanchored"))
    print(f"build_annotations.py: {len(items)} items, {n_un} unanchored, "
          f"class={klass}, inline_only={inline_only}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
