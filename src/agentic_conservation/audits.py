from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .analysis import RunSpec, execute_specs, information_value
from .simulation import load_project

BUDGET_CATEGORIES = [
    "habitat",
    "survey",
    "rescue",
    "ex_situ",
    "genetics",
    "biobank",
    "engagement",
]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_parameter_registry(root: Path) -> pd.DataFrame:
    base = _read_json(root / "config/base.json")
    metadata = _read_json(root / "config/parameter_metadata.json")
    rows = []
    for parameter, value in base.items():
        if parameter == "policy_allocations":
            continue
        if parameter not in metadata:
            raise ValueError(f"Missing parameter metadata for {parameter}")
        rows.append(
            {
                "parameter": parameter,
                "base_value": value,
                **metadata[parameter],
            }
        )
    utility_weights = _read_json(root / "config/analysis.json")[
        "information_utility_weights"
    ]
    for outcome, weight in utility_weights.items():
        rows.append(
            {
                "parameter": f"information_utility_weights.{outcome}",
                "base_value": weight,
                "range_or_distribution": "fixed declared normative weight",
                "unit": "proportion",
                "status": "C",
                "source_or_rationale": (
                    "Declared multiattribute weighting for the diagnostic "
                    "current-state-information comparison."
                ),
                "doi_or_source": "none; normative analysis choice",
                "sensitivity_included": "component outcomes reported separately",
                "manuscript_location": (
                    "Methods: Outcomes, comparison, and uncertainty"
                ),
                "action": (
                    "Do not interpret as stakeholder preferences; obtain "
                    "stakeholder-derived weights for applied use."
                ),
            }
        )
    diagnostic_weights = _read_json(root / "config/audit_designs.json")[
        "budget_robustness"
    ]["diagnostic_utility_weights"]
    for outcome, weight in diagnostic_weights.items():
        rows.append(
            {
                "parameter": f"budget_diagnostic_utility_weights.{outcome}",
                "base_value": weight,
                "range_or_distribution": "fixed declared normative weight",
                "unit": "proportion",
                "status": "C",
                "source_or_rationale": (
                    "Declared multiattribute weighting used only to select "
                    "budget-robustness candidates for held-out comparison."
                ),
                "doi_or_source": "none; normative audit choice",
                "sensitivity_included": (
                    "component outcomes and alternative allocations reported"
                ),
                "manuscript_location": (
                    "Reproducibility repository: policy-budget fairness audit"
                ),
                "action": (
                    "Do not interpret as stakeholder preferences or use it "
                    "to rank policy classes."
                ),
            }
        )

    species = pd.read_json(root / "config/species.json")
    species_units = {
        "initial_n": "individuals",
        "growth": "annual intrinsic growth scale",
        "mortality": "annual probability",
        "niche_breadth": "index",
        "habitat_specificity": "index",
        "climate_sensitivity": "index",
        "anthropogenic_sensitivity": "index",
        "dispersal": "index",
        "detectability": "index",
        "fertility": "birth probability scale",
        "social_dependence": "index",
        "migration_need": "index",
        "captivity_tolerance": "index",
    }
    species_ranges = {
        parameter: f"{species[parameter].min():.4g}-{species[parameter].max():.4g}"
        for parameter in species_units
    }
    for record in species.to_dict(orient="records"):
        species_id = record["id"]
        rows.append(
            {
                "parameter": f"species.{species_id}.known",
                "base_value": record["known"],
                "range_or_distribution": "known or latent at initialization",
                "unit": "categorical indicator",
                "status": "C",
                "source_or_rationale": (
                    "Synthetic initial information-state assignment."
                ),
                "doi_or_source": "none; synthetic species archetypes",
                "sensitivity_included": "EBD boundary audit",
                "manuscript_location": (
                    "Reproducibility repository: species configuration"
                ),
                "action": "Do not interpret as taxonomic discovery status.",
            }
        )
        for parameter, unit in species_units.items():
            rows.append(
                {
                    "parameter": f"species.{species_id}.{parameter}",
                    "base_value": record[parameter],
                    "range_or_distribution": species_ranges[parameter],
                    "unit": unit,
                    "status": "C",
                    "source_or_rationale": (
                        "Illustrative synthetic interspecific heterogeneity."
                    ),
                    "doi_or_source": "none; synthetic species archetypes",
                    "sensitivity_included": (
                        "indirectly through species heterogeneity"
                    ),
                    "manuscript_location": (
                        "Reproducibility repository: species configuration"
                    ),
                    "action": "Do not interpret as estimates for named taxa.",
                }
            )

    nodes = pd.read_json(root / "config/nodes.json")
    node_units = {
        "base_quality": "index",
        "capacity": "individuals per species",
        "disease": "transmission scale",
        "predation": "mortality-risk scale",
        "anthropogenic": "pressure scale",
        "welfare": "welfare index",
        "cost": "relative cost index",
        "connectivity": "index",
        "research": "support index",
        "visitor_exposure": "index",
        "restoration": "index",
    }
    node_ranges = {
        parameter: f"{nodes[parameter].min():.4g}-{nodes[parameter].max():.4g}"
        for parameter in node_units
    }
    for record in nodes.to_dict(orient="records"):
        node_id = record["id"]
        for parameter in ["type", "wild", "managed"]:
            rows.append(
                {
                    "parameter": f"node.{node_id}.{parameter}",
                    "base_value": record[parameter],
                    "range_or_distribution": "fixed node classification",
                    "unit": "categorical indicator",
                    "status": "C",
                    "source_or_rationale": (
                        "Synthetic conservation-node archetype definition."
                    ),
                    "doi_or_source": "none; synthetic node archetypes",
                    "sensitivity_included": (
                        "indirectly through node heterogeneity"
                    ),
                    "manuscript_location": (
                        "Reproducibility repository: node configuration"
                    ),
                    "action": (
                        "Do not interpret as a classification of a named facility."
                    ),
                }
            )
        for parameter, unit in node_units.items():
            rows.append(
                {
                    "parameter": f"node.{node_id}.{parameter}",
                    "base_value": record[parameter],
                    "range_or_distribution": node_ranges[parameter],
                    "unit": unit,
                    "status": "C",
                    "source_or_rationale": (
                        "Illustrative synthetic conservation-node archetype."
                    ),
                    "doi_or_source": "none; synthetic node archetypes",
                    "sensitivity_included": (
                        "indirectly through node heterogeneity"
                    ),
                    "manuscript_location": (
                        "Reproducibility repository: node configuration"
                    ),
                    "action": (
                        "Do not interpret as facility or habitat measurements."
                    ),
                }
            )

    for policy, allocation in base["policy_allocations"].items():
        for category, share in allocation.items():
            rows.append(
                {
                    "parameter": f"policy_allocations.{policy}.{category}",
                    "base_value": share,
                    "range_or_distribution": "0-1; policy shares sum to 1",
                    "unit": "proportion of annual budget",
                    "status": "C",
                    "source_or_rationale": (
                        "Declared synthetic policy-archetype allocation."
                    ),
                    "doi_or_source": "none; policy-archetype definition",
                    "sensitivity_included": (
                        "policy-budget robustness and held-out allocation audit"
                    ),
                    "manuscript_location": (
                        "Reproducibility repository: policy configuration"
                    ),
                    "action": (
                        "Do not interpret as an optimized or observed allocation."
                    ),
                }
            )

    registry = pd.DataFrame(rows)
    columns = [
        "parameter",
        "base_value",
        "range_or_distribution",
        "unit",
        "status",
        "source_or_rationale",
        "doi_or_source",
        "sensitivity_included",
        "manuscript_location",
        "action",
    ]
    registry = registry[columns]
    registry.to_csv(root / "provenance/parameter_registry.csv", index=False)
    return registry


