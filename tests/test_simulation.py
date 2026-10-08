from pathlib import Path

import numpy as np
import pandas as pd

from agentic_conservation.analysis import information_value
from agentic_conservation.simulation import load_project, run_simulation

ROOT = Path(__file__).resolve().parents[1]


def test_all_policies_execute_and_respect_budget():
    project = load_project(ROOT)
    for policy in [f"S{i}" for i in range(8)]:
        result = run_simulation(project, policy, seed=7, overrides={"years": 8})
        assert 0 <= result["survival_100"] <= 1
        assert result["species_retained_100"] <= len(project.species)
        assert result["cost"] >= 0
        assert result["cost"] <= result["available_budget"] + 1e-8
        if policy == "S0":
            assert result["cost"] == 0


def test_stable_habitat_harmful_relocation_not_advantageous():
    project = load_project(ROOT)
    overrides = {
        "years": 40,
        "scenario": "stationary",
        "habitat_deterioration": 0.0,
        "climate_velocity": 0.0,
        "relocation_mortality": 0.30,
        "relocation_stress": 0.65,
        "movement_disease_risk": 0.40,
        "catastrophe_probability": 0.0,
        "funding_collapse_probability": 0.0,
    }
    fixed = run_simulation(project, "S6", 11, overrides)
    circulation = run_simulation(project, "S4", 11, overrides)
    assert circulation["relocation_burden"] > fixed["relocation_burden"]
    assert circulation["lifetime_welfare"] <= fixed["lifetime_welfare"] * 1.15


def test_origin_collapse_can_penalize_refuge_and_return():
    project = load_project(ROOT)
    overrides = {
        "years": 60,
        "scenario": "abrupt_collapse",
        "climate_velocity": 0.04,
        "catastrophe_probability": 0.0,
    }
    origin = run_simulation(project, "S3", 23, overrides)
    global_allocation = run_simulation(project, "S5", 23, overrides)
    assert global_allocation["survival_100"] > origin["survival_100"]
    assert global_allocation["wild_abundance"] > origin["wild_abundance"]


def test_s3_uses_refuge_and_returns_when_origin_recovers():
    project = load_project(ROOT)
    refuge = run_simulation(
        project,
        "S3",
        23,
        {
            "years": 20,
            "scenario": "abrupt_collapse",
            "catastrophe_probability": 0.0,
            "s3_refuge_trigger": 0.70,
            "s3_return_threshold": 0.95,
        },
    )
    restored = run_simulation(
        project,
        "S3",
        23,
        {
            "years": 20,
            "scenario": "restoration",
            "habitat_deterioration": 0.05,
            "catastrophe_probability": 0.0,
            "s3_refuge_trigger": 0.65,
            "s3_return_threshold": 0.60,
            "s3_return_delay": 2,
        },
    )
    assert refuge["refuge_moves"] > 0
    assert restored["refuge_moves"] > 0
    assert restored["origin_returns"] > 0


def test_relocation_mortality_applies_only_to_moved_agents():
    project = load_project(ROOT)
    no_move = run_simulation(
        project,
        "S6",
        19,
        {
            "years": 1,
            "relocation_mortality": 1.0,
            "catastrophe_probability": 0.0,
        },
    )
    assert no_move["relocation_burden"] == 0
    assert no_move["total_abundance"] > 0


def test_stable_benign_environment_does_not_require_intervention():
    project = load_project(ROOT)
    benign = run_simulation(
        project,
        "S0",
        17,
        {
            "years": 100,
            "scenario": "stationary",
            "habitat_deterioration": 0.0,
            "climate_velocity": 0.0,
            "catastrophe_probability": 0.0,
            "anthropogenic_pressure_multiplier": 0.0,
            "predation_multiplier": 0.5,
            "mortality_multiplier": 0.75,
        },
    )
    assert benign["species_retained_100"] >= 5


def test_severe_captivity_burden_reduces_welfare():
    project = load_project(ROOT)
    overrides = {"years": 35, "captivity_welfare_penalty": 0.70}
    captivity = run_simulation(project, "S2", 23, overrides)
    habitat = run_simulation(project, "S6", 23, overrides)
    assert captivity["lifetime_welfare"] < habitat["lifetime_welfare"]


def test_near_zero_survey_cost_increases_discovery():
    project = load_project(ROOT)
    low_cost = run_simulation(project, "S7", 31, {"years": 60, "survey_cost": 0.1})
    high_cost = run_simulation(project, "S7", 31, {"years": 60, "survey_cost": 80.0})
    assert low_cost["discovered_latent"] >= high_cost["discovered_latent"]


