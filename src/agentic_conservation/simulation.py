from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

WILD_TYPES = {
    "original_wild_habitat",
    "alternative_wild_habitat",
    "protected_reserve",
    "semi_wild_pre_release",
}
MANAGED_TYPES = {
    "protected_reserve",
    "conventional_zoo",
    "conservation_zoo",
    "breeding_center",
    "semi_wild_pre_release",
    "rehabilitation_facility",
}
POLICIES = [f"S{i}" for i in range(8)]
RNG_STREAMS = {
    "initialization": 1,
    "funding": 2,
    "catastrophe": 3,
    "observation": 4,
    "discovery": 5,
    "movement": 6,
    "disease": 7,
    "demography": 8,
}


@dataclass(frozen=True)
class Project:
    config: dict
    species: pd.DataFrame
    nodes: pd.DataFrame


@dataclass(frozen=True)
class MovementResult:
    moved_indices: np.ndarray
    released_indices: np.ndarray
    refuge_moves: int
    origin_returns: int


def _keyed_rng(seed: int, process: str, year: int = 0) -> np.random.Generator:
    return np.random.default_rng(
        np.random.SeedSequence([seed, RNG_STREAMS[process], year])
    )


def load_project(root: str | Path) -> Project:
    root = Path(root)
    with (root / "config/base.json").open() as handle:
        config = json.load(handle)
    species = pd.read_json(root / "config/species.json")
    nodes = pd.read_json(root / "config/nodes.json")
    return Project(config=config, species=species, nodes=nodes)


def _initialize_agents(project: Project, rng: np.random.Generator) -> dict[str, np.ndarray]:
    species = project.species
    total = int(species.initial_n.sum())
    sp = np.repeat(np.arange(len(species)), species.initial_n.to_numpy(dtype=int))
    origin = np.zeros(total, dtype=np.int16)
    return {
        "species": sp.astype(np.int16),
        "sex": rng.integers(0, 2, total, dtype=np.int8),
        "age": rng.integers(0, 16, total, dtype=np.int16),
        "origin": origin.copy(),
        "node": origin.copy(),
        "founder": np.arange(total, dtype=np.int32),
        "inbreeding": np.zeros(total, dtype=float),
        "health": rng.uniform(0.75, 1.0, total),
        "infection": (rng.random(total) < 0.025).astype(np.int8),
        "wildness": rng.uniform(0.72, 1.0, total),
        "habituation": rng.uniform(0.0, 0.15, total),
        "stress_tolerance": rng.uniform(0.25, 0.9, total),
        "foraging": rng.uniform(0.65, 1.0, total),
        "release_ready": rng.uniform(0.5, 0.9, total),
        "alive": np.ones(total, dtype=bool),
    }


def _append_births(
    agents: dict[str, np.ndarray],
    births: list[tuple[int, int, int, float]],
    rng: np.random.Generator,
    maximum: int,
) -> None:
    available = maximum - int(np.sum(agents["alive"]))
    if available <= 0 or not births:
        return
    births = births[:available]
    n = len(births)
    species = np.array([x[0] for x in births], dtype=np.int16)
    node = np.array([x[1] for x in births], dtype=np.int16)
    founder = np.array([x[2] for x in births], dtype=np.int32)
    inbreeding = np.array([x[3] for x in births], dtype=float)
    additions = {
        "species": species,
        "sex": rng.integers(0, 2, n, dtype=np.int8),
        "age": np.zeros(n, dtype=np.int16),
        "origin": node.copy(),
        "node": node,
        "founder": founder,
        "inbreeding": inbreeding,
        "health": rng.uniform(0.85, 1.0, n),
        "infection": np.zeros(n, dtype=np.int8),
        "wildness": rng.uniform(0.75, 1.0, n),
        "habituation": rng.uniform(0.0, 0.08, n),
        "stress_tolerance": rng.uniform(0.25, 0.9, n),
        "foraging": rng.uniform(0.70, 1.0, n),
        "release_ready": rng.uniform(0.35, 0.65, n),
        "alive": np.ones(n, dtype=bool),
    }
    dead = np.flatnonzero(~agents["alive"])
    reused = min(len(dead), n)
    if reused:
        slots = dead[:reused]
        for key, value in additions.items():
            agents[key][slots] = value[:reused]
    if reused < n:
        for key, value in additions.items():
            agents[key] = np.concatenate([agents[key], value[reused:]])