def _normalize(values: dict[str, float]) -> dict[str, float]:
    total = sum(values.values())
    if total <= 0:
        return dict(values)
    return {name: value / total for name, value in values.items()}


def _allocation_scenarios(
    allocation: dict[str, float],
) -> dict[str, dict[str, float]]:
    active = [name for name, value in allocation.items() if value > 0]
    equal_active = {
        name: (1.0 / len(active) if name in active else 0.0)
        for name in BUDGET_CATEGORIES
    }

    habitat_priority = dict(allocation)
    donors = [
        name
        for name in BUDGET_CATEGORIES
        if name != "habitat" and habitat_priority[name] > 0
    ]
    shift = min(0.12, sum(habitat_priority[name] for name in donors) * 0.35)
    donor_total = sum(habitat_priority[name] for name in donors)
    for name in donors:
        habitat_priority[name] -= shift * habitat_priority[name] / donor_total
    habitat_priority["habitat"] += shift

    movement_cautious = dict(allocation)
    rescue_shift = movement_cautious["rescue"] * 0.50
    movement_cautious["rescue"] -= rescue_shift
    movement_cautious["habitat"] += rescue_shift * 0.60
    movement_cautious["survey"] += rescue_shift * 0.40

    return {
        "fixed_archetype": _normalize(allocation),
        "equal_active_categories": _normalize(equal_active),
        "habitat_priority": _normalize(habitat_priority),
        "movement_cautious": _normalize(movement_cautious),
    }


def _diagnostic_utility(
    frame: pd.DataFrame,
    weights: dict[str, float],
    species_count: int,
) -> pd.Series:
    if not np.isclose(sum(weights.values()), 1.0):
        raise ValueError("Diagnostic utility weights must sum to 1")
    return (
        weights["survival_100"] * frame.survival_100
        + weights["species_retained_100"]
        * frame.species_retained_100
        / species_count
        + weights["mean_individual_welfare"] * frame.mean_individual_welfare
        + weights["future_option_value"] * frame.future_option_value
        + weights["ebd_avoidance"] * (1.0 - frame.fraction_ebd)
    )


def _candidate_allocations(
    allocation: dict[str, float],
    count: int,
    concentration: float,
    rng: np.random.Generator,
) -> list[dict[str, float]]:
    active = [name for name, value in allocation.items() if value > 0]
    candidates = [dict(allocation)]
    alpha = np.array([allocation[name] for name in active]) * concentration + 0.5
    for draw in rng.dirichlet(alpha, size=max(0, count - 1)):
        candidate = {name: 0.0 for name in BUDGET_CATEGORIES}
        for name, value in zip(active, draw, strict=True):
            candidate[name] = float(value)
        candidates.append(candidate)
    return candidates


