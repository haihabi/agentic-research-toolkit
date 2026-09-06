# Prior art — the material `paper-review-base.md` is distilled from

Read **only in Phase 0** (authoring / refresh). A per-run review never opens this
file. When refreshing the base prompt, re-fetch these URLs, update the "as of"
notes, and bump `last_reviewed` in `prompts/paper-review-base.md`.

`last_reviewed: 2026-09-06`

---

## A. Human reviewer / editor guidance

### NeurIPS — Reviewer Guidelines
`https://neurips.cc/Conferences/2025/ReviewerGuidelines`

- Form fields: Summary; Strengths And Weaknesses; Quality; Clarity; Significance;
  Originality; Questions; Limitations; Overall; Confidence; Ethical concerns;
  plus code-of-conduct / responsible-reviewing acknowledgements.
- Quality / Clarity / Significance / Originality scale: `4 excellent · 3 good ·
  2 fair · 1 poor`.
- Overall: `6 Strong Accept · 5 Accept · 4 Borderline accept · 3 Borderline
  reject · 2 Reject · 1 Strong Reject`.
- Confidence: `5 absolutely certain · 4 confident · 3 fairly confident ·
  2 willing to defend · 1 educated guess`.
- Criterion definitions worth quoting: Quality = technical soundness + claims
  supported + methods appropriate + completeness + authors honest about
  limitations. Originality "does not necessarily require introducing an entirely
  new method". Significance = impact, adoption, advance over prior work.
- Norms: be specific not vague; be constructive; stay flexible in discussion;
  report ethics concerns immediately.

### ICLR — Reviewer Guide + Area Chair Guide
`https://iclr.cc/Conferences/2025/ReviewerGuide` · `https://iclr.cc/Conferences/2025/ACGuide`

- Review skeleton: summary of claimed contributions → strengths & weaknesses
  (comprehensive) → initial recommendation (accept/reject) + one or two key
  reasons → supporting arguments → clarifying questions → improvement feedback
  (explicitly not part of the decision) → Code of Ethics report.
- Four assessment questions: (1) specific problem addressed? (2) approach well
  motivated and well placed in the literature? (3) do the claims / results hold
  up to scientific scrutiny? (4) does it contribute new, relevant knowledge?
- Norm, quoted: "a lack of state-of-the-art results does not by itself
  constitute grounds for rejection." Reviews should be "timely and substantive".
  Points reviewers to Dennett's "Criticising with Kindness".

### ICML — Reviewer Instructions
`https://icml.cc/Conferences/2025/ReviewerInstructions`

- Similar field set to NeurIPS with different wording; confirms that field names
  and scales vary conference-to-conference and year-to-year, which is why the
  per-run venue profile exists.

### CVF (CVPR / ICCV) — Reviewer Guidelines
`https://cvpr.thecvf.com/Conferences/2025/ReviewerGuidelines` ·
`https://iccv.thecvf.com/Conferences/2025/ReviewerGuidelines`

- Rating typically `1..10` (strong reject … strong accept) plus a separate
  confidence rating; heavy emphasis on not rejecting for missing experiments the
  paper did not promise, and on justifying the rating in the text.

### IEEE — reviewer guidance and society editorial procedures
IEEE Author/Reviewer resources (`https://www.ieee.org/`), plus a society example:
SPS Conference Editorial Procedures for ICASSP
`https://2025.ieeeicassp.org/editorial-procedures/`

- Goal, quoted in substance: accept papers that are "technically sound and make
  an original and substantial contribution"; rate on **quality, relevance, and
  correctness**.
- Scoring norm: use the whole range; give the top/bottom score when deserved and
  defensible; reserve mid scores for genuinely middling papers, not for
  low-confidence or low-effort reviews.
- Review-quality norm: sketchy / short / superficial reviews are not acceptable;
  be specific and detailed; be fair.
- Conferences vs. Transactions: IEEE Transactions ("Information for Reviewers"
  pages, per journal) use longer referee reports and a recommendation set that
  includes **revise & resubmit** (author revision rounds), unlike the
  single-shot accept/reject of most conferences.
- IEEE publication ethics / plagiarism policy applies
  (`https://www.ieee.org/publications/rights/plagiarism/plagiarism.html`).

### Nature / Springer Nature — peer-review policy and guide to referees
`https://www.nature.com/nature/for-referees` (guide to referees; login-gated,
canonical content well established) ·
`https://www.nature.com/nature-portfolio/editorial-policies`

- Referee report is essentially free-form prose, but referees are asked to
  address: is the claim novel and (for the top journals) of broad significance;
  are the conclusions fully supported by the data; are statistics and methodology
  sound and reported to the journal's standards; specific numbered major points;
  minor points.
- Split: comments to the authors vs. **confidential comments to the editor**
  (including the recommendation and any concerns not to be shared verbatim).
- Recommendation options at editor level: publish as is / accept after minor
  revision / major revision (further review) / reject. Reject-and-resubmit
  ("editorially rejected but a new submission would be considered") is common.
- Required around a submission: reporting summary / reporting standards
  checklists (life sciences), data availability statement, code availability
  statement, competing-interests declaration.

