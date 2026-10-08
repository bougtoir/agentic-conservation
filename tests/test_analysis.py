from pathlib import Path

import numpy as np
import pandas as pd

from agentic_conservation.analysis import (
    SENSITIVITY_RANGES,
    information_weight_sensitivity,
    pareto_dominance_pairs,
    pareto_flags,
    sensitivity_audit,
    threshold_stability_audit,
)


def test_sensitivity_audit_aggregates_replicates_by_design(tmp_path: Path) -> None:
    (tmp_path / "results").mkdir()
    (tmp_path / "docs").mkdir()
    designs = []
    outcomes = []
    for design_id in range(6):
        parameters = {
            name: low + (high - low) * design_id / 5
            for name, (low, high) in SENSITIVITY_RANGES.items()
        }
        designs.append({"design_id": design_id, **parameters})
        for policy_index, policy in enumerate(["S4", "S6", "S7"]):
            for replicate in range(3):
                outcomes.append(
                    {
                        "design_id": design_id,
                        "policy": policy,
                        "survival_100": design_id + policy_index + replicate / 10,
                        "fraction_ebd": 1 - design_id / 10,
                        "mean_individual_welfare": 0.5 + design_id / 20,
                        "future_option_value": 0.2 + policy_index / 10,
                    }
                )
    associations, interactions = sensitivity_audit(
        tmp_path, pd.DataFrame(outcomes), pd.DataFrame(designs)
    )
    assert set(associations.n_designs) == {6}
    assert set(associations.replicates_per_design) == {3}
    assert len(interactions) > 0


def test_threshold_stability_reports_all_sweeps(tmp_path: Path) -> None:
    (tmp_path / "results").mkdir()
    (tmp_path / "docs").mkdir()
    rows = []
    for sweep in ["first", "second"]:
        for x in [0.0, 1.0]:
            for y in [0.0, 1.0]:
                for replicate in range(4):
                    seed = 1000 + replicate
                    for policy, value in [
                        ("S6", 0.4),
                        ("S7", 0.5 if x + y > 0 else 0.3),
                    ]:
                        rows.append(
                            {
                                "sweep": sweep,
                                "x": x,
                                "y": y,
                                "seed": seed,
                                "policy": policy,
                                "survival_100": value,
                            }
                        )
    summary = threshold_stability_audit(tmp_path, pd.DataFrame(rows))
    assert set(summary.sweep) == {"first", "second"}
    assert np.all(summary.final_n == 4)
    assert np.all(summary.cells == 4)


def test_information_weight_sensitivity_reweights_paired_components() -> None:
    outcomes = pd.DataFrame(
        [
            {
                "policy": "S7",
                "seed": 1,
                "oracle": False,
                "survival_100": 0.2,
                "future_option_value": 0.8,
                "habitat_integrity": 0.5,
                "fraction_ebd": 0.5,
                "mean_individual_welfare": 0.8,
            },
            {
                "policy": "S7",
                "seed": 1,
                "oracle": True,
                "survival_100": 0.8,
                "future_option_value": 0.2,
                "habitat_integrity": 0.5,
                "fraction_ebd": 0.5,
                "mean_individual_welfare": 0.2,
            },
        ]
    )
    scenarios = {
        "persistence": {
            "survival_100": 1.0,
            "future_option_value": 0.0,
            "habitat_integrity": 0.0,
            "ebd_avoidance": 0.0,
            "mean_individual_welfare": 0.0,
        },
        "welfare": {
            "survival_100": 0.0,
            "future_option_value": 0.0,
            "habitat_integrity": 0.0,
            "ebd_avoidance": 0.0,
            "mean_individual_welfare": 1.0,
        },
    }
    result = information_weight_sensitivity(outcomes, scenarios).set_index(
        "scenario"
    )
    assert result.loc["persistence", "estimate"] > 0
    assert result.loc["welfare", "estimate"] < 0


def test_pareto_uses_all_six_objectives_and_reports_dominators() -> None:
    rows = []
    for policy, values in {
        "A": (0.8, 0.8, 4.0, 0.1, 10.0, 0.7),
        "B": (0.7, 0.7, 3.0, 0.2, 11.0, 0.6),
        "C": (0.9, 0.6, 4.5, 0.1, 12.0, 0.8),
    }.items():
        survival, welfare, genetics, ebd, cost, future_option = values
        rows.append(
            {
                "policy": policy,
                "oracle": False,
                "survival_100": survival,
                "mean_individual_welfare": welfare,
                "founder_effective": genetics,
                "fraction_ebd": ebd,
                "cost": cost,
                "future_option_value": future_option,
            }
        )
    pareto = pareto_flags(pd.DataFrame(rows)).set_index("policy")
    assert pareto.loc["A", "pareto_efficient"]
    assert not pareto.loc["B", "pareto_efficient"]
    assert pareto.loc["B", "dominated_by"] == "A"
    assert pareto.loc["C", "pareto_efficient"]
    pairs = pareto_dominance_pairs(pareto.reset_index())
    reported_pairs = pairs[
        ["dominated_policy", "dominating_policy"]
    ].itertuples(index=False, name=None)
    assert list(reported_pairs) == [("B", "A")]
    assert (pairs.filter(like="_advantage") >= 0).all(axis=None)