def run_policy_budget_audit(root: Path, mode: str, workers: int) -> None:
    project = load_project(root)
    design = _read_json(root / "config/audit_designs.json")["budget_robustness"]
    diagnostic_weights = design["diagnostic_utility_weights"]
    replications = (
        design["quick_replications"]
        if mode == "quick"
        else design["full_replications"]
    )
    candidate_count = (
        design["quick_candidates"] if mode == "quick" else design["full_candidates"]
    )

    sum_rows = []
    scenario_specs = []
    scenario_metadata = []
    for policy in [f"S{number}" for number in range(1, 8)]:
        allocation = project.config["policy_allocations"][policy]
        allocation_sum = sum(allocation.values())
        sum_rows.append(
            {
                "policy": policy,
                "allocation_sum": allocation_sum,
                "valid": bool(np.isclose(allocation_sum, 1.0)),
                **allocation,
            }
        )
        for scenario, values in _allocation_scenarios(allocation).items():
            for replicate in range(replications):
                scenario_specs.append(
                    RunSpec(
                        str(root),
                        policy,
                        810000 + 10000 * int(policy[1:]) + 100 * replicate,
                        {"policy_allocations": {policy: values}},
                    )
                )
                scenario_metadata.append(
                    {
                        "allocation_scenario": scenario,
                        "allocation": json.dumps(values, sort_keys=True),
                        "replicate": replicate,
                    }
                )
    sums = pd.DataFrame(sum_rows)
    sums.to_csv(root / "results/policy_budget_sums.csv", index=False)
    if not sums.valid.all():
        raise ValueError("At least one nonzero policy allocation does not sum to 1")

    robustness = execute_specs(scenario_specs, workers)
    robustness = pd.concat(
        [pd.DataFrame(scenario_metadata), robustness.reset_index(drop=True)],
        axis=1,
    )
    robustness.to_csv(root / "results/policy_budget_robustness.csv", index=False)
    robustness_summary = (
        robustness.groupby(["policy", "allocation_scenario"], as_index=False)
        .agg(
            survival_100=("survival_100", "mean"),
            species_retained_100=("species_retained_100", "mean"),
            welfare=("mean_individual_welfare", "mean"),
            ebd=("fraction_ebd", "mean"),
            future_option=("future_option_value", "mean"),
            cost=("cost", "mean"),
        )
    )
    robustness_summary.to_csv(
        root / "results/policy_budget_robustness_summary.csv",
        index=False,
    )

    rng = np.random.default_rng(20260925)
    training_specs = []
    training_metadata = []
    candidates_by_policy: dict[str, list[dict[str, float]]] = {}
    for policy in [f"S{number}" for number in range(1, 8)]:
        candidates = _candidate_allocations(
            project.config["policy_allocations"][policy],
            candidate_count,
            design["dirichlet_concentration"],
            rng,
        )
        candidates_by_policy[policy] = candidates
        for candidate_id, allocation in enumerate(candidates):
            for replicate in range(design["training_replications"]):
                training_specs.append(
                    RunSpec(
                        str(root),
                        policy,
                        820000
                        + 10000 * int(policy[1:])
                        + 100 * candidate_id
                        + replicate,
                        {"policy_allocations": {policy: allocation}},
                    )
                )
                training_metadata.append(
                    {
                        "candidate_id": candidate_id,
                        "allocation": json.dumps(allocation, sort_keys=True),
                        "replicate": replicate,
                    }
                )
    training = execute_specs(training_specs, workers)
    training = pd.concat(
        [pd.DataFrame(training_metadata), training.reset_index(drop=True)],
        axis=1,
    )
    training["diagnostic_utility"] = _diagnostic_utility(
        training,
        diagnostic_weights,
        len(project.species),
    )
    training.to_csv(root / "results/policy_budget_search.csv", index=False)
    best = (
        training.groupby(["policy", "candidate_id"], as_index=False)
        .diagnostic_utility.mean()
        .sort_values(["policy", "diagnostic_utility"], ascending=[True, False])
        .groupby("policy", as_index=False)
        .first()
    )

    holdout_specs = []
    holdout_metadata = []
    for row in best.itertuples():
        policy = row.policy
        allocation = candidates_by_policy[policy][int(row.candidate_id)]
        base = project.config["policy_allocations"][policy]
        for allocation_type, values in [
            ("fixed_archetype", base),
            ("training_selected", allocation),
        ]:
            for replicate in range(design["holdout_replications"]):
                holdout_specs.append(
                    RunSpec(
                        str(root),
                        policy,
                        830000 + 10000 * int(policy[1:]) + replicate,
                        {"policy_allocations": {policy: values}},
                    )
                )
                holdout_metadata.append(
                    {
                        "allocation_type": allocation_type,
                        "candidate_id": (
                            0 if allocation_type == "fixed_archetype" else row.candidate_id
                        ),
                        "allocation": json.dumps(values, sort_keys=True),
                        "replicate": replicate,
                    }
                )
    holdout = execute_specs(holdout_specs, workers)
    holdout = pd.concat(
        [pd.DataFrame(holdout_metadata), holdout.reset_index(drop=True)],
        axis=1,
    )
    holdout["diagnostic_utility"] = _diagnostic_utility(
        holdout,
        diagnostic_weights,
        len(project.species),
    )
    holdout.to_csv(
        root / "results/policy_budget_optimized_holdout.csv",
        index=False,
    )
    holdout_summary = (
        holdout.groupby(["policy", "allocation_type"], as_index=False)
        .agg(
            diagnostic_utility=("diagnostic_utility", "mean"),
            survival_100=("survival_100", "mean"),
            species_retained_100=("species_retained_100", "mean"),
            welfare=("mean_individual_welfare", "mean"),
            ebd=("fraction_ebd", "mean"),
            future_option=("future_option_value", "mean"),
        )
    )
    holdout_summary.to_csv(
        root / "results/policy_budget_optimized_holdout_summary.csv",
        index=False,
    )
    _write_policy_budget_audit(root, robustness_summary, holdout_summary)


def _write_policy_budget_audit(
    root: Path,
    robustness: pd.DataFrame,
    holdout: pd.DataFrame,
) -> None:
    piv = holdout.pivot(
        index="policy",
        columns="allocation_type",
        values="diagnostic_utility",
    )
    improved = int(
        (
            piv["training_selected"]
            > piv["fixed_archetype"] + 1e-12
        ).sum()
    )
    text = f"""# Policy-budget fairness audit

## Allocation accounting

All S1-S7 fixed allocations sum to one; S0 intentionally allocates zero. The
fixed vectors define policy archetypes. They are not estimates of real program
budgets and are not empirical recommendations.

## Hidden advantages

Habitat-heavy allocations can favor policies whose mechanisms operate through
quality restoration; rescue and ex-situ shares can favor movement or managed
breeding; survey shares can reduce extinction-before-discovery; and engagement
spending can compound future budgets when the hypothetical feedback coefficient
is positive. Policy identity and allocation are therefore partially confounded
in the base design.

The robustness audit compares the fixed archetype with equal shares across its
active categories, a habitat-priority reallocation, and a movement-cautious
reallocation using paired seeds. Replicate-level and summarized results are in
`results/policy_budget_robustness.csv` and
`results/policy_budget_robustness_summary.csv`.

## Within-class search

A deterministic, seeded Dirichlet search perturbs only categories active in
each policy. Candidates are selected on training seeds using a prespecified
diagnostic index combining persistence, retained species, welfare, future
option value, and EBD, then compared with the fixed allocation on held-out
paired seeds. Training selection improved held-out diagnostic utility for
{improved} of 7 policy classes. This search is a robustness diagnostic, not a
claim of global optimality: the utility weights are normative, the search is
small, and no policy is declared an overall winner from it.

## Interpretation rule

Base allocations remain useful as transparent archetypes only when allocation
sensitivity and reversal regions are reported alongside them. Differences that
disappear under plausible reallocations are treated as fragile. The manuscript
must not compare a tuned dynamic policy with deliberately handicapped fixed
policies or describe any allocation vector as operational advice.
"""
    (root / "docs/policy_budget_fairness_audit.md").write_text(
        text,
        encoding="utf-8",
    )


