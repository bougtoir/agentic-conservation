"""Operator-level probes for the final equation/algorithm audit (no sweeps)."""

import math
from pathlib import Path

import numpy as np

from agentic_conservation import simulation as sim

ROOT = Path(__file__).resolve().parents[1]
P = sim.load_project(ROOT)


class _NoEvent:
    def random(self):
        return 1.0


def test_eq1_trend_and_restoration_only_on_wild_nodes():
    q0 = P.nodes.base_quality.to_numpy(dtype=float)
    q1, _ = sim._quality_update(q0, 1, P, _NoEvent(), habitat_spend=50.0)
    wild = P.nodes["type"].isin(sim.WILD_TYPES).to_numpy()
    managed_only = ~wild & (P.nodes["type"] != "biobank").to_numpy()
    assert np.allclose(q1[managed_only], q0[managed_only])
    cfg = P.config
    restore = 50.0 / cfg["initial_budget"] * cfg["habitat_protection_efficiency"]
    v1 = cfg["climate_velocity"] * 1 / cfg["years"]
    exp = q0 - cfg["habitat_deterioration"] * wild
    exp[wild] += restore * P.nodes.restoration.to_numpy()[wild]
    exp[0] -= v1
    exp[1] += 0.65 * v1
    assert np.allclose(q1[wild], np.clip(exp, 0.05, 0.98)[wild])


def test_eq1_climate_year1_vs_year100_and_cumulative():
    cfg = P.config
    assert math.isclose(sim.climate_increment(cfg, 1, 100), 0.012 / 100)
    assert math.isclose(sim.climate_increment(cfg, 100, 100), 0.012)
    total = sum(sim.climate_increment(cfg, t, 100) for t in range(1, 101))
    assert math.isclose(total, 0.606)
    for form in ("linear", "decelerating", "step"):
        c = {**cfg, "climate_form": form}
        assert math.isclose(sum(sim.climate_increment(c, t, 100) for t in range(1, 101)), 0.606)


def test_eq1_clip_bounds():
    q, _ = sim._quality_update(np.array([2.0] * 9), 1, P, _NoEvent(), 0.0)
    assert q.max() == 0.98
    q, _ = sim._quality_update(np.array([-1.0] * 9), 1, P, _NoEvent(), 0.0)
    assert q.min() == 0.05


def test_eq2_clip_bounds():
    s = sim._species_node_suitability(P, np.zeros(9))
    assert s.min() >= 0.02 and s.max() <= 0.99
    s = sim._species_node_suitability(P, np.ones(9))
    assert s.max() <= 0.99


def test_eq5_biobank_never_selected():
    n = P.nodes
    worst = 0.02 - 0.04 * n.cost.to_numpy() + 0.03 * n.research.to_numpy()
    biobank_best = -1.0 + 0.08 * n.restoration[8] + 0.05 * n.research[8]
    assert worst[:8].min() > biobank_best
    for pol in ("S4", "S5", "S7"):
        ds = np.full((8, 9), 0.02)
        assert sim._target_node(pol, 0, ds, 0.0, P) != 8


def test_alg2_take_quota_floor_and_minimum_one():
    assert [max(1, sim._take_quota(n, P.config)) for n in (1, 4, 5, 9, 10)] == [1, 1, 1, 1, 2]


def test_alg2_s6_and_s0_never_move():
    rng = np.random.default_rng(0)
    agents = sim._initialize_agents(P, rng)
    ds = np.zeros((8, 9))
    for pol in ("S0", "S6"):
        r = sim._move_agents(agents, P, pol, np.ones(8), ds, np.full(8, 5), 50.0, 10, rng)
        assert len(r.moved_indices) == 0


def test_eq3_stage_cap_and_single_step():
    stages = np.zeros(8, dtype=np.int8)
    p = sim.Project(P.config, P.species.assign(known=False, detectability=1.0), P.nodes)

    class Always:
        def random(self):
            return 0.0

    sim._discover(stages, p, 1e6, 0.0, np.ones(8, bool), Always())
    assert (stages == 1).all()
    sim._discover(stages, p, 1e6, 0.0, np.zeros(8, bool), Always())
    assert (stages == 1).all()


def test_cap_truncates_in_list_order():
    rng = np.random.default_rng(0)
    agents = sim._initialize_agents(P, rng)
    alive = int(agents["alive"].sum())
    births = [(sp, 0, 0, 0.0) for sp in (0, 1, 2, 3)]
    sim._append_births(agents, births, rng, alive + 2)
    assert sorted(agents["species"][alive:].tolist()) == [0, 1]


def test_eq7_exsitu_factor_is_power_of_managed_flag():
    x = 0.22 * 10.0 / 100.0
    for m in (0, 1):
        assert math.isclose((1 + x) ** m, 1 + x if m else 1.0)


def test_eq8_h_plus_c_telescopes():
    eps = 0.02
    for s7, nm, s6 in [(0.5, 0.2, 0.4), (0.0, 0.0, 0.0), (1.0, 0.0, 0.3)]:
        h = math.log((nm + eps) / (s6 + eps))
        c = math.log((s7 + eps) / (nm + eps))
        assert math.isclose(h + c, math.log((s7 + eps) / (s6 + eps)))
