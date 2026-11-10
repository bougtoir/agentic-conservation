"""Minimal mean-field subsystem for the S6-vs-S7 policy-reversal theory.

Purpose
-------
The full individual-based model (IBM) couples nine nodes, eight species,
observation noise, ex-situ demography, welfare, genetics and feedback.
This module isolates the smallest subsystem in which the S6 (habitat-first)
versus S7 (hybrid/circulation) reversal can occur, while preserving the
channels that actually carry the effect:

* habitat restoration vs circulation (the nominal reversal),
* ex-situ breeding benefit at managed targets,
* engagement -> budget feedback driven by visitor exposure,
* latent (undiscovered) fraction, which cannot be relocated until detected,
* survey spend -> detection rate.

State (deterministic mean field): per node ``j`` a KNOWN population
``n_j`` and an ORIGIN-only latent population ``ell`` (undiscovered
individuals cannot be moved), plus node qualities ``q_j`` and engagement.

Per-year update uses the same quantities as the IBM:

    s_j      = q_j * (0.72 + 0.28 b) - spec * (1 - q_j) * 0.32       (E1)
    births_j = n_j * female_frac * (m + g) * (0.5 + f) * s_j * 5
               * (1 - dens_j) * (1 + ex_b * ex_situ_spend / B_t)
               [managed only]                                     (E11/E12)
    surv_j   = 1 - m*mu - (1 - s_j)*0.24 - a_j*sens*alpha*0.08
               + managed: research_j*0.035 | wild: -pred_j*pm*0.035
               - (1 - health)*0.08 - inbreeding*imb_pen            (E2)
    q_j(t+1) = clip(q_j - trend - climate_j(t) - E[hit_j]
                    + habitat_spend/B0 * e * restoration_j)      (E14-E17)
    B_t      = B * (0.82 + 0.24 * engagement_t)
    engagement_{t+1} = clip(engagement + coeff*(exposure +
                    eng_spend/B_t*0.2) + feedback*habitat_signal)
    P_detect = min(0.60, background + 0.06*survey_spend/survey_cost
                    + habitat_spend/1000)

Movement (S7 rule): up to ``cap = floor(rescue_spend/2.5)`` KNOWN
at-risk (s < 0.58) origin individuals, at most 20% of candidates,
pay relocation mortality tau and an expected disease multiplier, then
grow at the target node chosen by the same rule as the IBM
(cost/research/restoration-weighted argmax with origin fidelity).

The headline output is the derived condition index Psi (see
THEORY_DERIVATION.md): the log ratio of terminal population under the
circulation rule versus the habitat rule, with a channel decomposition.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_config(root: Path = ROOT) -> dict:
    cfg = json.loads((root / "config" / "base.json").read_text())
    nodes = json.loads((root / "config" / "nodes.json").read_text())
    species = json.loads((root / "config" / "species.json").read_text())
    return {"config": cfg, "nodes": nodes, "species": species}


def representative_traits(species: list[dict]) -> dict:
    """Initial-population-weighted mean traits (one effective species)."""
    total = sum(s["initial_n"] for s in species)
    keys = (
        "growth",
        "mortality",
        "niche_breadth",
        "habitat_specificity",
        "climate_sensitivity",
        "anthropogenic_sensitivity",
        "fertility",
        "captivity_tolerance",
        "migration_need",
    )
    return {k: sum(s[k] * s["initial_n"] for s in species) / total for k in keys} | {
        "initial_n": total
    }


def suitability(quality: float, traits: dict, node: dict) -> float:
    """E1 suitability (wild and managed terms; no disease/inbreeding mods)."""
    base = quality * (0.72 + 0.28 * traits["niche_breadth"])
    base -= traits["habitat_specificity"] * (1.0 - quality) * 0.32
    if not node["wild"]:
        base += (traits["captivity_tolerance"] - 0.5) * 0.25
        base -= traits["migration_need"] * 0.24
    return base


def s7_target(q, nodes, traits, origin_fidelity) -> int:
    """Replicates ``_target_node`` for the S7 rule (Algorithm 2)."""
    best_i, best_v = -1, -math.inf
    for i, node in enumerate(nodes):
        if node["type"] == "biobank":
            continue
        v = suitability(q[i], traits, node)
        v -= node["cost"] * 0.04
        v += node["research"] * 0.03
        v += node["restoration"] * 0.08
        v += node["research"] * 0.05
        if i == 0:
            v += origin_fidelity
        if v > best_v:
            best_i, best_v = i, v
    return best_i


def _scenario_trend(cfg: dict) -> float:
    det = cfg["habitat_deterioration"]
    return {
        "stationary": 0.0,
        "abrupt_collapse": 0.0,
        "slow_deterioration": det * 0.5,
        "rapid_deterioration": det * 2.0,
        "restoration": -det * 0.6,
    }.get(cfg["scenario"], det)


def run_minimal_species(
    bundle: dict,
    sp: dict,
    allocation: dict[str, float],
    circulation: bool,
    overrides: dict | None = None,
    decomposition: bool = False,
    quota_series: list[int] | None = None,
) -> dict:
    """Rollout for a single species (density is species-local in the IBM,
    so species are demographically independent given shared budget/quality
    dynamics — which are species-independent)."""
    """Deterministic mean-field rollout for one policy rule.

    allocation   : spend shares (same semantics as policy_allocations).
    circulation  : apply the S7 movement rule if True, else never move.
    latent_fraction : share of the initial population that starts
        undiscovered and therefore unmovable until detected.
    """
    cfg = dict(bundle["config"])
    cfg.update(overrides or {})
    nodes = bundle["nodes"]
    tr = {
        k: sp[k]
        for k in (
            "growth",
            "mortality",
            "niche_breadth",
            "habitat_specificity",
            "climate_sensitivity",
            "anthropogenic_sensitivity",
            "fertility",
            "captivity_tolerance",
            "migration_need",
            "initial_n",
        )
    }
    T = int(cfg["years"])
    B0 = float(cfg["initial_budget"])
    wild = [i for i, n_ in enumerate(nodes) if n_["wild"]]
    n_wild = len(wild)

    L = 0.0 if sp["known"] else 1.0
    n = [0.0] * len(nodes)
    n[0] = float(tr["initial_n"]) * (1.0 - L)
    ell = float(tr["initial_n"]) * L  # latent cohort, origin only
    q = [node["base_quality"] for node in nodes]
    trend = _scenario_trend(cfg)
    e_hit = cfg["catastrophe_probability"] * 0.27 / max(n_wild, 1)
    tau = cfg["relocation_mortality"]
    quar_cov = 0.0
    survey_cost = max(cfg["survey_cost"], 1e-9)
    engagement = 0.5
    # Mean-field constants for terms the deterministic model cannot carry:
    # health ~ E[0.7], inbreeding ~ 0.08 (baseline), female-and-adult share ~0.25.
    HEALTH, INBREEDING, FEMALE_FRAC = 0.70, 0.08, 0.25
    MIN_BREEDING_POP = cfg.get("_min_breeding_pop", 4.0)  # mate proxy

    m, g, f = tr["mortality"], tr["growth"], tr["fertility"]
    sens_a = tr["anthropogenic_sensitivity"]
    mu = cfg["mortality_multiplier"]
    pm = cfg["predation_multiplier"]
    alpha = cfg["anthropogenic_pressure_multiplier"]

    moved_total = 0.0
    trace = []
    for t in range(T):
        budget = B0 * (0.82 + 0.24 * engagement)
        rescue_spend = allocation.get("rescue", 0.0) * budget
        habitat_spend = allocation.get("habitat", 0.0) * budget
        ex_situ_spend = allocation.get("ex_situ", 0.0) * budget
        survey_spend = allocation.get("survey", 0.0) * budget
        cap = int(rescue_spend / 2.5)

        s = [suitability(q[i], tr, nodes[i]) for i in range(len(nodes))]
        ex_mult = 1.0 + cfg["ex_situ_breeding_benefit"] * (ex_situ_spend / max(budget, 1.0))
        for i, nd in enumerate(nodes):
            if nd["capacity"] <= 0 or n[i] <= 0:
                continue
            # Mate limitation proxy: in the IBM births require co-located
            # mature females AND males; a dribble of relocated individuals
            # at a fresh node cannot breed. Mean-field surrogate: no
            # recruitment below MIN_BREEDING_POP residents.
            dens = min(1.0, n[i] / max(nd["capacity"], 1))
            births = (
                n[i]
                * FEMALE_FRAC
                * (m + g)
                * (0.5 + f)
                * max(s[i], 0.0)
                * 5.0
                * max(0.05, 1.0 - dens)
                * (1.0 if n[i] >= MIN_BREEDING_POP else 0.0)
            )
            if not nd["wild"]:
                births *= ex_mult
            surv = (
                1.0
                - m * mu
                - (1.0 - max(s[i], 0.0)) * 0.24
                - nd["anthropogenic"] * sens_a * alpha * 0.08
                - (1.0 - HEALTH) * 0.08
                - INBREEDING * cfg["inbreeding_mortality_penalty"]
            )
            if not nd["wild"]:
                surv += nd["research"] * 0.035
            else:
                surv -= nd["predation"] * pm * 0.035
            n[i] += births - n[i] * (1.0 - min(0.995, max(0.05, surv)))

        # Latent cohort: same demography at origin, no relocation
        dens0 = min(1.0, (n[0] + ell) / max(nodes[0]["capacity"], 1))
        births_l = (
            ell * FEMALE_FRAC * (m + g) * (0.5 + f) * max(s[0], 0.0) * 5.0 * max(0.05, 1.0 - dens0)
        )
        surv_l = (
            1.0
            - m * mu
            - (1.0 - max(s[0], 0.0)) * 0.24
            - nodes[0]["anthropogenic"] * sens_a * alpha * 0.08
            - (1.0 - HEALTH) * 0.08
            - INBREEDING * cfg["inbreeding_mortality_penalty"]
            - nodes[0]["predation"] * pm * 0.035
        )
        ell += births_l - ell * (1.0 - min(0.995, max(0.05, surv_l)))
        # Species-level discovery: in the IBM a latent species becomes
        # known as a whole after a stage-progression delay; per-individual
        # detection would leak the cohort to safety too early. Deterministic
        # surrogate: the remaining cohort joins the movable pool at its
        # expected discovery year (geometric mean of the IBM's detection
        # hazard, discounted by the species' own detectability).
        p_detect = min(
            0.60,
            cfg["background_detection_probability"]
            + 0.06 * survey_spend / survey_cost
            + habitat_spend / 1000.0,
        ) * float(sp.get("detectability", 0.6))
        t_disc = math.ceil(1.0 / max(p_detect, 1e-9))
        if ell > 0 and t >= t_disc:
            n[0] += ell
            ell = 0.0

        # S7 circulation rule on at-risk KNOWN origin residents
        moves = 0.0
        tgt = -1
        quota = quota_series[t] if quota_series is not None else cap
        if circulation and quota > 0 and s[0] < 0.58 and n[0] > 0:
            tgt = s7_target(q, nodes, tr, cfg["origin_fidelity"])
            if tgt != 0 and nodes[tgt]["capacity"] > 0:
                space = max(0.0, nodes[tgt]["capacity"] - n[tgt])
                moves = min(quota, math.ceil(n[0] * 0.2), space)
                n[0] -= moves
                # transit disease: quarantine coverage scales with rescue
                quar_cov = min(
                    1.0, rescue_spend / max(moves * cfg["quarantine_cost_per_move"], 1e-9)
                )
                infect_p = cfg["movement_disease_risk"] * (
                    1.0 - quar_cov * cfg["quarantine_effectiveness"]
                )
                # infected movers pay 0.14 mortality for ~1/0.32 years
                n[tgt] += moves * (1.0 - tau) * (1.0 - infect_p * 0.14)
                moved_total += moves

        for i in wild:
            climate = cfg["climate_velocity"] * t / max(T, 1)
            dq = (
                -trend
                - (climate if i == 0 else -climate * 0.65)
                - e_hit
                + (habitat_spend / max(B0, 1.0))
                * cfg["habitat_protection_efficiency"]
                * nodes[i]["restoration"]
            )
            q[i] = min(0.98, max(0.05, q[i] + dq))
        if cfg["scenario"] == "abrupt_collapse" and t == max(2, T // 3):
            q[0] -= 0.70

        # engagement -> next-year budget feedback
        occupied = [i for i in range(len(nodes)) if n[i] > 1.0]
        exposure = (
            sum(nodes[i]["visitor_exposure"] for i in occupied) / len(occupied) if occupied else 0.0
        )
        habitat_signal = sum(q[i] for i in wild[:3]) / min(3, len(wild))
        engagement = min(
            1.5,
            max(
                0.0,
                engagement
                + cfg["engagement_coefficient"]
                * (exposure + allocation.get("engagement", 0.0) * 0.2)
                + cfg["engagement_habitat_feedback"] * habitat_signal,
            ),
        )

        for i in range(len(nodes)):
            n[i] = max(0.0, n[i])
        if decomposition:
            trace.append(
                {
                    "year": t,
                    "n0": n[0],
                    "ell": ell,
                    "q0": q[0],
                    "s0": s[0],
                    "moves": moves,
                    "engagement": engagement,
                }
            )
    out = {
        "n_T": sum(n) + ell,
        "n_T_known": max(0.0, sum(n)),
        "n_T_latent": max(0.0, ell),
        "n0_known": float(tr["initial_n"]) * (1.0 - L),
        "n0_latent": float(tr["initial_n"]) * L,
        "moved": moved_total,
        "q0_T": q[0],
    }
    if decomposition:
        out["trace"] = trace
    return out


def run_minimal(
    bundle: dict, allocation: dict[str, float], circulation: bool, overrides: dict | None = None
) -> dict:
    """Species-level rollout: one deterministic run per species, then the
    IBM's own metric — fraction of species extant at T (survival_100)."""
    cfg = dict(bundle["config"])
    cfg.update(overrides or {})
    species = [dict(s) for s in bundle["species"]]
    L = cfg.get("latent_fraction_proxy")
    if L is not None:
        k = int(round(float(L) * len(species)))
        for sp in species:
            sp["known"] = True
        for sp in species[-k:] if k else []:
            sp["known"] = False
    # Shared rescue capacity: the IBM's per-year cap (~rescue_spend/2.5)
    # is a TOTAL across species, allocated in risk order. Approximate with
    # an equal quota cap_t // N_atrisk(t), N_atrisk from an environment-only
    # pre-pass of origin quality (engagement feedback neglected here).
    nodes = bundle["nodes"]
    B0 = float(cfg["initial_budget"])
    T = int(cfg["years"])
    wild = [i for i, nd in enumerate(nodes) if nd["wild"]]
    trend = _scenario_trend(cfg)
    e_hit = cfg["catastrophe_probability"] * 0.27 / max(len(wild), 1)
    hab = allocation.get("habitat", 0.0) * B0
    qO = nodes[0]["base_quality"]
    quota_series = []
    for t in range(T):
        cap_t = int(allocation.get("rescue", 0.0) * B0 / 2.5)
        n_at = sum(1 for sp in species if suitability(qO, sp, nodes[0]) < 0.58 and sp["known"])
        quota_series.append(max(1, cap_t // max(1, n_at)) if cap_t > 0 else 0)
        climate = cfg["climate_velocity"] * t / max(T, 1)
        qO = min(
            0.98,
            max(
                0.05,
                qO
                - trend
                - climate
                - e_hit
                + hab
                / max(B0, 1.0)
                * cfg["habitat_protection_efficiency"]
                * nodes[0]["restoration"],
            ),
        )

    extant, n_T, moved = [], [], 0.0
    for sp in species:
        out = run_minimal_species(
            bundle, sp, allocation, circulation, overrides, quota_series=quota_series
        )
        total = out["n_T_known"] + out["n_T_latent"]
        moved += out["moved"]
        n0 = out["n0_known"] + out["n0_latent"]
        # smoothed extant indicator ~ P(species persists)
        extant.append(total / (total + 0.05 * n0))
        n_T.append(total)
    return {
        "survival": float(sum(extant) / len(species)),
        "extant_frac": [round(e, 4) for e in extant],
        "n_T": sum(n_T),
        "moved": moved,
    }


def psi_index(
    bundle: dict, alloc_circ: dict, alloc_hab: dict, overrides: dict | None = None
) -> dict:
    """Derived condition index Psi and channel decomposition.

    Psi = log( survival(circulation rule) / survival(habitat rule) )
    where survival = fraction of species extant at T (IBM survival_100).
      habitat channel     = log( surv(circ-budget, no-move) / surv(hab-budget) )
      circulation channel = log( surv(circ-budget, move)    / surv(circ-budget, no-move) )
    """
    oc = run_minimal(bundle, alloc_circ, True, overrides)
    oh = run_minimal(bundle, alloc_hab, False, overrides)
    on = run_minimal(bundle, alloc_circ, False, overrides)
    # Persistence floor: a pseudo-cohort's smoothed survival cannot fall
    # below ~1 individual per species; bounds channel log-ratios.
    eps = 0.02
    return {
        "psi": math.log((oc["survival"] + eps) / (oh["survival"] + eps)),
        "habitat_channel": math.log((on["survival"] + eps) / (oh["survival"] + eps)),
        "circulation_channel": math.log((oc["survival"] + eps) / (on["survival"] + eps)),
        "surv_circ": oc["survival"],
        "surv_hab": oh["survival"],
        "surv_nc": on["survival"],
        "n_T_circ": oc["n_T"],
        "n_T_hab": oh["n_T"],
        "n_T_nc": on["n_T"],
    }
