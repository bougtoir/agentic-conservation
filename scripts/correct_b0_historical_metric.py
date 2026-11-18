"""Versioned correction of the historical B0 determinate-cell accuracy.

`tables/table9_reversal_predictors.csv` (historical, frozen) lists B0 (always
S6) determinate accuracy as 0.0. That value is a literal in
`scripts/build_outputs.py::_table_reversal_predictors`, not a computed metric.
This script recomputes every determinate-cell accuracy from the stored
per-cell record `results/reversal/holdout_metrics.csv` with the same
definition used for Ψ in `scripts/run_reversal_theory.py`
(determinate cell: obs_sign != 0, i.e. |mean S7 − S6| > 2 paired MC SE;
accuracy = share of determinate cells whose predicted sign equals obs_sign)
and writes a distinct corrected table. The historical file is not modified.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CELLS = "results/reversal/holdout_metrics.csv"
VALUES = "results/reversal/manuscript_reversal_values.csv"
ORIGINAL = "tables/table9_reversal_predictors.csv"
CORRECTED = "tables/table9_reversal_predictors_corrected_v1.csv"


def determinate_accuracy(pred: np.ndarray, obs: np.ndarray) -> float:
    """Share of determinate cells (obs != 0) whose predicted sign equals obs."""
    pred, obs = np.asarray(pred), np.asarray(obs)
    det = obs != 0
    return float((pred[det] == obs[det]).mean()) if det.any() else float("nan")


def all_cell_accuracy(pred: np.ndarray, obs: np.ndarray) -> float:
    """Share of all cells whose predicted sign equals obs (indeterminate obs = 0
    is never matched by a ±1 prediction)."""
    return float((np.asarray(pred) == np.asarray(obs)).mean())


def corrected_table(root: Path = ROOT) -> pd.DataFrame:
    m = pd.read_csv(root / CELLS)
    v = pd.read_csv(root / VALUES).set_index("value_id").estimate
    orig = pd.read_csv(root / ORIGINAL)
    obs = m.obs_sign.to_numpy()
    preds = {
        "Psi (minimal-model criterion)": m.pred_sign.to_numpy(),
        "B0 always-S6": np.full(len(m), -1),
        "B1 single-parameter threshold (dev-fitted)": m.pred_B1.to_numpy(),
        "B2 logistic surrogate (dev-fitted)": m.pred_B2.to_numpy(),
    }
    regret = {"Psi (minimal-model criterion)": v.regret_psi, "B0 always-S6": v.regret_B0}
    rows = []
    for name, pred in preds.items():
        o = orig.set_index("predictor").loc[name]
        det = determinate_accuracy(pred, obs)
        src = "unchanged (recomputed, equal)"
        if name == "B0 always-S6":
            src = "corrected: original literal 0.0 in scripts/build_outputs.py"
        elif pd.isna(o.determinate_accuracy):
            src = "added: not reported in the original table"
        rows.append(
            {
                "predictor": name,
                "cells": len(m),
                "determinate_cells": int((obs != 0).sum()),
                "determinate_correct": int((pred[obs != 0] == obs[obs != 0]).sum()),
                "determinate_accuracy": det,
                "all_cell_accuracy": all_cell_accuracy(pred, obs),
                "balanced_accuracy_3class": float(o.balanced_accuracy_3class),
                "regret": float(regret[name]) if name in regret else float("nan"),
                "original_determinate_accuracy": o.determinate_accuracy,
                "determinate_accuracy_status": src,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    t = corrected_table()
    t.to_csv(ROOT / CORRECTED, index=False)
    for f in (CELLS, VALUES, ORIGINAL, CORRECTED):
        print(hashlib.sha256((ROOT / f).read_bytes()).hexdigest(), f)
    print(t.to_string())


if __name__ == "__main__":
    main()
