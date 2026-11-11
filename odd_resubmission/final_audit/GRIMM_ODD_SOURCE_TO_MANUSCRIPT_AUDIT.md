# Grimm ODD 2020 / S1 source-to-manuscript audit (independent re-check)

Sources (re-verified this pass): `data/raw/odd_2020_sources/` — S1-ODD.pdf sha256 `3e92ba51…2a43fe88` (503,054 B) and jasss_23_2_7.html sha256 `f33043d2…bbece17` (149,842 B) match `ACQUISITION_LEDGER.csv` (retrieved 2026-11-09T22:52:09Z from https://www.jasss.org/23/2/7/). Grimm et al. 2020, JASSS 23(2) 7, doi:10.18564/jasss.4259.

Method: S1 checklists were re-extracted from the PDF (pdftotext; checklists at S1 pp. 6, 10, 14, 15–23, 25, 26, 28) and compared item by item with the text of `EM_ODD_REVISED_MANUSCRIPT_CLEAN_FINAL.docx`, and with the code (`src/agentic_conservation/simulation.py`). The earlier `ODD_2020_S1_CROSSWALK.csv` was not used as evidence.

Result: 47 requirements — PASS 37, PARTIAL 10, FAIL 0 (see `GRIMM_ODD_COMPLIANCE_MATRIX.csv`).

Order of elements in the manuscript: 2.1 Purpose and patterns → 2.2 Entities, state variables, and scales → 2.3 Process overview and scheduling → 2.4 Design concepts (11 concepts, each labelled) → 2.5 Initialization → 2.6 Input data → 2.7 Submodels. This is the ODD 2020 order (main article: "Purpose and patterns" is element 1 and patterns are the new aspect).

PARTIAL items (none changes a conclusion): Table 2 lacks an explicit dynamic/static column; scale rationale is one clause; Basic principles does not say whether manager rules are new or existing theory; initialization rationale implicit; no isolated submodel tests; five submodel rationale blocks (2.7.3, 2.7.4, 2.7.5, 2.7.7, 2.7.10) are compressed paragraphs rather than the eight labelled parts used for Eqs. 1, 2, 5–7.

ODD is a description standard. Meeting S1 does not validate the biology; the manuscript says so (Section 4: external validation absent).

Mechanism classes (manuscript Table 3 class labels and 2.7 blocks): biologically supported in direction only — habitat loss, captivity and inbreeding costs, translocation costs, detection delay; computational conventions — index-order population cap, survival floor 0.05, quality clipping; synthetic assumptions — all magnitudes, implicit space, non-decreasing engagement; uncalibrated coefficients — E1–E12 literals (ten varied in Q3); normative evaluation choices — welfare burdens, utility weights, Pareto set without a weighted winner.