def test_ex_situ_persistence_is_not_wild_restoration():
    project = load_project(ROOT)
    overrides = {
        "years": 60,
        "ex_situ_breeding_benefit": 2.0,
        "release_survival_penalty": 0.95,
        "movement_disease_risk": 0.0,
        "relocation_mortality": 0.05,
        "catastrophe_probability": 0.0,
    }
    captivity = run_simulation(project, "S2", 10, overrides)
    assert captivity["total_abundance"] > 0
    assert captivity["wild_abundance"] == 0


def test_no_latent_species_recovers_observed_species_behavior():
    project = load_project(ROOT)
    known_project = type(project)(
        config=project.config,
        species=project.species[project.species.known].reset_index(drop=True),
        nodes=project.nodes,
    )
    result = run_simulation(known_project, "S7", 43, {"years": 20})
    assert result["n_ebd"] == 0
    assert result["fraction_ebd"] == 0


def test_unlimited_budget_weakens_cost_constraint():
    project = load_project(ROOT)
    low = run_simulation(project, "S7", 47, {"years": 25, "initial_budget": 25.0})
    high = run_simulation(project, "S7", 47, {"years": 25, "initial_budget": 10000.0})
    assert high["cost"] > low["cost"]
    assert high["biobank_coverage"] >= low["biobank_coverage"]


def test_high_movement_disease_makes_circulation_riskier():
    project = load_project(ROOT)
    overrides = {"years": 35, "movement_disease_risk": 0.95}
    circulation = run_simulation(project, "S4", 59, overrides)
    habitat = run_simulation(project, "S6", 59, overrides)
    assert circulation["relocation_burden"] > habitat["relocation_burden"]
    assert np.isfinite(circulation["disease_prevalence"])
    assert circulation["disease_prevalence"] > habitat["disease_prevalence"]
    assert circulation["survival_100"] < habitat["survival_100"]


def test_welfare_includes_wild_and_managed_burdens():
    project = load_project(ROOT)
    wild = run_simulation(project, "S6", 61, {"years": 20})
    managed = run_simulation(project, "S2", 61, {"years": 20})
    disabled = run_simulation(
        project,
        "S2",
        61,
        {"years": 20, "welfare_enabled": False},
    )
    assert wild["welfare_burden_predation"] > 0
    assert wild["welfare_burden_food_insecurity"] > 0
    assert managed["welfare_burden_restriction"] > 0
    assert managed["welfare_burden_crowding"] > 0
    assert disabled["mean_individual_welfare"] == 1


def test_feature_off_switches_are_mechanically_active():
    project = load_project(ROOT)
    disease_on = run_simulation(
        project,
        "S4",
        67,
        {"years": 30, "movement_disease_risk": 0.8},
    )
    disease_off = run_simulation(
        project,
        "S4",
        67,
        {
            "years": 30,
            "movement_disease_risk": 0.8,
            "disease_enabled": False,
        },
    )
    biobank_off = run_simulation(
        project,
        "S7",
        67,
        {"years": 30, "biobank_enabled": False},
    )
    assert disease_on["disease_prevalence"] > 0
    assert disease_on["quarantine_cost"] > 0
    assert disease_off["disease_prevalence"] == 0
    assert disease_off["quarantine_cost"] == 0
    assert biobank_off["biobank_coverage"] == 0


def test_engagement_sign_changes_feedback_direction():
    project = load_project(ROOT)
    common = {"years": 20, "engagement_habitat_feedback": 0.0}
    positive = run_simulation(
        project,
        "S2",
        71,
        {**common, "engagement_coefficient": 0.18},
    )
    zero = run_simulation(
        project,
        "S2",
        71,
        {**common, "engagement_coefficient": 0.0},
    )
    negative = run_simulation(
        project,
        "S2",
        71,
        {**common, "engagement_coefficient": -0.18},
    )
    assert positive["engagement"] > zero["engagement"] > negative["engagement"]
    assert positive["available_budget"] > zero["available_budget"]


def test_information_effect_does_not_use_hindsight_action_retention():
    outcomes = pd.DataFrame(
        [
            {
                "policy": "S7",
                "seed": 1,
                "oracle": False,
                "survival_100": 0.8,
                "future_option_value": 0.8,
                "habitat_integrity": 0.8,
                "fraction_ebd": 0.1,
                "mean_individual_welfare": 0.8,
            },
            {
                "policy": "S7",
                "seed": 1,
                "oracle": True,
                "survival_100": 0.1,
                "future_option_value": 0.1,
                "habitat_integrity": 0.1,
                "fraction_ebd": 0.9,
                "mean_individual_welfare": 0.1,
            },
        ]
    )
    information = information_value(
        outcomes,
        {
            "survival_100": 0.35,
            "future_option_value": 0.20,
            "habitat_integrity": 0.15,
            "ebd_avoidance": 0.15,
            "mean_individual_welfare": 0.15,
        },
    )
    utility = information[information.metric == "decision_utility"].iloc[0]
    assert utility.estimate < 0
