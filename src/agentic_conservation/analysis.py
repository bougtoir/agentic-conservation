from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path

import numpy as np
import pandas as pd

from .simulation import POLICIES, load_project, run_simulation


@dataclass(frozen=True)
class RunSpec:
    root: str
    policy: str
    seed: int
    overrides: dict
    oracle: bool = False


def _execute(spec: RunSpec) -> dict:
    project = load_project(spec.root)
    result = run_simulation(
        project,
        spec.policy,
        spec.seed,
        overrides=spec.overrides,
        oracle=spec.oracle,
    )
    result["config_hash"] = hashlib.sha256(
        json.dumps(spec.overrides, sort_keys=True).encode()
    ).hexdigest()[:16]
    return result


def execute_specs(specs: list[RunSpec], workers: int = 2) -> pd.DataFrame:
    if workers <= 1:
        rows = [_execute(spec) for spec in specs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(_execute, specs, chunksize=max(1, len(specs) // (workers * 8))))
    return pd.DataFrame(rows)


def _half_width(values: pd.Series) -> float:
    clean = values.dropna().to_numpy(dtype=float)
    if len(clean) < 2:
        return math.inf
    return float(1.96 * np.std(clean, ddof=1) / np.sqrt(len(clean)))


def select_replications(pilot: pd.DataFrame, maximum: int = 256) -> pd.DataFrame:
    rows = []
    for policy, frame in pilot.groupby("policy"):
        for metric, target in {
            "survival_100": 0.035,
            "fraction_ebd": 0.06,
            "lifetime_welfare": max(1.0, frame["lifetime_welfare"].mean() * 0.035),
        }.items():
            sd = float(frame[metric].std(ddof=1))
            required = int(math.ceil((1.96 * sd / target) ** 2)) if sd > 0 else len(frame)
            rows.append(
                {
                    "policy": policy,
                    "metric": metric,
                    "pilot_n": len(frame),
                    "standard_deviation": sd,
                    "target_half_width": target,
                    "required_n": min(maximum, max(32, required)),
                }
            )
    return pd.DataFrame(rows)


def summarize_policy_outcomes(outcomes: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "survival_50",
        "survival_100",
        "species_retained_100",
        "wild_abundance",
        "fraction_ebd",
        "lifetime_welfare",
        "mean_individual_welfare",
        "founder_effective",
        "mean_inbreeding",
        "heterozygosity_proxy",
        "successful_reintroductions",
        "cost",
        "available_budget",
        "cost_per_species_retained",
        "engagement",
        "habitat_integrity",
        "future_option_value",
        "disease_prevalence",
        "relocation_burden",
        "quarantine_cost",
        "biobank_coverage",
        "welfare_burden_predation",
        "welfare_burden_food_insecurity",
        "welfare_burden_crowding",
        "welfare_burden_restriction",
        "welfare_burden_infection",
        "welfare_burden_habituation",
        "welfare_burden_relocation",
        "refuge_moves",
        "origin_returns",
        "total_abundance",
    ]
    rows = []
    for (policy, oracle), frame in outcomes.groupby(["policy", "oracle"]):
        for metric in metrics:
            values = frame[metric].dropna()
            rows.append(
                {
                    "policy": policy,
                    "oracle": oracle,
                    "metric": metric,
                    "estimate": float(values.mean()),
                    "lower": float(values.quantile(0.025)),
                    "upper": float(values.quantile(0.975)),
                    "mc_half_width": _half_width(values),
                    "n": len(values),
                }
            )
    return pd.DataFrame(rows)


def information_value(
    outcomes: pd.DataFrame, weights: dict[str, float]
) -> pd.DataFrame:
    s7 = outcomes[outcomes.policy == "S7"].copy()
    if not np.isclose(sum(weights.values()), 1.0):
        raise ValueError("Information-utility weights must sum to one")
    s7["decision_utility"] = (
        weights["survival_100"] * s7.survival_100
        + weights["future_option_value"] * s7.future_option_value
        + weights["habitat_integrity"] * s7.habitat_integrity
        + weights["ebd_avoidance"] * (1.0 - s7.fraction_ebd)
        + weights["mean_individual_welfare"] * s7.mean_individual_welfare
    )
    feasible = s7[~s7.oracle].set_index("seed")
    current_state = s7[s7.oracle].set_index("seed")
    paired = feasible.join(
        current_state,
        lsuffix="_feasible",
        rsuffix="_oracle",
        how="inner",
    )
    rows = []
    for metric in [
        "decision_utility",
        "survival_100",
        "future_option_value",
        "fraction_ebd",
    ]:
        difference = (
            paired[f"{metric}_oracle"] - paired[f"{metric}_feasible"]
        )
        rows.append(
            {
                "metric": metric,
                "estimate": float(difference.mean()),
                "lower": float(difference.quantile(0.025)),
                "upper": float(difference.quantile(0.975)),
                "mc_half_width": _half_width(difference),
                "n": len(difference),
            }
        )
    return pd.DataFrame(rows)


def information_weight_sensitivity(
    outcomes: pd.DataFrame, weight_sets: dict[str, dict[str, float]]
) -> pd.DataFrame:
    rows = []
    for scenario, weights in weight_sets.items():
        utility = information_value(outcomes, weights)
        decision_utility = utility[
            utility.metric == "decision_utility"
        ].iloc[0]
        rows.append(
            {
                "scenario": scenario,
                **weights,
                "estimate": decision_utility.estimate,
                "lower": decision_utility.lower,
                "upper": decision_utility.upper,
                "mc_half_width": decision_utility.mc_half_width,
                "n": decision_utility.n,
            }
        )
    return pd.DataFrame(rows)


PARETO_TOLERANCE = 1e-12
PARETO_OBJECTIVES = {
    "survival": "maximize",
    "welfare": "maximize",
    "genetics": "maximize",
    "ebd": "minimize",
    "cost": "minimize",
    "future_option": "maximize",
}


def pareto_flags(
    outcomes: pd.DataFrame,
    tolerance: float = PARETO_TOLERANCE,
) -> pd.DataFrame:
    summary = (
        outcomes[~outcomes.oracle]
        .groupby("policy", as_index=False)
        .agg(
            survival=("survival_100", "mean"),
            welfare=("mean_individual_welfare", "mean"),
            genetics=("founder_effective", "mean"),
            ebd=("fraction_ebd", "mean"),
            cost=("cost", "mean"),
            future_option=("future_option_value", "mean"),
        )
    )
    objectives = summary[["survival", "welfare", "genetics", "future_option"]].to_numpy()
    objectives = np.column_stack(
        [objectives, -summary["ebd"].to_numpy(), -summary["cost"].to_numpy()]
    )
    dominated = np.zeros(len(summary), dtype=bool)
    dominated_by: list[list[str]] = [[] for _ in range(len(summary))]
    for i in range(len(summary)):
        for j in range(len(summary)):
            if i == j:
                continue
            weakly_better = np.all(objectives[j] >= objectives[i] - tolerance)
            strictly_better = np.any(objectives[j] > objectives[i] + tolerance)
            if weakly_better and strictly_better:
                dominated[i] = True
                dominated_by[i].append(str(summary.loc[j, "policy"]))
    summary["pareto_efficient"] = ~dominated
    summary["dominated_by"] = [
        ";".join(policies) for policies in dominated_by
    ]
    summary["dominance_tolerance"] = tolerance
    return summary


def pareto_dominance_pairs(pareto: pd.DataFrame) -> pd.DataFrame:
    directions = {
        "survival": 1,
        "welfare": 1,
        "genetics": 1,
        "ebd": -1,
        "cost": -1,
        "future_option": 1,
    }
    rows = []
    indexed = pareto.set_index("policy")
    for dominated in pareto.itertuples():
        if not dominated.dominated_by:
            continue
        for dominator_policy in dominated.dominated_by.split(";"):
            dominator = indexed.loc[dominator_policy]
            row = {
                "dominated_policy": dominated.policy,
                "dominating_policy": dominator_policy,
                "tolerance": dominated.dominance_tolerance,
            }
            for metric, direction in directions.items():
                row[f"{metric}_advantage"] = direction * (
                    float(dominator[metric]) - float(getattr(dominated, metric))
                )
            rows.append(row)
    return pd.DataFrame(rows)


def write_pareto_verification(root: Path, pareto: pd.DataFrame) -> None:
    pairs = pareto_dominance_pairs(pareto)
    pairs.to_csv(root / "results/pareto_dominance.csv", index=False)
    objectives = "\n".join(
        f"- `{metric}`: {direction}"
        for metric, direction in PARETO_OBJECTIVES.items()
    )
    pair_lines = "\n".join(
        f"- {row.dominated_policy} is dominated by {row.dominating_policy}."
        for row in pairs.itertuples()
    )
    if not pair_lines:
        pair_lines = "- No dominance pairs."
    efficient = ", ".join(
        pareto.loc[pareto.pareto_efficient, "policy"].astype(str)
    )
    (root / "docs/pareto_verification.md").write_text(
        f"""# Six-objective Pareto verification

The production policy means are compared without a weighted overall score.
Objective directions are:

{objectives}

Dominance requires another policy to be no worse on all six objectives within
an absolute numerical tolerance of {PARETO_TOLERANCE:g}, and better by more
than that tolerance on at least one objective. This tolerance handles floating
point equality; it is not a claim that Monte Carlo uncertainty is zero.

The nondominated policies are {efficient}. Pairwise dominance records are:

{pair_lines}

`results/pareto_front.csv` stores the objective means, Pareto flag, dominators,
and tolerance. `results/pareto_dominance.csv` stores the nonnegative
direction-adjusted objective advantages for every dominance pair. The
manuscript policy-outcome table reports the same production means and
intervals; `results/manuscript_values.csv` stores each policy's Pareto
indicator and the nondominated count.
""",
        encoding="utf-8",
    )


def latin_hypercube(rng: np.random.Generator, n: int, dimensions: int) -> np.ndarray:
    samples = np.empty((n, dimensions))
    for column in range(dimensions):
        points = (np.arange(n) + rng.random(n)) / n
        rng.shuffle(points)
        samples[:, column] = points
    return samples


SENSITIVITY_RANGES = {
    "habitat_deterioration": (0.0, 0.025),
    "climate_velocity": (0.0, 0.05),
    "relocation_mortality": (0.0, 0.20),
    "relocation_stress": (0.0, 0.55),
    "ex_situ_breeding_benefit": (0.0, 0.55),
    "release_survival_penalty": (0.0, 0.30),
    "movement_disease_risk": (0.0, 0.40),
    "captivity_welfare_penalty": (0.0, 0.50),
    "survey_cost": (0.5, 60.0),
    "engagement_coefficient": (-0.12, 0.24),
    "initial_budget": (30.0, 220.0),
    "habitat_protection_efficiency": (0.005, 0.08),
}


def build_sensitivity_specs(
    root: Path, n: int, replicates: int = 1, seed: int = 20260924
) -> tuple[list[RunSpec], pd.DataFrame]:
    rng = np.random.default_rng(seed)
    names = list(SENSITIVITY_RANGES)
    lhs = latin_hypercube(rng, n, len(names))
    designs = []
    specs = []
    for row_id, values in enumerate(lhs):
        overrides = {}
        design = {"design_id": row_id}
        for name, unit in zip(names, values, strict=True):
            low, high = SENSITIVITY_RANGES[name]
            overrides[name] = low + unit * (high - low)
            design[name] = overrides[name]
        designs.append(design)
        for replicate in range(replicates):
            for policy in ["S4", "S6", "S7"]:
                specs.append(
                    RunSpec(
                        root=str(root),
                        policy=policy,
                        seed=800000 + row_id * 100 + replicate,
                        overrides=overrides,
                    )
                )
    return specs, pd.DataFrame(designs)


def sensitivity_audit(
    root: Path, outcomes: pd.DataFrame, design: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    merged = outcomes.merge(design, on="design_id", how="left")
    metrics = [
        "survival_100",
        "fraction_ebd",
        "mean_individual_welfare",
        "future_option_value",
    ]
    parameters = list(SENSITIVITY_RANGES)
    design_means = (
        merged.groupby(["policy", "design_id"], as_index=False)[metrics + parameters]
        .mean()
    )
    association_rows = []
    interaction_rows = []
    for policy, frame in design_means.groupby("policy"):
        for metric in metrics:
            for parameter in parameters:
                association_rows.append(
                    {
                        "policy": policy,
                        "metric": metric,
                        "parameter": parameter,
                        "spearman_rho": frame[[parameter, metric]]
                        .corr(method="spearman")
                        .iloc[0, 1],
                        "n_designs": len(frame),
                        "replicates_per_design": int(
                            merged[merged.policy == policy]
                            .groupby("design_id")
                            .size()
                            .min()
                        ),
                    }
                )
            ranked = frame[parameters + [metric]].rank(method="average")
            ranked = (ranked - ranked.mean()) / ranked.std(ddof=0)
            y = ranked[metric].to_numpy(dtype=float)
            for first, second in combinations(parameters, 2):
                x_first = ranked[first].to_numpy(dtype=float)
                x_second = ranked[second].to_numpy(dtype=float)
                main = np.column_stack([np.ones(len(frame)), x_first, x_second])
                y_residual = y - main @ np.linalg.lstsq(main, y, rcond=None)[0]
                interaction = x_first * x_second
                interaction_residual = interaction - main @ np.linalg.lstsq(
                    main, interaction, rcond=None
                )[0]
                denominator = np.linalg.norm(y_residual) * np.linalg.norm(
                    interaction_residual
                )
                score = (
                    float(np.dot(y_residual, interaction_residual) / denominator)
                    if denominator > 0
                    else np.nan
                )
                interaction_rows.append(
                    {
                        "policy": policy,
                        "metric": metric,
                        "parameter_1": first,
                        "parameter_2": second,
                        "partial_rank_interaction": score,
                        "n_designs": len(frame),
                    }
                )
    associations = pd.DataFrame(association_rows)
    interactions = pd.DataFrame(interaction_rows)
    associations.to_csv(root / "results/sensitivity_associations.csv", index=False)
    interactions.to_csv(root / "results/sensitivity_interactions.csv", index=False)

    range_lines = "\n".join(
        f"- `{name}`: uniform Latin-hypercube range [{low:g}, {high:g}]"
        for name, (low, high) in SENSITIVITY_RANGES.items()
    )
    strongest = interactions.assign(
        absolute=lambda frame: frame.partial_rank_interaction.abs()
    ).nlargest(12, "absolute")
    interaction_lines = "\n".join(
        f"- {row.policy} {row.metric}: `{row.parameter_1}` × "
        f"`{row.parameter_2}` = {row.partial_rank_interaction:.3f}"
        for row in strongest.itertuples()
    )
    n_designs = int(design.design_id.nunique())
    n_replicates = int(associations.replicates_per_design.min())
    (root / "docs/global_sensitivity_audit.md").write_text(
        f"""# Global sensitivity audit

The production design uses {n_designs} stratified Latin-hypercube points and
{n_replicates} stochastic replicates per point for S4, S6, and S7. Replicates
are averaged before association analysis, preventing a repeated parameter row
from being treated as an independent design.

Main effects are descriptive Spearman rank associations. Pairwise interactions
are descriptive partial rank associations between the outcome residual and
the product of two rank-standardized inputs after removing their two main
effects. They are screening statistics, not causal effects or significance
tests. Morris screening was not added because it would require a separate
trajectory design while providing less direct information about the requested
pairwise interactions.

## Registered ranges

{range_lines}

## Strongest absolute interaction screens

{interaction_lines}

Complete main-effect and interaction results are stored in
`results/sensitivity_associations.csv` and
`results/sensitivity_interactions.csv`.
"""
    )
    return associations, interactions


def threshold_stability_audit(root: Path, sweeps: pd.DataFrame) -> pd.DataFrame:
    paired = (
        sweeps[sweeps.policy.isin(["S6", "S7"])]
        .pivot_table(
            index=["sweep", "x", "y", "seed"],
            columns="policy",
            values="survival_100",
        )
        .dropna()
        .reset_index()
    )
    paired["difference"] = paired.S7 - paired.S6
    maximum = int(paired.groupby(["sweep", "x", "y"]).size().min())
    prefixes = sorted({maximum, max(2, maximum // 2), max(2, maximum // 4)})
    rows = []
    for keys, frame in paired.groupby(["sweep", "x", "y"]):
        ordered = frame.sort_values("seed")
        final_mean = float(ordered.difference.iloc[:maximum].mean())
        final_sign = int(np.sign(final_mean)) if not np.isclose(final_mean, 0.0) else 0
        for n in prefixes:
            values = ordered.difference.iloc[:n]
            estimate = float(values.mean())
            sign = int(np.sign(estimate)) if not np.isclose(estimate, 0.0) else 0
            rows.append(
                {
                    "sweep": keys[0],
                    "x": keys[1],
                    "y": keys[2],
                    "n": n,
                    "estimate": estimate,
                    "mcse": (
                        float(values.std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan
                    ),
                    "sign": sign,
                    "final_sign": final_sign,
                    "sign_stable": sign == final_sign,
                }
            )
    cells = pd.DataFrame(rows)
    final = cells[cells.n == maximum]
    half = cells[cells.n == max(2, maximum // 2)]
    half_stability = half.set_index(["sweep", "x", "y"])["sign_stable"]
    cells["stable_from_half_n"] = cells.set_index(
        ["sweep", "x", "y"]
    ).index.map(half_stability)
    cells["robust_direction"] = 0
    final_mask = cells.n == maximum
    cells.loc[final_mask, "robust_direction"] = np.where(
        cells.loc[final_mask, "stable_from_half_n"]
        & (
            cells.loc[final_mask, "estimate"].abs()
            > 1.96 * cells.loc[final_mask, "mcse"]
        ),
        cells.loc[final_mask, "sign"],
        0,
    )
    cells.to_csv(root / "results/threshold_cell_stability.csv", index=False)
    final = cells[cells.n == maximum]
    summary_rows = []
    for sweep, frame in final.groupby("sweep"):
        half_frame = half[half.sweep == sweep]
        summary_rows.append(
            {
                "sweep": sweep,
                "cells": len(frame),
                "s7_higher": int((frame.sign > 0).sum()),
                "s6_higher": int((frame.sign < 0).sum()),
                "ties": int((frame.sign == 0).sum()),
                "sign_stable_at_half_n": int(half_frame.sign_stable.sum()),
                "robust_s7_higher": int((frame.robust_direction > 0).sum()),
                "robust_s6_higher": int((frame.robust_direction < 0).sum()),
                "indeterminate": int((frame.robust_direction == 0).sum()),
                "half_n": max(2, maximum // 2),
                "final_n": maximum,
                "median_absolute_contrast": float(frame.estimate.abs().median()),
                "mean_mcse": float(frame.mcse.mean()),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(root / "results/threshold_sweep_audit.csv", index=False)
    lines = "\n".join(
        f"- `{row.sweep}`: robust S7-higher cells "
        f"{row.robust_s7_higher}/{row.cells}, robust S6-higher cells "
        f"{row.robust_s6_higher}/{row.cells}, indeterminate cells "
        f"{row.indeterminate}/{row.cells}; {row.sign_stable_at_half_n}/"
        f"{row.cells} raw signs stable from N={row.half_n} to N={row.final_n}."
        for row in summary.itertuples()
    )
    (root / "docs/threshold_stability_audit.md").write_text(
        f"""# Two-factor threshold stability audit

All five prespecified sweeps use paired process-keyed seeds for S6 and S7.
Cell means and Monte Carlo standard errors are evaluated at nested replicate
prefixes {", ".join(str(value) for value in prefixes)}. A direction is called
robust only when its sign is unchanged from N={max(2, maximum // 2)} to
N={maximum} and its absolute paired mean exceeds 1.96 Monte Carlo standard
errors. Other cells are classified as indeterminate rather than used to count
policy reversals.

{lines}

Cell-level estimates and sign checks are stored in
`results/threshold_cell_stability.csv`; sweep summaries are stored in
`results/threshold_sweep_audit.csv`.
"""
    )
    return summary


SWEEPS = {
    "deterioration_relocation": (
        "habitat_deterioration",
        (0.0, 0.025),
        "relocation_stress",
        (0.0, 0.60),
    ),
    "latent_survey": ("latent_fraction_proxy", (0.0, 0.60), "survey_cost", (0.5, 60.0)),
    "climate_assisted_risk": (
        "climate_velocity",
        (0.0, 0.05),
        "relocation_mortality",
        (0.0, 0.25),
    ),
    "captivity_breeding": (
        "captivity_welfare_penalty",
        (0.0, 0.55),
        "ex_situ_breeding_benefit",
        (0.0, 0.60),
    ),
    "engagement_habitat": (
        "engagement_coefficient",
        (-0.15, 0.25),
        "habitat_protection_efficiency",
        (0.005, 0.08),
    ),
}


def build_sweep_specs(root: Path, grid: int, replicates: int) -> tuple[list[RunSpec], pd.DataFrame]:
    specs = []
    design_rows = []
    design_id = 0
    for sweep, (x_name, x_range, y_name, y_range) in SWEEPS.items():
        for x, y in product(np.linspace(*x_range, grid), np.linspace(*y_range, grid)):
            overrides = {}
            latent_fraction = None
            if x_name == "latent_fraction_proxy":
                latent_fraction = float(x)
                overrides[x_name] = float(x)
            else:
                overrides[x_name] = float(x)
            overrides[y_name] = float(y)
            design_rows.append(
                {
                    "design_id": design_id,
                    "sweep": sweep,
                    "x_name": x_name,
                    "x": x,
                    "y_name": y_name,
                    "y": y,
                    "latent_fraction_proxy": latent_fraction,
                }
            )
            for replicate in range(replicates):
                for policy in ["S4", "S6", "S7"]:
                    specs.append(
                        RunSpec(
                            root=str(root),
                            policy=policy,
                            seed=900000 + design_id * 100 + replicate,
                            overrides=overrides,
                        )
                    )
            design_id += 1
    return specs, pd.DataFrame(design_rows)


ABLATIONS = {
    "human_feedback": {
        "engagement_coefficient": 0.0,
        "engagement_habitat_feedback": 0.0,
    },
    "latent_species": {"latent_fraction_proxy": 0.0},
    "genetics": {"genetics_enabled": False},
    "climate": {"climate_velocity": 0.0},
    "biobank": {"biobank_enabled": False},
    "disease": {"disease_enabled": False},
    "welfare": {"welfare_enabled": False},
    "partial_observability": {"observation_noise": 0.0, "quality_observation_noise": 0.0},
    "origin_fidelity": {"origin_fidelity": 0.0},
}


ADVERSE = {
    "excellent_origin": {
        "scenario": "stationary",
        "habitat_deterioration": 0.0,
        "catastrophe_probability": 0.0,
    },
    "high_relocation_harm": {
        "relocation_mortality": 0.25,
        "relocation_stress": 0.65,
        "movement_disease_risk": 0.65,
    },
    "zero_breeding_advantage": {"ex_situ_breeding_benefit": 0.0},
    "high_captivity_penalty": {"captivity_welfare_penalty": 0.70},
    "efficient_restoration": {"habitat_protection_efficiency": 0.12},
    "negative_engagement": {"engagement_coefficient": -0.18},
}


def build_named_specs(
    root: Path, designs: dict[str, dict], replicates: int, seed_offset: int
) -> tuple[list[RunSpec], pd.DataFrame]:
    specs = []
    rows = []
    for design_id, (name, overrides) in enumerate(designs.items()):
        rows.append({"design_id": design_id, "name": name, "overrides": json.dumps(overrides)})
        for replicate in range(replicates):
            for policy in ["S4", "S6", "S7"]:
                specs.append(
                    RunSpec(
                        root=str(root),
                        policy=policy,
                        seed=seed_offset + design_id * 100 + replicate,
                        overrides=overrides,
                    )
                )
    return specs, pd.DataFrame(rows)


def manuscript_values(
    summary: pd.DataFrame, root: Path, information: pd.DataFrame
) -> pd.DataFrame:
    unit_map = {
        "survival_50": "proportion",
        "survival_100": "proportion",
        "species_retained_100": "species",
        "wild_abundance": "individuals",
        "fraction_ebd": "proportion",
        "lifetime_welfare": "welfare-person-years_per_year",
        "mean_individual_welfare": "mean_welfare_index",
        "founder_effective": "effective_founders",
        "mean_inbreeding": "proportion",
        "heterozygosity_proxy": "proportion",
        "successful_reintroductions": "individual_movements",
        "cost": "budget_units",
        "available_budget": "budget_units",
        "cost_per_species_retained": "budget_units_per_species",
        "engagement": "index",
        "habitat_integrity": "index",
        "future_option_value": "index",
        "disease_prevalence": "proportion",
        "relocation_burden": "stress-weighted_movements",
        "quarantine_cost": "budget_units",
        "biobank_coverage": "proportion",
        "welfare_burden_predation": "mean_welfare_burden",
        "welfare_burden_food_insecurity": "mean_welfare_burden",
        "welfare_burden_crowding": "mean_welfare_burden",
        "welfare_burden_restriction": "mean_welfare_burden",
        "welfare_burden_infection": "mean_welfare_burden",
        "welfare_burden_habituation": "mean_welfare_burden",
        "welfare_burden_relocation": "mean_welfare_burden",
        "refuge_moves": "individual_movements",
        "origin_returns": "individual_movements",
        "total_abundance": "individuals",
    }
    values = summary.copy()
    values["value_id"] = [
        f"{row.policy.lower()}_{row.metric}{'_oracle' if row.oracle else ''}"
        for row in values.itertuples()
    ]
    values["analysis"] = "paired_monte_carlo"
    values["unit"] = values.metric.map(unit_map)
    values["source_file"] = "results/policy_outcomes.csv"
    values["source_code"] = "src/agentic_conservation/analysis.py"
    values["seed/config"] = "seeds listed in policy_outcomes.csv; config/base.json"
    values = values[
        [
            "value_id",
            "analysis",
            "estimate",
            "lower",
            "upper",
            "unit",
            "source_file",
            "source_code",
            "seed/config",
        ]
    ]
    information_values = pd.DataFrame(
        {
            "value_id": "current_state_information_" + information.metric,
            "analysis": "paired_current_state_information",
            "estimate": information.estimate,
            "lower": information.lower,
            "upper": information.upper,
            "unit": np.where(
                information.metric == "decision_utility", "weighted_utility_index", "proportion"
            ),
            "source_file": "results/information_value.csv",
            "source_code": "src/agentic_conservation/analysis.py",
            "seed/config": "paired S7 keyed streams; no hindsight action retention",
        }
    )
    values = pd.concat([values, information_values], ignore_index=True)
    values.to_csv(root / "results/manuscript_values.csv", index=False)
    return values


def _final_output_paths(root: Path) -> list[Path]:
    paths = []
    for relative in [
        "data/processed",
        "docs",
        "figures",
        "manuscript",
        "results",
        "submission",
        "tables",
    ]:
        paths.extend(path for path in (root / relative).rglob("*") if path.is_file())
    for relative in [
        "BLOCKED_ITEMS.md",
        "FINAL_REPORT.md",
        "FINAL_SUBMISSION_READINESS.md",
        "provenance/consequential_choices.md",
        "provenance/hard_code_audit.md",
        "provenance/source_ledger.csv",
        "provenance/vm_environment.txt",
    ]:
        paths.append(root / relative)
    return paths


def write_run_manifest(
    root: Path,
    mode: str,
    counts: dict,
    files: list[Path] | None = None,
) -> None:
    files = _final_output_paths(root) if files is None else files
    output_hashes = {}
    for path in files:
        if path.exists():
            output_hashes[str(path.relative_to(root))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    input_paths = sorted((root / "config").glob("*.json"))
    input_paths.extend(sorted((root / "scripts").glob("*.py")))
    input_paths.extend(sorted((root / "src/agentic_conservation").glob("*.py")))
    input_paths.extend(sorted((root / "tests").glob("*.py")))
    input_paths.extend(
        sorted(path for path in (root / "data/raw").rglob("*") if path.is_file())
    )
    input_paths.extend(
        [
            root / "Makefile",
            root / "pyproject.toml",
            root / "requirements.txt",
            root / "requirements-dev.txt",
        ]
    )
    input_hashes = {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in input_paths
    }
    git_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    manifest = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "git_commit": git_commit,
        "python": sys.version,
        "platform": platform.platform(),
        "counts": counts,
        "input_sha256": input_hashes,
        "output_sha256": output_hashes,
    }
    (root / "provenance/run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )


def run_pipeline(root: Path, mode: str) -> None:
    root = root.resolve()
    (root / "results/checkpoints").mkdir(parents=True, exist_ok=True)
    (root / "provenance").mkdir(parents=True, exist_ok=True)
    workers = 2
    configured_analyses = json.loads((root / "config/analysis.json").read_text())
    analysis_config = configured_analyses[mode]
    information_weights = configured_analyses["information_utility_weights"]
    pilot_n = int(analysis_config["pilot_replications"])
    pilot_specs = [
        RunSpec(str(root), policy, 100000 + seed, {})
        for seed in range(pilot_n)
        for policy in POLICIES
    ]
    pilot = execute_specs(pilot_specs, workers)
    convergence = select_replications(pilot)
    convergence.to_csv(root / "results/convergence.csv", index=False)
    selected = int(analysis_config["policy_replications"])

    policy_specs = [
        RunSpec(str(root), policy, 200000 + seed, {})
        for seed in range(selected)
        for policy in POLICIES
    ]
    oracle_specs = [
        RunSpec(str(root), "S7", 200000 + seed, {}, oracle=True) for seed in range(selected)
    ]
    outcomes = execute_specs(policy_specs + oracle_specs, workers)
    outcomes.to_csv(root / "results/policy_outcomes.csv", index=False)
    summary = summarize_policy_outcomes(outcomes)
    summary.to_csv(root / "results/policy_summary.csv", index=False)
    information = information_value(outcomes, information_weights)
    information.to_csv(root / "results/information_value.csv", index=False)
    information_weight_sensitivity(
        outcomes, configured_analyses["information_weight_scenarios"]
    ).to_csv(root / "results/information_weight_sensitivity.csv", index=False)
    pareto = pareto_flags(outcomes)
    pareto.to_csv(root / "results/pareto_front.csv", index=False)
    write_pareto_verification(root, pareto)
    manuscript_values(summary, root, information)

    trajectory_rows = []
    project = load_project(root)
    for policy in POLICIES:
        result = run_simulation(project, policy, 314159, return_trajectory=True)
        trajectory_rows.extend(result["trajectory"])
    pd.DataFrame(trajectory_rows).to_csv(root / "results/trajectories.csv", index=False)

    sensitivity_n = int(analysis_config["sensitivity_designs"])
    sensitivity_reps = int(analysis_config["sensitivity_replicates"])
    sensitivity_specs, sensitivity_design = build_sensitivity_specs(
        root, sensitivity_n, sensitivity_reps
    )
    sensitivity = execute_specs(sensitivity_specs, workers)
    sensitivity["design_id"] = np.repeat(
        sensitivity_design.design_id.to_numpy(), sensitivity_reps * 3
    )
    sensitivity.to_csv(root / "results/sensitivity_outcomes.csv", index=False)
    sensitivity_design.to_csv(root / "results/sensitivity_design.csv", index=False)
    sensitivity_audit(root, sensitivity, sensitivity_design)

    grid = int(analysis_config["sweep_grid_points"])
    sweep_reps = int(analysis_config["sweep_replicates"])
    sweep_specs, sweep_design = build_sweep_specs(root, grid, sweep_reps)
    sweeps = execute_specs(sweep_specs, workers)
    repetitions_per_design = sweep_reps * 3
    sweeps["design_id"] = np.repeat(
        sweep_design.design_id.to_numpy(), repetitions_per_design
    )
    sweeps = sweeps.merge(sweep_design, on="design_id", how="left")
    sweeps.to_csv(root / "results/threshold_sweeps.csv", index=False)
    threshold_stability_audit(root, sweeps)

    named_reps = int(analysis_config["named_design_replicates"])
    ablation_specs, ablation_design = build_named_specs(root, ABLATIONS, named_reps, 600000)
    ablations = execute_specs(ablation_specs, workers)
    ablations["design_id"] = np.repeat(
        ablation_design.design_id.to_numpy(), named_reps * 3
    )
    ablations = ablations.merge(ablation_design, on="design_id", how="left")
    ablations.to_csv(root / "results/ablations.csv", index=False)

    adverse_specs, adverse_design = build_named_specs(root, ADVERSE, named_reps, 700000)
    adverse = execute_specs(adverse_specs, workers)
    adverse["design_id"] = np.repeat(adverse_design.design_id.to_numpy(), named_reps * 3)
    adverse = adverse.merge(adverse_design, on="design_id", how="left")
    adverse.to_csv(root / "results/adverse_conditions.csv", index=False)

    checkpoint = {
        "mode": mode,
        "selected_replications": selected,
        "completed": True,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    (root / "results/checkpoints/pipeline.json").write_text(
        json.dumps(checkpoint, indent=2) + "\n"
    )
    files = [
        root / "results/policy_outcomes.csv",
        root / "results/policy_summary.csv",
        root / "results/information_value.csv",
        root / "results/pareto_front.csv",
        root / "results/manuscript_values.csv",
        root / "results/sensitivity_outcomes.csv",
        root / "results/sensitivity_associations.csv",
        root / "results/sensitivity_interactions.csv",
        root / "results/threshold_sweeps.csv",
        root / "results/threshold_cell_stability.csv",
        root / "results/threshold_sweep_audit.csv",
        root / "results/ablations.csv",
        root / "results/adverse_conditions.csv",
    ]
    write_run_manifest(
        root,
        mode,
        {
            "pilot_replications_per_policy": pilot_n,
            "selected_replications_per_policy": selected,
            "sensitivity_designs": sensitivity_n,
            "sensitivity_replications": sensitivity_reps,
            "sweep_grid": grid,
            "sweep_replications": sweep_reps,
            "ablation_replications": named_reps,
        },
        files,
    )
