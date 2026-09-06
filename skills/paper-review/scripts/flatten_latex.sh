#!/usr/bin/env bash
# flatten_latex.sh <root.tex> [out-dir]
#
# Flattens a multi-file LaTeX project into a single file with `latexpand` and
# writes a section -> line map. Outputs, in <out-dir> (default: alongside root):
#   flat.tex        the flattened source
#   section-map.tsv  TAB-separated: <flat-line>\t<level>\t<section title>\t<orig-file>:<orig-line>
#
# Degrades gracefully: if `latexpand` is missing, copies the root file to
# flat.tex, still builds a best-effort map from that one file, and warns.

set -euo pipefail

root="${1:?usage: flatten_latex.sh <root.tex> [out-dir]}"
[ -f "$root" ] || { echo "flatten_latex.sh: no such file: $root" >&2; exit 1; }
root_dir="$(cd "$(dirname "$root")" && pwd)"
root_base="$(basename "$root")"
out_dir="${2:-$root_dir}"
mkdir -p "$out_dir"
flat="$out_dir/flat.tex"
map="$out_dir/section-map.tsv"

if command -v latexpand >/dev/null 2>&1; then
  ( cd "$root_dir" && latexpand --keep-comments "$root_base" ) > "$flat"
else
  echo "flatten_latex.sh: latexpand not found; using root file only" >&2
  cp "$root" "$flat"
fi

# Build the section map from the flattened file. latexpand --keep-comments emits
# `%%% <file>` provenance markers we use to recover original file:line.
python3 - "$flat" "$map" <<'PY'
import re, sys
flat, mapfile = sys.argv[1], sys.argv[2]
sec = re.compile(r'\\(part|chapter|section|subsection|subsubsection)\*?\s*\{')
prov = re.compile(r'^%+\s*(?:latexpand:\s*)?(?:from\s+)?(.+\.tex)\b', re.I)
cur_file, cur_off = "flat.tex", 0
rows = []
with open(flat, encoding="utf-8", errors="replace") as fh:
    for i, line in enumerate(fh, 1):
        m = prov.match(line.strip())
        if m:
            cur_file, cur_off = m.group(1).strip(), i
            continue
        m = sec.search(line)
        if m:
            # crude brace-balanced title extraction
            rest = line[m.end():]
            depth, title = 1, []
            for ch in rest:
                if ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0: break
                title.append(ch)
            orig_line = i - cur_off if cur_file != "flat.tex" else i
            rows.append((i, m.group(1), ''.join(title).strip(), f"{cur_file}:{orig_line}"))
with open(mapfile, "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write("\t".join(str(x) for x in r) + "\n")
print(f"flatten_latex.sh: {len(rows)} sections -> {mapfile}", file=sys.stderr)
PY

echo "$flat"