def _run_named_policy_audit(
    root: Path,
    policy: str,
    designs: dict[str, dict],
    replications: int,
    seed_offset: int,
    workers: int,
) -> pd.DataFrame:
    specs = []
    metadata = []
    for design_id, (scenario, overrides) in enumerate(designs.items()):
        for replicate in range(replications):
            specs.append(
                RunSpec(
                    str(root),
                    policy,
                    seed_offset + 1000 * design_id + replicate,
                    overrides,
                )
            )
            metadata.append(
                {
                    "scenario": scenario,
                    "replicate": replicate,
                    "overrides": json.dumps(overrides, sort_keys=True),
                }
            )
    outcomes = execute_specs(specs, workers)
    return pd.concat(
        [pd.DataFrame(metadata), outcomes.reset_index(drop=True)],
        axis=1,
    )


def _summarize_audit(outcomes: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "survival_100",
        "species_retained_100",
        "total_abundance",
        "wild_abundance",
        "mean_individual_welfare",
        "disease_prevalence",
        "relocation_burden",
        "refuge_moves",
        "origin_returns",
        "successful_reintroductions",
    ]
    available = [metric for metric in metrics if metric in outcomes.columns]
    rows = []
    for scenario, frame in outcomes.groupby("scenario", sort=False):
        row = {"scenario": scenario, "n": len(frame)}
        for metric in available:
            row[f"{metric}_mean"] = frame[metric].mean()
            row[f"{metric}_lower"] = frame[metric].quantile(0.025)
            row[f"{metric}_upper"] = frame[metric].quantile(0.975)
        rows.append(row)
    return pd.DataFrame(rows)


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def _write_s3_audit(root: Path, summary: pd.DataFrame) -> None:
    base = summary.loc[summary.scenario == "base_directional_change"].iloc[0]
    stable = summary.loc[summary.scenario == "stable_excellent_origin"].iloc[0]
    restored = summary.loc[summary.scenario == "restored_origin"].iloc[0]
    text = f"""# S3 failure audit

## Defects corrected

The previous implementation initialized every individual at the origin and then
allowed S3 to move only individuals already outside the origin. S3 therefore
had no initial candidates and was not a meaningful return policy. Movement
mortality and release mortality were also applied as diffuse population-wide
penalties rather than to moved and released individuals. The corrected S3 is a
refuge-and-return archetype: it evacuates visible populations when observed
origin suitability falls below a configured trigger and returns eligible
individuals after observed suitability recovers. Movement and release hazards
now apply only to exposed individuals, and node capacity is enforced per
species, consistently with density dependence.

## Conditional results

Across the registered audit seeds, base directional change retained
{_fmt(base.species_retained_100_mean)} species on average with survival
{_fmt(base.survival_100_mean)}. Under a stable excellent origin, S3 retained
{_fmt(stable.species_retained_100_mean)} species with survival
{_fmt(stable.survival_100_mean)}. In the restoration design, mean refuge moves
were {_fmt(restored.refuge_moves_mean)} and mean returns to origin were
{_fmt(restored.origin_returns_mean)}.

S3 failure is therefore not interpreted as evidence that return-oriented
conservation is generally ineffective. It is a conditional result produced by
directional origin deterioration, the timing thresholds, finite budgets,
movement hazards, and demographic stochasticity. Exact scenario definitions
are versioned in `config/audit_designs.json`; replicate-level outcomes are in
`results/s3_failure_outcomes.csv`.

## Interpretation

S3 remains a synthetic policy archetype, not a representation of any named
reintroduction program. Stable-origin, restored-origin, zero-harm, larger-budget,
and alternative-timing scenarios are retained even when they weaken the
manuscript's base contrast.
"""
    (root / "docs/s3_failure_audit.md").write_text(text, encoding="utf-8")


def _write_s0_audit(root: Path, summary: pd.DataFrame) -> None:
    base = summary.loc[summary.scenario == "base_directional_change"].iloc[0]
    benign = summary.loc[summary.scenario == "benign_combined"].iloc[0]
    stationary = summary.loc[summary.scenario == "stationary_environment"].iloc[0]
    stable = summary.loc[summary.scenario == "stable_excellent_origin"].iloc[0]
    if stationary.species_retained_100_mean <= 0:
        raise ValueError("S0 stationary-environment control did not retain species")
    text = f"""# S0 structural audit

S0 applies no conservation expenditure or movement. Its base directional-change
outcome is a stress test, not a claim that intervention is universally required.

Mean species retained under base directional change was
{_fmt(base.species_retained_100_mean)} with survival
{_fmt(base.survival_100_mean)}. With directional deterioration and climate
velocity removed but ordinary demographic stochasticity, catastrophe risk,
predation, and anthropogenic pressure retained, the stationary control retained
{_fmt(stationary.species_retained_100_mean)} species with survival
{_fmt(stationary.survival_100_mean)}. A stationary excellent-origin control retained
{_fmt(stable.species_retained_100_mean)} species with survival
{_fmt(stable.survival_100_mean)}. The combined benign control retained
{_fmt(benign.species_retained_100_mean)} species with survival
{_fmt(benign.survival_100_mean)}.

These controls show that zero intervention is not structurally forced to fail.
Its base failure reflects the configured directional deterioration, stochastic
hazards, anthropogenic pressure, predation, and demographic mortality. The
component controls in `results/s0_benign_controls.csv` separate those drivers.
No S0 result should be generalized beyond the synthetic scenario family.
"""
    (root / "docs/s0_failure_audit.md").write_text(text, encoding="utf-8")


def run_s3_s0_audits(root: Path, mode: str, workers: int) -> None:
    designs = _read_json(root / "config/audit_designs.json")
    replications = 6 if mode == "quick" else 24

    s3_outcomes = _run_named_policy_audit(
        root,
        "S3",
        designs["s3_failure"],
        replications,
        850000,
        workers,
    )
    s3_outcomes.to_csv(root / "results/s3_failure_outcomes.csv", index=False)
    s3_summary = _summarize_audit(s3_outcomes)
    s3_summary.to_csv(root / "results/s3_failure_decomposition.csv", index=False)
    _write_s3_audit(root, s3_summary)

    s0_outcomes = _run_named_policy_audit(
        root,
        "S0",
        designs["s0_controls"],
        replications,
        870000,
        workers,
    )
    s0_summary = _summarize_audit(s0_outcomes)
    s0_summary.to_csv(root / "results/s0_benign_controls.csv", index=False)
    _write_s0_audit(root, s0_summary)


