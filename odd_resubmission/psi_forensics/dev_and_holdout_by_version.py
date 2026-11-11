"""Forensic: dev (125 cells) and holdout (56 cells) sign accuracy for each recovered model version.

V0 = launch state of the 2026-10-28T03:06:31Z holdout run (reconstructed; reproduces holdout_psi.csv exactly).
V1 = committed f964b66 model. Holdout IBM signs come from the unchanged results/reversal/holdout_metrics.csv.
Exploratory/forensic only; no registry is written.
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from agentic_conservation.analysis import SWEEPS  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cells = pd.read_csv(ROOT / "results/threshold_cell_stability.csv")
cells = cells[cells.n == 8][["sweep", "x", "y", "final_sign"]].drop_duplicates()
hm = pd.read_csv(ROOT / "results/reversal/holdout_metrics.csv")
hp = pd.read_csv(ROOT / "results/reversal/holdout_psi.csv")
print("holdout_metrics columns:", list(hm.columns))
obs_col = [c for c in hm.columns if c in ("obs_sign", "sign", "ibm_sign")][0]
obs = hm.set_index("cell")[obs_col]
diff_col = [c for c in hm.columns if c in ("mean_diff", "ibm_mean_diff", "diff")]
rows = []
for label, fname, extra in [
    ("V0_launch_state_mbp4", "minimal_model_reconstructed_holdout_launch_state.py", {}),
    ("V0_launch_state_mbp8", "minimal_model_reconstructed_holdout_launch_state.py", {"_min_breeding_pop": 8.0}),
    ("V1_committed_f964b66_mbp4", "minimal_model_f964b66.py", {}),
    ("V1_committed_f964b66_mbp8", "minimal_model_f964b66.py", {"_min_breeding_pop": 8.0}),
]:
    m = load(label, HERE / fname)
    b = m.load_config(ROOT)
    pa = b["config"]["policy_allocations"]
    dev = []
    for _, r in cells.iterrows():
        xn, _, yn, _ = SWEEPS[r.sweep]
        ov = {xn: float(r.x), yn: float(r.y)} | extra
        dev.append((r.final_sign, m.psi_index(b, pa["S7"], pa["S6"], ov)["psi"]))
    dev = np.array(dev)
    dpred = np.where(dev[:, 1] > 0, 1, -1)
    det = dev[:, 0] != 0
    hpsi = np.array([m.psi_index(b, pa["S7"], pa["S6"], json.loads(o) | extra)["psi"] for o in hp.overrides])
    hpred = np.where(hpsi > 0, 1, -1)
    o = obs.reindex(hp.cell).to_numpy()
    hdet = o != 0
    row = {
        "version": label,
        "dev_acc_all": (dpred == dev[:, 0]).mean(),
        "dev_acc_det": (dpred[det] == dev[det, 0]).mean(),
        "holdout_acc_all": (hpred == o).mean(),
        "holdout_acc_det": (hpred[hdet] == o[hdet]).mean(),
    }
    if diff_col:
        d = hm.set_index("cell")[diff_col[0]].reindex(hp.cell).to_numpy()
        # registry definition (run_reversal_theory.stage_metrics): mean(best - picked)
        row["holdout_regret"] = float(np.mean(np.where(hpred == np.sign(d), 0.0, np.abs(d))))
    rows.append(row)
out = pd.DataFrame(rows)
out.to_csv(HERE / "dev_and_holdout_by_version.csv", index=False)
print(out.to_string(index=False))