def _quality_update(
    baseline: np.ndarray,
    year: int,
    project: Project,
    rng: np.random.Generator,
    habitat_spend: float,
) -> tuple[np.ndarray, str]:
    cfg = project.config
    nodes = project.nodes
    quality = baseline.copy()
    wild = nodes["type"].isin(WILD_TYPES).to_numpy()
    scenario = cfg["scenario"]
    deterioration = cfg["habitat_deterioration"]
    if scenario == "stationary":
        trend = 0.0
    elif scenario == "abrupt_collapse":
        trend = 0.0
    elif scenario == "slow_deterioration":
        trend = deterioration * 0.5
    elif scenario == "rapid_deterioration":
        trend = deterioration * 2.0
    elif scenario == "restoration":
        trend = -deterioration * 0.6
    else:
        trend = deterioration
    quality[wild] -= trend
    directional = cfg["climate_velocity"] * year / max(cfg["years"], 1)
    quality[0] -= directional
    quality[1] += directional * 0.65
    quality[wild] += (
        habitat_spend
        / max(cfg["initial_budget"], 1.0)
        * cfg["habitat_protection_efficiency"]
        * nodes.loc[wild, "restoration"].to_numpy()
    )
    event = "none"
    if scenario == "abrupt_collapse" and year == max(2, cfg["years"] // 3):
        quality[0] -= 0.70
        event = "abrupt_collapse:origin"
    if rng.random() < cfg["catastrophe_probability"]:
        candidates = np.flatnonzero(wild)
        hit = int(rng.choice(candidates))
        quality[hit] -= rng.uniform(0.16, 0.38)
        event_type = str(rng.choice(["wildfire", "flood", "heatwave"]))
        event = f"{event_type}:{nodes.iloc[hit]['id']}"
    return np.clip(quality, 0.05, 0.98), event


def _species_node_suitability(project: Project, quality: np.ndarray) -> np.ndarray:
    species = project.species
    nodes = project.nodes
    specificity = species.habitat_specificity.to_numpy()[:, None]
    breadth = species.niche_breadth.to_numpy()[:, None]
    wild = nodes["type"].isin(WILD_TYPES).to_numpy()[None, :]
    managed = nodes["type"].isin(MANAGED_TYPES).to_numpy()[None, :]
    base = quality[None, :] * (0.72 + 0.28 * breadth)
    base -= specificity * (1.0 - quality[None, :]) * 0.32
    tolerance = species.captivity_tolerance.to_numpy()[:, None]
    base += managed * (~wild) * (tolerance - 0.5) * 0.25
    migration = species.migration_need.to_numpy()[:, None]
    base -= managed * (~wild) * migration * 0.24
    return np.clip(base, 0.02, 0.99)


def _observed_state(
    agents: dict[str, np.ndarray],
    project: Project,
    stages: np.ndarray,
    delayed_quality: np.ndarray,
    current_quality: np.ndarray,
    rng: np.random.Generator,
    oracle: bool,
) -> tuple[np.ndarray, np.ndarray]:
    counts = np.zeros(len(project.species), dtype=float)
    alive = agents["alive"]
    for sp in range(len(project.species)):
        counts[sp] = np.sum(alive & (agents["species"] == sp))
    if oracle:
        return counts, current_quality.copy()
    visible = stages >= 2
    noise = rng.lognormal(0.0, project.config["observation_noise"], len(counts))
    observed = np.where(visible, np.maximum(0.0, counts * noise), np.nan)
    quality = np.clip(
        delayed_quality
        + rng.normal(0.0, project.config["quality_observation_noise"], len(delayed_quality)),
        0.0,
        1.0,
    )
    return observed, quality


def _target_node(
    policy: str,
    sp: int,
    decision_suitability: np.ndarray,
    origin_fidelity: float,
    project: Project,
) -> int:
    nodes = project.nodes
    score = decision_suitability[sp].copy()
    score -= nodes.cost.to_numpy() * 0.04
    score += nodes.research.to_numpy() * 0.03
    score[8] = -1.0
    if policy == "S2":
        return int(nodes.index[nodes.id == "zoo"][0])
    if policy == "S3":
        return int(nodes.index[nodes.id == "origin"][0])
    if policy == "S4":
        score += nodes["type"].isin(
            {"protected_reserve", "conservation_zoo", "breeding_center", "semi_wild_pre_release"}
        ).to_numpy() * 0.10
    if policy == "S7":
        score += nodes.restoration.to_numpy() * 0.08
        score += nodes.research.to_numpy() * 0.05
    if policy == "S6":
        return int(nodes.index[nodes.id == "origin"][0])
    score[0] += origin_fidelity
    return int(np.argmax(score))


def _move_agents(
    agents: dict[str, np.ndarray],
    project: Project,
    policy: str,
    observed_counts: np.ndarray,
    decision_suitability: np.ndarray,
    stages: np.ndarray,
    rescue_spend: float,
    year: int,
    rng: np.random.Generator,
) -> MovementResult:
    if policy in {"S0", "S6"} or rescue_spend <= 0:
        empty = np.array([], dtype=int)
        return MovementResult(empty, empty, 0, 0)
    nodes = project.nodes
    alive = agents["alive"]
    moved = 0
    moved_indices: list[np.ndarray] = []
    released_indices: list[np.ndarray] = []
    refuge_moves = 0
    origin_returns = 0
    capacity = max(1, int(rescue_spend / 2.5))
    visible_species = np.flatnonzero(stages >= 2)
    if len(visible_species) == 0:
        empty = np.array([], dtype=int)
        return MovementResult(empty, empty, 0, 0)
    risk = []
    for sp in visible_species:
        count = observed_counts[sp]
        origin_score = decision_suitability[sp, 0]
        risk.append((np.nan_to_num(1.0 / (1.0 + count)) + (1.0 - origin_score), int(sp)))
    for _, sp in sorted(risk, reverse=True):
        if moved >= capacity:
            break
        mask = alive & (agents["species"] == sp)
        if policy == "S1":
            mask &= nodes.iloc[agents["node"]]["type"].isin(MANAGED_TYPES).to_numpy()
        elif policy == "S3":
            origin_score = decision_suitability[sp, 0]
            if origin_score < project.config["s3_refuge_trigger"]:
                mask &= agents["node"] == 0
                refuge_targets = nodes.index[
                    nodes.id.isin(["conservation_zoo", "breeding"])
                ].to_numpy()
                target_scores = (
                    decision_suitability[sp, refuge_targets]
                )
                target = int(refuge_targets[np.argmax(target_scores)])
                movement_mode = "refuge"
            elif (
                year >= project.config["s3_return_delay"]
                and origin_score >= project.config["s3_return_threshold"]
            ):
                mask &= (agents["node"] != 0) & (agents["release_ready"] >= 0.40)
                target = 0
                movement_mode = "return"
            else:
                continue
        else:
            current_score = decision_suitability[sp, agents["node"]]
            mask &= current_score < 0.58
        candidates = np.flatnonzero(mask)
        if len(candidates) == 0:
            continue
        if policy != "S3":
            target = _target_node(
                policy,
                sp,
                decision_suitability,
                project.config["origin_fidelity"] if policy in {"S4", "S7"} else 0.0,
                project,
            )
            movement_mode = "other"
        if policy == "S1":
            wild_targets = np.flatnonzero(nodes["type"].isin(WILD_TYPES).to_numpy())
            target_scores = decision_suitability[sp, wild_targets]
            target = int(wild_targets[np.argmax(target_scores)])
        candidates = candidates[agents["node"][candidates] != target]
        if len(candidates) == 0:
            continue
        target_capacity = int(nodes.iloc[target].capacity)
        target_occupancy = int(
            np.sum(
                alive
                & (agents["species"] == sp)
                & (agents["node"] == target)
            )
        )
        target_space = max(0, target_capacity - target_occupancy)
        take = min(
            len(candidates),
            capacity - moved,
            max(1, len(candidates) // 5),
            target_space,
        )
        if take <= 0:
            continue
        chosen = rng.choice(candidates, take, replace=False)
        previous = agents["node"][chosen].copy()
        agents["node"][chosen] = target
        agents["health"][chosen] *= 1.0 - project.config["relocation_stress"] * (
            1.0 - agents["stress_tolerance"][chosen]
        )
        agents["habituation"][chosen] = np.clip(
            agents["habituation"][chosen] + (0.08 if nodes.iloc[target]["managed"] else -0.05),
            0.0,
            1.0,
        )
        agents["wildness"][chosen] = np.clip(
            agents["wildness"][chosen] + (0.06 if nodes.iloc[target]["wild"] else -0.07),
            0.0,
            1.0,
        )
        agents["release_ready"][chosen] = np.clip(
            agents["release_ready"][chosen]
            + (0.05 if nodes.iloc[target]["type"] == "semi_wild_pre_release" else -0.01),
            0.0,
            1.0,
        )
        moved += take
        moved_indices.append(chosen)
        from_managed = nodes.iloc[previous]["managed"].to_numpy()
        to_wild = bool(nodes.iloc[target]["wild"])
        released = chosen[from_managed & to_wild]
        if len(released):
            released_indices.append(released)
        if movement_mode == "refuge":
            refuge_moves += take
        elif movement_mode == "return":
            origin_returns += take
    all_moved = (
        np.concatenate(moved_indices) if moved_indices else np.array([], dtype=int)
    )
    all_released = (
        np.concatenate(released_indices)
        if released_indices
        else np.array([], dtype=int)
    )
    return MovementResult(all_moved, all_released, refuge_moves, origin_returns)


def _discover(
    stages: np.ndarray,
    project: Project,
    survey_spend: float,
    habitat_spend: float,
    extant: np.ndarray,
    rng: np.random.Generator,
) -> None:
    scale = survey_spend / max(project.config["survey_cost"], 1e-9)
    background = project.config["background_detection_probability"]
    for sp, row in project.species.iterrows():
        if row["known"] or stages[sp] >= 5 or not extant[sp]:
            continue
        stage = stages[sp]
        detect = float(row.detectability)
        probabilities = [
            min(0.95, background + 0.16 * scale * detect),
            min(0.85, background + 0.12 * scale),
            min(0.75, background + 0.10 * scale),
            min(0.65, background + 0.09 * scale),
            min(0.60, background + 0.06 * scale + habitat_spend / 1000.0),
        ]
        if rng.random() < probabilities[stage]:
            stages[sp] += 1


def _genetic_metrics(agents: dict[str, np.ndarray], species_count: int) -> tuple[float, float]:
    alive = agents["alive"]
    founder_effective = []
    mean_inbreeding = []
    for sp in range(species_count):
        mask = alive & (agents["species"] == sp)
        if not np.any(mask):
            continue
        _, counts = np.unique(agents["founder"][mask], return_counts=True)
        frequencies = counts / counts.sum()
        founder_effective.append(1.0 / np.sum(frequencies**2))
        mean_inbreeding.append(float(np.mean(agents["inbreeding"][mask])))
    return (
        float(np.mean(founder_effective)) if founder_effective else 0.0,
        float(np.mean(mean_inbreeding)) if mean_inbreeding else np.nan,
    )


def run_simulation(
    project: Project,
    policy: str,
    seed: int,
    overrides: dict | None = None,
    oracle: bool = False,
    return_trajectory: bool = False,
) -> dict:
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy}")
    if overrides:
        overrides = dict(overrides)
        config = dict(project.config)
        latent_fraction = overrides.pop("latent_fraction_proxy", None)
        latent_detectability = overrides.pop("latent_detectability_override", None)
        config.update(overrides)
        species = project.species.copy()
        if latent_fraction is not None:
            n_latent = int(round(float(latent_fraction) * len(species)))
            species["known"] = True
            if n_latent:
                species.loc[species.index[-n_latent:], "known"] = False
        if latent_detectability is not None:
            species.loc[~species.known, "detectability"] = float(
                latent_detectability
            )
        project = Project(config=config, species=species, nodes=project.nodes)
    cfg = project.config
    agents = _initialize_agents(project, _keyed_rng(seed, "initialization"))
    quality = project.nodes.base_quality.to_numpy(dtype=float)
    if "origin_quality_override" in cfg:
        quality[0] = float(cfg["origin_quality_override"])
    quality_history = [quality.copy()]
    stages = np.where(project.species.known.to_numpy(), 5, 0).astype(np.int8)
    ebd_year = np.full(len(project.species), -1, dtype=np.int16)
    allocation = cfg["policy_allocations"][policy]
    budget = 0.0 if policy == "S0" else cfg["initial_budget"]
    total_cost = 0.0
    total_available_budget = 0.0
    cumulative_welfare = 0.0
    cumulative_mean_welfare = 0.0
    cumulative_welfare_burdens = {
        "predation": 0.0,
        "food_insecurity": 0.0,
        "crowding": 0.0,
        "restriction": 0.0,
        "infection": 0.0,
        "habituation": 0.0,
        "relocation": 0.0,
    }
    cumulative_disease = 0.0
    cumulative_quarantine_cost = 0.0
    relocation_burden = 0.0
    successful_reintroductions = 0
    refuge_moves = 0
    origin_returns = 0
    biobank = np.zeros(len(project.species), dtype=float)
    engagement = 0.5
    trajectory = []
    survival_50 = np.nan
    biodiversity_50 = np.nan
    events: list[str] = []

    for year in range(1, cfg["years"] + 1):
        funding_rng = _keyed_rng(seed, "funding", year)
        catastrophe_rng = _keyed_rng(seed, "catastrophe", year)
        observation_rng = _keyed_rng(seed, "observation", year)
        discovery_rng = _keyed_rng(seed, "discovery", year)
        movement_rng = _keyed_rng(seed, "movement", year)
        disease_rng = _keyed_rng(seed, "disease", year)
        demography_rng = _keyed_rng(seed, "demography", year)
        if (
            policy != "S0"
            and funding_rng.random() < cfg["funding_collapse_probability"]
        ):
            budget *= 0.72
            events.append(f"{year}:funding_collapse")
        budget = max(0.0, budget)
        allocation_total = sum(allocation.values())
        if allocation_total > 1.0 + 1e-9:
            raise ValueError(f"{policy} allocation exceeds the annual budget")
        total_available_budget += budget
        spending = {
            key: budget * value / max(allocation_total, 1.0)
            for key, value in allocation.items()
        }
        total_cost += sum(spending.values())
        new_quality, event = _quality_update(
            quality,
            year,
            project,
            catastrophe_rng,
            spending.get("habitat", 0.0),
        )
        if event != "none":
            events.append(f"{year}:{event}")
        quality = new_quality
        quality_history.append(quality.copy())
        delay = max(0, int(cfg["observation_delay"]))
        delayed_index = max(0, len(quality_history) - 1 - delay)
        delayed_quality = quality_history[delayed_index]
        suitability = _species_node_suitability(project, quality)
        observed_counts, observed_quality = _observed_state(
            agents,
            project,
            stages,
            delayed_quality,
            quality,
            observation_rng,
            oracle,
        )
        decision_suitability = _species_node_suitability(project, observed_quality)
        extant_before_discovery = np.array(
            [
                np.any(agents["alive"] & (agents["species"] == species_id))
                for species_id in range(len(project.species))
            ]
        )
        _discover(
            stages,
            project,
            spending.get("survey", 0.0),
            spending.get("habitat", 0.0),
            extant_before_discovery,
            discovery_rng,
        )
        movement = _move_agents(
            agents,
            project,
            policy,
            observed_counts,
            decision_suitability,
            stages,
            spending.get("rescue", 0.0),
            year,
            movement_rng,
        )
        moved = len(movement.moved_indices)
        released = len(movement.released_indices)
        successful_reintroductions += released
        refuge_moves += movement.refuge_moves
        origin_returns += movement.origin_returns
        relocation_burden += moved * cfg["relocation_stress"]

        alive = agents["alive"]
        if moved:
            movement_deaths = movement.moved_indices[
                movement_rng.random(moved) < cfg["relocation_mortality"]
            ]
            agents["alive"][movement_deaths] = False
        if released:
            release_deaths = movement.released_indices[
                agents["alive"][movement.released_indices]
                & (movement_rng.random(released) < cfg["release_survival_penalty"])
            ]
            agents["alive"][release_deaths] = False
        if cfg.get("disease_enabled", True) and moved:
            quarantine_cost = moved * cfg["quarantine_cost_per_move"]
            quarantine_coverage = min(
                1.0,
                spending.get("rescue", 0.0) / max(quarantine_cost, 1e-9),
            )
            cumulative_quarantine_cost += min(
                quarantine_cost,
                spending.get("rescue", 0.0),
            )
            moved_susceptible = movement.moved_indices[
                agents["alive"][movement.moved_indices]
                & (agents["infection"][movement.moved_indices] == 0)
            ]
            if len(moved_susceptible):
                infected_in_transit = moved_susceptible[
                    disease_rng.random(len(moved_susceptible))
                    < cfg["movement_disease_risk"]
                    * (
                        1.0
                        - quarantine_coverage
                        * cfg["quarantine_effectiveness"]
                    )
                ]
                agents["infection"][infected_in_transit] = 1

        alive = agents["alive"]
        node = agents["node"]
        sp = agents["species"]
        if cfg.get("disease_enabled", True):
            for node_id in range(len(project.nodes) - 1):
                local = alive & (node == node_id)
                if not np.any(local):
                    continue
                prevalence = float(np.mean(agents["infection"][local] == 1))
                susceptible = local & (agents["infection"] == 0)
                infection_p = np.clip(
                    project.nodes.iloc[node_id].disease * prevalence,
                    0.0,
                    0.65,
                )
                agents["infection"][
                    susceptible & (disease_rng.random(len(alive)) < infection_p)
                ] = 1
                infected = local & (agents["infection"] == 1)
                recover = infected & (disease_rng.random(len(alive)) < 0.32)
                agents["infection"][recover] = 2
        else:
            agents["infection"][:] = 0

        alive = agents["alive"]
        node = agents["node"]
        sp = agents["species"]
        managed = project.nodes.iloc[node]["managed"].to_numpy()
        wild = project.nodes.iloc[node]["wild"].to_numpy()
        habitat = suitability[sp, node]
        pressure = (
            project.nodes.iloc[node].anthropogenic.to_numpy()
            * project.species.iloc[sp].anthropogenic_sensitivity.to_numpy()
            * cfg["anthropogenic_pressure_multiplier"]
        )
        infection_penalty = (agents["infection"] == 1) * 0.14
        base_mortality = (
            project.species.iloc[sp].mortality.to_numpy()
            * cfg["mortality_multiplier"]
        )
        survival_p = (
            1.0
            - base_mortality
            - (1.0 - habitat) * 0.24
            - pressure * 0.08
            - infection_penalty
        )
        survival_p += managed * project.nodes.iloc[node].research.to_numpy() * 0.035
        survival_p -= (
            wild
            * project.nodes.iloc[node].predation.to_numpy()
            * cfg["predation_multiplier"]
            * 0.035
        )
        survival_p -= (1.0 - agents["health"]) * 0.08
        survival_p -= (
            agents["inbreeding"]
            * cfg["inbreeding_mortality_penalty"]
        )
        survival_p = np.clip(survival_p, 0.05, 0.995)
        agents["alive"][
            alive & (demography_rng.random(len(alive)) > survival_p)
        ] = False

        alive = agents["alive"]
        agents["age"][alive] += 1
        agents["health"][alive] = np.clip(
            agents["health"][alive]
            + demography_rng.normal(0.0, 0.015, np.sum(alive)),
            0.35,
            1.0,
        )
        births: list[tuple[int, int, int, float]] = []
        for species_id in range(len(project.species)):
            for node_id in range(len(project.nodes) - 1):
                local = alive & (agents["species"] == species_id) & (agents["node"] == node_id)
                females = local & (agents["sex"] == 0) & (agents["age"] >= 2)
                males = local & (agents["sex"] == 1) & (agents["age"] >= 2)
                if not np.any(females) or not np.any(males):
                    continue
                row = project.species.iloc[species_id]
                density = np.sum(local) / max(project.nodes.iloc[node_id].capacity, 1)
                rate = (
                    (row.mortality + row.growth)
                    * (0.50 + row.fertility)
                    * suitability[species_id, node_id]
                    * max(0.05, 1.0 - density)
                    * 5.0
                )
                if project.nodes.iloc[node_id].managed:
                    rate *= 1.0 + cfg["ex_situ_breeding_benefit"] * (
                        spending.get("ex_situ", 0.0) / max(budget, 1.0)
                    )
                local_infection = float(
                    np.mean(agents["infection"][local] == 1)
                )
                rate *= max(
                    0.05,
                    1.0
                    - local_infection
                    * cfg["infection_fertility_penalty"],
                )
                rate *= max(
                    0.05,
                    1.0
                    - float(np.mean(agents["inbreeding"][local]))
                    * cfg["inbreeding_fertility_penalty"],
                )
                expected = np.sum(females) * rate
                number = int(demography_rng.poisson(max(0.0, expected)))
                if number == 0:
                    continue
                mothers = demography_rng.choice(
                    np.flatnonzero(females),
                    number,
                    replace=True,
                )
                male_indices = np.flatnonzero(males)
                diversity_aware = (
                    cfg.get("genetics_enabled", True)
                    and spending.get("genetics", 0.0) > 0
                    and policy != "S0"
                )
                for mother in mothers:
                    father_pool = male_indices
                    if diversity_aware:
                        different_founder = father_pool[
                            agents["founder"][father_pool]
                            != agents["founder"][mother]
                        ]
                        if len(different_founder):
                            father_pool = different_founder
                        weights = np.clip(
                            1.0 - agents["inbreeding"][father_pool],
                            0.05,
                            None,
                        )
                        weights /= weights.sum()
                        father = int(
                            demography_rng.choice(
                                father_pool,
                                p=weights,
                            )
                        )
                    else:
                        father = int(demography_rng.choice(father_pool))
                    same_founder = agents["founder"][mother] == agents["founder"][father]
                    child_inbreeding = (
                        0.5
                        * (agents["inbreeding"][mother] + agents["inbreeding"][father])
                        + (0.08 if same_founder else 0.0)
                    )
                    if diversity_aware:
                        child_inbreeding *= 0.82
                    founder = int(
                        agents["founder"][mother]
                        if demography_rng.random() < 0.5
                        else agents["founder"][father]
                    )
                    births.append((species_id, node_id, founder, child_inbreeding))
        _append_births(
            agents,
            births,
            demography_rng,
            int(cfg["max_individuals"]),
        )

        alive = agents["alive"]
        biobank *= 1.0 - cfg["biobank_annual_decay"]
        for species_id in range(len(project.species)):
            extant = np.any(alive & (agents["species"] == species_id))
            if (
                not extant
                and not project.species.iloc[species_id].known
                and stages[species_id] < 2
                and ebd_year[species_id] < 0
            ):
                ebd_year[species_id] = year
            if (
                extant
                and stages[species_id] >= 2
                and cfg.get("biobank_enabled", True)
            ):
                biobank[species_id] = np.clip(
                    biobank[species_id]
                    + spending.get("biobank", 0.0) / max(budget, 1.0) * 0.05,
                    0.0,
                    1.0,
                )

        alive = agents["alive"]
        node = agents["node"]
        managed = project.nodes.iloc[node]["managed"].to_numpy()
        wild = project.nodes.iloc[node]["wild"].to_numpy()
        moved_recently = np.zeros(len(alive), dtype=bool)
        moved_recently[movement.moved_indices] = True
        node_welfare = project.nodes.iloc[node].welfare.to_numpy()
        occupancy = np.zeros(len(project.nodes), dtype=float)
        for node_id in range(len(project.nodes) - 1):
            occupancy[node_id] = (
                np.sum(alive & (node == node_id))
                / max(project.nodes.iloc[node_id].capacity, 1)
            )
        migration_need = (
            project.species.iloc[agents["species"]]
            .migration_need.to_numpy()
        )
        burdens = {
            "predation": (
                wild
                * project.nodes.iloc[node].predation.to_numpy()
                * cfg["wild_predation_welfare_weight"]
            ),
            "food_insecurity": (
                1.0 - suitability[agents["species"], node]
            )
            * cfg["food_insecurity_welfare_weight"],
            "crowding": (
                managed
                * occupancy[node]
                * cfg["managed_crowding_welfare_weight"]
            ),
            "restriction": (
                managed
                * migration_need
                * cfg["managed_restriction_welfare_weight"]
            ),
            "infection": (
                agents["infection"] == 1
            )
            * cfg["infection_welfare_weight"],
            "habituation": (
                agents["habituation"]
                * migration_need
                * cfg["habituation_welfare_weight"]
            ),
            "relocation": (
                moved_recently
                * cfg["relocation_stress"]
                * cfg["relocation_welfare_weight"]
            ),
        }
        captivity_burden = (
            managed
            * cfg["captivity_welfare_penalty"]
            * (1.0 - agents["stress_tolerance"])
        )
        if cfg.get("welfare_enabled", True):
            welfare = node_welfare - captivity_burden
            for burden in burdens.values():
                welfare -= burden
        else:
            welfare = np.ones(len(alive), dtype=float)
            burdens = {
                name: np.zeros(len(alive), dtype=float)
                for name in burdens
            }
        for name, burden in burdens.items():
            cumulative_welfare_burdens[name] += (
                float(np.mean(burden[alive])) if np.any(alive) else 0.0
            )
        cumulative_welfare += float(np.sum(np.clip(welfare[alive], 0.0, 1.0)))
        cumulative_mean_welfare += (
            float(np.mean(np.clip(welfare[alive], 0.0, 1.0))) if np.any(alive) else 0.0
        )
        cumulative_disease += (
            float(np.mean(agents["infection"][alive] == 1)) if np.any(alive) else 0.0
        )
        visitor_exposure = project.nodes.iloc[node].visitor_exposure.to_numpy()
        exposure = float(np.mean(visitor_exposure[alive])) if np.any(alive) else 0.0
        habitat_signal = float(np.mean(quality[:3]))
        engagement_effect = cfg["engagement_coefficient"] * (
            exposure
            + spending.get("engagement", 0.0)
            / max(budget, 1.0)
            * 0.2
        )
        engagement = float(
            np.clip(
                engagement
                + engagement_effect
                + cfg["engagement_habitat_feedback"] * habitat_signal,
                0.0,
                1.5,
            )
        )
        if policy != "S0":
            budget = cfg["initial_budget"] * (0.82 + 0.24 * engagement)

        counts = np.array([
            np.sum(agents["alive"] & (agents["species"] == x))
            for x in range(len(project.species))
        ])
        extant = counts > 0
        if year == 50:
            survival_50 = float(np.mean(extant))
            biodiversity_50 = int(np.sum(extant))
        if return_trajectory:
            trajectory.append(
                {
                    "year": year,
                    "policy": policy,
                    "seed": seed,
                    "total_abundance": int(counts.sum()),
                    "species_retained": int(extant.sum()),
                    "latent_ebd": int(np.sum(ebd_year > 0)),
                    "wild_abundance": int(
                        np.sum(
                            agents["alive"]
                            & project.nodes.iloc[agents["node"]]["wild"].to_numpy()
                        )
                    ),
                    "mean_welfare": float(np.mean(welfare[alive])) if np.any(alive) else 0.0,
                    "engagement": engagement,
                    "habitat_integrity": float(np.mean(quality[:3])),
                    "budget": budget,
                }
            )

    alive = agents["alive"]
    counts = np.array(
        [np.sum(alive & (agents["species"] == x)) for x in range(len(project.species))]
    )
    extant = counts > 0
    founder_effective, mean_inbreeding = _genetic_metrics(agents, len(project.species))
    wild_mask = project.nodes.iloc[agents["node"]]["wild"].to_numpy()
    n_ebd = int(np.sum(ebd_year > 0))
    latent_count = int(np.sum(~project.species.known.to_numpy()))
    future_option = float(
        0.45 * np.mean(extant)
        + 0.25 * min(founder_effective / 25.0, 1.0)
        + 0.20 * np.mean(biobank)
        + 0.10 * np.mean(quality[:3])
    )
    result = {
        "policy": policy,
        "engine": {
            "S0": "none",
            "S1": "rule",
            "S2": "rule",
            "S3": "rule",
            "S4": "state_dependent_rule",
            "S5": "greedy_expected_utility",
            "S6": "rule",
            "S7": "forward_rollout_proxy",
        }[policy],
        "oracle": oracle,
        "seed": seed,
        "survival_50": survival_50,
        "survival_100": float(np.mean(extant)),
        "species_retained_50": biodiversity_50,
        "species_retained_100": int(np.sum(extant)),
        "total_abundance": int(counts.sum()),
        "wild_abundance": int(np.sum(alive & wild_mask)),
        "n_ebd": n_ebd,
        "fraction_ebd": n_ebd / max(latent_count, 1),
        "p_ebd": float(n_ebd > 0),
        "mean_time_to_ebd": float(np.mean(ebd_year[ebd_year > 0]))
        if np.any(ebd_year > 0)
        else np.nan,
        "lifetime_welfare": cumulative_welfare / max(cfg["years"], 1),
        "mean_individual_welfare": cumulative_mean_welfare / max(cfg["years"], 1),
        "founder_effective": founder_effective,
        "mean_inbreeding": mean_inbreeding,
        "heterozygosity_proxy": 1.0 - mean_inbreeding
        if np.isfinite(mean_inbreeding)
        else np.nan,
        "successful_reintroductions": successful_reintroductions,
        "refuge_moves": refuge_moves,
        "origin_returns": origin_returns,
        "cost": total_cost,
        "available_budget": total_available_budget,
        "cost_per_species_retained": total_cost / max(np.sum(extant), 1),
        "engagement": engagement,
        "habitat_integrity": float(np.mean(quality[:3])),
        "future_option_value": future_option,
        "disease_prevalence": cumulative_disease / max(cfg["years"], 1),
        "quarantine_cost": cumulative_quarantine_cost,
        "relocation_burden": relocation_burden,
        "biobank_coverage": float(np.mean(biobank)),
        "discovered_latent": int(np.sum((stages >= 2) & (~project.species.known.to_numpy()))),
        "events": "|".join(events),
    }
    for name, burden in cumulative_welfare_burdens.items():
        result[f"welfare_burden_{name}"] = burden / max(cfg["years"], 1)
    if return_trajectory:
        result["trajectory"] = trajectory
    return result
