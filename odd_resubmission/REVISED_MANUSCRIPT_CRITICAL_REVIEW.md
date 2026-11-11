# Critical pre-submission review of the revised manuscript (reviewer stance)

Reviewed file: `odd_resubmission/submission/EM_ODD_REVISED_MANUSCRIPT_CLEAN.docx` (built by
`src/agentic_conservation/documents_em_odd.py`). Ranked by severity × fix value × feasibility.
Mechanical QC is in `FINAL_ODD_QC_MATRIX.md`; passing it does not make the package ready.

## Must fix before submission (blocking)
1. **Decision letter quoted — resolved 2026-11-10.** The author supplied the letter; each
   response point now quotes the Associate Editor or Editor-in-Chief verbatim (original spelling
   kept). The letter contains no reviewer reports; the response says so rather than inventing any.
2. **Public mirror and commit reference — synced, residual risk.** The mirror was fast-forwarded
   without deletions or history rewrite (`PUBLIC_MIRROR_COMMIT.txt`, cited in the cover letter)
   and reproduction from a clean clone was checked. The scheduled sync still maps an older branch
   to the mirror with force-push; that mapping must be retired before submission.
3. **Author block.** Affiliation ("Independent researcher") and contact line are placeholders to
   be confirmed by the author.

## High priority (scientific)
4. **The headline ordering is conditional.** S6 > S7 in the base case (−0.055, ≈2.5 SE) reverses
   under every alternative climate trajectory (Q2), under suitability intercept ×1.5 (Q3), and
   under three ablations (disease, engagement feedback, origin fidelity; point estimates). The
   text now says so in the Abstract, Results and Discussion; a hostile reviewer may still ask why
   the accelerating trajectory is the default. Answer available: it is one scenario, the least
   exposure of the four, stated as an exploratory structural assumption.
5. **E1 intercept ×1.5 was not evaluated on held-out cells** (frozen stage-2 cap). Stated in 3.5.
   Running it now would be exploratory and outside the frozen plan; left as stated.
6. **Ψ confirmatory scope.** 34/60 determinate cells, one error (C21). Pass is limited to V1 and the
   shipped structure; matched-climate Ψ results are exploratory. Stated in 3.6 and Discussion.
7. **Bundled contrast.** S6 and S7 differ in all seven allocation channels and the movement rule;
   Ψ predicts the bundled contrast and does not isolate circulation. Stated in 2.10.1 and 4.
8. **Ablations and LHS have no SE in the text.** Reported as point estimates (Appendix A).

## Medium priority
9. Tracked version is a reconstructed paragraph/word comparison, not Word revision marks; tables
   are not diffed. Stated at the top of the tracked file.
10. Patterns P1 and P3 are partly built in; stated as weak tests in 2.1.
11. Inert traits (climate sensitivity, dispersal, social dependence, node connectivity) are listed
    in Table 2 rather than removed, to keep the configuration and code unchanged.

## Optional
12. Graphical abstract (optional at Ecological Modelling) not prepared.
13. A full ODD document as Appendix B (TRACE-style) could be added; the main text already holds the
    essential description as required.
