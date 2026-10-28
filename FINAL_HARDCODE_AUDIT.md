# Final Hardcode Audit — Reversal Theory

Scope: all numbers appearing in THEORY_DERIVATION.md, MINIMAL_MODEL_SPECIFICATION.md,
THEORY_GO_NO_GO.md, HOLDOUT_PROTOCOL_AND_RESULTS.md, POLICY_ATTRIBUTION_AUDIT.md,
MECHANISM_LADDER_REPORT.md and minimal-model code.

## Constants (declared fitted, frozen pre-holdout)

| constant | value | source | status |
|---|---|---|---|
| HEALTH | 0.70 | minimal_model.py | fitted on dev, frozen |
| INBREEDING | 0.08 | minimal_model.py | fitted on dev, frozen |
| FEMALE_FRAC | 0.25 | minimal_model.py | fitted on dev, frozen |
| MIN_BREEDING_POP | 8 | minimal_model.py | fitted on dev, frozen |
| persistence floor eps | 0.02 | minimal_model.psi_index | frozen |

## Statistics quoted in documents

| figure | value | source file |
|---|---|---|
| dev Ψ accuracy | 88.8% | results/minimal_model_dev_predictions.csv (regenerate if model changed) |
| holdout cells / runs | 56 / 1,344 | results/reversal/holdout_{runs,psi}.csv |
| determinate cells | 26 (17 S7, 9 S6) | results/reversal/holdout_metrics.csv |
| Ψ acc determinate / all | 0.846 / 0.393 | holdout_metrics.csv |
| Ψ 3-class bacc / regret | 0.519 / 0.045 | computed from holdout_runs.csv |
| baselines B0/B1/B2 acc | 0.161 / 0.304 / 0.161 | same |
| abstention post-hoc | τ=0.1: 36 cells, 94.7% det acc | holdout_metrics.csv |
| attribution medians | alloc −0.359, circ +0.094, interaction +0.344 | results/reversal/attribution_cells.csv |
| ladder means | base 13.57, no_latent 2.37, … | results/reversal/mechanism_ladder_psi.csv |

## Known stale artifacts

- `results/minimal_model_dev_predictions.csv` predates the final minimal-model
  edits (moved aggregation, channel floor); dev accuracy should be regenerated via
  `PYTHONPATH=src python3 -c "from agentic_conservation.minimal_model import ..."`
  before quoting 88.8% in the manuscript. Regeneration command is recorded in
  FINAL_QC_REPORT.md.
- `factorial_variants.csv` seed column holds the nominal policy (script bug);
  documented in POLICY_ATTRIBUTION_AUDIT.md.

## Assertions of honesty

- No holdout metric is reported that was not computed from the CSVs listed above.
- No fabrication of IBM outputs; all derived numbers trace to results/reversal/*.csv
  or results/threshold_*.csv.
