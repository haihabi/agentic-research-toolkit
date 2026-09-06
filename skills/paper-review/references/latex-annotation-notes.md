# LaTeX annotation notes (`todonotes` edge cases)

Guidance for `scripts/build_annotations.py` / `scripts/inject_todonotes.py` and
for the Overleaf-mode edits. Goal: add margin/inline review notes that compile on
the first try and are trivial to remove.

## The markup we insert

Preamble (once, after the last existing `\usepackage`, before `\begin{document}`):

```latex
% paper-review: begin
\usepackage[colorinlistoftodos,textsize=small,prependcaption]{todonotes}
% paper-review: end
```

Right after `\begin{document}` ... `\maketitle` (or after `\maketitle` if
present):

```latex
\listoftodos  % paper-review
```

Per item, inserted immediately after the sentence that the `quote` matches:

```latex
\todo[color=orange!80]{[B-07][missing-results/major] Claim of "consistent gains" not shown for settings C-E $\rightarrow$ add runs or scope the claim.}  % paper-review B-07
```

Items with no line anchor (PDF-only location, or `quote` not found in source) go
at the start of the matching `\section` as:

```latex
\todo[inline, color=orange!80]{[B-07] ...}  % paper-review B-07
```

Figure-related `missing-*` items use `\missingfigure{[B-07] ...}` in place of the
figure or at the section start.

Every inserted line ends with a `% paper-review <id>` trailing comment so the
notes can be stripped with one `grep -v`.

## Colour by severity

`blocking` → `red!70` · `major` → `orange!80` · `minor` → `blue!40` ·
`nit` → `gray!30`.

## Edge cases

- **Package already loaded.** If `\usepackage[...]{todonotes}` is already in the
  preamble, do not add it again; reuse it. If it is loaded with `disable`, remove
  `disable` inside the `% paper-review` markers and note it in `annotations.diff`.
- **No preamble in the anchored file (multi-file projects).** Anchors live in
  `sections/*.tex`; the preamble edit must target the root file (the one with
  `\documentclass`). `build_annotations.py` locates the root by scanning for
  `\documentclass`, matching `compile_project`'s own auto-detection.
- **`\maketitle` inside a `\twocolumn[...]` block (IEEEtran, acmart).** Put
  `\listoftodos` after the block closes, not inside it. If detecting the block is
  unreliable, fall back to placing `\listoftodos` right before the first
  `\section`.
- **`todonotes` + `\marginpar`-hostile classes (IEEEtran, llncs).** Margins are
  narrow or absent. Use `\todo[inline, ...]` for *all* notes in these classes;
  detect via `\documentclass{IEEEtran|llncs|acmart}` and set an `inline_only`
  flag.
- **`beamer`.** Refuse: `todonotes` does not behave in frames. Emit
  `review-B-point-by-point.md` only and say why in the run summary.
- **`quote` matches multiple places.** Anchor at the first match inside the
  section named in `location.section`; if the section name does not resolve, use
  the first match in the whole document and downgrade to `\todo[inline]`.
- **`quote` matches nothing** (paraphrase, PDF text differs from source, quote
  spans a macro). Fall back to section-start `\todo[inline]`; list these items in
  the run summary as "unanchored".
- **Unicode / special chars in the note text.** Escape `#`, `%`, `&`, `_`, `$`,
  `^`, `~`, `{`, `}` and `\` for LaTeX; render `->` as `$\rightarrow$`.
- **`\input` vs `\include` vs `\subfile`.** Resolve all three when building the
  section→line map. `latexpand` handles `\input`/`\include`; `\subfile` needs a
  manual join.
- **Overleaf compiler.** Read `% !TEX program` / the project's `latexmkrc` or
  Menu compiler setting; pass the matching `engine` to `compile_project`. If
  unknown, let `compile_project` auto-detect (pdflatex default).

## Reversibility

- **Local mode:** the annotated tree is a copy under `annotated/`; the original
  is untouched. Nothing to revert.
- **Overleaf mode:** every commit message is
  `paper-review: todonotes (<n> notes) [run <timestamp>]` (plus one
  `paper-review: todonotes preamble [run <timestamp>]`). `overleaf-commits.md`
  records the commit range. To revert: `git revert` the range in the Overleaf
  git mirror, or delete all lines matching `% paper-review` and the block between
  `% paper-review: begin` / `% paper-review: end`, then re-sync.
