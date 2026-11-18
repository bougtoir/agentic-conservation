# FINAL HANDOFF — inline figures, appendix removed

Verdict: **CONDITIONAL GO** (not SUBMISSION READY). Not merged, not submitted,
no editor contacted.

## Versions

- wip branch: `devin/1794992060-em-odd-inline-figures` (base master 35c5deb9cbf4).
- Generator commit published as release: wip 1cdae79f868c → public commit
  4ccbc9c72c43, tag **odd-2020-revision-v3.2-inline** (cited in the manuscript
  and cover letter). Superseded intermediate tags: v3-inline (d92b23c01af7),
  v3.1-inline (10046dad043c). `odd-2020-revision-v2` (21770296ff24) unchanged.
- Public `main` at 4ccbc9c72c43 after three fast-forward pushes (no force, no deletions).

## Files modified or added

- `src/agentic_conservation/documents_em_odd.py`: inline figures with editable
  captions; former appendix tables integrated (Table 9 LHS profile, Table 10
  ablations/adverse conditions in a landscape section, Table 11 historical
  baselines, interaction-screen and alternative-weight text); Appendix builder
  removed; author metadata; structured OMML equations split into lines within
  the margin; new output names under `odd_resubmission/submission/integrated/`.
- `scripts/make_odd_figures.py`: corrected Figure 1 and historical-Ψ figure variants.
- `scripts/build_integrated_submission.py`, `scripts/qc_integrated_submission.py`, `Makefile` (`make integrated`), `README.md`.
- `figures/odd/fig1_network_living_nodes.png`, `figures/odd/fig_psi_historical_v0.png` (new; originals unchanged).

## Tables renumbered

Tables 1–8 unchanged; former Table 9 (Ψ) → Table 11; new Table 9 (from A1),
Table 10 (A3). A2 and A4 → text; A5 → rows and note of Table 11; A6/A7 stay in
the repository. Details: APPENDIX_ELIMINATION_CROSSWALK.md.

## Figure pages (PDF, 45 pages)

Fig. 1 p6, 2 p10, 3 p12, 4 p23, 5 p24, 6 p25, 7 p26, 8 p28, 9 p34, 10 p36.

## Mathematical presentation

No equation changed mathematically. Equations are structured OMML
(sub/superscripts, parentheses); long ones are split at top-level operators;
Eqs. 1, 2, 6 write `clip(z; lo, hi)` with z the unclipped argument; "~" is
written "∼".

## Numbers

Unchanged: every canonical value (Q1–Q3, historical V0 Ψ 0.846/0.393/0.0450,
prospective 33/34, 0.971 [0.851, 0.995], all-cell 0.550, regret 0.0095 vs
0.0759/0.0807, ablation and LHS values). New derived values, all from
preserved per-seed or per-cell records: paired SE of S7 − S6 in Table 10;
historical B0 determinate accuracy 0.346 (canonical table literal 0.0 is
wrong, not edited), B1 0.423/0.286, B2 0.423/0.196 (determinate/all-cell).

## Tests and audits run (logs in this directory)

pytest 43 passed; ruff clean; final_numeric_audit 157/157; QC 113/113;
clean clone of the v3.2 tag: pytest, numeric audit, Ψ reconstruction 56/56,
rebuild identical except the commit placeholder; visual inspection of all
45 PDF pages, every figure and every equation.

## Author actions

1. Review the narrowed ablation statement in the cover letter and Section 3.5
   (only the disease ablation exceeds 2 SE).
2. Review the corrected Figure 1 and Figure 9 variants and the caption
   corrections of Figures 4, 7 and 10.
3. Decide on archiving and deleting the five retired wip branches that can
   still force-push the public `main`.
4. Approve merge of the PR and, separately, submission.
