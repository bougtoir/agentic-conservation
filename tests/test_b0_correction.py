import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "b0", ROOT / "scripts/correct_b0_historical_metric.py"
)
b0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b0)


def test_toy_cells_with_indeterminate_and_ties():
    # 3 S7-favoured, 2 S6-favoured, 3 indeterminate (obs 0)
    obs = np.array([1, 1, 1, -1, -1, 0, 0, 0])
    always_s6 = np.full(len(obs), -1)
    assert b0.determinate_accuracy(always_s6, obs) == 2 / 5
    assert b0.all_cell_accuracy(always_s6, obs) == 2 / 8
    perfect = np.array([1, 1, 1, -1, -1, 1, -1, 1])
    assert b0.determinate_accuracy(perfect, obs) == 1.0
    assert np.isnan(b0.determinate_accuracy(always_s6, np.zeros(4)))


def test_historical_b0_from_cell_records():
    m = pd.read_csv(ROOT / b0.CELLS)
    assert len(m) == 56
    assert (m.obs_sign == 1).sum() == 17 and (m.obs_sign == -1).sum() == 9
    t = b0.corrected_table(ROOT).set_index("predictor")
    row = t.loc["B0 always-S6"]
    assert row.determinate_correct == 9 and row.determinate_cells == 26
    assert abs(row.determinate_accuracy - 9 / 26) < 1e-12
    assert abs(row.all_cell_accuracy - 9 / 56) < 1e-12
    orig = pd.read_csv(ROOT / b0.ORIGINAL).set_index("predictor")
    assert orig.loc["B0 always-S6", "determinate_accuracy"] == 0.0
    psi = t.loc["Psi (minimal-model criterion)"]
    assert (
        round(psi.determinate_accuracy, 3)
        == orig.loc["Psi (minimal-model criterion)", "determinate_accuracy"]
    )
    for name in orig.index:
        assert round(t.loc[name, "all_cell_accuracy"], 3) == orig.loc[name, "all_cell_accuracy"]


def test_corrected_csv_matches_generator():
    saved = pd.read_csv(ROOT / b0.CORRECTED)
    pd.testing.assert_frame_equal(
        saved, b0.corrected_table(ROOT).reset_index(drop=True), check_dtype=False
    )
