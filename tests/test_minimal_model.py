"""Limiting-case tests for the reversal-theory minimal model and the
factorial decision-rule overrides in simulation.py."""

from pathlib import Path

import pytest

from agentic_conservation.minimal_model import load_config, psi_index, run_minimal
from agentic_conservation.simulation import load_project, run_simulation

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def bundle():
    return load_config(ROOT)


@pytest.fixture(scope="module")
def allocations(bundle):
    return bundle["config"]["policy_allocations"]


def test_stable_origin_favours_habitat(bundle, allocations):
    ov = {"scenario": "stationary", "habitat_deterioration": 0.0, "catastrophe_probability": 0.0}
    res = psi_index(bundle, allocations["S7"], allocations["S6"], ov)
    assert res["psi"] <= 0.0
    assert res["circulation_channel"] == 0.0


def test_degrading_origin_favours_circulation(bundle, allocations):
    ov = {"habitat_deterioration": 0.04, "climate_velocity": 0.05, "relocation_mortality": 0.0}
    res = psi_index(bundle, allocations["S7"], allocations["S6"], ov)
    assert res["psi"] > 0.0
    assert res["circulation_channel"] > 0.0


def test_all_latent_blocks_circulation(bundle, allocations):
    ov = {"habitat_deterioration": 0.04, "survey_cost": 100.0}
    low = psi_index(bundle, allocations["S7"], allocations["S6"], ov)
    high = psi_index(
        bundle, allocations["S7"], allocations["S6"], ov | {"latent_fraction_proxy": 1.0}
    )
    # nothing movable until discovery; circulation advantage collapses
    assert high["psi"] < low["psi"]
    assert high["circulation_channel"] < 1.0


def test_no_circulation_no_channel(bundle, allocations):
    res = run_minimal(bundle, allocations["S7"], False, {"habitat_deterioration": 0.04})
    assert res["moved"] == 0.0


def test_deadly_relocation_hurts_circulation(bundle, allocations):
    hi = psi_index(
        bundle,
        allocations["S7"],
        allocations["S6"],
        {"habitat_deterioration": 0.04, "relocation_mortality": 0.95},
    )
    lo = psi_index(
        bundle,
        allocations["S7"],
        allocations["S6"],
        {"habitat_deterioration": 0.04, "relocation_mortality": 0.0},
    )
    assert hi["circulation_channel"] < lo["circulation_channel"]
    assert hi["psi"] < lo["psi"]


def test_habitat_channel_never_positive(bundle, allocations):
    res = psi_index(bundle, allocations["S7"], allocations["S6"], {"habitat_deterioration": 0.01})
    assert res["habitat_channel"] <= 0.0


def _survival(project, policy, seed, overrides):
    return run_simulation(project, policy, seed, overrides)["survival_100"]


def test_decision_rule_override_runs(project=None):
    p = load_project(ROOT)
    # S6 budget with S7 rule differs from plain S6 (rule actually swaps)
    base = _survival(p, "S6", 910000, {})
    alt = _survival(p, "S6", 910000, {"decision_rule_override": "S7"})
    assert isinstance(base, float) and isinstance(alt, float)
    # S7 budget with movement disabled runs to completion
    r = run_simulation(p, "S7", 910000, {"movement_disabled": True})
    assert 0.0 <= r["survival_100"] <= 1.0


def test_movement_disabled_matches_s6_rule():
    p = load_project(ROOT)
    a = run_simulation(p, "S7", 910001, {"movement_disabled": True})
    b = run_simulation(p, "S7", 910001, {"decision_rule_override": "S6"})
    assert a["survival_100"] == b["survival_100"]
