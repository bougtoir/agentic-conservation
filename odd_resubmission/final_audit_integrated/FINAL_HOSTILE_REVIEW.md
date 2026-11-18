# FINAL HOSTILE REVIEW (integrated, appendix-free version)

Reviewer stance: an ODD-literate associate editor who rejected the previous
version for missing rationale, reading the new layout as a complete article.
Ranked by severity, effect of a fix and feasibility (note-6 convention).

## Must address before submission (author decision)

1. **Author review of changed claims.** The cover letter and Section 3.5 now
   say that only the disease ablation reversed the ordering beyond Monte Carlo
   error; the previous text also named the engagement feedback. This follows
   from the paired SE (12 seeds) shown in Table 10 and is a narrowing, but it
   changes a signed statement. Fix: author confirms the wording.
2. **Mirror `main` can still be reset by old branches** (see
   FINAL_PUBLIC_VERSION_AND_SYNC_AUDIT.md). The manuscript cites a tag, so
   the reference is not broken, but a reviewer opening the repository front
   page may see obsolete files. Fix: approve archiving and deleting the five
   retired branches.

## High priority

3. **Grimm's central request (rationale for every equation and algorithm)** is
   met for Eqs. 1, 2, 6, 7 and Algorithm 2 with full seven-part blocks;
   2.7.3, 2.7.4, 2.7.5, 2.7.7 and 2.7.10 carry the rationale in a shorter
   paragraph (PARTIAL in the S1 audit). Acceptable, but an ODD reviewer may ask
   for the same block format. Fix: optional, text only.
4. **Table 10 is honest but weak evidence.** 12 paired seeds per design; 11
   of 15 S7 − S6 differences are within 2 SE. The text now says so, and the
   table shows S4 and the poor outcomes (e.g. S6 0.188 without engagement
   feedback). No fix needed beyond what is written; more seeds would be a new
   simulation and was not run.
5. **Historical comparator error in a canonical table.**
   `tables/table9_reversal_predictors.csv` lists B0 determinate accuracy 0.0
   (a literal in `scripts/build_outputs.py`); the per-cell record gives 0.346,
   which Table 11 reports. The canonical file was not edited. A reviewer
   comparing the repository table with Table 11 will see the difference;
   the crosswalk documents it.

## Medium priority

6. **Notation.** Structured equations show proper subscripts, but the
   following "where" sentences still write b_x, M_j, r_j with underscores.
   Eqs. 1, 2 and 6 use a local auxiliary z for the unclipped argument; z is
   defined inside each equation. Fix: optional typesetting pass.
7. **Length.** About 5,700 words (Introduction to Declarations, excluding
   captions and notes), 11 tables, 10 figures, 45 PDF pages. The Elsevier guide
   checked on 2026-10-27 sets no hard word or figure limit and allows
   embedded figures; not re-checked in this task.
8. **Rendering.** Equations and tables were inspected in the LibreOffice
   PDF; Microsoft Word was not available. The DOCX uses standard OMML
   (m:sSub, m:sSup, m:d) and fixed table grids, so Word should lay out the
   same content, but line breaks may differ.

## Optional

9. Figure 10 appears two pages after its first citation because the 3.7
   text continues; it is still adjacent to its section.
10. Three public tags for this version (v3-inline, v3.1-inline, v3.2-inline);
    only v3.2 is cited. Superseded tags are documented, not deleted.

## Transparency and placement of the integrated material

- Former appendix results are now visible where they are interpreted:
  Table 9 (LHS profile) and the interaction screen in 3.5, Table 10
  (ablations and adverse conditions, landscape, two-row header repeated on
  each page), alternative weights in 3.7, historical V0 and B0–B2 in
  Table 11. Each is labelled descriptive, exploratory, historical or
  confirmatory as appropriate.
- Figures 1–10 are inline, in order, each directly after the paragraph that
  first cites it, with editable captions; Figure 1 no longer suggests that
  animals move into the biobank, and Figure 9 no longer claims a frozen
  held-out test.

Verdict from this review: no unresolved scientific or provenance
contradiction; items 1–2 need the author.