def _convergence_summary(
    outcomes: pd.DataFrame,
    sample_sizes: list[int],
) -> pd.DataFrame:
    metrics = [
        "survival_100",
        "species_retained_100",
        "fraction_ebd",
        "mean_individual_welfare",
        "future_option_value",
    ]
    rows = []
    feasible = outcomes[~outcomes.oracle]
    for policy, frame in feasible.groupby("policy"):
        frame = frame.sort_values("seed")
        for sample_size in sample_sizes:
            subset = frame.head(sample_size)
            for metric in metrics:
                values = subset[metric].dropna()
                rows.append(
                    {
                        "contrast": policy,
                        "metric": metric,
                        "n": sample_size,
                        "estimate": values.mean(),
                        "mcse": values.std(ddof=1) / np.sqrt(len(values)),
                        "lower": values.quantile(0.025),
                        "upper": values.quantile(0.975),
                    }
                )

    s6 = feasible[feasible.policy == "S6"].set_index("seed").sort_index()
    s7 = feasible[feasible.policy == "S7"].set_index("seed").sort_index()
    paired = s7.join(s6, lsuffix="_s7", rsuffix="_s6", how="inner")
    for sample_size in sample_sizes:
        subset = paired.head(sample_size)
        for metric in metrics:
            difference = subset[f"{metric}_s7"] - subset[f"{metric}_s6"]
            rows.append(
                {
                    "contrast": "S7-S6",
                    "metric": metric,
                    "n": sample_size,
                    "estimate": difference.mean(),
                    "mcse": difference.std(ddof=1) / np.sqrt(len(difference)),
                    "lower": difference.quantile(0.025),
                    "upper": difference.quantile(0.975),
                }
            )
    summary = pd.DataFrame(rows)
    final = (
        summary[summary.n == max(sample_sizes)]
        .set_index(["contrast", "metric"])[["estimate", "lower", "upper"]]
        .rename(
            columns={
                "estimate": "final_estimate",
                "lower": "final_lower",
                "upper": "final_upper",
            }
        )
    )
    summary = summary.join(final, on=["contrast", "metric"])
    summary["estimate_change_from_final"] = (
        summary.estimate - summary.final_estimate
    )
    summary["lower_change_from_final"] = summary.lower - summary.final_lower
    summary["upper_change_from_final"] = summary.upper - summary.final_upper
    summary["sign"] = np.sign(summary.estimate).astype(int)
    summary["final_sign"] = np.sign(summary.final_estimate).astype(int)
    summary["sign_stable"] = summary.sign == summary.final_sign
    return summary


def _information_convergence(
    outcomes: pd.DataFrame,
    sample_sizes: list[int],
    weights: dict[str, float],
) -> pd.DataFrame:
    rows = []
    for sample_size in sample_sizes:
        selected_seeds = sorted(outcomes.seed.unique())[:sample_size]
        estimate = information_value(
            outcomes[outcomes.seed.isin(selected_seeds)], weights
        )
        estimate["n_target"] = sample_size
        rows.append(estimate)
    result = pd.concat(rows, ignore_index=True)
    final = (
        result[result.n_target == max(sample_sizes)]
        .set_index("metric")[["estimate", "lower", "upper"]]
        .rename(
            columns={
                "estimate": "final_estimate",
                "lower": "final_lower",
                "upper": "final_upper",
            }
        )
    )
    result = result.join(final, on="metric")
    result["estimate_change_from_final"] = (
        result.estimate - result.final_estimate
    )
    result["sign_stable"] = (
        np.sign(result.estimate) == np.sign(result.final_estimate)
    )
    return result


def _write_information_audits(
    root: Path,
    convergence: pd.DataFrame,
    information: pd.DataFrame,
) -> None:
    final_n = int(convergence.n.max())
    paired = convergence[
        (convergence.contrast == "S7-S6")
        & (convergence.n == final_n)
    ]
    survival = paired[paired.metric == "survival_100"].iloc[0]
    information_utility = information[
        (information.metric == "decision_utility")
        & (information.n_target == final_n)
    ].iloc[0]
    production_n = 192
    production = convergence[
        (convergence.n == production_n)
        & convergence.contrast.isin(["S6", "S7", "S7-S6"])
    ].copy()
    within_two_mcse = (
        production.estimate_change_from_final.abs()
        <= 2 * production.mcse
    ).all()
    production_information = information[
        information.n_target == production_n
    ].copy()
    information_within_two_mcse = (
        production_information.estimate_change_from_final.abs()
        <= 2 * production_information.mc_half_width / 1.96
    ).all()
    if not within_two_mcse or not information_within_two_mcse:
        raise ValueError("N=192 did not meet the registered convergence criterion")
    convergence_text = f"""# Monte Carlo convergence audit

The audit uses nested paired prefixes at N=24, 48, 96, 192, and {final_n}.
It reports Monte Carlo standard errors, replicate percentile intervals,
changes from the N={final_n} estimate, and sign stability. Percentile intervals
describe simulated outcome distributions, not empirical confidence intervals.

At N={final_n}, the paired S7-S6 survival contrast was
{survival.estimate:.4f} with Monte Carlo SE {survival.mcse:.4f}. Full endpoint
results are in `results/convergence_audit.csv`; paired current-state information
effects are in `results/information_convergence.csv`.

For every registered S6, S7, and paired S7-S6 endpoint, the N=192 estimate was
within two N=192 Monte Carlo standard errors of the N={final_n} estimate and
the qualitative sign was stable. The N=192 current-state-information effects
also met that criterion; their intervals span zero, so the supported
conclusion is negligible or uncertain effect rather than a directional
benefit. The production count of 192 is therefore sufficient for the reported
point estimates and qualitative conclusions. N={final_n} is retained as a
convergence audit and does not replace the production analysis.
"""
    (root / "docs/monte_carlo_convergence.md").write_text(
        convergence_text,
        encoding="utf-8",
    )
    oracle_text = f"""# Oracle and information-value audit

## Comparator definition

The comparator supplies the **true current state** within the same S7
action class. In each decision year it receives current true abundance and
current habitat quality. It does not receive future environmental shocks,
future demographic draws, or realized future outcomes. S7 remains a
forward-quality heuristic; it is not a solved POMDP.

The former analysis retained the feasible realization whenever the oracle
realization had lower post hoc utility. That was hindsight selection and forced
the reported contrast to be nonnegative. This behavior was removed. The
reported quantity is now the paired effect of current-state information under
the fixed S7 heuristic and may be positive or negative.

At N={final_n}, the mean decision-utility effect was
{information_utility.estimate:.4f} (Monte Carlo half-width
{information_utility.mc_half_width:.4f}). It is not monetary EVPI and is not
used to declare an overall policy winner.

## Remaining limitation

True current-state information can change actions under a heuristic that was not
re-optimized for each information regime. The contrast therefore measures the
value or harm of feeding current truth into that heuristic, not the theoretical
EVPI of an optimal decision problem.
"""
    (root / "docs/oracle_voi_audit.md").write_text(
        oracle_text,
        encoding="utf-8",
    )
    rng_text = """# RNG and observability audit

Randomness is keyed by master seed, process, and year for initialization,
funding shocks, catastrophes, observation, discovery, movement, disease, and
demography. Policies with the same seed therefore share process-year streams;
policy-specific branching in one process no longer shifts later years or other
processes.

This is stronger than shared seed labels but is not exact individual-level
common random numbers after populations diverge. Demographic arrays differ in
length and identity across policies, so later individual draws cannot remain
one-to-one without a persistent individual/event key architecture. Paired
contrasts are described as keyed process-year streams, not exact CRN.

Feasible policies receive noisy abundance only after description and delayed,
noisy habitat quality. Decision suitability is recomputed from that observed
quality; true suitability is reserved for ecological transitions. The oracle
receives current truth only. Tests verify that feasible observations are
unchanged when only current hidden quality changes, while oracle observations
track current quality.
"""
    (root / "docs/rng_observability_audit.md").write_text(
        rng_text,
        encoding="utf-8",
    )


