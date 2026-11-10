"""Summarise Q1-Q3 runs (results/odd_verification/*_runs.csv) per the frozen
plan in odd_resubmission/Q1_Q3_PREREGISTRATION.md (incl. amendment A1)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_odd_verification import (  # noqa: E402
    CLIMATE_FORMS,
    ENDPOINTS,
    OUT,
    POLICIES,
    cumulative_exposure,
    holdout_cells,
    paired,
    psi_metrics,
    q3_stage1_table,
    recompute_psi,
)

ROOT = Path(__file__).resolve().parents[1]


def _holdout_cells(runs):
    runs = runs.copy()
    return runs


def q1_summary(psi_reg, psi_code):
    base = pd.read_csv(OUT / "q1_base_runs.csv")
    hold = pd.read_csv(OUT / "q1_holdout_runs.csv")
    po = pd.read_csv(ROOT / "results/policy_outcomes.csv")
    po = po[~po.oracle]
    chk = base.merge(
        po[["policy", "seed", "survival_100"]], on=["policy", "seed"], suffixes=("", "_reg")
    )
    reg_ok = bool(np.allclose(chk.survival_100, chk.survival_100_reg, atol=1e-12))
    hr = pd.read_csv(ROOT / "results/reversal/holdout_runs.csv")
    chk2 = hold.merge(
        hr[["cell", "policy", "seed", "survival_100"]],
        on=["cell", "policy", "seed"],
        suffixes=("", "_reg"),
    )
    hold_ok = bool(np.allclose(chk2.survival_100, chk2.survival_100_reg, atol=1e-12)) and len(
        chk2
    ) == len(hold)
    means = base.groupby("policy")[ENDPOINTS].mean().loc[POLICIES]
    ses = base.groupby("policy")[ENDPOINTS].sem().loc[POLICIES]
    rows, prow = [], []
    for ep in ENDPOINTS:
        c = paired(base[base.policy.isin(["S6", "S7"])], ep).iloc[0]
        tau = kendalltau(means["survival_100"], means[ep]).statistic
        order = " > ".join(means[ep].sort_values(ascending=False).index)
        rows.append(
            {
                "endpoint": ep,
                "S6_mean": c.S6,
                "S7_mean": c.S7,
                "S7_minus_S6": c.mean_diff,
                "se": c.se,
                "sign": int(c.sign),
                "kendall_tau_vs_individual": tau,
                "ranking": order,
            }
        )
        cell = paired(hold, ep)
        for name, psi in (("psi_reg", psi_reg), ("psi_code", psi_code)):
            prow.append({"endpoint": ep, "psi": name} | psi_metrics(cell, psi))
    means.join(ses, rsuffix="_se").to_csv(OUT / "q1_base_policy_means.csv")
    pd.DataFrame(rows).to_csv(OUT / "q1_base_contrast.csv", index=False)
    pd.DataFrame(prow).to_csv(OUT / "q1_holdout_psi_metrics.csv", index=False)
    signs = pd.concat({ep: paired(hold, ep)["sign"] for ep in ENDPOINTS}, axis=1)
    signs.to_csv(OUT / "q1_holdout_cell_signs.csv")
    return {"registry_reproduced_base": reg_ok, "registry_reproduced_holdout": hold_ok}


def q2_summary(psi_reg, psi_code_ship):
    hold0 = pd.read_csv(OUT / "q1_holdout_runs.csv")
    base0 = pd.read_csv(OUT / "q1_base_runs.csv")
    base0 = base0[base0.policy.isin(["S6", "S7"])]
    rows, prow = [], []
    for form in ["accelerating"] + CLIMATE_FORMS:
        if form == "accelerating":
            base, hold, psi_alt = base0, hold0, psi_code_ship
        else:
            base = pd.read_csv(OUT / f"q2_{form}_base_runs.csv")
            hold = pd.read_csv(OUT / f"q2_{form}_holdout_runs.csv")
            psi_alt = recompute_psi({"climate_form": form})
        total, exposure = cumulative_exposure(form)
        for ep in ENDPOINTS[:2]:
            c = paired(base, ep).iloc[0]
            cell = paired(hold, ep)
            ref = paired(hold0, ep)["sign"]
            det_ref = ref != 0
            agree = float((cell["sign"][det_ref] == ref[det_ref]).mean())
            rows.append(
                {
                    "climate_form": form,
                    "endpoint": ep,
                    "year100_displacement": total,
                    "cumulative_exposure_disp_years": exposure,
                    "exposure_ratio_vs_shipped": exposure / cumulative_exposure("accelerating")[1],
                    "realised_origin_quality_mean_S6": base[
                        base.policy == "S6"
                    ].origin_quality_mean.mean(),
                    "realised_origin_quality_mean_S7": base[
                        base.policy == "S7"
                    ].origin_quality_mean.mean(),
                    "S6_mean": c.S6,
                    "S7_mean": c.S7,
                    "S7_minus_S6": c.mean_diff,
                    "se": c.se,
                    "sign": int(c.sign),
                    "holdout_det_sign_agreement_vs_shipped": agree,
                }
            )
            for name, psi in (
                ("b1_psi_reg", psi_reg),
                ("b1_psi_code", psi_code_ship),
                ("b2_psi_code_alt", psi_alt),
            ):
                prow.append(
                    {"climate_form": form, "endpoint": ep, "psi": name} | psi_metrics(cell, psi)
                )
        prow.append(
            {
                "climate_form": form,
                "endpoint": "-",
                "psi": "b3_sign_flips_vs_shipped_psi_code",
                "cells": int((np.sign(psi_alt) != np.sign(psi_code_ship)).sum()),
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "q2_summary.csv", index=False)
    pd.DataFrame(prow).to_csv(OUT / "q2_psi_metrics.csv", index=False)


def q3_summary(psi_reg, psi_code_ship):
    t = q3_stage1_table()
    sel = pd.read_csv(OUT / "q3_stage2_selection.csv")
    prow = []
    for r in sel[sel.stage2_evaluated].itertuples():
        tag = f"{r.literal}_x{r.factor}"
        f = OUT / f"q3_stage2_{tag}_holdout_runs.csv"
        if not f.exists():
            continue
        hold = pd.read_csv(f)
        val = t[(t.literal == r.literal) & (t.factor == r.factor)].value.iloc[0]
        psi_alt = recompute_psi({"structural": {r.literal: val}})
        for ep in ENDPOINTS[:2]:
            cell = paired(hold, ep)
            for name, psi in (
                ("b1_psi_reg", psi_reg),
                ("b1_psi_code", psi_code_ship),
                ("b2_psi_code_alt", psi_alt),
            ):
                prow.append(
                    {"literal": r.literal, "factor": r.factor, "endpoint": ep, "psi": name}
                    | psi_metrics(cell, psi)
                )
    pd.DataFrame(prow).to_csv(OUT / "q3_stage2_psi_metrics.csv", index=False)


if __name__ == "__main__":
    hc = holdout_cells().set_index("cell")
    psi_reg = hc["psi"]
    psi_code = recompute_psi({})
    pd.DataFrame({"psi_reg": psi_reg, "psi_code": psi_code}).to_csv(OUT / "psi_reg_vs_code.csv")
    stages = sys.argv[1:] or ["q1", "q2", "q3"]
    if "q1" in stages:
        print(json.dumps(q1_summary(psi_reg, psi_code)))
    if "q2" in stages:
        q2_summary(psi_reg, psi_code)
    if "q3" in stages:
        q3_summary(psi_reg, psi_code)
