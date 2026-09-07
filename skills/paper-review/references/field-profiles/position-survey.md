# Field profile — Position papers, surveys, and meta-science (`position-survey`)

`last_reviewed: 2026-09-06`

## 1. What this profile covers

Papers whose contribution is synthesis or argument rather than a new empirical or
formal result: position / opinion papers, systematisation-of-knowledge (SoK),
literature surveys and taxonomies, reproducibility and meta-science reports,
methodology critiques, and roadmap papers. **Do not** use for: an empirical
replication study with new runs (`empirical-ml` or the matching field), a paper
whose real contribution is a method with a survey section attached.

## 2. What "validity" means here

- **For surveys / SoK** — is the scope defined and defended? Is the selection of
  works systematic and reasonably complete (search method stated for a
  systematic review; no glaring omissions for a narrative one)? Is the
  organising taxonomy coherent, mutually exclusive where it claims to be, and an
  advance on how the field already organises itself? Are individual works
  represented accurately?
- **For position papers** — is the thesis clearly stated and falsifiable-ish? Is
  each step of the argument supported by evidence or citation rather than
  assertion? Are the strongest counterarguments engaged, not strawmanned? Are
  the paper's own assumptions and the author's stake acknowledged?
- **For meta-science / reproducibility reports** — is the methodology for the
  meta-analysis or reproduction sound and pre-specified? Are claims about "the
  literature" backed by a defined sample?

## 3. Evidence standard

The evidence is **the quality and completeness of the scholarship and the
argument** — citations, accurate representation of prior work, logical structure,
and engagement with opposing views. No new experiments or proofs are expected; a
survey that runs no experiments is not deficient for that. A position paper is
not refuted by "you did not build it". Where the paper does make empirical
meta-claims, those are held to ordinary standards.

**`work_spec` for `needs-new-work` here** is rare: `kind` is usually `analysis`
(e.g. "make the selection systematic: state the search, screen, and inclusion
criteria") with `goal`, `design`, `acceptance`. Most fixes are `kind: edit`
(add the omitted works and position them; correct a misdescription; tighten the
scope statement) or `kind: response_text`.

## 4. What "novelty" and "significance" look like here

A synthesis that lets people see the field more clearly; a taxonomy people will
adopt; a well-argued reframing or warning that changes the research agenda; a
rigorous account of what does and does not replicate. Significance is argued by
usefulness to the community and by the importance of the question.

## 5. Taxonomy categories: load-bearing vs. rarely applicable

Load-bearing: `missing-related-work` (omitted key works; misrepresenting cited
ones), `unsupported-claim` (argumentative leaps; "everyone does X" without
evidence), `scope-framing` (undefined or self-serving scope; title promises more
than delivered), `methodological-concern` (non-systematic selection presented as
systematic; cherry-picked evidence), `novelty-significance` (taxonomy or thesis
not an advance on existing framings), `missing-context`. Usually **not
applicable**: `missing-results`, `reproducibility` as artifact release.

## 6. Persona emphasis

- **P1 (validity)** — argument structure, selection method, accuracy of how
  prior work is described, engagement with counterarguments.
- **P2 (novelty/positioning)** — is the synthesis / thesis genuinely new, or a
  restatement of an existing framing / a known debate.
- **P3 (clarity)** — is the taxonomy usable; is the through-line followable; are
  claims and citations tightly coupled.

## 7. Common failure modes

Scope gerrymandered to claim completeness; key works or a whole subfield missing;
cited works misdescribed; taxonomy categories that overlap or do not cover the
space; thesis asserted, not argued; counterarguments strawmanned or ignored;
"position" that is really an un-evaluated method proposal; survey with no
synthetic contribution beyond a list.

## 8. Do-not-import

- `missing-results` / "run an experiment" from `empirical-ml` — the contribution
  is synthesis or argument.
- Proof demands from `theory-proofs`.
- Artifact-release reproducibility, except for the defined corpus of a systematic
  review or meta-analysis.
