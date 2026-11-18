# B0 HISTORICAL METRIC CORRECTION

## Finding

`tables/table9_reversal_predictors.csv` (historical, frozen) lists the
always-S6 comparator B0 with `determinate_accuracy = 0.0`. The generator
`scripts/build_outputs.py::_table_reversal_predictors` writes this value as a
literal (`"determinate_accuracy": 0.0`), introduced in commit ba665ea88
(2026-10-28, "Integrate reversal theory …"). Every other entry of that row is
read from `results/reversal/manuscript_reversal_values.csv`; no determinate
accuracy for B0 was ever computed there. It is a coding error, not an
alternative definition: no metric in the code base gives 0.0 for always-S6
on these cells.

## Definition (as implemented for Ψ in `scripts/run_reversal_theory.py`)

- Cell: one of the 56 historical held-out cells, 12 paired seeds.
- Observed sign `obs_sign` ∈ {+1 (S7 higher), −1 (S6 higher), 0
  (indeterminate)}: ±1 when |mean S7 − S6| > 2 paired MC SE, else 0.
- B0 predicts −1 (S6) in every cell.
- Determinate accuracy = (cells with obs ≠ 0 and pred = obs) / (cells with obs ≠ 0).
- All-cell accuracy = (cells with pred = obs) / 56; a ±1 prediction never
  matches an indeterminate cell.
- Regret = mean over the 56 cells of (best observed policy mean − mean of the
  chosen policy); for B0 the chosen policy is always S6.

## Counts from `results/reversal/holdout_metrics.csv`

17 cells S7 higher, 9 cells S6 higher, 30 indeterminate.

| Predictor | determinate correct / 26 | determinate accuracy | all-cell accuracy | regret | original table |
|---|---|---|---|---|---|
| Ψ (V0) | 22 | 0.846154 | 0.392857 | 0.045015 | 0.846 / 0.393 / 0.045 (equal) |
| B0 always-S6 | 9 | **0.346154** | 0.160714 | 0.083705 | **0.000** / 0.161 / 0.084 |
| B1 threshold | 16 | 0.615385 | 0.285714 | not computed | NaN / 0.286 / NaN |
| B2 logistic | 11 | 0.423077 | 0.196429 | not computed | NaN / 0.196 / NaN |

Only B0 determinate accuracy is corrected. B1/B2 determinate accuracies are
additions (the original table left them empty), labelled as such. All-cell
accuracies, balanced accuracies and regrets agree with the original table to
its three-decimal rounding. B0 all-cell accuracy (9/56) and determinate
accuracy (9/26) differ only in the denominator.

## Artifacts

| File | Role | SHA-256 |
|---|---|---|
| results/reversal/holdout_metrics.csv | per-cell record (input) | 54d2bf489c0abed9a705f98cbd8fd81cd6ca3157b3eb5df3b97cbfef44536c98 |
| results/reversal/manuscript_reversal_values.csv | historical registry (input; regrets) | a3b9f983b2ec42a39c83b192406a7e7e24c5f0b54fbccc9d5e117145cddfb600 |
| tables/table9_reversal_predictors.csv | historical table, unchanged | 1f975d6cc5484e1cb8a14a01c0ad647dc6f1dce8f974565465a438348beb1f1d |
| tables/table9_reversal_predictors_corrected_v1.csv | corrected, versioned output | a7d905af00e68ba39de0c41b0a971e6f7f372cb095e1b923603ae8522aff6c60 |

Generator: `scripts/correct_b0_historical_metric.py` (no literals; recomputes
from the per-cell record). Tests: `tests/test_b0_correction.py` — a toy set of
3 S7, 2 S6 and 3 indeterminate cells (always-S6 → 2/5 determinate, 2/8
all-cell; empty determinate set → NaN), the historical counts (17/9/30;
B0 9/26 and 9/56), agreement of the unchanged metrics with the original
table, and regeneration equality of the corrected CSV. The manuscript
(Table 11 and its note) reads the corrected CSV; the QC script compares the
Table 11 rows with it. No simulation was rerun.

Independent second count: `pandas` filter `obs_sign != 0` → 26 cells; of
these `obs_sign == -1` → 9 (same as the toy-tested function).
