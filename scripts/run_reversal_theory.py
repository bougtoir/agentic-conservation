"""Reversal-theory experiment pipeline (Phase 4-7 of the post-merge spec).

Stages
------
A. attribution: run the two missing factorial comparators (S6_C = S6
   budget + S7 movement rule; S7_NC = S7 budget, movement disabled) on
   the same 125 dev cells and paired seeds used in threshold_sweeps.csv,
   then decompose S7 - S6 into allocation / circulation / interaction.
B. holdout: 56 frozen unseen configurations x {S6, S7} x 12 paired
   seeds; minimal-model Psi per config; metrics vs baselines.
C. mechanism ladder: minimal-model mechanism toggles -> Psi boundary
   shifts (model-side) combined with existing ablations.csv (IBM-side).

Outputs under results/reversal/.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agentic_conservation.analysis import SWEEPS  # noqa: E402
from agentic_conservation.minimal_model import load_config, psi_index  # noqa: E402
from agentic_conservation.simulation import load_project, run_simulation  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "reversal"
OUT.mkdir(parents=True, exist_ok=True)

DEV_REPS = 8
HOLDOUT_REPS = 12


def _run_one(args):
    policy, seed, overrides = args
    p = load_project(ROOT)
    r = run_simulation(p, policy, seed, overrides)
    return {
        "policy": policy,
        "seed": seed,
        "survival_100": r["survival_100"],
        "total_abundance": r["total_abundance"],
    }


# ---------------------------------------------------------------- holdout grid
def holdout_designs() -> list[dict]:
    d = []
    # 12 in-domain midpoints
    d += [
        {
            "group": "in_domain",
            "name": "det_reloc_mid",
            "overrides": {"habitat_deterioration": x, "relocation_stress": y},
        }
        for x, y in [
            (0.003125, 0.075),
            (0.003125, 0.225),
            (0.009375, 0.075),
            (0.009375, 0.225),
            (0.021875, 0.075),
            (0.021875, 0.225),
        ]
    ]
    d += [
        {
            "group": "in_domain",
            "name": "latent_survey_mid",
            "overrides": {"latent_fraction_proxy": x, "survey_cost": y},
        }
        for x, y in [(0.075, 8.0), (0.225, 8.0), (0.375, 38.0), (0.525, 38.0)]
    ]
    d += [
        {
            "group": "in_domain",
            "name": "climate_mort_mid",
            "overrides": {"climate_velocity": x, "relocation_mortality": y},
        }
        for x, y in [(0.00625, 0.0625), (0.04375, 0.1875)]
    ]
    # 16 shifted-domain (beyond dev ranges)
    d += [
        {"group": "shifted", "name": n, "overrides": o}
        for n, o in [
            ("det_high", {"habitat_deterioration": 0.030}),
            ("det_vhigh", {"habitat_deterioration": 0.0375}),
            ("reloc_mort_high", {"relocation_mortality": 0.30}),
            ("reloc_mort_vhigh", {"relocation_mortality": 0.45}),
            ("climate_high", {"climate_velocity": 0.055}),
            ("climate_vhigh", {"climate_velocity": 0.070}),
            ("exsitu_high", {"ex_situ_breeding_benefit": 0.70}),
            ("exsitu_vhigh", {"ex_situ_breeding_benefit": 0.90}),
            ("captivity_high", {"captivity_welfare_penalty": 0.65}),
            ("captivity_vhigh", {"captivity_welfare_penalty": 0.80}),
            ("latent_high", {"latent_fraction_proxy": 0.70}),
            ("latent_vhigh", {"latent_fraction_proxy": 0.85}),
            ("survey_very_expensive", {"survey_cost": 100.0}),
            ("engagement_neg", {"engagement_coefficient": -0.25}),
            ("protection_eff_high", {"habitat_protection_efficiency": 0.14}),
            ("reloc_stress_high", {"relocation_stress": 0.90}),
        ]
    ]
    # 12 joint/interaction
    d += [
        {"group": "joint", "name": n, "overrides": o}
        for n, o in [
            ("det_climate", {"habitat_deterioration": 0.020, "climate_velocity": 0.04}),
            ("det_relocmort", {"habitat_deterioration": 0.015, "relocation_mortality": 0.20}),
            ("climate_latent", {"climate_velocity": 0.030, "latent_fraction_proxy": 0.30}),
            ("exsitu_relocmort", {"ex_situ_breeding_benefit": 0.50, "relocation_mortality": 0.10}),
            (
                "det_prot_latent",
                {
                    "habitat_deterioration": 0.010,
                    "habitat_protection_efficiency": 0.06,
                    "latent_fraction_proxy": 0.20,
                },
            ),
            ("climate_prot", {"climate_velocity": 0.025, "habitat_protection_efficiency": 0.04}),
            ("det_exsitu", {"habitat_deterioration": 0.015, "ex_situ_breeding_benefit": 0.40}),
            ("relocmort_stress", {"relocation_mortality": 0.15, "relocation_stress": 0.45}),
            ("det_survey", {"habitat_deterioration": 0.020, "survey_cost": 40.0}),
            ("climate_disease", {"climate_velocity": 0.030, "movement_disease_risk": 0.10}),
            (
                "prot_relocmort",
                {"habitat_protection_efficiency": 0.08, "relocation_mortality": 0.18},
            ),
            (
                "det3",
                {
                    "habitat_deterioration": 0.018,
                    "climate_velocity": 0.020,
                    "relocation_stress": 0.30,
                },
            ),
        ]
    ]
    # 8 out-of-domain
    d += [
        {"group": "ood", "name": n, "overrides": o}
        for n, o in [
            ("rapid_deterioration", {"scenario": "rapid_deterioration"}),
            ("short_horizon", {"years": 50}),
            ("long_horizon", {"years": 150}),
            ("mortality_high", {"mortality_multiplier": 1.5}),
            ("poor_origin", {"origin_quality_override": 0.45}),
            ("low_budget", {"initial_budget": 60.0}),
            ("high_catastrophe", {"catastrophe_probability": 0.08}),
            ("slow_det_climate", {"scenario": "slow_deterioration", "climate_velocity": 0.04}),
        ]
    ]
    # 8 hostile
    d += [
        {"group": "hostile", "name": n, "overrides": o}
        for n, o in [
            (
                "stable_origin",
                {
                    "scenario": "stationary",
                    "habitat_deterioration": 0.0,
                    "catastrophe_probability": 0.0,
                },
            ),
            ("movement_harm", {"relocation_mortality": 0.50, "movement_disease_risk": 0.20}),
            (
                "easy_restoration",
                {"habitat_protection_efficiency": 0.15, "habitat_deterioration": 0.01},
            ),
            (
                "no_breeding_benefit",
                {"ex_situ_breeding_benefit": 0.0, "relocation_mortality": 0.02},
            ),
            ("all_latent_expensive", {"latent_fraction_proxy": 0.90, "survey_cost": 100.0}),
            (
                "bad_engagement_captivity",
                {"engagement_coefficient": -0.30, "captivity_welfare_penalty": 0.60},
            ),
            ("high_predation", {"predation_multiplier": 3.0}),
            ("high_anthro", {"anthropogenic_pressure_multiplier": 2.0}),
        ]
    ]
    for i, row in enumerate(d):
        row["cell"] = f"H{i:02d}"
    return d


def stage_attribution() -> pd.DataFrame:
    """Factorial comparators on dev cells (paired with existing seeds)."""
    cells = pd.read_csv(ROOT / "results" / "threshold_cell_stability.csv")
    cells = cells[cells.n == 8][["sweep", "x", "y"]].drop_duplicates()
    jobs = []
    for di, (_, r) in enumerate(cells.iterrows()):
        xn, _, yn, _ = SWEEPS[r.sweep]
        ov = {xn: float(r.x), yn: float(r.y)}
        for rep in range(DEV_REPS):
            seed = 900000 + di * 100 + rep
            jobs.append((di, r.sweep, "S6_C", "S6", seed, ov | {"decision_rule_override": "S7"}))
            jobs.append((di, r.sweep, "S7_NC", "S7", seed, ov | {"movement_disabled": True}))
    print(f"[attribution] {len(jobs)} runs", flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(_run_one, (j[3], j[4], j[5])) for j in jobs]
        for j, f in zip(jobs, futs):
            r = f.result()
            rows.append(
                {
                    "design_id": j[0],
                    "sweep": j[1],
                    "variant": j[2],
                    "seed": j[4],
                    "survival_100": r["survival_100"],
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "factorial_variants.csv", index=False)
    return df


def stage_holdout(bundle) -> pd.DataFrame:
    designs = holdout_designs()
    jobs = []
    for d in designs:
        for rep in range(HOLDOUT_REPS):
            seed = 910000 + int(d["cell"][1:]) * 100 + rep
            for pol in ("S6", "S7"):
                jobs.append((d["cell"], d["name"], d["group"], pol, seed, d["overrides"]))
    print(f"[holdout] {len(jobs)} runs", flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(_run_one, (j[3], j[4], j[5])) for j in jobs]
        for j, f in zip(jobs, futs):
            r = f.result()
            rows.append(
                {
                    "cell": j[0],
                    "name": j[1],
                    "group": j[2],
                    "policy": j[3],
                    "seed": j[4],
                    "survival_100": r["survival_100"],
                    "abundance": r["total_abundance"],
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "holdout_runs.csv", index=False)

    pa = bundle["config"]["policy_allocations"]
    psi_rows = []
    for d in designs:
        res = psi_index(bundle, pa["S7"], pa["S6"], d["overrides"])
        psi_rows.append(
            {
                "cell": d["cell"],
                "name": d["name"],
                "group": d["group"],
                "psi": res["psi"],
                "habitat_channel": res["habitat_channel"],
                "circulation_channel": res["circulation_channel"],
                "overrides": json.dumps(d["overrides"]),
            }
        )
    pd.DataFrame(psi_rows).to_csv(OUT / "holdout_psi.csv", index=False)
    return df


def stage_mechanism_ladder(bundle) -> None:
    """Minimal-model toggles: which mechanism moves the Psi boundary?"""
    pa = bundle["config"]["policy_allocations"]
    toggles = {
        "no_engagement": {"engagement_coefficient": 0.0, "engagement_habitat_feedback": 0.0},
        "no_exsitu": {"ex_situ_breeding_benefit": 0.0},
        "no_latent": {"latent_fraction_proxy": 0.0},
        "no_climate": {"climate_velocity": 0.0},
        "high_mate_limit": {"_min_breeding_pop": 20.0},
        "no_mate_limit": {"_min_breeding_pop": 0.0},
    }
    rows = []
    # psi over deterioration x relocation_mortality grid for each toggle
    for label, extra in [("base", {})] + list(toggles.items()):
        for det in np.linspace(0.0, 0.04, 9):
            for rm in np.linspace(0.0, 0.5, 9):
                ov = {
                    "habitat_deterioration": float(det),
                    "relocation_mortality": float(rm),
                    **extra,
                }
                r = psi_index(bundle, pa["S7"], pa["S6"], ov)
                rows.append({"toggle": label, "det": det, "rm": rm, "psi": r["psi"]})
    pd.DataFrame(rows).to_csv(OUT / "mechanism_ladder_psi.csv", index=False)


def main():
    t0 = time.time()
    bundle = load_config(ROOT)
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("all", "attribution"):
        stage_attribution()
    if stage in ("all", "holdout"):
        stage_holdout(bundle)
    if stage in ("all", "metrics"):
        stage_metrics(bundle)
    if stage in ("all", "ladder"):
        stage_mechanism_ladder(bundle)
    print(f"done in {time.time() - t0:.0f}s")


def stage_metrics(bundle) -> None:
    """Canonical metric computation: dev predictions, holdout signs,
    baselines B0/B1/B2, regrets, failure-region stats. Writes
    results/reversal/holdout_metrics.csv and
    results/reversal/manuscript_reversal_values.csv."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import balanced_accuracy_score

    pa = bundle["config"]["policy_allocations"]

    # --- dev predictions (x,y in stability CSV are raw parameter values)
    stab = pd.read_csv(ROOT / "results" / "threshold_cell_stability.csv")
    stab8 = stab[stab["n"] == 8].reset_index(drop=True)
    rows = []
    for r in stab8.itertuples():
        ov = {SWEEPS[r.sweep][0]: float(r.x), SWEEPS[r.sweep][2]: float(r.y)}
        res = psi_index(bundle, pa["S7"], pa["S6"], ov)
        rows.append(
            {
                "sweep": r.sweep,
                "x": r.x,
                "y": r.y,
                "sign": r.final_sign,
                "psi": res["psi"],
                "hab": res["habitat_channel"],
                "circ": res["circulation_channel"],
                "pred": np.sign(res["psi"]),
            }
        )
    dev = pd.DataFrame(rows)
    dev.to_csv(ROOT / "results" / "minimal_model_dev_predictions.csv", index=False)
    dev_det = dev[dev["sign"] != 0]
    dev_acc_all = float((dev.pred == dev["sign"]).mean())
    dev_acc_det = float((dev_det.pred == dev_det["sign"]).mean())

    # --- dev feature matrix for baseline fitting
    params = sorted({v[0] for v in SWEEPS.values()} | {v[2] for v in SWEEPS.values()})
    X_dev = np.zeros((len(stab8), len(params)))
    for i, r in enumerate(stab8.itertuples()):
        xp, (x0, x1), yp, (y0, y1) = SWEEPS[r.sweep]
        X_dev[i, params.index(xp)] = x0 + r.x * (x1 - x0) if abs(r.x) <= 1 else r.x
        # x,y are raw values; use them directly
        X_dev[i, params.index(xp)] = float(r.x)
        X_dev[i, params.index(yp)] = float(r.y)
    y_dev = stab8.final_sign.values

    # --- holdout cell means and signs
    runs = pd.read_csv(OUT / "holdout_runs.csv")
    psi = pd.read_csv(OUT / "holdout_psi.csv")
    piv = runs.pivot_table(
        index=["cell", "name", "group", "seed"],
        columns="policy",
        values="survival_100",
    ).reset_index()
    piv["diff"] = piv["S7"] - piv["S6"]
    cell = (
        piv.groupby(["cell", "name", "group"])
        .agg(
            mean_diff=("diff", "mean"),
            se=("diff", lambda s: float(s.std(ddof=1)) / np.sqrt(len(s))),
        )
        .reset_index()
    )
    cell["obs_sign"] = np.where(
        np.abs(cell["mean_diff"]) > 2 * cell["se"], np.sign(cell["mean_diff"]), 0
    )
    m = cell.merge(psi, on=["cell", "name", "group"], how="left")
    m["pred_sign"] = np.sign(m["psi"])

    # --- baselines
    Xh = np.zeros((len(m), len(params)))
    for i, d in enumerate(m["overrides"].apply(json.loads)):
        for k, v in d.items():
            if k in params:
                Xh[i, params.index(k)] = v
    OBS = m.obs_sign.values
    P = m.pred_sign.values
    # B1: best single-parameter threshold on dev
    best = (0.0, params[0], 0.0, 1)
    for j, pn in enumerate(params):
        vals = np.unique(np.abs(X_dev[:, j]))
        vals = vals[vals > 0]
        if len(vals) == 0:
            continue
        for tt in np.quantile(vals, [0.25, 0.5, 0.75]):
            for direc in (1, -1):
                pred = np.where(X_dev[:, j] >= tt, direc, -direc)
                a = float((pred == y_dev).mean())
                if a > best[0]:
                    best = (a, pn, float(tt), direc)
    _, b1_param, b1_thr, b1_dir = best
    pred_B1 = np.where(Xh[:, params.index(b1_param)] >= b1_thr, b1_dir, -b1_dir)
    # B2: L2 logistic on overrides
    lr = LogisticRegression(C=1.0, max_iter=5000).fit(X_dev, y_dev)
    pred_B2 = lr.predict(Xh)
    m["pred_B1"] = pred_B1
    m["pred_B2"] = pred_B2
    m.to_csv(OUT / "holdout_metrics.csv", index=False)

    # --- headline metrics
    det = m[m.obs_sign != 0]
    acc_all = float((P == OBS).mean())
    acc_det = float((det.pred_sign == det.obs_sign).mean())
    bacc3 = float(balanced_accuracy_score(OBS, P))
    tp = int(((det.pred_sign == 1) & (det.obs_sign == 1)).sum())
    fn = int(((det.pred_sign == -1) & (det.obs_sign == 1)).sum())
    tn = int(((det.pred_sign == -1) & (det.obs_sign == -1)).sum())
    fp = int(((det.pred_sign == 1) & (det.obs_sign == -1)).sum())
    sens = tp / (tp + fn) if tp + fn else float("nan")
    spec = tn / (tn + fp) if tn + fp else float("nan")

    cellS = piv.groupby("cell")[["S6", "S7"]].mean()
    best_v = cellS.max(axis=1)
    psi_map = m.set_index("cell").pred_sign.loc[cellS.index]
    picked = np.where(psi_map > 0, "S7", "S6")
    regret = float(np.mean([best_v[c] - cellS.loc[c, p] for c, p in zip(cellS.index, picked)]))
    regret_B0 = float((best_v - cellS["S6"]).mean())

    nb = m[np.abs(m.psi) < 0.2]
    nb_acc = float((nb.pred_sign == nb.obs_sign).mean()) if len(nb) else float("nan")
    tau01 = m[np.abs(m.psi) >= 0.1]
    tau01_det = tau01[tau01.obs_sign != 0]
    abst_acc = (
        float((tau01_det.pred_sign == tau01_det.obs_sign).mean())
        if len(tau01_det)
        else float("nan")
    )

    def acc(pred):
        return float((pred == OBS).mean())

    def bacc(pred):
        return float(balanced_accuracy_score(OBS, pred))

    rows_out = [
        ("dev_cells", len(dev), "development sweep cells at n=8"),
        ("dev_det_cells", len(dev_det), "development cells with nonzero robust sign"),
        ("dev_acc_all", dev_acc_all, "Psi sign accuracy, all dev cells"),
        ("dev_acc_det", dev_acc_det, "Psi sign accuracy, determinate dev cells"),
        ("holdout_cells", len(m), "held-out cells"),
        ("holdout_det_cells", int((OBS != 0).sum()), "held-out determinate cells"),
        ("holdout_s7_cells", int((OBS == 1).sum()), "held-out cells favouring S7"),
        ("holdout_s6_cells", int((OBS == -1).sum()), "held-out cells favouring S6"),
        ("holdout_ind_cells", int((OBS == 0).sum()), "held-out indeterminate cells"),
        ("psi_acc_all", acc_all, "Psi sign accuracy, all held-out cells"),
        ("psi_acc_det", acc_det, "Psi sign accuracy, determinate held-out cells"),
        ("psi_bacc3", bacc3, "Psi balanced accuracy, 3-class"),
        ("psi_sensitivity", sens, "Psi sensitivity for S7-favoured cells"),
        ("psi_specificity", spec, "Psi specificity for S6-favoured cells"),
        (
            "psi_bacc2",
            float((sens + spec) / 2),
            "Psi two-class balanced accuracy on determinate cells",
        ),
        ("regret_psi", regret, "decision regret of Psi's sign as policy pick"),
        ("regret_B0", regret_B0, "decision regret of always-S6 baseline"),
        ("B0_acc_all", acc([-1] * len(OBS)), "always-S6 sign accuracy"),
        ("B0_bacc", bacc([-1] * len(OBS)), "always-S6 balanced accuracy"),
        ("B1_param", b1_param, "B1 threshold parameter (dev-fitted)"),
        ("B1_threshold", b1_thr, "B1 threshold value (dev-fitted)"),
        ("B1_dev_acc", float(best[0]), "B1 sign accuracy on dev"),
        ("B1_acc_all", acc(pred_B1), "B1 sign accuracy, held-out"),
        ("B1_bacc", bacc(pred_B1), "B1 balanced accuracy, held-out"),
        ("B2_dev_acc", float((lr.predict(X_dev) == y_dev).mean()), "B2 sign accuracy on dev"),
        ("B2_acc_all", acc(pred_B2), "B2 sign accuracy, held-out"),
        ("B2_bacc", bacc(pred_B2), "B2 balanced accuracy, held-out"),
        ("near_boundary_cells", len(nb), "cells with |Psi| < 0.2"),
        ("near_boundary_acc", nb_acc, "Psi sign accuracy within |Psi| < 0.2"),
        ("abstain_tau01_cells", len(tau01), "cells covered by |Psi| >= 0.1 abstention"),
        ("abstain_tau01_acc_det", abst_acc, "determinate accuracy under |Psi| >= 0.1 abstention"),
    ]
    vals = pd.DataFrame(rows_out, columns=["value_id", "estimate", "definition"])
    vals.to_csv(OUT / "manuscript_reversal_values.csv", index=False)
    print(
        f"[metrics] dev acc {dev_acc_all:.3f} (det {dev_acc_det:.3f}); "
        f"holdout acc {acc_all:.3f} (det {acc_det:.3f}); regret {regret:.4f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