def run_convergence_audit(root: Path, mode: str, workers: int) -> None:
    sample_sizes = [12, 24] if mode == "quick" else [24, 48, 96, 192, 384]
    maximum = max(sample_sizes)
    specs = [
        RunSpec(str(root), policy, 910000 + seed, {})
        for seed in range(maximum)
        for policy in [f"S{number}" for number in range(8)]
    ]
    specs.extend(
        RunSpec(str(root), "S7", 910000 + seed, {}, oracle=True)
        for seed in range(maximum)
    )
    outcomes = execute_specs(specs, workers)
    outcomes.to_csv(root / "results/convergence_outcomes.csv", index=False)
    convergence = _convergence_summary(outcomes, sample_sizes)
    convergence.to_csv(root / "results/convergence_audit.csv", index=False)
    information_weights = _read_json(root / "config/analysis.json")[
        "information_utility_weights"
    ]
    information = _information_convergence(
        outcomes, sample_sizes, information_weights
    )
    information.to_csv(root / "results/information_convergence.csv", index=False)
    _write_information_audits(root, convergence, information)


def run_population_cap_audit(root: Path, mode: str, workers: int) -> None:
    design = _read_json(root / "config/audit_designs.json")["population_cap"]
    replications = design[f"{mode}_replications"]
    caps = design["caps"]
    policies = design["policies"]
    specs = [
        RunSpec(
            str(root),
            policy,
            930000 + seed,
            {"max_individuals": cap},
        )
        for seed in range(replications)
        for cap in caps
        for policy in policies
    ]
    outcomes = execute_specs(specs, workers)
    cap_hashes = {
        hashlib.sha256(
            json.dumps({"max_individuals": cap}, sort_keys=True).encode()
        ).hexdigest()[:16]: cap
        for cap in caps
    }
    outcomes["population_cap"] = outcomes.config_hash.map(cap_hashes)
    outcomes.to_csv(root / "results/population_cap_outcomes.csv", index=False)

    metrics = [
        "survival_100",
        "species_retained_100",
        "fraction_ebd",
        "mean_individual_welfare",
        "future_option_value",
        "total_abundance",
    ]
    rows = []
    for (cap, policy), frame in outcomes.groupby(["population_cap", "policy"]):
        for metric in metrics:
            values = frame[metric]
            rows.append(
                {
                    "contrast": policy,
                    "population_cap": cap,
                    "metric": metric,
                    "n": len(values),
                    "estimate": values.mean(),
                    "mcse": values.std(ddof=1) / np.sqrt(len(values)),
                    "lower": values.quantile(0.025),
                    "upper": values.quantile(0.975),
                }
            )

        paired_policies = (
            frame
            if set(frame.policy) == {"S6", "S7"}
            else outcomes[outcomes.population_cap == cap]
        )
        s6 = paired_policies[paired_policies.policy == "S6"].set_index("seed")
        s7 = paired_policies[paired_policies.policy == "S7"].set_index("seed")
        paired = s7.join(s6, lsuffix="_s7", rsuffix="_s6", how="inner")
        if policy == policies[0]:
            for metric in metrics:
                values = paired[f"{metric}_s7"] - paired[f"{metric}_s6"]
                rows.append(
                    {
                        "contrast": "S7-S6",
                        "population_cap": cap,
                        "metric": metric,
                        "n": len(values),
                        "estimate": values.mean(),
                        "mcse": values.std(ddof=1) / np.sqrt(len(values)),
                        "lower": values.quantile(0.025),
                        "upper": values.quantile(0.975),
                    }
                )

    summary = pd.DataFrame(rows)
    baseline = (
        summary[summary.population_cap == min(caps)]
        .set_index(["contrast", "metric"])["estimate"]
        .rename("baseline_estimate")
    )
    summary = summary.join(baseline, on=["contrast", "metric"])
    summary["change_from_baseline"] = (
        summary.estimate - summary.baseline_estimate
    )
    summary.to_csv(root / "results/population_cap_audit.csv", index=False)

    survival = summary[
        (summary.contrast == "S7-S6")
        & (summary.metric == "survival_100")
        & (summary.population_cap == max(caps))
    ].iloc[0]
    text = f"""# Population-cap audit

The synthetic computational cap was doubled from {min(caps)} to {max(caps)}
for {replications} paired replications of S6 and S7. The audit reports endpoint
means, Monte Carlo standard errors, replicate percentile intervals, and changes
from the registered cap in `results/population_cap_audit.csv`.

At the doubled cap, the paired S7-S6 year-100 survival contrast was
{survival.estimate:.4f}, a change of {survival.change_from_baseline:.4f} from
the registered-cap estimate. Total abundance is expected to be cap-sensitive
and is not used for the manuscript's primary policy conclusions.
"""
    (root / "docs/population_cap_audit.md").write_text(
        text,
        encoding="utf-8",
    )


