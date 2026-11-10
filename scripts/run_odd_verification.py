"""ODD-resubmission targeted verification (Q1-Q3), frozen plan in
odd_resubmission/Q1_Q3_PREREGISTRATION.md. Writes results/odd_verification/.

Usage: python scripts/run_odd_verification.py {q1,q2,q3s1,q3s2,report} [workers]
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agentic_conservation.minimal_model import load_config, psi_index  # noqa: E402
from agentic_conservation.simulation import (  # noqa: E402
    STRUCTURAL_DEFAULTS,
    climate_increment,
    load_project,
    run_simulation,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "odd_verification"
OUT.mkdir(parents=True, exist_ok=True)
POLICIES = ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7"]
ENDPOINTS = ["survival_100", "viable_persistence_100", "wild_persistence_100"]
BASE_SEEDS = list(range(200000, 200192))
Q3_SEEDS = list(range(200000, 200048))
HOLDOUT_REPS = 12
CLIMATE_FORMS = ["linear", "decelerating", "step"]
Q3_LITERALS = [
    "e1_intercept",
    "e1_breadth_slope",
    "e1_specificity_penalty",
    "e1_tolerance_bonus",
    "e1_migration_penalty",
    "e6_eligibility_threshold",
    "e6_take_fraction",
    "e11_habitat_mortality",
    "e11_pressure_mortality",
    "e12_birth_scale",
]
SHIPPED = {**STRUCTURAL_DEFAULTS, "e6_take_fraction": 0.20}
STAGE2_CAP = 6


def _run(args):
    tag, cell, policy, seed, overrides = args
    r = run_simulation(load_project(ROOT), policy, seed, overrides)
    row = {"tag": tag, "cell": cell, "policy": policy, "seed": seed}
    for k in ENDPOINTS + ["total_abundance", "origin_quality_mean"]:
        row[k] = r[k]
    return row


def _execute(jobs, workers, name):
    print(f"[{name}] {len(jobs)} runs", flush=True)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(_run, jobs, chunksize=4))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / f"{name}_runs.csv", index=False)
    return df


def holdout_cells() -> pd.DataFrame:
    m = pd.read_csv(ROOT / "results/reversal/holdout_metrics.csv")
    return m[["cell", "name", "group", "overrides", "psi"]].copy()


def holdout_jobs(tag, extra):
    jobs = []
    for r in holdout_cells().itertuples():
        ov = json.loads(r.overrides) | extra
        for rep in range(HOLDOUT_REPS):
            seed = 910000 + int(r.cell[1:]) * 100 + rep
            for pol in ("S6", "S7"):
                jobs.append((tag, r.cell, pol, seed, ov))
    return jobs


def base_jobs(tag, policies, seeds, extra):
    return [(tag, "base", p, s, dict(extra)) for p in policies for s in seeds]


def recompute_psi(extra) -> pd.Series:
    b = load_config()
    pa = b["config"]["policy_allocations"]
    out = {}
    for r in holdout_cells().itertuples():
        out[r.cell] = psi_index(b, pa["S7"], pa["S6"], json.loads(r.overrides) | extra)["psi"]
    return pd.Series(out)


def paired(df, endpoint):
    piv = df.pivot_table(index=["cell", "seed"], columns="policy", values=endpoint).reset_index()
    piv["d"] = piv["S7"] - piv["S6"]
    g = piv.groupby("cell")
    cell = pd.DataFrame(
        {
            "mean_diff": g["d"].mean(),
            "se": g["d"].apply(lambda s: float(s.std(ddof=1)) / np.sqrt(len(s))),
            "S6": g["S6"].mean(),
            "S7": g["S7"].mean(),
            "n": g["d"].size(),
        }
    )
    cell["sign"] = np.where(
        np.abs(cell["mean_diff"]) > 2 * cell["se"], np.sign(cell["mean_diff"]), 0
    ).astype(int)
    return cell


def psi_metrics(cell, psi) -> dict:
    pred = np.sign(psi.loc[cell.index]).astype(int)
    obs = cell["sign"]
    det = obs != 0
    best = cell[["S6", "S7"]].max(axis=1)
    picked = np.where(pred > 0, cell["S7"], cell["S6"])
    return {
        "cells": len(cell),
        "det_cells": int(det.sum()),
        "s7_cells": int((obs == 1).sum()),
        "s6_cells": int((obs == -1).sum()),
        "ind_cells": int((obs == 0).sum()),
        "acc_all": float((pred == obs).mean()),
        "acc_det": float((pred[det] == obs[det]).mean()) if det.any() else float("nan"),
        "regret_psi": float((best - picked).mean()),
        "regret_always_S6": float((best - cell["S6"]).mean()),
    }


def cumulative_exposure(form, v=0.012, T=100):
    cfg = {"climate_velocity": v, "climate_form": form}
    inc = [climate_increment(cfg, t, T) for t in range(1, T + 1)]
    cum = np.cumsum(inc)
    return float(cum[-1]), float(cum.sum())


# ------------------------------------------------------------------ stages
def q1(workers):
    _execute(base_jobs("q1", POLICIES, BASE_SEEDS, {}), workers, "q1_base")
    _execute(holdout_jobs("q1", {}), workers, "q1_holdout")


def q2(workers):
    for form in CLIMATE_FORMS:
        ex = {"climate_form": form}
        _execute(base_jobs(form, ["S6", "S7"], BASE_SEEDS, ex), workers, f"q2_{form}_base")
        _execute(holdout_jobs(form, ex), workers, f"q2_{form}_holdout")


def q3_values():
    out = []
    for lit in Q3_LITERALS:
        for f in (0.5, 1.5):
            out.append((lit, f, SHIPPED[lit] * f))
    return out


def q3s1(workers):
    jobs = []
    for lit, f, val in q3_values():
        tag = f"{lit}@{f}"
        jobs += base_jobs(tag, ["S6", "S7"], Q3_SEEDS, {"structural": {lit: val}})
    _execute(jobs, workers, "q3_stage1_base")
    rows = []
    for lit, f, val in q3_values():
        psi = recompute_psi({"structural": {lit: val}})
        for c, v in psi.items():
            rows.append({"tag": f"{lit}@{f}", "cell": c, "psi": v})
    pd.DataFrame(rows).to_csv(OUT / "q3_stage1_psi.csv", index=False)


def q3_stage1_table():
    ref_runs = pd.read_csv(OUT / "q1_base_runs.csv")
    ref_runs = ref_runs[ref_runs.seed.isin(Q3_SEEDS) & ref_runs.policy.isin(["S6", "S7"])]
    runs = pd.read_csv(OUT / "q3_stage1_base_runs.csv")
    psi = pd.read_csv(OUT / "q3_stage1_psi.csv")
    psi0 = recompute_psi({})
    rows = []
    for lit, f, val in q3_values():
        tag = f"{lit}@{f}"
        row = {"literal": lit, "factor": f, "value": val, "shipped": SHIPPED[lit]}
        for ep in ENDPOINTS[:2]:
            ref = paired(ref_runs, ep).iloc[0]
            per = paired(runs[runs.tag == tag], ep).iloc[0]
            row[f"{ep}_ref_diff"] = ref.mean_diff
            row[f"{ep}_ref_se"] = ref.se
            row[f"{ep}_ref_sign"] = int(ref.sign)
            row[f"{ep}_diff"] = per.mean_diff
            row[f"{ep}_se"] = per.se
            row[f"{ep}_sign"] = int(per.sign)
            row[f"{ep}_S6"] = per.S6
            row[f"{ep}_S7"] = per.S7
        p = psi[psi.tag == tag].set_index("cell")["psi"].loc[psi0.index]
        # Amendment A1: flips are counted against Psi_code at shipped settings.
        row["psi_sign_flips"] = int((np.sign(p) != np.sign(psi0)).sum())
        ep = "survival_100"
        row["material_sign"] = row[f"{ep}_sign"] != row[f"{ep}_ref_sign"]
        row["material_shift"] = (
            abs(row[f"{ep}_diff"] - row[f"{ep}_ref_diff"]) > 2 * row[f"{ep}_ref_se"]
        )
        row["material_psi"] = row["psi_sign_flips"] >= 5
        row["material"] = row["material_sign"] or row["material_shift"] or row["material_psi"]
        rows.append(row)
    t = pd.DataFrame(rows)
    t["shift_abs"] = (t["survival_100_diff"] - t["survival_100_ref_diff"]).abs()
    t.to_csv(OUT / "q3_stage1_summary.csv", index=False)
    return t


def q3s2(workers):
    t = q3_stage1_table()
    mat = t[t.material].sort_values(["psi_sign_flips", "shift_abs"], ascending=False)
    chosen = mat.head(STAGE2_CAP)
    pd.DataFrame(
        {
            "literal": mat.literal,
            "factor": mat.factor,
            "stage2_evaluated": mat.index.isin(chosen.index),
        }
    ).to_csv(OUT / "q3_stage2_selection.csv", index=False)
    for r in chosen.itertuples():
        tag = f"{r.literal}@{r.factor}"
        _execute(
            holdout_jobs(tag, {"structural": {r.literal: r.value}}),
            workers,
            f"q3_stage2_{tag.replace('@', '_x')}_holdout",
        )


if __name__ == "__main__":
    stage = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    {"q1": q1, "q2": q2, "q3s1": q3s1, "q3s2": q3s2}[stage](workers)
