# Journal fit and APC audit — Ecological Modelling (provisional target)

Verified 2026-10-27 UTC against the live Elsevier "Guide for authors" page
(sciencedirect.com/journal/ecological-modelling/publish/guide-for-authors),
the journal homepage APC statement, and third-party bibliometric aggregators.
Live instructions must be rechecked on the submission date.

## Identity

- Journal: Ecological Modelling — International Journal on Ecological
  Modelling and Systems Ecology (Elsevier B.V., Netherlands).
- ISSN 0304-3800 (print) / 1872-7026 (electronic).
- Affiliated with the International Society of Ecological Modelling (ISEM).

## Scope fit

Live aims/scope (verbatim keywords): "new mathematical models and systems
analysis for describing ecological processes, and novel applications of
models for environmental management … process-based models embedded in
theory with explicit causative agents … computer simulations …
socio-ecological systems."

This project is an individual-based stochastic simulation of in situ / ex
situ conservation resource allocation under environmental change, partial
observation, and latent biodiversity — a novel model application for
environmental management. Scope fit is direct, conditional on the
manuscript presenting the model itself transparently (the Conservation
Biology version did not — see EDITORIAL_RESPONSE_MATRIX.md criticism 1).

## Article type

- Target type: **Original research paper (regular paper)** — original
  research, IMRAD. No word limit is stated for regular papers in the live
  guide; length is governed by relevance and the editorial policy on the
  ECOMOD homepage.
- Not pursued: Short communication (≤6 printed pages), Viewpoint (≤2,000
  words), Jorgensen R&R (invited), review, book review, letters.

## Peer review

- **Single anonymized review** (live guide: "This journal follows a single
  anonymized review process"), minimum two reviewers.
- Consequence: the Conservation Biology package's double-blind
  anonymization machinery (anonymous review manuscript, suppressed author
  identifiers) is NOT required for Ecological Modelling. The title page
  with author names/affiliations belongs in the submission. The retarget
  keeps the anonymized build available but produces a non-anonymous
  manuscript DOCX.

## Fees / open access

- Hybrid journal. Live homepage: open access is **optional**; Article
  Publishing Charge USD 3,290 (excl. taxes) applies **only** if the author
  selects open access.
- The subscription (traditional) publication route carries **no mandatory
  author charges**: no submission fee and no mandatory page charge is
  listed in the live guide.
- Verdict: satisfies the zero-mandatory-APC rule via the subscription
  route. OA will not be selected.

## Journal metrics — honest status

- Third-party aggregators (Scimago-derived listings, June 2026 release):
  JIF ≈ 3.5; SJR 0.859; **SJR quartile Q1** in both "Ecological Modeling"
  and "Ecology" categories.
- **JCR quartile cannot be verified from an authoritative source**: the
  Journal Citation Reports interface is paywalled and third-party
  aggregators disagree on the JIF-quartile boundary within "Ecology"
  (JIF ~3.5 is near the Q1/Q2 cut). The prompt's provisional-target rule
  therefore records: Q1 verified by SJR, NOT verifiable by JCR.
- If strict JCR-Q1 verification is required before locking, alternative
  eligible modelling venues with hybrid (subscription) routes include
  Journal of Theoretical Biology (Elsevier hybrid, Q1 SJR) and Methods in
  Ecology and Evolution (hybrid but increasingly OA-dependent — would need
  live re-verification). This flag is reported to the user; the retarget
  proceeds on Ecological Modelling as instructed.

## Format essentials for the rebuild (live guide)

- File format: Word or LaTeX accepted; editable files required at
  revision (submission can be single PDF/DOCX initially).
- Required elements: title page (title, authors, affiliations,
  corresponding author), abstract, keywords, highlights (Elsevier
  standard — verify count/length on the portal at submission),
  declarations (competing interests, funding, data statement, generative-AI
  declaration), references (Elsevier author–date Harvard style family;
  exact style per ECOMOD editorial policy).
- Math formulae: editable equations (not images); DOCX build must use
  OMML.
- Figures/tables: may be embedded or separate; numbered and cited in
  order. Supplementary material allowed and clearly labelled.
- Generative AI: Elsevier policy requires a declaration section naming
  the tool and scope of use; AI cannot be an author. The existing
  AI_USE_DISCLOSURE_DRAFT covers this and will be regenerated in
  Elsevier form.
- Data statement: Elsevier requires a data availability statement;
  code/data repo link (bougtoir/agentic-conservation) satisfies this.

## AI-policy note

Elsevier permits disclosed generative-AI assistance for language/
readability support and requires the declaration; it does not forbid
AI-assisted analysis code. The retarget nonetheless keeps the human
author responsible for interpretation per the existing HUMAN_AUTHORING
convention.