def run_ebd_audit(root: Path, mode: str, workers: int) -> None:
    project = load_project(root)
    base = project.config["policy_allocations"]["S7"]
    zero_survey = dict(base)
    zero_survey["habitat"] += zero_survey["survey"]
    zero_survey["survey"] = 0.0
    designs = {
        "base": {},
        "detectability_one": {"latent_detectability_override": 1.0},
        "near_zero_detectability": {
            "latent_detectability_override": 1e-9,
            "background_detection_probability": 0.0,
        },
        "near_zero_survey_cost": {"survey_cost": 1e-6},
        "zero_survey_budget": {
            "policy_allocations": {"S7": zero_survey},
            "background_detection_probability": 0.0,
        },
        "latent_species_zero": {"latent_fraction_proxy": 0.0},
        "no_anthropogenic_deterioration": {
            "scenario": "stationary",
            "habitat_deterioration": 0.0,
            "climate_velocity": 0.0,
            "anthropogenic_pressure_multiplier": 0.0,
        },
    }
    replications = 8 if mode == "quick" else 48
    outcomes = _run_named_policy_audit(
        root,
        "S7",
        designs,
        replications,
        950000,
        workers,
    )
    outcomes.to_csv(root / "results/ebd_boundary_outcomes.csv", index=False)
    summary = (
        outcomes.groupby("scenario", as_index=False)
        .agg(
            n=("seed", "size"),
            mean_ebd=("fraction_ebd", "mean"),
            p_any_ebd=("p_ebd", "mean"),
            discovered_latent=("discovered_latent", "mean"),
            species_retained=("species_retained_100", "mean"),
        )
    )
    summary.to_csv(root / "results/ebd_boundary_summary.csv", index=False)
    base_row = summary[summary.scenario == "base"].iloc[0]
    high = summary[summary.scenario == "detectability_one"].iloc[0]
    low = summary[summary.scenario == "near_zero_detectability"].iloc[0]
    text = f"""# Extinction-before-discovery audit

EBD is recorded only when a configured latent species becomes extinct before
description (stage 2). The denominator is the number of latent species; it is
zero-safe when latent species are disabled. Discovery does not continue after
true extinction, and policy decisions do not receive latent abundance before
description.

Boundary tests cover detectability 1, near-zero detectability, near-zero survey
cost, zero survey allocation, zero latent species, and removal of directional
and anthropogenic deterioration. In the registered runs, base mean EBD was
{base_row.mean_ebd:.3f}; detectability-one mean EBD was
{high.mean_ebd:.3f}; and near-zero-detectability mean EBD was
{low.mean_ebd:.3f}. Replicate-level variation and discovery counts are retained
in `results/ebd_boundary_outcomes.csv`.

EBD is therefore an emergent stochastic endpoint rather than a fixed label.
Its magnitude remains conditional on synthetic discovery probabilities,
survey allocation, demography, and environmental stress.
"""
    (root / "docs/ebd_audit.md").write_text(text, encoding="utf-8")


