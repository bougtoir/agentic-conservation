# Reversal Theory Integration — Evidence Map

Every integrated claim maps to a canonical source. Commit base: devin/1793300000-reversal-theory (PR #744).

| Manuscript claim | Source | Code entry | Registry key |
|---|---|---|---|
| Psi = ln((M_S7,rule+eps)/(M_S6+eps)) = H + C | minimal_model.psi_index | src/agentic_conservation/minimal_model.py:psi_index | psi, habitat_channel, circulation_channel |
| eps = 0.02 persistence floor | psi_index | same | — |
| Semi-analytical approximation; 4 fitted constants | minimal_model.py constants | HEALTH, INBREEDING, FEMALE_FRAC, MIN_BREEDING_POP | fitted on 125 dev cells, frozen pre-holdout |
| dev sign accuracy 0.888 all / 0.910 determinate (n=122) | results/minimal_model_dev_predictions.csv | run_reversal_theory.stage_metrics | dev_acc_all, dev_acc_det |
| 56 held-out cells; 26 determinate (17 S7, 9 S6); 30 indeterminate | results/reversal/holdout_{runs,psi,metrics}.csv | stage_holdout, stage_metrics | holdout_* |
| held-out det sign acc 0.846; sens 1.00; spec 0.556 | holdout_metrics.csv | stage_metrics | psi_acc_det, psi_sensitivity, psi_specificity |
| all-cell acc 0.393; 3-class bacc 0.519 | same | same | psi_acc_all, psi_bacc3 |
| regret 0.045 vs B0 0.084 | same | same (mean survival forgone vs observed best policy) | regret_psi, regret_B0 |
| baselines B0 0.161 / B1 0.286 / B2 0.196 all-cell | same | B1: dev-fitted threshold on climate_velocity; B2: L2 logistic | B0_acc_all, B1_*, B2_* |
| near-boundary |Psi|<0.2: acc 0.174 (23 cells) | same | near_boundary_* |
| post-hoc abstention |Psi|>=0.1: 36 cells, det acc 0.947 | same | abstain_tau01_* |
| attribution: circ drives S7 cells (+0.16 main / +0.30 interaction); alloc shift drives S6 cells (−0.54); non-additive | results/reversal/attribution_cells.csv | stage_attribution (S6_C, S7_NC arms) | POLICY_ATTRIBUTION_AUDIT.md |
| latent cohort load-bearing (−83% mean Psi removed); mate limit shifts boundary | results/reversal/mechanism_ladder_psi.csv | stage_mechanism_ladder | MECHANISM_LADDER_REPORT.md |
| verdict B (LIMITED) | THEORY_GO_NO_GO.md | frozen gates recorded before holdout | — |

## Integrity checks
- Holdout untouched: seeds 910000+ disjoint from dev 900000+; cells disjoint from
  125 dev designs; formula and constants frozen in THEORY_GO_NO_GO.md before runs.
- No tautology: Psi uses pre-policy quantities only; M computed without observing
  the S7−S6 comparison outcome.
- Not analytical-exact: Ψ is explicitly labelled a semi-analytical approximation;
  no "universal law" wording anywhere (grep-verified).
- Leakage check: B1/B2 fitted only on dev cells; abstention threshold τ=0.1 is
  labelled post-hoc characterization in both docs and manuscript.
