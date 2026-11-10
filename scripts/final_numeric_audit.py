"""Independent recomputation of the primary numerical claims from run-level outputs.

Re-derives, without the project's summariser or metric code, the S7 - S6 contrasts
(Q1-Q3), the closed-form climate exposure, the historical V0 held-out metrics and the
prospective confirmatory metrics, and compares them with the stored registries.
Writes results/final_audit/numeric_recompute.csv. Exit code 1 on any mismatch.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
OV = R / "odd_verification"
C = R / "psi_confirmatory"
TOL = 1e-9
ENDPOINTS = ["survival_100", "viable_persistence_100", "wild_persistence_100"]
rows: list[dict] = []


def check(claim: str, recomputed: float, stored: float, source: str, tol: float = TOL) -> None:
    ok = (math.isnan(recomputed) and math.isnan(stored)) or abs(recomputed - stored) <= tol
    rows.append(dict(claim=claim, recomputed=recomputed, stored=stored, ok=ok, source=source))


def paired(runs: pd.DataFrame, col: str, keys=("cell",)) -> pd.DataFrame:
    w = runs.pivot_table(index=[*keys, "seed"], columns="policy", values=col).reset_index()
    w["d"] = w["S7"] - w["S6"]
    g = w.groupby(list(keys))
    out = pd.DataFrame(
        {
            "S6": g["S6"].mean(),
            "S7": g["S7"].mean(),
            "d": g["d"].mean(),
            "se": g["d"].std(ddof=1) / np.sqrt(g["d"].count()),
            "n": g["d"].count(),
        }
    )
    return out


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


# Q1 base contrasts
q1 = pd.read_csv(OV / "q1_base_runs.csv")
q1c = pd.read_csv(OV / "q1_base_contrast.csv").set_index("endpoint")
for ep in ENDPOINTS:
    p = paired(q1, ep).iloc[0]
    s = q1c.loc[ep]
    check(f"Q1 {ep} S6 mean", p.S6, s.S6_mean, "q1_base_contrast.csv")
    check(f"Q1 {ep} S7 mean", p.S7, s.S7_mean, "q1_base_contrast.csv")
    check(f"Q1 {ep} S7-S6", p.d, s.S7_minus_S6, "q1_base_contrast.csv")
    check(f"Q1 {ep} SE", p.se, s.se, "q1_base_contrast.csv")
    check(f"Q1 {ep} n paired seeds", p.n, 192, "design")

# Q2 closed-form exposure and contrasts
v, T = 0.012, 100
t = np.arange(1, T + 1)
incr = {
    "accelerating": v * t / T,
    "linear": np.full(T, v * (T + 1) / 2 / T),
    "decelerating": v * (T + 1 - t) / T,
}
step = np.zeros(T)
step[t == T // 2] = v * (T + 1) / 2  # whole displacement in year 50 (implemented step)
incr["step"] = step
q2 = pd.read_csv(OV / "q2_summary.csv")
q2 = q2[q2.endpoint == "survival_100"].set_index("climate_form")
for form, inc in incr.items():
    disp = np.cumsum(inc)
    check(
        f"Q2 {form} year-100 displacement",
        disp[-1],
        q2.loc[form].year100_displacement,
        "closed form vs q2_summary.csv",
        1e-9,
    )
    check(
        f"Q2 {form} cumulative exposure",
        disp.sum(),
        q2.loc[form].cumulative_exposure_disp_years,
        "closed form vs q2_summary.csv",
        1e-6,
    )
    if form != "accelerating":
        p = paired(pd.read_csv(OV / f"q2_{form}_base_runs.csv"), "survival_100").iloc[0]
        check(f"Q2 {form} S7-S6", p.d, q2.loc[form].S7_minus_S6, f"q2_{form}_base_runs.csv")
        check(f"Q2 {form} SE", p.se, q2.loc[form].se, f"q2_{form}_base_runs.csv")

# Q3 stage-1 contrasts
q3 = pd.read_csv(OV / "q3_stage1_base_runs.csv")
q3s = pd.read_csv(OV / "q3_stage1_summary.csv")
pp = paired(q3, "survival_100", keys=("tag",))
for _, s in q3s.iterrows():
    tag = f"{s.literal}@{s.factor:g}"
    if tag not in pp.index:
        rows.append(
            dict(
                claim=f"Q3 {tag}",
                recomputed=float("nan"),
                stored=s.survival_100_diff,
                ok=False,
                source="tag missing",
            )
        )
        continue
    check(f"Q3 {tag} S7-S6", pp.loc[tag].d, s.survival_100_diff, "q3_stage1_base_runs.csv")
    check(f"Q3 {tag} SE", pp.loc[tag].se, s.survival_100_se, "q3_stage1_base_runs.csv")
reversals = sorted(
    f"{s.literal}@{s.factor:g}"
    for _, s in q3s.iterrows()
    if s.survival_100_diff > 2 * s.survival_100_se
)
check(
    "Q3 perturbations with determinate S7 > S6 (count)",
    len(reversals),
    1,
    "expect only e1_intercept x1.5",
)
rows[-1]["source"] += f": {reversals}"


def sign_metrics(cell: pd.DataFrame, psi: pd.Series) -> dict:
    det = cell[(cell.d.abs() > 2 * cell.se)]
    obs = np.sign(det.d)
    pred = np.where(psi.loc[det.index] > 0, 1, -1)
    best = cell[["S6", "S7"]].max(axis=1)
    picked = np.where(psi.loc[cell.index] > 0, cell.S7, cell.S6)
    obs_all = np.where(cell.d.abs() > 2 * cell.se, np.sign(cell.d), 0)
    return dict(
        cells=len(cell),
        det=len(det),
        s7=int((obs == 1).sum()),
        correct=int((obs == pred).sum()),
        acc_det=float((obs == pred).mean()),
        acc_all=float((obs_all == np.where(psi.loc[cell.index] > 0, 1, -1)).mean()),
        regret=float((best - picked).mean()),
        r6=float((best - cell.S6).mean()),
        r7=float((best - cell.S7).mean()),
    )


# Historical V0 held-out
hr = pd.read_csv(R / "reversal/holdout_runs.csv")
hp = pd.read_csv(R / "reversal/holdout_psi.csv").set_index("cell").psi
m = sign_metrics(paired(hr, "survival_100"), hp)
q1h = pd.read_csv(OV / "q1_holdout_psi_metrics.csv")
ref = q1h[(q1h.endpoint == "survival_100") & (q1h.psi == "psi_reg")].iloc[0]
check("V0 held-out determinate cells", m["det"], ref.det_cells, "holdout_runs + holdout_psi")
check("V0 held-out determinate accuracy", m["acc_det"], ref.acc_det, "holdout_runs + holdout_psi")
check("V0 held-out all-cell accuracy", m["acc_all"], ref.acc_all, "holdout_runs + holdout_psi")
check("V0 held-out regret", m["regret"], ref.regret_psi, "holdout_runs + holdout_psi")

# Prospective confirmatory
ir = pd.read_csv(C / "ibm_runs.csv")
pr = pd.read_csv(C / "psi_predictions.csv").set_index("cell").psi
des = pd.read_csv(C / "designs.csv").set_index("cell")
met = pd.read_csv(C / "metrics.csv").set_index(["endpoint", "stratum"])
check("confirmatory cells", ir.cell.nunique(), 60, "ibm_runs.csv")
check(
    "confirmatory paired seeds per cell",
    ir.groupby(["cell", "policy"]).seed.nunique().min(),
    12,
    "ibm_runs.csv",
)
for ep in ENDPOINTS:
    cell = paired(ir, ep)
    for stratum, idx in [
        ("all", cell.index),
        *[(g, des.index[des.group == g]) for g in ("in_domain", "shifted")],
    ]:
        if (ep, stratum) not in met.index:
            continue
        s = met.loc[(ep, stratum)]
        mm = sign_metrics(cell.loc[idx], pr)
        lo, hi = wilson(mm["correct"], mm["det"]) if mm["det"] else (float("nan"),) * 2
        tag = f"confirmatory {ep} {stratum}"
        check(f"{tag} determinate cells", mm["det"], s.det_cells, "ibm_runs + psi_predictions")
        check(f"{tag} S7 cells", mm["s7"], s.s7_cells, "ibm_runs + psi_predictions")
        check(f"{tag} determinate accuracy", mm["acc_det"], s.acc_det, "ibm_runs + psi_predictions")
        check(f"{tag} all-cell accuracy", mm["acc_all"], s.acc_all, "ibm_runs + psi_predictions")
        check(f"{tag} Wilson lower", lo, s.acc_det_wilson_lo, "independent Wilson", 1e-6)
        check(f"{tag} Wilson upper", hi, s.acc_det_wilson_hi, "independent Wilson", 1e-6)
        check(f"{tag} regret Psi", mm["regret"], s.regret_psi, "ibm_runs + psi_predictions")
        check(f"{tag} regret always-S6", mm["r6"], s.regret_always_S6, "ibm_runs")
        check(f"{tag} regret always-S7", mm["r7"], s.regret_always_S7, "ibm_runs")

out = pd.DataFrame(rows)
(R / "final_audit").mkdir(exist_ok=True)
out.to_csv(R / "final_audit/numeric_recompute.csv", index=False)
print(f"{out.ok.sum()}/{len(out)} checks match")
print(out[~out.ok].to_string())
raise SystemExit(0 if out.ok.all() else 1)