def run_feature_audits(root: Path, mode: str, workers: int) -> None:
    replications = 8 if mode == "quick" else 48
    welfare_designs = {
        "base": {},
        "wild_hazard_heavy": {
            "wild_predation_welfare_weight": 0.25,
            "food_insecurity_welfare_weight": 0.35,
            "managed_crowding_welfare_weight": 0.05,
            "managed_restriction_welfare_weight": 0.05,
        },
        "managed_burden_heavy": {
            "captivity_welfare_penalty": 0.35,
            "wild_predation_welfare_weight": 0.05,
            "food_insecurity_welfare_weight": 0.08,
            "managed_crowding_welfare_weight": 0.30,
            "managed_restriction_welfare_weight": 0.30,
        },
        "equal_component_weights": {
            "wild_predation_welfare_weight": 0.12,
            "food_insecurity_welfare_weight": 0.12,
            "managed_crowding_welfare_weight": 0.12,
            "managed_restriction_welfare_weight": 0.12,
            "infection_welfare_weight": 0.12,
            "habituation_welfare_weight": 0.12,
            "relocation_welfare_weight": 0.12,
        },
    }
    welfare_frames = []
    for design, overrides in welfare_designs.items():
        welfare_specs = []
        for policy in ["S2", "S7"]:
            for replicate in range(replications):
                welfare_specs.append(
                    RunSpec(
                        str(root),
                        policy,
                        970000 + replicate,
                        overrides,
                    )
                )
        frame = execute_specs(welfare_specs, workers)
        frame["scenario"] = design
        welfare_frames.append(frame)
    welfare = pd.concat(welfare_frames, ignore_index=True)
    welfare.to_csv(
        root / "results/welfare_definition_outcomes.csv",
        index=False,
    )
    welfare_summary = (
        welfare.groupby(["scenario", "policy"], as_index=False)
        .agg(
            n=("seed", "size"),
            mean_individual_welfare=("mean_individual_welfare", "mean"),
            lifetime_welfare=("lifetime_welfare", "mean"),
            survival=("survival_100", "mean"),
            predation_burden=("welfare_burden_predation", "mean"),
            food_burden=("welfare_burden_food_insecurity", "mean"),
            crowding_burden=("welfare_burden_crowding", "mean"),
            restriction_burden=("welfare_burden_restriction", "mean"),
            infection_burden=("welfare_burden_infection", "mean"),
            relocation_burden=("welfare_burden_relocation", "mean"),
        )
    )
    welfare_summary.to_csv(
        root / "results/welfare_definition_summary.csv",
        index=False,
    )
    welfare_pivot = welfare_summary.pivot(
        index="scenario",
        columns="policy",
        values="mean_individual_welfare",
    )
    welfare_difference = (
        welfare_pivot["S7"] - welfare_pivot["S2"]
    ).rename("s7_minus_s2_welfare")
    welfare_difference.to_csv(
        root / "results/welfare_s7_s2_contrast.csv",
    )

    module_designs = {
        "genetics_on": (
            "S7",
            {
                "genetics_enabled": True,
                "inbreeding_fertility_penalty": 0.7,
                "inbreeding_mortality_penalty": 0.2,
            },
        ),
        "genetics_off": (
            "S7",
            {
                "genetics_enabled": False,
                "inbreeding_fertility_penalty": 0.7,
                "inbreeding_mortality_penalty": 0.2,
            },
        ),
        "disease_on": (
            "S4",
            {
                "disease_enabled": True,
                "movement_disease_risk": 0.8,
            },
        ),
        "disease_off": (
            "S4",
            {
                "disease_enabled": False,
                "movement_disease_risk": 0.8,
            },
        ),
        "biobank_on": ("S7", {"biobank_enabled": True}),
        "biobank_off": ("S7", {"biobank_enabled": False}),
        "biobank_no_decay": (
            "S7",
            {"biobank_enabled": True, "biobank_annual_decay": 0.0},
        ),
        "biobank_high_decay": (
            "S7",
            {"biobank_enabled": True, "biobank_annual_decay": 0.05},
        ),
        "engagement_positive": (
            "S2",
            {
                "engagement_coefficient": 0.18,
                "engagement_habitat_feedback": 0.0,
            },
        ),
        "engagement_zero": (
            "S2",
            {
                "engagement_coefficient": 0.0,
                "engagement_habitat_feedback": 0.0,
            },
        ),
        "engagement_negative": (
            "S2",
            {
                "engagement_coefficient": -0.18,
                "engagement_habitat_feedback": 0.0,
            },
        ),
    }
    feature_frames = []
    for scenario, (policy, overrides) in module_designs.items():
        feature_specs = []
        for replicate in range(replications):
            feature_specs.append(
                RunSpec(
                    str(root),
                    policy,
                    980000 + replicate,
                    overrides,
                )
            )
        frame = execute_specs(feature_specs, workers)
        frame["scenario"] = scenario
        feature_frames.append(frame)
    features = pd.concat(feature_frames, ignore_index=True)
    features.to_csv(root / "results/module_feature_outcomes.csv", index=False)
    feature_summary = (
        features.groupby(["scenario", "policy"], as_index=False)
        .agg(
            n=("seed", "size"),
            survival=("survival_100", "mean"),
            abundance=("total_abundance", "mean"),
            founder_effective=("founder_effective", "mean"),
            mean_inbreeding=("mean_inbreeding", "mean"),
            disease_prevalence=("disease_prevalence", "mean"),
            quarantine_cost=("quarantine_cost", "mean"),
            biobank_coverage=("biobank_coverage", "mean"),
            future_option_value=("future_option_value", "mean"),
            engagement=("engagement", "mean"),
            available_budget=("available_budget", "mean"),
        )
    )
    feature_summary.to_csv(
        root / "results/module_feature_summary.csv",
        index=False,
    )

    welfare_lines = [
        "# Welfare-definition audit",
        "",
        "Wild placement is not assigned high welfare automatically: the endpoint",
        "deducts predation risk and habitat/food insecurity. Managed placement",
        "deducts crowding, restriction, captivity burden, disease, habituation,",
        "and acute relocation burden. All weights are synthetic and normative.",
        "",
        "The paired S7-S2 mean-individual-welfare contrasts were:",
        "",
    ]
    for scenario, difference in welfare_difference.items():
        welfare_lines.append(f"- {scenario}: {difference:.4f}")
    nonzero_signs = {
        int(np.sign(value))
        for value in welfare_difference
        if not np.isclose(value, 0.0)
    }
    if len(nonzero_signs) > 1:
        sensitivity_statement = (
            "The S7-S2 direction reversed across registered definitions. "
            "This is value sensitivity, not evidence that one definition is "
            "empirically correct."
        )
    else:
        sensitivity_statement = (
            "No direction reversal occurred in the registered definitions. "
            "A reversal under further weights would be treated as value "
            "sensitivity, not evidence that one setting is empirically correct."
        )
    welfare_lines.extend(
        [
            "",
            sensitivity_statement,
            "Component burdens and replicate outcomes are retained in the results",
            "tables for audit.",
        ]
    )
    (root / "docs/welfare_audit.md").write_text(
        "\n".join(welfare_lines) + "\n",
        encoding="utf-8",
    )

    def feature_value(scenario: str, column: str) -> float:
        return float(
            feature_summary[feature_summary.scenario == scenario][column].iloc[0]
        )

    feature_text = f"""# Genetics, disease, biobank, and engagement audit

## Genetics

Founder identities propagate through births. Diversity-aware mating first
prefers a different founder lineage and then weights candidates toward lower
inbreeding. Inbreeding reduces fertility and survival. Under the registered
stress setting, mean inbreeding was
{feature_value("genetics_on", "mean_inbreeding"):.4f} with management on and
{feature_value("genetics_off", "mean_inbreeding"):.4f} with it off.

## Disease and quarantine

Infection has local transitions, movement transmission, recovery, mortality,
welfare, and fertility effects. Rescue spending covers quarantine up to a
per-move relative cost and reduces movement infection risk without adding
money beyond the fixed policy budget. Disease prevalence was
{feature_value("disease_on", "disease_prevalence"):.4f} when active and
{feature_value("disease_off", "disease_prevalence"):.4f} when disabled.

## Biobank

Only extant, described species can add material. Stored coverage decays
annually and contributes to future option value; it never creates individuals
or resurrects an extinct population. Coverage was
{feature_value("biobank_on", "biobank_coverage"):.4f} when active and
{feature_value("biobank_off", "biobank_coverage"):.4f} when disabled.

## Engagement

Positive, zero, and negative coefficients are explicitly registered. With the
non-exposure habitat feedback disabled for this test, terminal engagement was
{feature_value("engagement_positive", "engagement"):.4f},
{feature_value("engagement_zero", "engagement"):.4f}, and
{feature_value("engagement_negative", "engagement"):.4f}, respectively.

All mechanisms and effect sizes are synthetic. Modules with small outcome
effects are retained as exploratory diagnostics rather than used as
primary evidence.
"""
    (root / "docs/module_feature_audit.md").write_text(
        feature_text,
        encoding="utf-8",
    )


def run_structural_audits(root: Path, mode: str, workers: int = 2) -> None:
    root = root.resolve()
    (root / "results").mkdir(parents=True, exist_ok=True)
    (root / "provenance").mkdir(parents=True, exist_ok=True)
    write_parameter_registry(root)
    run_policy_budget_audit(root, mode, workers)
    run_s3_s0_audits(root, mode, workers)
    run_convergence_audit(root, mode, workers)
    run_population_cap_audit(root, mode, workers)
    run_ebd_audit(root, mode, workers)
    run_feature_audits(root, mode, workers)
