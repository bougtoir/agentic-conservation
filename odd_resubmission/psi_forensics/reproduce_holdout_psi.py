"""Forensic check: does the reconstructed 03:06:31Z model state reproduce holdout_psi.csv?"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


stored = pd.read_csv(ROOT / "results/reversal/holdout_psi.csv")
rows = []
for label, fname, extra in [
    ("committed_f964b66", "minimal_model_f964b66.py", {}),
    ("reconstructed_launch_state_mbp4", "minimal_model_reconstructed_holdout_launch_state.py", {}),
    ("reconstructed_launch_state_mbp8", "minimal_model_reconstructed_holdout_launch_state.py", {"_min_breeding_pop": 8.0}),
]:
    m = load(label, HERE / fname)
    b = m.load_config(ROOT)
    pa = b["config"]["policy_allocations"]
    out = []
    for _, r in stored.iterrows():
        ov = json.loads(r.overrides) | extra
        res = m.psi_index(b, pa["S7"], pa["S6"], ov)
        out.append([res["psi"], res["habitat_channel"], res["circulation_channel"]])
    out = np.array(out)
    ref = stored[["psi", "habitat_channel", "circulation_channel"]].to_numpy()
    diff = np.abs(out - ref)
    rows.append({
        "candidate": label,
        "max_abs_diff_psi": diff[:, 0].max(),
        "max_abs_diff_channels": diff[:, 1:].max(),
        "exact_cells_1e-9": int((diff.max(axis=1) < 1e-9).sum()),
        "sign_agreement": int((np.sign(out[:, 0]) == np.sign(ref[:, 0])).sum()),
        "n_cells": len(stored),
    })
res = pd.DataFrame(rows)
res.to_csv(HERE / "holdout_psi_reproduction_check.csv", index=False)
print(res.to_string(index=False))
