"""Prospective confirmatory evaluation of the frozen reduced Psi criterion.

Stages (see odd_resubmission/PSI_CONFIRMATORY_VALIDATION_PLAN.md):
  design   -> results/psi_confirmatory/designs.csv            (rule-based, fixed RNG)
  predict  -> results/psi_confirmatory/psi_predictions.csv    (frozen Psi; no IBM run)
  ibm      -> results/psi_confirmatory/ibm_runs.csv           (only after freeze commit)
  evaluate -> results/psi_confirmatory/metrics.csv, cell_results.csv
Design and predictions are committed BEFORE any IBM outcome exists.
"""

from __future__ import annotations

import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from agentic_conservation.analysis import SWEEPS  # noqa: E402
from agentic_conservation.minimal_model import load_config, psi_index  # noqa: E402
from agentic_conservation.simulation import load_project, run_simulation  # noqa: E402

OUT = ROOT / "results" / "psi_confirmatory"
DESIGN_SEED = 20261110
N_IN, N_SHIFT = 40, 20
REPS = 12
SEED_BASE = 5_000_000
PARAMS = {}
for _, (xn, xr, yn, yr) in SWEEPS.items():
    PARAMS[xn] = xr
    PARAMS[yn] = yr


def _dev_and_old_holdout():
    seen = []
    for _, (xn, xr, yn, yr) in SWEEPS.items():
        for x in np.linspace(*xr, 5):
            for y in np.linspace(*yr, 5):
                seen.append({xn: float(x), yn: float(y)})
    hp = pd.read_csv(ROOT / "results/reversal/holdout_psi.csv")
    seen += [json.loads(o) for o in hp.overrides]
    return seen


def _clash(ov, seen):
    for s in seen:
        if set(s) == set(ov) and all(abs(s[k] - ov[k]) < 1e-6 for k in ov):
            return True
    return False


def designs() -> pd.DataFrame:
    rng = np.random.default_rng(np.random.SeedSequence(DESIGN_SEED))
    names = sorted(PARAMS)
    seen = _dev_and_old_holdout()
    rows = []
    while len(rows) < N_IN + N_SHIFT:
        shifted = len(rows) >= N_IN
        k = int(rng.integers(1, 3)) if shifted else 3
        chosen = list(rng.choice(names, size=k, replace=False))
        ov = {}
        for p in chosen:
            lo, hi = PARAMS[p]
            if shifted:
                ov[p] = float(rng.uniform(hi, hi + 0.5 * (hi - lo)))
            else:
                ov[p] = float(rng.uniform(lo, hi))
        if _clash(ov, seen):
            continue
        seen.append(ov)
        rows.append(
            {
                "cell": f"C{len(rows):02d}",
                "group": "shifted" if shifted else "in_domain",
                "overrides": json.dumps(ov, sort_keys=True),
            }
        )
    return pd.DataFrame(rows)


def stage_design():
    OUT.mkdir(parents=True, exist_ok=True)
    designs().to_csv(OUT / "designs.csv", index=False)


def stage_predict():
    d = pd.read_csv(OUT / "designs.csv")
    b = load_config(ROOT)
    pa = b["config"]["policy_allocations"]
    rows = []
    for _, r in d.iterrows():
        res = psi_index(b, pa["S7"], pa["S6"], json.loads(r.overrides))
        rows.append(
            {
                "cell": r.cell,
                "psi": res["psi"],
                "habitat_channel": res["habitat_channel"],
                "circulation_channel": res["circulation_channel"],
                "pred_sign": 1 if res["psi"] > 0 else -1,
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "psi_predictions.csv", index=False)


def _run(args):
    cell, policy, seed, ov = args
    r = run_simulation(load_project(ROOT), policy, seed, ov)
    return {
        "cell": cell,
        "policy": policy,
        "seed": seed,
        "survival_100": r["survival_100"],
        "viable_persistence_100": r["viable_persistence_100"],
        "wild_persistence_100": r["wild_persistence_100"],
    }


def stage_ibm(workers: int = 2):
    d = pd.read_csv(OUT / "designs.csv")
    jobs = []
    for _, r in d.iterrows():
        ov = json.loads(r.overrides)
        for rep in range(REPS):
            seed = SEED_BASE + int(r.cell[1:]) * 100 + rep
            for pol in ("S6", "S7"):
                jobs.append((r.cell, pol, seed, ov))
    print(f"[confirmatory ibm] {len(jobs)} runs", flush=True)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(_run, jobs, chunksize=4))
    pd.DataFrame(rows).to_csv(OUT / "ibm_runs.csv", index=False)


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def stage_evaluate():
    d = pd.read_csv(OUT / "designs.csv")
    pr = pd.read_csv(OUT / "psi_predictions.csv").set_index("cell")
    runs = pd.read_csv(OUT / "ibm_runs.csv")
    out_rows, cell_rows = [], []
    for endpoint in ("survival_100", "viable_persistence_100", "wild_persistence_100"):
        piv = runs.pivot_table(index=["cell", "seed"], columns="policy", values=endpoint)
        piv["d"] = piv["S7"] - piv["S6"]
        g = piv.groupby("cell")
        cell = pd.DataFrame(
            {
                "mean_S6": g["S6"].mean(),
                "mean_S7": g["S7"].mean(),
                "mean_diff": g["d"].mean(),
                "se": g["d"].std(ddof=1) / np.sqrt(g["d"].count()),
            }
        )
        cell["obs_sign"] = np.where(
            np.abs(cell.mean_diff) > 2 * cell.se, np.sign(cell.mean_diff), 0
        ).astype(int)
        cell = cell.join(pr[["psi", "pred_sign"]]).join(d.set_index("cell")[["group"]])
        cell["endpoint"] = endpoint
        cell_rows.append(cell.reset_index())
        for grp, c in [("all", cell)] + list(cell.groupby("group")):
            det = c[c.obs_sign != 0]
            k = int((det.pred_sign == det.obs_sign).sum())
            lo, hi = wilson(k, len(det))
            best = np.maximum(c.mean_S6, c.mean_S7)
            picked = np.where(c.pred_sign == 1, c.mean_S7, c.mean_S6)
            out_rows.append(
                {
                    "endpoint": endpoint,
                    "stratum": grp,
                    "cells": len(c),
                    "det_cells": len(det),
                    "s7_cells": int((c.obs_sign == 1).sum()),
                    "s6_cells": int((c.obs_sign == -1).sum()),
                    "indeterminate_cells": int((c.obs_sign == 0).sum()),
                    "acc_all": float((c.pred_sign == c.obs_sign).mean()),
                    "acc_det": k / len(det) if len(det) else float("nan"),
                    "acc_det_wilson_lo": lo,
                    "acc_det_wilson_hi": hi,
                    "regret_psi": float((best - picked).mean()),
                    "regret_always_S6": float((best - c.mean_S6).mean()),
                    "regret_always_S7": float((best - c.mean_S7).mean()),
                }
            )
    pd.concat(cell_rows).to_csv(OUT / "cell_results.csv", index=False)
    m = pd.DataFrame(out_rows)
    m.to_csv(OUT / "metrics.csv", index=False)
    print(m.to_string(index=False))


if __name__ == "__main__":
    stage = sys.argv[1]
    if stage == "design":
        stage_design()
    elif stage == "predict":
        stage_predict()
    elif stage == "ibm":
        stage_ibm(int(sys.argv[2]) if len(sys.argv) > 2 else 2)
    elif stage == "evaluate":
        stage_evaluate()