### OpenReview / manuscript-system live forms
Fetched per run for the exact venue+year. OpenReview venue pages expose the
current review form JSON (field names, enum labels, rating ranges). Journal
manuscript systems (ScholarOne, Editorial Manager) rarely expose the form
publicly — fall back to the journal's "guide for referees" page and, failing
that, `assets/fallback-forms/journal-referee-report.md`.

---

## B. LLM / agent paper-review systems

### The AI Scientist (Sakana)
Paper `https://arxiv.org/abs/2408.06292` · code
`https://github.com/SakanaAI/AI-Scientist` (`ai_scientist/perform_review.py`)

- Reviewer system prompt: "You are an AI researcher who is reviewing a paper that
  was submitted to a prestigious ML venue. Be critical and cautious in your
  decision." (Two documented bias variants — "if unsure, reject" and "if unsure,
  accept" — **we deliberately do not adopt**; the base prompt forbids bias
  instructions.)
- The NeurIPS reviewer guidelines and the review form are pasted **into** the
  prompt.
- Output format: `THOUGHT` (free reasoning) then `REVIEW JSON` with fields
  Summary, Strengths, Weaknesses, Originality (1-4), Quality (1-4), Clarity
  (1-4), Significance (1-4), Soundness (1-4), Presentation (1-4), Contribution
  (1-4), Overall (1-10), Confidence (1-5), Questions, Limitations, Ethical
  Concerns (bool), Decision (accept/reject).
- Pipeline: `num_reviews_ensemble` independent reviews → numeric scores averaged
  → a meta-reviewer prompted to "act as an Area Chair" produces the final review
  and decision. Optional self-reflection rounds per reviewer. Few-shot example
  reviews can be supplied.
- Reported: ~65-70% balanced accuracy vs. human accept/reject; roughly
  inter-human agreement.
  → We adopt: guidelines-in-prompt, THOUGHT + structured form, reflection pass,
  ensemble + area-chair merge. We drop: the bias knob.

### Reviewer2
`https://arxiv.org/abs/2402.10886`

- Two-stage: a "prompt generator" first produces the set of aspects / questions
  the specific paper should be evaluated on, then a second stage writes the
  review conditioned on that. Improves coverage and specificity vs. a fixed
  prompt.
  → We adopt: the per-run tailored prompt (base + venue profile) is our version
  of stage one.

### AgentReview
EMNLP 2024 · `https://github.com/Ahren09/AgentReview`

- Five-phase review-process simulation with reviewer, author, and area-chair
  agents, each with configurable latent traits (commitment, knowledgeability, AC
  style).
  → We adopt: separate reviewer and area-chair agents; distinct reviewer
  emphases (our personas) rather than random traits.

### MARG (Multi-Agent Review Generation)
`https://arxiv.org/abs/2401.04259`

- Leader / worker / expert agents; paper text distributed across workers to
  exceed the base model's context; sub-tasks specialised by comment type
  (experiments, clarity, impact).
  → We adopt: per-emphasis personas; chunked reading for long papers.

### DeepReviewer / DeepReviewer 2.0
`https://arxiv.org/abs/2503.08569` · `https://arxiv.org/abs/2604.09590`

- Traceability made a first-class requirement: each review claim tied to a
  locatable evidence span.
  → We adopt: every comment carries a `quote` anchor + `evidence` field; this is
  also what the LaTeX annotation pass keys on.

### TreeReview
`https://arxiv.org/abs/2506.07642`

- Review as a dynamically expanded tree of questions — go deep only where the
  answers warrant it.
  → Optional structuring idea for the questioning section of the base prompt;
  not currently a hard requirement.

### SEA (Standardize–Evaluate–Analyze) and other self-correction reviewers
- Standardise the output shape, then a self-correction pass over the draft.
  → We adopt: the mandatory reflection pass.

### Survey — LLMs for automated scholarly paper review
`https://arxiv.org/abs/2501.10326`

- Landscape and, more usefully here, the evaluation pitfalls (position bias,
  verbosity bias, prompt-injection from the PDF, leakage of the decision).
  → Feeds `support/evals/skills/paper-review/README.md`.

---

## C. Peer-review comment / aspect taxonomies

### PeerRead
Kang et al., NAACL 2018 · `https://aclanthology.org/N18-1149`

- Aspect set: Substance, Clarity, Appropriateness, Impact, Meaningful
  Comparison, Originality, Soundness/Correctness. Substance (0.59) and Clarity
  (0.42) correlate most with the overall recommendation.

### Identifying Aspects in Peer Reviews
`https://arxiv.org/abs/2504.06910` (Findings of EMNLP 2025)

- Data-driven 3-level taxonomy, ~4.8k extracted aspects grouped into 16 broad
  categories. Explicitly removes "too general" labels: Strength, Weakness,
  Question, Comment.
  → Our Axis 1 is a re-cut of these two, keyed to author actions; the mapping
  table in `review-comment-taxonomy.md` records the correspondence.

### Peer review analyze / ReviVal
PLOS ONE 2021 (`https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0259238`)

- Comment-level schemes: purpose (evaluative vs. actionable), informativeness.
  → Feeds Axis 3 (actionability).
