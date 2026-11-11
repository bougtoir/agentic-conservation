# FINAL_REVERSAL_THEORY_AUDIT — PASS (bounded claim verified)

All mandatory claims verified against canonical files (not transcriptions):
results/reversal/manuscript_reversal_values.csv, holdout_metrics.csv,
results/minimal_model_dev_predictions.csv, attribution_cells.csv,
mechanism_ladder_psi.csv, THEORY_GO_NO_GO.md.

- Verdict B (LIMITED) stated; no universal-law wording. PASS.
- 0.846 sign accuracy labelled determinate-only (26 of 56 held-out cells:
  17 S7, 9 S6). PASS — §3.7 states conditioning explicitly.
- All-cell accuracy 0.393 with the 30 indeterminate cells named; equally
  visible in same paragraph. PASS.
- |Psi|<0.2 → 0.174 accuracy over 23 cells, labelled "at chance". PASS.
- Denominators: 125 dev / 122 determinate dev / 56 holdout disjoint; dev
  0.888/0.910 never conflated with holdout. PASS.
- Regret 0.045 = mean survival forgone (units: year-100 species fraction),
  vs B0 0.084; baselines B0 0.161 / B1 0.286 / B2 0.196 all-cell. PASS.
- Abstention |Psi|>=0.1 labelled "post-hoc characterization, not part of the
  frozen formula" verbatim in §3.7. PASS.
- Bundled contrast: "not the isolated causal effect of circulation" stated in
  Results and Discussion; attribution medians (+0.16/+0.30 circ; -0.54
  allocation) sourced from attribution_cells.csv. PASS.
- Mechanism ladder: latent cohort removal cuts mean Psi ~83%; mate limit
  shifts boundary — reported as reduced-model interventions, bounded. PASS.
- Denominator hygiene: 125 sweep cells (35 S7 / 26 S6 / 64 indeterminate)
  kept distinct from theory-dev and holdout cells. PASS.
- Leakage: seeds/cells disjoint; formula + 4 constants frozen pre-holdout in
  THEORY_GO_NO_GO.md; B1/B2 fitted on dev only. PASS.
