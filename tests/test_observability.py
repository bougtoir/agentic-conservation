from pathlib import Path

import numpy as np

from agentic_conservation.simulation import (
    _initialize_agents,
    _keyed_rng,
    _observed_state,
    load_project,
    run_simulation,
)

ROOT = Path(__file__).resolve().parents[1]


def test_keyed_rng_separates_processes_and_years():
    first = _keyed_rng(41, "catastrophe", 7).random(5)
    repeated = _keyed_rng(41, "catastrophe", 7).random(5)
    other_process = _keyed_rng(41, "observation", 7).random(5)
    other_year = _keyed_rng(41, "catastrophe", 8).random(5)
    assert np.array_equal(first, repeated)
    assert not np.array_equal(first, other_process)
    assert not np.array_equal(first, other_year)


def test_feasible_observation_does_not_access_current_quality():
    project = load_project(ROOT)
    agents = _initialize_agents(project, _keyed_rng(3, "initialization"))
    stages = np.full(len(project.species), 5, dtype=np.int8)
    delayed = np.full(len(project.nodes), 0.4)
    low_current = np.full(len(project.nodes), 0.1)
    high_current = np.full(len(project.nodes), 0.9)
    low = _observed_state(
        agents,
        project,
        stages,
        delayed,
        low_current,
        _keyed_rng(3, "observation", 1),
        False,
    )
    high = _observed_state(
        agents,
        project,
        stages,
        delayed,
        high_current,
        _keyed_rng(3, "observation", 1),
        False,
    )
    assert np.array_equal(low[0], high[0])
    assert np.array_equal(low[1], high[1])


def test_oracle_receives_current_quality_without_future_lookahead():
    project = load_project(ROOT)
    agents = _initialize_agents(project, _keyed_rng(3, "initialization"))
    stages = np.full(len(project.species), 5, dtype=np.int8)
    delayed = np.full(len(project.nodes), 0.4)
    current = np.linspace(0.2, 0.8, len(project.nodes))
    _, observed_quality = _observed_state(
        agents,
        project,
        stages,
        delayed,
        current,
        _keyed_rng(3, "observation", 1),
        True,
    )
    assert np.array_equal(observed_quality, current)


def test_detectability_and_survey_effort_change_discovery():
    project = load_project(ROOT)
    high_detectability = project.species.copy()
    high_detectability.loc[~high_detectability.known, "detectability"] = 1.0
    low_detectability = project.species.copy()
    low_detectability.loc[~low_detectability.known, "detectability"] = 1e-9
    project_type = type(project)
    high = run_simulation(
        project_type(project.config, high_detectability, project.nodes),
        "S7",
        37,
        {
            "years": 40,
            "survey_cost": 0.01,
            "scenario": "stationary",
            "catastrophe_probability": 0.0,
        },
    )
    low = run_simulation(
        project_type(project.config, low_detectability, project.nodes),
        "S7",
        37,
        {
            "years": 40,
            "survey_cost": 1000.0,
            "background_detection_probability": 0.0,
            "scenario": "stationary",
            "catastrophe_probability": 0.0,
        },
    )
    assert high["discovered_latent"] >= low["discovered_latent"]


def test_zero_survey_allocation_remains_valid_ebd_boundary():
    project = load_project(ROOT)
    allocation = dict(project.config["policy_allocations"]["S7"])
    allocation["habitat"] += allocation["survey"]
    allocation["survey"] = 0.0
    result = run_simulation(
        project,
        "S7",
        39,
        {
            "years": 30,
            "policy_allocations": {"S7": allocation},
            "background_detection_probability": 0.0,
        },
    )
    assert 0 <= result["fraction_ebd"] <= 1
    assert result["discovered_latent"] == 0
