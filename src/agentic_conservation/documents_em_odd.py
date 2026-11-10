"""ODD 2020-structured revision of the Ecological Modelling manuscript.

Builds a NEW submission referring to ECOMOD-26-2231. Every number is read
from preserved registries at build time: the canonical results, the Q1–Q3
verification outputs and the prospective Ψ confirmatory evaluation. The
submitted manuscript (manuscript/EM_MANUSCRIPT.docx) is never modified.
"""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_COLOR_INDEX  # noqa: F401
from docx.shared import Pt, RGBColor

from agentic_conservation.documents import (
    _add_heading,
    _add_paragraph,
    _add_table,
    _add_title,
    _citer,
    _configure_document,
    _reference_text,
    _sweep_counts,
    _validate_office_file,
)
from agentic_conservation.documents_em import _omml_equation

TITLE = (
    "When does a dynamic conservation network pay? An ODD-documented "
    "individual-based model of habitat, managed-care and discovery policies "
    "under directional change"
)
OUT_DIR = "odd_resubmission/submission"
MIRROR_TAG = "odd-2020-revision-v1"
EXTRA_REFERENCES = [
    {
        "key": "grimm_2020",
        "doi": "10.18564/jasss.4259",
        "reference_authors": (
            "Grimm V, Railsback SF, Vincenot CE, Berger U, Gallagher C, "
            "DeAngelis DL, Edmonds B, Ge J, Giske J, Groeneveld J, Johnston AS, "
            "Milles A, Nabe-Nielsen J, Polhill JG, Radchuk V, Rohwäder MS, "
            "Stillman RA, Thiele JC, Ayllón D"
        ),
        "citation": "Grimm et al. 2020",
        "year": 2020,
        "title": (
            "The ODD protocol for describing agent-based and other simulation "
            "models: a second update to improve clarity, replication, and "
            "structural realism"
        ),
        "journal": "Journal of Artificial Societies and Social Simulation",
        "volume": "23",
        "issue": "2",
        "pages": "7",
    },
    {
        "key": "grimm_2005",
        "doi": "10.1126/science.1116681",
        "reference_authors": (
            "Grimm V, Revilla E, Berger U, Jeltsch F, Mooij WM, Railsback SF, "
            "Thulke HH, Weiner J, Wiegand T, DeAngelis DL"
        ),
        "citation": "Grimm et al. 2005",
        "year": 2005,
        "title": ("Pattern-oriented modeling of agent-based complex systems: lessons from ecology"),
        "journal": "Science",
        "volume": "310",
        "issue": "5750",
        "pages": "987-991",
    },
]


# --------------------------------------------------------------------- values
def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return x


def load_values(root: Path) -> dict:
    """Collect every number used in the text from preserved registries."""
    r = root / "results"
    o = r / "odd_verification"
    c = r / "psi_confirmatory"
    v: dict = {}
    summary = pd.read_csv(r / "policy_summary.csv")
    summary = summary[~summary.oracle]
    v["summary"] = summary.set_index(["policy", "metric"])
    v["rev"] = (
        pd.read_csv(r / "reversal/manuscript_reversal_values.csv")
        .set_index("value_id")
        .estimate.map(_num)
    )
    info = pd.read_csv(r / "information_value.csv").set_index("metric")
    v["info"] = info.loc["decision_utility"]
    v["sweep_s6"], v["sweep_s7"], v["sweep_ind"] = _sweep_counts(root)
    v["q1_means"] = pd.read_csv(o / "q1_base_policy_means.csv").set_index("policy")
    v["q1_contrast"] = pd.read_csv(o / "q1_base_contrast.csv").set_index("endpoint")
    v["q1_holdout"] = pd.read_csv(o / "q1_holdout_psi_metrics.csv")
    v["q1_trans"] = pd.read_csv(o / "q1_endpoint_sign_transitions.csv")
    v["q2"] = pd.read_csv(o / "q2_summary.csv")
    v["q2_psi"] = pd.read_csv(o / "q2_psi_metrics.csv")
    v["q3"] = pd.read_csv(o / "q3_stage1_summary.csv")
    v["q3_sel"] = pd.read_csv(o / "q3_stage2_selection.csv")
    v["q3_psi"] = pd.read_csv(o / "q3_stage2_psi_metrics.csv")
    v["conf"] = pd.read_csv(c / "metrics.csv")
    v["conf_cells"] = pd.read_csv(c / "cell_results.csv")
    v["conf_design"] = pd.read_csv(c / "designs.csv")
    v["forensic"] = pd.read_csv(
        root / "odd_resubmission/psi_forensics/dev_and_holdout_by_version.csv"
    )
    return v


def est(v: dict, policy: str, metric: str) -> float:
    return float(v["summary"].loc[(policy, metric)].estimate)


def ival(v: dict, policy: str, metric: str) -> str:
    row = v["summary"].loc[(policy, metric)]
    return f"{row.estimate:.3f} [{row.lower:.3f}, {row.upper:.3f}]"


def q1(v: dict, endpoint: str, psi: str) -> pd.Series:
    t = v["q1_holdout"]
    return t[(t.endpoint == endpoint) & (t.psi == psi)].iloc[0]


def q2(v: dict, form: str, endpoint: str = "survival_100") -> pd.Series:
    t = v["q2"]
    return t[(t.climate_form == form) & (t.endpoint == endpoint)].iloc[0]


def q2psi(v: dict, form: str, psi: str) -> pd.Series:
    t = v["q2_psi"]
    return t[(t.climate_form == form) & (t.endpoint == "survival_100") & (t.psi == psi)].iloc[0]


def conf(v: dict, endpoint: str = "survival_100", stratum: str = "all") -> pd.Series:
    t = v["conf"]
    return t[(t.endpoint == endpoint) & (t.stratum == stratum)].iloc[0]


def trans(v: dict, other: str, a: int, b: int) -> int:
    t = v["q1_trans"]
    row = t[
        (t.comparison == f"survival_100_vs_{other}") & (t.sign_survival == a) & (t.sign_other == b)
    ]
    return int(row.cells.iloc[0])


# ------------------------------------------------------------------- numbering
class Numbering:
    """Tables and figures are numbered in order of first appearance."""

    def __init__(self) -> None:
        self.tables: list[str] = []
        self.figures: list[str] = []
        self.figure_files: list[tuple[str, Path, str]] = []

    def t(self, key: str) -> str:
        if key not in self.tables:
            self.tables.append(key)
        return f"Table {self.tables.index(key) + 1}"

    def f(self, key: str) -> str:
        if key not in self.figures:
            self.figures.append(key)
        return f"Fig. {self.figures.index(key) + 1}"


FIGURES = {
    "network": (
        "figures/fig1_conservation_network.png",
        "Conservation network represented in the model. Arrows denote "
        "potential movement among wild, managed, transitional and "
        "rehabilitation nodes; the biobank holds genetic material only.",
    ),
    "observation": (
        "figures/fig7_partial_observation_architecture.png",
        "Separation of true ecological state, observations, policy "
        "actions and realised outcomes (ODD Sensing and Observation).",
    ),
    "trajectories": (
        "figures/fig2_century_trajectories.png",
        "Mean 100-year trajectories under the eight policies in the "
        "base scenario. Synthetic model outcomes, not forecasts.",
    ),
    "pareto": (
        "figures/fig3_pareto_outcomes.png",
        "Multi-objective policy comparison and Pareto status.",
    ),
    "tradeoffs": (
        "figures/fig6_objective_tradeoffs.png",
        "Normalised cross-objective outcomes (descriptive normalisation; not a cardinal utility).",
    ),
    "reversal": (
        "figures/fig4_policy_reversal_thresholds.png",
        "Policy-reversal surfaces for two-factor sweeps: S7 − S6 difference in year-100 survival.",
    ),
    "climate_forms": (
        "figures/odd/fig_q2_climate_forms.png",
        "Climate-trajectory verification (Q2). (a) Cumulative "
        "origin-quality displacement for four trajectories with the "
        "same year-100 displacement; the legend gives cumulative "
        "exposure (displacement-years). (b) Base-scenario S7 − S6 "
        "contrast in year-100 survival with ±2 SE (192 paired seeds).",
    ),
    "ebd": (
        "figures/fig5_extinction_before_discovery.png",
        "Extinction before discovery across latent-species fraction and survey-cost conditions.",
    ),
    "origin_future": (
        "figures/fig9_origin_future_optimum.png",
        "Origin-to-alternative habitat-quality shift produced by the "
        "deterministic part of directional change (shipped "
        "accelerating form).",
    ),
    "psi": (
        "figures/fig10_reversal_psi.png",
        "Historical held-out evaluation of Ψ (V0 launch-state implementation; "
        "see Section 2.10.2) against the observed S7 − S6 difference on the "
        "56 held-out cells. Filled: determinate cells; crosses: indeterminate.",
    ),
}


# -------------------------------------------------------------------- helpers
def _p(doc: Document, text: str) -> None:
    _add_paragraph(doc, text)


def _bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        para = doc.add_paragraph()
        para.paragraph_format.left_indent = Pt(18)
        para.add_run("- ").bold = True
        para.add_run(item)


def _algorithm(doc: Document, heading: str, lines: list[str]) -> None:
    _add_heading(doc, heading, level=3)
    for i, line in enumerate(lines, 1):
        para = doc.add_paragraph()
        para.paragraph_format.left_indent = Pt(18)
        para.add_run(f"{i}. ").bold = True
        para.add_run(line)


def _caption(doc: Document, n: Numbering, key: str, root: Path) -> None:
    rel, caption = FIGURES[key]
    label = n.f(key)
    n.figure_files.append((label, root / rel, caption))
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(8)
    para.add_run(f"{label.replace('Fig.', 'Figure')}. {caption}").italic = True
    para.add_run(" [Figure supplied as a separate file.]")


def _table(
    doc: Document, n: Numbering, key: str, frame: pd.DataFrame, caption: str, size: float = 8
) -> None:
    _add_table(doc, frame, n.t(key), caption, font_size=size)


def _rationale(doc: Document, items: list[tuple[str, str]]) -> None:
    """S1 rationale block: process, form, alternatives, assumptions, effect,
    evidence, missing evidence."""
    for label, text in items:
        para = doc.add_paragraph()
        para.paragraph_format.left_indent = Pt(12)
        para.add_run(f"{label}: ").bold = True
        para.add_run(text)


def _state_variable_table(root: Path) -> pd.DataFrame:
    sp = json.loads((root / "config/species.json").read_text())
    nodes = json.loads((root / "config/nodes.json").read_text())
    used = {
        "growth",
        "mortality",
        "niche_breadth",
        "habitat_specificity",
        "anthropogenic_sensitivity",
        "detectability",
        "fertility",
        "migration_need",
        "captivity_tolerance",
        "initial_n",
        "known",
    }
    inert = sorted(k for k in sp[0] if k not in used | {"id"})
    node_used = {
        "base_quality",
        "capacity",
        "disease",
        "predation",
        "anthropogenic",
        "welfare",
        "cost",
        "research",
        "visitor_exposure",
        "restoration",
        "wild",
        "managed",
        "type",
    }
    node_inert = sorted(k for k in nodes[0] if k not in node_used | {"id"})
    rows = [
        (
            "Individual",
            "species, sex, age (yr), current node, origin node, founder id",
            "categorical / integer",
            "demography, mate co-location, genetics",
        ),
        (
            "Individual",
            "health [0.35, 1], inbreeding F [0, 1], infection (S/I/R)",
            "continuous / categorical",
            "survival (Eq. 6), reproduction (Eq. 7)",
        ),
        (
            "Individual",
            "wildness, habituation, stress tolerance, release readiness",
            "continuous [0, 1]",
            "relocation stress, S3 return rule, welfare",
        ),
        (
            "Species (8)",
            "growth, mortality, niche breadth, habitat specificity, "
            "anthropogenic sensitivity, fertility, migration need, captivity "
            "tolerance, detectability",
            "traits [0, 1]",
            "Eqs. 2, 3, 6, 7",
        ),
        (
            "Species (8)",
            "knowledge stage 0–5 (5 known, 3 latent at t = 0); biobank coverage",
            "integer / [0, 1]",
            "visibility gate, option value",
        ),
        (
            "Species (8)",
            "not used by any process: " + ", ".join(inert),
            "configuration only",
            "inert; retained for transparency",
        ),
        (
            "Node (9)",
            "quality q_j(t), capacity, disease, predation, "
            "anthropogenic pressure, welfare standard, cost, research, visitor "
            "exposure, restoration potential, wild/managed flags",
            "index / count",
            "Eqs. 1, 2, 5–7, welfare, engagement",
        ),
        (
            "Node (9)",
            "not used by any process: " + ", ".join(node_inert),
            "configuration only",
            "inert (no network topology)",
        ),
        (
            "Manager (global)",
            "budget B_t, allocation shares a(π, c), observed counts and quality, engagement E_t",
            "budget units / index",
            "Algorithm 2, Eqs. 4–5",
        ),
        (
            "Environment (global)",
            "scenario, year t, catastrophe and funding-shock draws",
            "—",
            "Eq. 1, Algorithm 1",
        ),
    ]
    return pd.DataFrame(rows, columns=["entity", "state variables", "type/units", "used by"])


# ---------------------------------------------------------------- manuscript
def _literature(root: Path) -> pd.DataFrame:
    base = pd.read_csv(root / "data/processed/bibliography.csv")
    return pd.concat([base, pd.DataFrame(EXTRA_REFERENCES)], ignore_index=True)


def build_clean(root: Path) -> tuple[Path, Numbering]:
    v = load_values(root)
    lit = _literature(root)
    cite = _citer(lit)
    n = Numbering()
    rev = v["rev"]
    c1 = v["q1_contrast"]
    cf = conf(v)
    s6, s7 = "S6", "S7"
    d0 = float(c1.loc["survival_100"].S7_minus_S6)
    se0 = float(c1.loc["survival_100"].se)
    hist = q1(v, "survival_100", "psi_reg")
    acc = {f: q2(v, f) for f in ["accelerating", "linear", "decelerating", "step"]}
    q3 = v["q3"]
    flip = q3[(q3.survival_100_sign == 1)]
    e1hi = flip.iloc[0]

    def flips(lit: str, f: float) -> int:
        return int(q3[(q3.literal == lit) & (q3.factor == f)].psi_sign_flips.iloc[0])

    abl = pd.read_csv(root / "results/ablations.csv")
    abl_n = int(abl.groupby(["name", "policy"]).size().min())
    am = abl.groupby(["name", "policy"]).survival_100.mean().unstack()
    ad = (am.S7 - am.S6).round(3)
    labels = {
        "disease": "disease was removed",
        "human_feedback": "the engagement–budget feedback was removed",
        "origin_fidelity": "origin fidelity in targeting was removed",
        "partial_observability": "observation was perfect",
        "welfare": "welfare burdens were removed",
        "genetics": "genetics was removed",
        "biobank": "the biobank was removed",
        "climate": "directional climate was removed",
        "latent_species": "no species were latent",
    }
    abl_pos = ", ".join(f"{labels.get(k, k)} ({d:+.3f})" for k, d in ad.items() if d > 0.05)
    abl_neg = ", ".join(f"{labels.get(k, k)} ({d:+.3f})" for k, d in ad.items() if d < -0.05)
    abl_small = ", ".join(labels.get(k, k) for k, d in ad.items() if abs(d) <= 0.05)
    out = root / OUT_DIR / "EM_ODD_REVISED_MANUSCRIPT_CLEAN_FINAL.docx"
    out.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()
    _configure_document(doc, TITLE)
    doc.core_properties.subject = "Ecological Modelling new submission (ref. ECOMOD-26-2231)"
    _add_title(doc, TITLE, "Research paper")
    _p(doc, "Author: Tatsuki Onishi (corresponding author).")
    _p(doc, "Affiliation: Independent researcher.")
    _p(doc, "Corresponding author contact: see cover letter.")

    _add_heading(doc, "Highlights", 1)
    _bullets(
        doc,
        [
            "ODD 2020 description of a wild–managed conservation-network IBM.",
            "Habitat-first versus circulation ranking is conditional, not general.",
            "Climate timing at equal year-100 displacement reverses the base ranking.",
            "A reduced criterion Ψ passed a prospectively frozen 60-cell evaluation.",
            "Circulation gains are mostly persistence outside wild habitat.",
        ],
    )

    _add_heading(doc, "Abstract", 1)
    _p(
        doc,
        (
            "Conservation programmes increasingly link wild habitat, zoos, breeding "
            "centres, release stations and biobanks, but when moving animals through "
            "such a network outperforms investing in habitat is unclear. I describe, "
            "following the ODD protocol, an individual-based model of eight synthetic "
            "species in nine nodes over 100 annual steps with noisy, delayed "
            "observation, discovery of latent species, disease, inbreeding, welfare "
            "and budget feedback, and compare eight fixed decision rules. In the base "
            f"scenario a habitat-first rule (S6) retained {est(v, s6, 'survival_100'):.3f} "
            f"of species at year 100 versus {est(v, s7, 'survival_100'):.3f} for a "
            f"circulation portfolio (S7) (paired difference {d0:.3f}, SE {se0:.3f}), "
            "and this ordering held for individual, reproductive-proxy and wild "
            "persistence. Preregistered structural tests showed that the ordering is "
            "conditional: with the same year-100 climate displacement but earlier "
            "exposure, S7 outperformed S6 under all three alternative trajectories "
            f"(+{acc['linear'].S7_minus_S6:.3f} to +{acc['step'].S7_minus_S6:.3f}), "
            "and raising the baseline suitability intercept by 50% also reversed it "
            "in the base design (not re-tested on held-out cells). Most "
            "S7 advantages in held-out configurations were persistence outside wild "
            "nodes. A reduced two-channel criterion Ψ derived from the model "
            "equations was frozen and then evaluated on 60 untouched configurations: "
            f"it signed {cf.acc_det:.3f} of {int(cf.det_cells)} determinate cells "
            f"correctly (95% CI {cf.acc_det_wilson_lo:.3f}–{cf.acc_det_wilson_hi:.3f}) "
            f"with decision regret {cf.regret_psi:.4f} versus "
            f"{min(cf.regret_always_S6, cf.regret_always_S7):.4f} for the better fixed "
            "policy, within the shipped structural assumptions. An earlier held-out "
            "evaluation is reported as historical because it used an implementation "
            "that differed from the documented one. The results are model-specific "
            "mechanistic statements, not calibrated predictions for real taxa."
        ),
    )
    _p(
        doc,
        "Keywords: individual-based model; ODD protocol; ex situ conservation; "
        "reintroduction; climate trajectory; decision analysis",
    )

    # ---------------------------------------------------------- 1 Introduction
    _add_heading(doc, "1. Introduction", 1)
    _p(
        doc,
        (
            "Conservation of threatened species increasingly relies on networks that "
            "link wild reserves, zoos, breeding centres, pre-release stations, "
            "rehabilitation facilities and biobanks "
            f"{cite('conde_2011_science', 'conde_2013_plos', 'redford_2012')} "
            f"{cite('pritchard_2012', 'hoban_2020')}. "
            "Reintroduction biology documents both successes and recurrent failures "
            f"{cite('snyder_1996', 'jule_2008', 'seddon_2014')}, and decision analysis "
            "frames the choice among such actions as constrained allocation "
            f"{cite('mccarthy_possingham_2007', 'chades_2008', 'joseph_2009')}. What "
            "remains unclear is not whether circulation between wild and managed nodes "
            "can help "
            f"{cite('kaczensky_2007', 'mee_2007', 'delia_2015', 'gilbert_2017')}, but under "
            "which environmental and budgetary conditions it outperforms protecting "
            "and restoring habitat."
        ),
    )
    _p(
        doc,
        (
            "A model of that question must represent a combinatorial allocation "
            "across habitat, surveys, rescue, breeding, genetics, banking and "
            "engagement; a partially observed state in which some species are not "
            f"yet known {cite('williams_brown_2022', 'tedesco_2014', 'liu_2022')}; "
            "and objectives that conflict, including persistence, animal welfare and "
            f"cost {cite('harrington_2013', 'beausoleil_2018', 'mellor_2020')}. "
            "Individual-based models (IBMs) can represent these interacting processes, "
            "but their results can be assessed only if the model is described "
            "completely and the ecological reasons for each structural choice are "
            f"explicit. I therefore describe the model with the ODD protocol "
            f"{cite('grimm_2020')}, following its Supplement S1 guidance for each "
            "element, and I report the assumptions that decide the main result "
            "rather than only the result."
        ),
    )
    _p(
        doc,
        (
            "The study asks three questions. (i) Under which conditions does a "
            "circulation portfolio (S7) retain more species than habitat-first "
            "spending (S6), and how much does that answer depend on how persistence, "
            "climate trajectory and uncertain coefficients are specified? (ii) Can "
            "the direction of the S7–S6 contrast be predicted from a reduced "
            "criterion derived from the model's own equations, and does that "
            "prediction survive a prospectively frozen evaluation? (iii) How "
            "often are latent species lost before they become visible, and does "
            "perfect current-state information change the outcome? The model is a "
            "synthetic, uncalibrated system: its results are statements about "
            "mechanisms and their conditions, not forecasts for particular taxa."
        ),
    )

    # ---------------------------------------------------------- 2 Methods/ODD
    _add_heading(doc, "2. Methods", 1)
    _p(
        doc,
        (
            "Sections 2.1–2.7 follow the seven ODD elements and their order "
            f"{cite('grimm_2020')}. Each element is written to be readable without "
            "the code. Section 2.7 gives one subsection per submodel with its "
            "equation and its ecological rationale. Sections 2.8–2.10 describe the "
            "simulation experiments, the preregistered structural verification and "
            "the reduced criterion Ψ."
        ),
    )
    _add_heading(doc, "2.1 Purpose and patterns", 2)
    _p(
        doc,
        (
            "Purpose. The model is a theoretical-exposition model. Its specific "
            "purpose is to identify the conditions under which moving individuals "
            "among wild, managed and transitional nodes (circulation) retains more "
            "species over 100 years than spending the same budget on habitat, given "
            "noisy observation and species that are initially unknown to managers. "
            "\u2018Persistence\u2019 is the fraction of the eight species with at least "
            "one living individual at year 100 (individual persistence). Two "
            "stricter endpoints are also reported: at least one mature female and "
            "one mature male co-located in a non-biobank node (a reproductive proxy, "
            "not a guarantee of viability) and at least one individual in a wild node "
            "(wild persistence). \u2018Pays\u2019 means a positive paired S7 − S6 "
            "difference in a persistence endpoint that exceeds two Monte Carlo "
            "standard errors."
        ),
    )
    pat = pd.DataFrame(
        [
            (
                "P1",
                "Without intervention, directional habitat loss removes the "
                "species assemblage within a century",
                f"S0 individual persistence {est(v, 'S0', 'survival_100'):.3f}",
                "reproduced; partly built in (no management)",
            ),
            (
                "P2",
                "Captivity-centred strategies retain species but lose wild "
                f"populations {cite('snyder_1996', 'redford_2012')}",
                f"S2 persistence {v['q1_means'].loc['S2'].survival_100:.3f}, wild "
                f"{v['q1_means'].loc['S2'].wild_persistence_100:.3f}; S3 "
                f"{v['q1_means'].loc['S3'].survival_100:.3f}, wild "
                f"{v['q1_means'].loc['S3'].wild_persistence_100:.3f}",
                "reproduced (emergent)",
            ),
            (
                "P3",
                "Unknown species are lost more often than known ones "
                f"{cite('tedesco_2014', 'liu_2022')}",
                f"EBD fraction S0 {est(v, 'S0', 'fraction_ebd'):.3f}; lowest under any "
                f"policy {min(est(v, f'S{i}', 'fraction_ebd') for i in range(1, 8)):.3f}",
                "reproduced; visibility gate is imposed",
            ),
            (
                "P4",
                "Relocation becomes more valuable as habitat deteriorates faster "
                f"{cite('mclachlan_2007', 'richardson_2009')}",
                f"sweeps: {v['sweep_s7']} cells S7, {v['sweep_s6']} cells S6, "
                f"{v['sweep_ind']} indeterminate; S7 cells concentrate at high "
                "deterioration and climate velocity",
                "reproduced (emergent)",
            ),
        ],
        columns=["pattern", "general expectation", "model output (base or sweep)", "status"],
    )
    _p(
        doc,
        (
            "Patterns. The system is generic, so the evaluation patterns are general "
            "expectations from conservation practice rather than data from one "
            f"system {cite('grimm_2005')} ({n.t('patterns')}). They are used to "
            "judge whether the model is suitable for its purpose, not to calibrate "
            "it. P1 and P3 partly follow from the model's construction and so are "
            "weak tests; P2 and P4 are emergent."
        ),
    )
    _table(
        doc,
        n,
        "patterns",
        pat,
        "Evaluation patterns (ODD element 1) and whether the model reproduces them",
    )

    _add_heading(doc, "2.2 Entities, state variables, and scales", 2)
    _p(
        doc,
        (
            "The entities are individuals, species, nodes, one manager and the global "
            f"environment ({n.t('state')}; {n.f('network')}). Eight synthetic species "
            "differ in demographic and niche traits; five are known to the manager at "
            "the start (knowledge stage 5) and three are latent (stage 0). Nine nodes "
            "represent origin wild habitat, alternative wild habitat, a protected "
            "reserve, a conventional zoo, a conservation zoo, a breeding centre, a "
            "semi-wild pre-release station, a rehabilitation facility and a biobank. "
            "The biobank stores genetic material only; no individual ever occupies "
            "it. Space is implicit: nodes are not arranged on a map and have no "
            "adjacency, so any node can be reached from any other at the same cost. "
            "Three species traits (climate sensitivity, dispersal, social "
            "dependence) and the node attribute connectivity are present in the "
            "configuration but are not used by any process; they are listed as "
            "inert so that readers do not infer mechanisms that are absent. One time "
            "step is one year, the horizon is 100 years, and all quantities are in "
            "model units."
        ),
    )
    _table(
        doc, n, "state", _state_variable_table(root), "Entities and state variables (ODD element 2)"
    )
    _caption(doc, n, "network", root)
    params = pd.read_csv(root / "tables/table1_model_parameters.csv")
    _table(
        doc,
        n,
        "params",
        params,
        "Base parameter values (all synthetic, class C; model units)",
        size=7,
    )

    _add_heading(doc, "2.3 Process overview and scheduling", 2)
    _p(
        doc,
        (
            "Each year executes Algorithm 1 in a fixed order. Within a step, "
            "individuals are updated synchronously: survival, ageing and "
            "reproduction use the state at the start of that sub-step, and deaths "
            "are applied together after all survival draws. Nodes and species are "
            "processed in index order; this order matters only for the hard "
            "population cap, under which births are truncated in species-index "
            "order (a computational convention that did not change persistence "
            "endpoints when the cap was doubled). The order follows the management "
            "cycle: funds are received and allocated, the environment changes, the "
            "manager observes with delay, acts on what it observed, and the "
            "population then responds."
        ),
    )
    _algorithm(
        doc,
        "Algorithm 1 — one annual step (implemented order)",
        [
            "Funding shock: with probability 0.015 the budget is multiplied by 0.72 "
            "for this year only (not applied to S0).",
            "Allocation: spend_c = B_t · a(π, c) / Σ_c a(π, c) over seven channels "
            "(habitat, survey, rescue, ex situ, genetics, biobank, engagement).",
            "Environment: scenario trend, directional climate (Eq. 1), habitat "
            "investment, scheduled collapse (collapse scenario only) and random "
            "catastrophe; clip quality to [0.05, 0.98].",
            "Observation: true suitability (Eq. 2); noisy counts for visible species "
            "and one-year-delayed noisy quality; decision suitability from observed "
            "quality.",
            "Discovery: each latent species may advance one knowledge stage.",
            "Action: movement under the policy rule (Algorithm 2), with relocation "
            "stress, movement mortality, release mortality and transit infection.",
            "Within-node disease transmission and recovery.",
            "Survival: independent Bernoulli draws with Eq. 6; deaths applied.",
            "Ageing and health random walk.",
            "Reproduction (Eq. 7) with mate co-location and inbreeding; population cap 1200.",
            "Biobank update and extinction-before-discovery bookkeeping.",
            "Welfare accumulation.",
            "Engagement and next-year budget (Eq. 4).",
            "Output recording (annual trajectory; year-50 and year-100 snapshots).",
        ],
    )

    _add_heading(doc, "2.4 Design concepts", 2)
    dc = [
        (
            "Basic principles",
            "Allocation of a fixed budget among competing "
            "conservation actions under partial observability "
            f"{cite('joseph_2009', 'chades_2021')}; translocation as a capacity-"
            f"limited, costly intervention {cite('seddon_2014', 'dickens_2010')}; "
            "demography driven by habitat suitability.",
        ),
        (
            "Emergence",
            "Persistence, the policy ranking, the location of the "
            "S7–S6 reversal, extinction before discovery and the welfare–"
            "persistence trade-off emerge. Survival and fecundity rules, the "
            "visibility gate and the policy rules are imposed.",
        ),
        (
            "Adaptation",
            "Only the manager adapts: under each fixed rule it "
            "chooses which visible species to move and where, from observed counts "
            "and observed suitability (Algorithm 2). Individuals do not adapt.",
        ),
        (
            "Objectives",
            "Rules S4, S5 and S7 rank target nodes by a score "
            "(Eq. 5); S5 additionally uses a one-step greedy expected-utility "
            "proxy. No policy optimises the evaluation endpoints directly.",
        ),
        ("Learning", "Not modelled. Rules and allocation shares are constant."),
        (
            "Prediction",
            "S7 uses an implicit one-step forward-rollout proxy in "
            "target scoring; no other entity predicts.",
        ),
        (
            "Sensing",
            "The manager senses counts of visible species with "
            "log-normal error and node quality with a one-year lag and Gaussian "
            f"error ({n.f('observation')}). Latent species are not sensed.",
        ),
        (
            "Interaction",
            "Individuals interact indirectly through node-level "
            "crowding, infection prevalence and mate availability. There is no "
            "interspecific competition: crowding is computed per species.",
        ),
        (
            "Stochasticity",
            "Funding shocks, catastrophes, observation error, "
            "discovery, movement outcomes, infection, survival, births and health "
            "are random, so that replicate futures differ for the same policy. "
            "Paired seeds share environmental draws across policies; "
            "policy-dependent draws are not exact common random numbers.",
        ),
        (
            "Collectives",
            "Species and node populations are collectives defined "
            "by state variables; they have no behaviour of their own.",
        ),
        (
            "Observation",
            "Year-100 persistence (three endpoints), wild abundance, "
            "extinction before discovery, welfare, effective founders, cost and "
            "future-option value are recorded per replicate and summarised as means "
            "with replicate-distribution intervals and Monte Carlo SEs.",
        ),
    ]
    _rationale(doc, dc)
    _caption(doc, n, "observation", root)

    _add_heading(doc, "2.5 Initialization", 2)
    _p(
        doc,
        (
            "Each replicate starts from the same configuration (Tables "
            f"{n.t('state').split()[1]}–{n.t('params').split()[1]}): 364 individuals "
            "placed in wild nodes with species-specific initial sizes (32–58), "
            "random sex and age (0–15 yr), health drawn from U(0.75, 1), zero "
            "inbreeding and a 2.5% chance of initial infection. Node qualities "
            "start at their base values, the budget at 100, engagement at 0.5 and "
            "the biobank empty. Five species "
            "start known and three latent. Only the seed differs among replicates."
        ),
    )
    _add_heading(doc, "2.6 Input data", 2)
    _p(
        doc,
        (
            "The model uses no external time series as input. GBIF occurrence "
            "aggregates for three managed-species exemplars were persisted with a "
            "provenance ledger and are context only; the aggregates and the "
            "bibliographic evidence levels are in the public repository "
            "(tables/table5_empirical_coverage.csv, tables/table6_empirical_evidence.csv). "
            "They do not calibrate or validate any parameter."
        ),
    )

    # ------------------------------------------------------------ 2.7 Submodels
    _add_heading(doc, "2.7 Submodels", 2)
    _p(
        doc,
        (
            "Each submodel lists its equation and, following Supplement S1, the "
            "process it approximates, why the form was chosen, alternatives, "
            "simplifying assumptions, how they can affect the conclusions, the "
            "supporting evidence and the evidence that is missing. Numeric literals "
            "inside equations are synthetic unless stated; the ten literals that "
            "decide suitability, movement, survival and births were perturbed by "
            "±50% in Section 2.9 (Q3)."
        ),
    )
    _add_heading(doc, "2.7.1 Habitat quality and directional climate", 3)
    _omml_equation(
        doc,
        "q_j(t) = clip(q_j(t−1) − δ − 1[j=0]·v·t/T + 1[j=1]·0.65·v·t/T "
        "+ (spend_hab/B_0)·e·r_j − κ_j(t); 0.05, 0.98)   (1)",
    )
    _p(
        doc,
        (
            "where δ = 0.006 yr⁻¹ is background deterioration, v = 0.012 the "
            "climate velocity, T = 100 the horizon, e the habitat-protection "
            "efficiency, r_j the restoration potential and κ_j(t) a catastrophe "
            "loss (probability 0.035 yr⁻¹, size U(0.16, 0.38)). The annual climate "
            "decrement at the origin is v·t/T, so it increases each year and the "
            "cumulative displacement grows quadratically, reaching about 0.61 at "
            f"year 100 ({n.f('origin_future')}). The submitted version described "
            "this term in a way that could be read as linear; Eq. 1 is the "
            "implemented form."
        ),
    )
    _caption(doc, n, "origin_future", root)
    _rationale(
        doc,
        [
            (
                "Process",
                "directional loss of origin habitat, partial gain of an "
                "alternative habitat, and restoration proportional to spending.",
            ),
            (
                "Form",
                "additive annual increments keep the habitat budget transparent: "
                "the S6–S7 contrast is a race between Eq. 1 decline and habitat-spend "
                "recovery (S6 habitat share 0.68 vs S7 0.35).",
            ),
            (
                "Alternatives",
                "linear, decelerating and step trajectories with the "
                "same year-100 displacement were run as Q2 (Section 2.9); saturating "
                "restoration and spatially correlated catastrophes were not.",
            ),
            (
                "Assumptions",
                "accelerating change is one plausible scenario among "
                f"several {cite('hoegh_guldberg_2008', 'thomas_2011')}; it delivers "
                "the least cumulative exposure of the four forms tested.",
            ),
            (
                "Effect on conclusions",
                "large: the base-case sign of S7 − S6 reverses "
                "under each alternative trajectory (Section 3.4).",
            ),
            ("Evidence", f"direction only {cite('watson_2014', 'hoegh_guldberg_2008')}."),
            (
                "Missing evidence",
                "no system-specific trajectory or rate; the "
                "trajectory form is an exploratory structural assumption.",
            ),
        ],
    )
    _add_heading(doc, "2.7.2 Species–node suitability", 3)
    _omml_equation(
        doc,
        "s(x,j) = clip(q_j·(0.72 + 0.28·b_x) − 0.32·h_x·(1 − q_j) "
        "+ 0.25·M_j(1−W_j)(τ_x − 0.5) − 0.24·M_j(1−W_j)·m_x; 0.02, 0.99)   (2)",
    )
    _p(
        doc,
        (
            "where b_x is niche breadth, h_x habitat specificity, τ_x captivity "
            "tolerance, m_x migration need, and M_j, W_j indicate managed and wild "
            "nodes. Eq. 2 is used with true quality for ecology and with observed "
            "quality for decisions."
        ),
    )
    _rationale(
        doc,
        [
            ("Process", "how well a node meets a species' requirements."),
            (
                "Form",
                "linear in quality with a breadth slope, so generalists lose "
                "less than specialists when quality falls; managed-only nodes add a "
                "tolerance bonus and a migration-need penalty.",
            ),
            (
                "Alternatives",
                "logistic or threshold suitability and species-specific "
                "climate envelopes; not used because no data constrain their shape.",
            ),
            (
                "Assumptions",
                "one suitability index drives eligibility, targeting, "
                "survival and births; no species-specific climate response.",
            ),
            (
                "Effect on conclusions",
                f"the intercept 0.72 is load-bearing: at ×1.5 "
                f"the base S7 − S6 contrast became +{e1hi.survival_100_diff:.3f} "
                f"(SE {e1hi.survival_100_se:.3f}); at ×0.5 both policies lose almost all "
                "species (Section 3.5).",
            ),
            (
                "Evidence",
                "qualitative ex situ suitability literature "
                f"{cite('conde_2011_science', 'pritchard_2012')}.",
            ),
            ("Missing evidence", "all five literals are uncalibrated."),
        ],
    )
    _add_heading(doc, "2.7.3 Observation", 3)
    _p(
        doc,
        (
            "Observed counts are true counts × LogNormal(0, 0.18) for species at "
            "knowledge stage ≥ 2 and missing otherwise; observed quality is "
            "q_j(t − 1) + N(0, 0.10), clipped to [0, 1]. Rationale: monitoring error "
            f"and reporting lag are standard features of managed systems "
            f"{cite('williams_brown_2022')}. A binomial detection model or "
            "autocorrelated error were alternatives. The magnitudes are synthetic; "
            "the perfect-current-state comparator (Section 2.8) bounds their "
            "effect on outcomes."
        ),
    )
    _add_heading(doc, "2.7.4 Discovery of latent species", 3)
    _omml_equation(
        doc, "P(k → k+1) = min(cap_k, p_0 + c_k·spend_survey/c_survey · [d_x if k = 0])   (3)"
    )
    _p(
        doc,
        (
            "with background p_0 = 0.005 yr⁻¹, stage coefficients c_k = 0.16, 0.12, "
            "0.10, 0.09, 0.06, caps 0.95, 0.85, 0.75, 0.65, 0.60, survey cost 10 and "
            "detectability d_x (stage 0 only); the last stage also gains "
            "spend_hab/1000. "
            "A species becomes visible to decisions at stage 2. Rationale: detection "
            "and recognition of unknown taxa take time and effort "
            f"{cite('mora_2011', 'costello_2013', 'tedesco_2014')}. A single "
            "detection hazard or an occupancy–detection model were alternatives; "
            "the staged form makes the visibility delay explicit. Advancement is at "
            "most one stage per year; the coefficients are synthetic. This gate is "
            "a load-bearing input of Ψ (Section 2.10)."
        ),
    )
    _add_heading(doc, "2.7.5 Budget, engagement and funding shocks", 3)
    _omml_equation(
        doc,
        "E_{t+1} = clip(E_t + 0.08·(x̄ + 0.2·spend_eng/B_t) + 0.02·q̄_{0–2}; 0, 1.5),  "
        "B_{t+1} = B_0·(0.82 + 0.24·E_{t+1})   (4)",
    )
    _p(
        doc,
        (
            "where x̄ is the mean visitor exposure of the nodes occupied by living "
            "individuals, q̄_{0–2} the mean quality of the origin, alternative and "
            "reserve nodes, and E_0 = 0.5. Because every increment is non-negative, engagement "
            "never decreases; this is a simplification, not an empirical claim. "
            "The funding shock is a one-year budget reduction (×0.72), not a "
            "persistent collapse. Rationale: public engagement is one route by which "
            f"zoos contribute to conservation funding {cite('moss_2015')}; a "
            "saturating or decaying engagement function was an alternative. The "
            "fixed allocation shares (Table "
            f"{n.t('policies').split()[1]}) mean S6 and S7 differ in all seven "
            "channels at once, so their contrast is a bundled policy contrast."
        ),
    )
    pol = pd.read_csv(root / "tables/table2_policies.csv")
    _table(doc, n, "policies", pol, "Policies and allocation shares")
    _add_heading(doc, "2.7.6 Movement: capacity, eligibility, targets and costs", 3)
    _algorithm(
        doc,
        "Algorithm 2 — action selection per annual step",
        [
            "If π ∈ {S0, S6} or rescue spend = 0: no movement (S6's 3% rescue share "
            "is spent but never converted to moves).",
            "Capacity C = max(1, ⌊spend_rescue / 2.5⌋).",
            "Rank visible species by risk 1/(1 + n_obs) + (1 − observed origin suitability).",
            "Eligibility: S1 individuals in managed nodes; S2/S4/S5/S7 decision "
            "suitability < 0.58; S3 refuge if origin suitability < 0.48, return if "
            "year ≥ 5, suitability ≥ 0.62 and release readiness ≥ 0.40.",
            "Target: S1 best wild node; S2 conventional zoo; S3 best of {conservation "
            "zoo, breeding} or origin; S4/S5/S7 argmax of Eq. 5; biobank excluded.",
            "Take = min(candidates, C − moved, max(1, ⌊0.20·candidates⌋), target capacity).",
            "Apply relocation stress, movement mortality (0.025), release mortality "
            "for managed → wild moves (0.08) and transit infection "
            "0.03·(1 − 0.65·coverage).",
        ],
    )
    _omml_equation(
        doc,
        "score_j = s_obs(x,j) − 0.04·cost_j + 0.03·research_j + b_π,j + φ·1[j = origin]   (5)",
    )
    _rationale(
        doc,
        [
            (
                "Process",
                "capacity-limited translocation triggered by perceived "
                f"habitat inadequacy {cite('seddon_2014', 'dickens_2010', 'kock_2010')}.",
            ),
            (
                "Form",
                "a fixed cost per move and a suitability threshold give a "
                "transparent rule a manager could apply.",
            ),
            (
                "Alternatives",
                "distance-dependent costs and optimisation over moves; "
                "not used because the network has no topology.",
            ),
            (
                "Assumptions",
                "at least one move per year whenever rescue spend > 0; "
                "release events are counted before release mortality (reported as "
                "\u2018release events\u2019, not successful reintroductions).",
            ),
            (
                "Effect on conclusions",
                "threshold 0.58 × 0.5 widened the S6 advantage "
                "most strongly of all Q3 perturbations; take fraction changed magnitude "
                "only (Section 3.5).",
            ),
            (
                "Evidence",
                f"direction of costs {cite('dickens_2010', 'jule_2008', 'harrington_2013')}.",
            ),
            ("Missing evidence", "cost per move, threshold and take fraction are uncalibrated."),
        ],
    )
    _add_heading(doc, "2.7.7 Disease", 3)
    _p(
        doc,
        (
            "Susceptibles in node j are infected with probability clip(β_j · "
            "prevalence_j; 0, 0.65) and infected individuals recover with "
            "probability 0.32 to permanent immunity. A frequency-dependent SIR "
            f"form is the simplest representation {cite('kock_2010')}; annual steps "
            "are coarse for epidemics, and the disease ablation bounds its role."
        ),
    )
    _add_heading(doc, "2.7.8 Survival", 3)
    _omml_equation(
        doc,
        "p_i = clip(1 − μ_x·m − 0.24·(1 − s) − 0.08·a_i − 0.14·I_i + "
        "0.035·M_j·r_j − 0.035·W_j·ρ_j·m_ρ − 0.08·(1 − h_i) − 0.08·F_i; 0.05, 0.995)   (6)",
    )
    _rationale(
        doc,
        [
            (
                "Process",
                "annual survival lowered by intrinsic mortality μ_x, poor "
                "suitability s, anthropogenic pressure a_i, infection I_i, wild "
                "predation ρ_j, poor health h_i and inbreeding F_i; raised by research "
                "care r_j in managed nodes.",
            ),
            (
                "Form",
                "an additive hazard decomposition, so the contribution of each cause is readable.",
            ),
            (
                "Alternatives",
                "multiplicative (proportional-hazards) or age-specific "
                "survival; not used for transparency. There is no senescence.",
            ),
            ("Assumptions", "age-independent survival with a floor of 0.05."),
            (
                "Effect on conclusions",
                f"habitat mortality 0.24 × 1.5 flipped Ψ in {flips('e11_habitat_mortality', 1.5)} "
                "of 56 held-out cells but did not reverse the IBM contrast.",
            ),
            (
                "Evidence",
                f"directions of captivity and inbreeding effects "
                f"{cite('araki_2007', 'frankham_2008')}.",
            ),
            ("Missing evidence", "magnitudes are synthetic."),
        ],
    )
    _add_heading(doc, "2.7.9 Reproduction, genetics and population cap", 3)
    _omml_equation(
        doc,
        "births ~ Poisson(n_F·λ),  λ = (μ_x + g_x)(0.5 + f_x)·s·max(0.05, "
        "1 − n_xj/K_j)·5.0·(1 + 0.22·spend_exsitu/B_t)^{M_j}·max(0.05, "
        "1 − 0.30·inf_j)·max(0.05, 1 − 0.35·F̄)   (7)",
    )
    _rationale(
        doc,
        [
            (
                "Process",
                "births by co-located mature females (age ≥ 2) when at "
                "least one mature male is present.",
            ),
            (
                "Form",
                "scaling by (μ_x + g_x) makes replacement roughly balanced at "
                "good suitability; crowding is per species within node capacity.",
            ),
            (
                "Alternatives",
                "Beverton–Holt or Ricker density dependence, shared "
                "capacity across species, Allee effects.",
            ),
            (
                "Assumptions",
                "no interspecific competition; offspring inbreeding "
                "F = (F_m + F_f)/2 + 0.08 for same-founder pairs, × 0.82 with "
                "diversity-aware pairing; total population capped at 1200.",
            ),
            (
                "Effect on conclusions",
                f"birth scale 5.0 × 0.5 flipped Ψ in {flips('e12_birth_scale', 0.5)} of 56 "
                "held-out cells and made the S6 advantage determinate.",
            ),
            (
                "Evidence",
                f"direction of pedigree management benefits "
                f"{cite('williams_hoffman_2009', 'howell_2021')}.",
            ),
            ("Missing evidence", "the 5.0 scale and penalties are uncalibrated."),
        ],
    )
    _add_heading(doc, "2.7.10 Biobank, welfare and extinction before discovery", 3)
    _p(
        doc,
        (
            "Biobank coverage decays 1% per year and grows with biobank spending for "
            f"extant visible species {cite('bolton_2022')}; it never restores "
            "individuals and enters only the future-option value. Individual welfare "
            "is the node welfare standard minus seven additive burdens "
            f"{cite('mellor_2020', 'beausoleil_2018')}; it is a normative device "
            "and does not feed back on demography. A latent species that goes "
            "extinct while at stage < 2 is recorded as extinction before discovery "
            f"(EBD) {cite('boehm_cronk_2021')}, an endpoint defined by the model's "
            "visibility rule."
        ),
    )

    # ---------------------------------------------- 2.8 Simulation experiments
    _add_heading(doc, "2.8 Simulation experiments", 2)
    _p(
        doc,
        (
            "The base design runs 192 paired-seed replicates per policy; Monte Carlo "
            "convergence was checked with nested prefixes up to n = 384. Twelve "
            "parameters were varied by Latin hypercube (128 designs × 4 replicates) "
            "and summarised with Spearman rank correlations and partial-rank "
            "interaction screens (Appendix A, Tables A1–A2). Five two-factor sweeps "
            "(5 × 5 cells × 8 paired replicates) compared S4, S6 and S7; a cell's "
            "direction is robust only if sign-stable from n = 4 to n = 8 and the "
            "mean exceeds 1.96 Monte Carlo SEs. Nine feature ablations and six "
            "adverse-condition designs isolate mechanisms. A perfect-current-state "
            "comparator reruns S7 with true counts and quality on the same seeds; "
            "it keeps the S7 rule, so the paired difference is an information effect, "
            "not the expected value of perfect information. Policies are compared on "
            f"six objectives with exact-dominance Pareto flags {cite('kennedy_2008')} "
            "and no weighted winner."
        ),
    )
    _add_heading(doc, "2.9 Preregistered structural verification (Q1–Q3)", 2)
    _p(
        doc,
        (
            "Three construction choices that could decide the S7–S6 contrast were "
            "tested after the original submission with a plan, endpoints, seeds and "
            "materiality rules frozen and committed before any run. The default "
            "dynamics were not changed; the alternatives are opt-in configurations "
            "and observer outputs that draw no random numbers. Q1 recomputed the "
            "base scenario (all policies, seeds as in the base design) and the 56 "
            "held-out cells (Section 2.10) under individual, reproductive-proxy and "
            "wild persistence. Q2 replaced the accelerating climate decrement with "
            "linear, decelerating and mid-run step trajectories that have the same "
            "year-100 displacement; because equal endpoints do not mean equal "
            "exposure, cumulative exposure (the sum of displacement over years) is "
            "reported for each form. Q3 perturbed ten literals of Eqs. 2, 6, 7 and "
            "Algorithm 2 one at a time by ×0.5 and ×1.5 (48 paired seeds), all "
            "within their domains. A perturbation was material if the base contrast "
            "changed sign category, shifted by more than 2 SE, or flipped Ψ in at "
            "least 5 of 56 held-out cells; up to six material perturbations, ranked "
            "first by Ψ flips, received full held-out reruns. Policy-contrast "
            "sensitivity and Ψ sensitivity are reported separately."
        ),
    )
    _add_heading(doc, "2.10 Reduced reversal criterion Ψ", 2)
    _add_heading(doc, "2.10.1 Definition", 3)
    _p(
        doc,
        (
            "The sweeps map where the ranking reverses but do not explain it. I "
            "reduced the IBM to a per-species deterministic rollout that keeps "
            "Eqs. 2 and 6 with stochastic terms replaced by expectations, requires "
            "co-located mature females and males with a minimum breeding population "
            "(MIN_BREEDING_POP = 4), lets each latent cohort join the movable pool "
            "at its expected discovery year, and shares rescue capacity equally among "
            "at-risk species. Four constants (typical health, inbreeding load, "
            "female fraction, minimum breeding population) were set on 125 "
            "development sweep cells. The reduced persistence index M is computed "
            "for the S7 allocation with its movement rule, the S7 allocation with "
            "movement disabled, and the S6 allocation, and"
        ),
    )
    _omml_equation(
        doc,
        "Ψ = H + C,  H = ln[(M_S7,no-move + ε)/(M_S6 + ε)],  "
        "C = ln[(M_S7,rule + ε)/(M_S7,no-move + ε)],  ε = 0.02   (8)",
    )
    _p(
        doc,
        (
            "H is the habitat channel (the cost of S7's smaller habitat share) and C "
            "the circulation channel (what movement adds under the S7 budget); Ψ > 0 "
            "predicts S7. Because S7 and S6 differ in budget and in movement rule, "
            "Ψ predicts a bundled policy contrast; it does not isolate the causal "
            "effect of circulation. A cell is determinate when |mean S7 − S6| "
            "exceeds 2 Monte Carlo SEs and indeterminate otherwise. Decision regret "
            "is the mean year-100 persistence forgone by following the predicted "
            "sign instead of the better observed policy."
        ),
    )
    _add_heading(doc, "2.10.2 Provenance of the original held-out evaluation", 3)
    fz = v["forensic"]
    v0 = fz.iloc[0]
    v1 = fz.iloc[1]
    _p(
        doc,
        (
            f"The submitted version reported a held-out evaluation on "
            f"{int(rev.holdout_cells)} cells (12 paired seeds each, disjoint from "
            "development) as an evaluation of a frozen model with MIN_BREEDING_POP "
            "= 8. A forensic reconstruction for this revision showed that the stored "
            "held-out Ψ values were produced by the implementation loaded when that "
            "run started (V0: per-individual latent discovery, ε = 10⁻⁹, "
            "MIN_BREEDING_POP = 4), which reproduces all 56 stored values exactly. "
            "Two edits made while the run was in progress (cohort-level discovery; "
            "ε = 0.02) define the committed implementation V1, which is the one "
            "documented above. The value 8 was examined only in a development "
            "sweep and was never set in code. The submitted text paired V1 "
            f"development accuracy ({v1.dev_acc_all:.3f}) with V0 held-out accuracy; "
            f"V0's own development accuracy was {v0.dev_acc_all:.3f}. I therefore "
            "withdraw the claim that the original held-out analysis evaluated the "
            "documented frozen model. Its results are reported as historical (V0), "
            "V1 results on the same cells as exploratory, and the confirmatory test "
            "is the prospective evaluation below."
        ),
    )
    _add_heading(doc, "2.10.3 Prospective confirmatory evaluation", 3)
    ds = v["conf_design"]
    _p(
        doc,
        (
            f"After Q1–Q3, V1 Ψ was frozen and {len(ds)} new configurations were "
            f"generated by a fixed seed sequence ({int((ds.group == 'in_domain').sum())} "
            "joint three-parameter perturbations inside the development domain and "
            f"{int((ds.group == 'shifted').sum())} outside it), excluding duplicates "
            "of development and earlier held-out cells. Ψ predictions, the "
            "specification, metrics, exclusions and pass criteria were committed "
            "with a timestamp before any IBM run. Each cell ran 12 paired seeds "
            "from an unused seed range. The pre-specified criteria (primary "
            "endpoint individual persistence) were: determinate accuracy ≥ 0.75 "
            "with Wilson 95% lower bound > 0.5; Ψ regret below both always-S6 and "
            "always-S7; and at least 15 determinate cells."
        ),
    )

    # ---------------------------------------------------------------- Results
    _add_heading(doc, "3. Results", 1)
    _add_heading(doc, "3.1 Base scenario, patterns and trade-offs", 2)
    costs = [est(v, f"S{i}", "cost") for i in range(1, 8)]
    cost_span = (max(costs) - min(costs)) / min(costs)
    _p(
        doc,
        (
            f"S6 retained the most species at year 100 ({ival(v, s6, 'survival_100')}), "
            f"followed by S7 ({ival(v, s7, 'survival_100')}) and S4 "
            f"({ival(v, 'S4', 'survival_100')}) ({n.t('outcomes')}; "
            f"{n.f('trajectories')}). S0 lost every species (P1). S2 and S3 "
            "retained species only outside wild nodes (P2): S3 produced "
            f"{est(v, 'S3', 'successful_reintroductions'):.1f} release events per run "
            "but no wild persistence: no release established a persisting wild "
            "population. Six of eight policies were Pareto non-dominated (only S2 and "
            "S5 were dominated). S6 had the highest persistence, habitat integrity "
            f"({est(v, s6, 'habitat_integrity'):.3f} vs {est(v, s7, 'habitat_integrity'):.3f}), "
            f"welfare ({est(v, s6, 'mean_individual_welfare'):.3f} vs "
            f"{est(v, s7, 'mean_individual_welfare'):.3f}) and future-option value, "
            "whereas S7 had the highest wild abundance "
            f"({est(v, s7, 'wild_abundance'):.0f} vs {est(v, s6, 'wild_abundance'):.0f} "
            f"individuals; {n.f('pareto')}, {n.f('tradeoffs')}). Total cost "
            f"differed by at most {cost_span:.1%} among managed policies."
        ),
    )
    outc = pd.read_csv(root / "tables/table3_policy_outcomes.csv")
    _table(
        doc,
        n,
        "outcomes",
        outc,
        "Policy outcomes, base scenario: mean [2.5%, 97.5% replicate quantiles], 192 paired seeds",
        size=7,
    )
    _caption(doc, n, "trajectories", root)
    _caption(doc, n, "pareto", root)
    _caption(doc, n, "tradeoffs", root)
    _add_heading(doc, "3.2 Where the ranking reverses in the sweeps", 2)
    _p(
        doc,
        (
            f"Across the five sweeps {v['sweep_s7']} cells robustly favoured S7, "
            f"{v['sweep_s6']} favoured S6 and {v['sweep_ind']} were indeterminate at "
            "n = 8. S7 cells concentrated at high deterioration and climate velocity "
            "and where movement is cheap and survivable (P4); S6 cells where "
            "captivity benefit is low, habitat investment effective or survey "
            f"capacity limiting ({n.f('reversal')})."
        ),
    )
    _caption(doc, n, "reversal", root)

    _add_heading(doc, "3.3 Persistence endpoint (Q1)", 2)
    rows = []
    names = {
        "survival_100": "individual",
        "viable_persistence_100": "reproductive proxy",
        "wild_persistence_100": "wild",
    }
    for ep, name in names.items():
        c = c1.loc[ep]
        hr = q1(v, ep, "psi_reg")
        hc = q1(v, ep, "psi_code")
        rows.append(
            (
                name,
                f"{c.S6_mean:.3f}",
                f"{c.S7_mean:.3f}",
                f"{c.S7_minus_S6:.3f} ({c.se:.3f})",
                f"{c.kendall_tau_vs_individual:.2f}",
                f"{int(hr.s7_cells)}/{int(hr.s6_cells)}/{int(hr.ind_cells)}",
                f"{hr.acc_det:.3f}",
                f"{hc.acc_det:.3f}",
            )
        )
    q1t = pd.DataFrame(
        rows,
        columns=[
            "endpoint",
            "S6",
            "S7",
            "S7−S6 (SE)",
            "Kendall τ (8 policies)",
            "held-out S7/S6/indet.",
            "Ψ V0 det. acc.",
            "Ψ V1 det. acc. (exploratory)",
        ],
    )
    _p(
        doc,
        (
            "The base ordering S6 > S7 held under all three endpoints "
            f"({n.t('q1')}). The eight-policy ranking was identical for individual "
            "and reproductive-proxy persistence and changed for wild persistence "
            f"(τ = {c1.loc['wild_persistence_100'].kendall_tau_vs_individual:.2f}), "
            "because S2 and S3 have no wild persistence. In the held-out cells the "
            "reproductive proxy changed one cell. Wild persistence changed the "
            "picture: of the "
            f"{sum(trans(v, 'wild_persistence_100', 1, k) for k in (1, 0, -1))} "
            "cells in which S7 retained more species, "
            f"{trans(v, 'wild_persistence_100', 1, 1)} remained S7-favoured for "
            f"wild persistence, {trans(v, 'wild_persistence_100', 1, 0)} became "
            f"indeterminate and {trans(v, 'wild_persistence_100', 1, -1)} reversed. "
            "Most of S7's advantage is therefore persistence in managed or "
            "transitional nodes rather than in the wild."
        ),
    )
    _table(
        doc,
        n,
        "q1",
        q1t,
        "Q1: S7 − S6 contrast by persistence endpoint "
        "(base: 192 paired seeds; held-out: 56 cells × 12 paired seeds)",
        size=7,
    )

    _add_heading(doc, "3.4 Climate trajectory (Q2)", 2)
    rows = []
    for f, r in acc.items():
        b1 = q2psi(v, f, "b1_psi_code")
        b2 = q2psi(v, f, "b2_psi_code_alt")
        rows.append(
            (
                f,
                f"{r.cumulative_exposure_disp_years:.1f}",
                f"{r.exposure_ratio_vs_shipped:.2f}",
                f"{r.S6_mean:.3f}",
                f"{r.S7_mean:.3f}",
                f"{r.S7_minus_S6:+.3f} ({r.se:.3f})",
                f"{r.holdout_det_sign_agreement_vs_shipped:.2f}",
                f"{b1.acc_det:.2f}",
                f"{b2.acc_det:.2f}",
            )
        )
    q2t = pd.DataFrame(
        rows,
        columns=[
            "form",
            "cumulative exposure",
            "× shipped",
            "S6",
            "S7",
            "S7−S6 (SE)",
            "held-out agreement",
            "Ψ shipped climate",
            "Ψ matched climate",
        ],
    )
    _p(
        doc,
        (
            "All four trajectories reach the same year-100 displacement "
            f"({acc['accelerating'].year100_displacement:.3f}), but the alternatives "
            f"impose {acc['linear'].exposure_ratio_vs_shipped:.2f}–"
            f"{acc['decelerating'].exposure_ratio_vs_shipped:.2f} times the cumulative "
            f"exposure of the shipped accelerating form ({n.t('q2')}; "
            f"{n.f('climate_forms')}). The base contrast reversed under every "
            "alternative: S6 persistence fell from "
            f"{acc['accelerating'].S6_mean:.3f} to {acc['linear'].S6_mean:.3f}–"
            f"{acc['step'].S6_mean:.3f}, while S7 stayed between "
            f"{min(r.S7_mean for r in acc.values()):.3f} and "
            f"{max(r.S7_mean for r in acc.values()):.3f}. Agreement of determinate "
            "held-out signs with the shipped form was below the pre-stated 80% for "
            "every alternative, so the location of the reversal depends on the "
            "time course of exposure. In these forms earlier exposure also means "
            "larger cumulative exposure, so the design does not separate timing "
            "from cumulative dose. Endpoint matching is not exposure matching, and "
            "these comparisons should be read as different climate scenarios."
        ),
    )
    _table(
        doc,
        n,
        "q2",
        q2t,
        "Q2: climate trajectories with equal year-100 "
        "displacement (base: 192 paired seeds; held-out: 56 cells). Ψ columns "
        "give determinate held-out accuracy",
        size=7,
    )
    _caption(doc, n, "climate_forms", root)

    _add_heading(doc, "3.5 Coefficient perturbations, Latin hypercube and ablations (Q3)", 2)
    sel = v["q3_sel"]
    staged = {(r.literal, r.factor) for r in sel[sel.stage2_evaluated].itertuples()}
    q3t = pd.DataFrame(
        [
            (
                r.literal,
                r.factor,
                f"{r.value:g}",
                f"{r.survival_100_diff:+.3f} ({r.survival_100_se:.3f})",
                {1: "S7", -1: "S6", 0: "indet."}[int(r.survival_100_sign)],
                int(r.psi_sign_flips),
                "yes" if r.material else "no",
                "yes" if (r.literal, r.factor) in staged else "—",
            )
            for r in q3.itertuples()
        ],
        columns=[
            "literal",
            "factor",
            "value",
            "S7−S6 (SE)",
            "sign",
            "Ψ flips /56",
            "material",
            "held-out rerun",
        ],
    )
    ref = q3.iloc[0]
    _p(
        doc,
        (
            "On the 48 Q3 seeds the unperturbed contrast was "
            f"{ref.survival_100_ref_diff:.3f} (SE {ref.survival_100_ref_se:.3f}, "
            f"indeterminate). {int(q3.material.sum())} of {len(q3)} perturbations were "
            f"material ({n.t('q3')}), mostly because the contrast became determinately "
            "S6. Only one perturbation reversed the direction: the suitability "
            f"intercept ×1.5 gave +{e1hi.survival_100_diff:.3f} (SE "
            f"{e1hi.survival_100_se:.3f}). Under the frozen ranking rule it was not "
            "among the six held-out reruns, so its held-out effect is not evaluated. "
            "Halving the movement-eligibility threshold produced the largest shift "
            "towards S6. The specificity, tolerance and migration literals and the "
            "pressure mortality changed magnitude or determinacy only. Feature "
            f"ablations ({abl_n} paired seeds each, point estimates; Appendix A, "
            "Table A3) also moved the contrast: S7 had the higher persistence when "
            f"{abl_pos}, and S6 kept a clear advantage when {abl_neg}; differences "
            f"were within ±0.05 when {abl_small}. The ablations "
            "therefore confirm that the base ordering is conditional on several "
            "submodels, not only on the climate and suitability terms."
        ),
    )
    _table(
        doc,
        n,
        "q3",
        q3t,
        "Q3: one-at-a-time ±50% perturbations of ten "
        "literals (48 paired seeds; individual persistence)",
        size=7,
    )

    _add_heading(doc, "3.6 Predictive performance of Ψ", 2)
    hc = q1(v, "survival_100", "psi_code")
    rows = [
        (
            "historical held-out (V0)",
            "56",
            int(hist.det_cells),
            f"{hist.acc_det:.3f}",
            f"{hist.acc_all:.3f}",
            f"{hist.regret_psi:.4f}",
            f"{hist.regret_always_S6:.4f}",
            "historical",
        ),
        (
            "same cells, V1",
            "56",
            int(hc.det_cells),
            f"{hc.acc_det:.3f}",
            f"{hc.acc_all:.3f}",
            f"{hc.regret_psi:.4f}",
            f"{hc.regret_always_S6:.4f}",
            "exploratory",
        ),
    ]
    for stratum, label in [
        ("all", "prospective, all"),
        ("in_domain", "prospective, in-domain"),
        ("shifted", "prospective, shifted"),
    ]:
        r = conf(v, "survival_100", stratum)
        rows.append(
            (
                label,
                str(int(r.cells)),
                int(r.det_cells),
                f"{r.acc_det:.3f} [{r.acc_det_wilson_lo:.3f}, {r.acc_det_wilson_hi:.3f}]",
                f"{r.acc_all:.3f}",
                f"{r.regret_psi:.4f}",
                f"{min(r.regret_always_S6, r.regret_always_S7):.4f}",
                "confirmatory",
            )
        )
    psit = pd.DataFrame(
        rows,
        columns=[
            "evaluation",
            "cells",
            "determinate",
            "det. accuracy [Wilson 95%]",
            "all-cell accuracy",
            "Ψ regret",
            "best fixed-policy regret",
            "status",
        ],
    )
    cv = conf(v, "viable_persistence_100")
    cw = conf(v, "wild_persistence_100")
    _p(
        doc,
        (
            f"In the prospective evaluation ({n.t('psi')}) {int(cf.det_cells)} of "
            f"{int(cf.cells)} cells were determinate ({int(cf.s7_cells)} S7, "
            f"{int(cf.s6_cells)} S6), and Ψ signed {cf.acc_det:.3f} of them correctly "
            f"(Wilson 95% {cf.acc_det_wilson_lo:.3f}–{cf.acc_det_wilson_hi:.3f}). Ψ "
            f"regret was {cf.regret_psi:.4f} against {cf.regret_always_S6:.4f} for "
            f"always-S6 and {cf.regret_always_S7:.4f} for always-S7. All three "
            "pre-specified criteria were met. The secondary endpoints gave "
            f"{cv.acc_det:.3f} (reproductive proxy) and {cw.acc_det:.3f} (wild). "
            f"All-cell accuracy was only {cf.acc_all:.3f}, because Ψ always makes a "
            "call while many cells have no determinate answer at 12 replicates. In "
            f"the historical V0 evaluation Ψ signed {hist.acc_det:.3f} of "
            f"{int(hist.det_cells)} determinate cells correctly (Appendix A, Table A5), with "
            f"{rev.near_boundary_acc:.3f} accuracy among the "
            f"{int(rev.near_boundary_cells)} cells with |Ψ| < 0.2 "
            f"({n.f('psi')}); a post hoc abstention rule (|Ψ| ≥ 0.1) is reported "
            "there as descriptive only."
        ),
    )
    _p(
        doc,
        (
            "The prospective result holds only for the shipped structure. Under the "
            "alternative climate trajectories (Q2), Ψ computed with the shipped "
            "accelerating climate signed "
            f"{q2psi(v, 'linear', 'b1_psi_code').acc_det:.2f}, "
            f"{q2psi(v, 'decelerating', 'b1_psi_code').acc_det:.2f} and "
            f"{q2psi(v, 'step', 'b1_psi_code').acc_det:.2f} of determinate cells "
            "correctly; recomputed with the matching trajectory it gave "
            f"{q2psi(v, 'linear', 'b2_psi_code_alt').acc_det:.2f}, "
            f"{q2psi(v, 'decelerating', 'b2_psi_code_alt').acc_det:.2f} and "
            f"{q2psi(v, 'step', 'b2_psi_code_alt').acc_det:.2f}, an exploratory "
            "result. Among Q3 perturbations Ψ was most fragile to the suitability "
            f"intercept (×0.5: {flips('e1_intercept', 0.5)} of 56 sign flips), the "
            f"breadth slope (×1.5: {flips('e1_breadth_slope', 1.5)}) and the birth "
            f"scale (×0.5: {flips('e12_birth_scale', 0.5)})."
        ),
    )
    _table(
        doc,
        n,
        "psi",
        psit,
        "Predictive performance of Ψ for the S7 − S6 sign (individual persistence)",
        size=7,
    )
    _caption(doc, n, "psi", root)

    _add_heading(doc, "3.7 Extinction before discovery and information", 2)
    info = v["info"]
    _p(
        doc,
        (
            f"EBD affected {ival(v, 'S1', 'fraction_ebd')} of latent species under "
            f"the best feasible policy and {ival(v, 'S0', 'fraction_ebd')} without "
            "intervention. Survey investment reduces EBD but cannot remove it, "
            "because detection saturates and a species below stage 2 cannot be "
            f"moved ({n.f('ebd')}). The paired perfect-current-state effect on the "
            f"utility index was {info.estimate:.3f} [{info.lower:.3f}, "
            f"{info.upper:.3f}]: under these rules better current observation gave "
            "no detectable improvement. This does not show that information has no "
            "value, because the comparator keeps the S7 decision rule and removes "
            "only current-state observation error; it does not test information "
            f"used by a different or adaptive rule {cite('canessa_2015')}."
        ),
    )
    _caption(doc, n, "ebd", root)

    # ------------------------------------------------------------- Discussion
    _add_heading(doc, "4. Discussion", 1)
    _p(
        doc,
        (
            "Whether circulation pays in this model is decided by how much and how "
            "early origin habitat is lost relative to what habitat spending can "
            "recover, by baseline suitability, and by the costs and capacity of "
            "movement. Under the shipped accelerating trajectory, habitat-first "
            "spending retains more species; with the same year-100 displacement but "
            "earlier exposure, circulation does. The reversal is therefore a located, "
            "conditional result, not a general ranking of the two strategies, and "
            "its location moves with the time course, and hence the cumulative "
            "amount, of climate exposure. This is "
            f"consistent with the view that relocation is a response to rapid change "
            f"rather than a default {cite('mclachlan_2007', 'richardson_2009')}, but "
            "the model does not test that view against data."
        ),
    )
    _p(
        doc,
        (
            "The endpoint analysis qualifies the conservation reading. The "
            "reproductive proxy barely changed the results, but most held-out "
            "advantages of S7 disappeared when only wild persistence counted. In the "
            "model, circulation mainly keeps species alive in managed and "
            "transitional nodes, which matches the long-standing concern that "
            "captive persistence need not mean wild recovery "
            f"{cite('snyder_1996', 'redford_2012')}."
        ),
    )
    _p(
        doc,
        (
            "Five kinds of evidence should be kept apart. Computational "
            "reproducibility is established: the committed code regenerates the "
            "registries and every number in this paper (the historical V0 values "
            "through the committed forensic reconstruction). Ecological plausibility is "
            "supported only qualitatively, by the four evaluation patterns, two of "
            "which partly follow from the construction. Mechanistic explanation is "
            "provided by Ψ, whose habitat and circulation channels account for the "
            "direction of the contrast within the shipped structure. Predictive "
            "performance is established for that structure by a prospective, "
            "pre-registered evaluation; it does not transfer to other climate "
            "trajectories unless Ψ is given the matching trajectory. External "
            "validation is absent: the system is synthetic, and GBIF aggregates are "
            "context, not calibration."
        ),
    )
    _p(
        doc,
        (
            "This revision corrects two errors in the submitted version. The climate "
            "term was implemented as an accelerating decrement, not the form the "
            "text implied, and this choice decides the base-case sign. The original "
            "held-out evaluation of Ψ used an implementation that differed from the "
            "documented one; it is now reported as historical, and the predictive "
            "claim rests on a new prospective evaluation. Both corrections narrow the "
            "claims of the paper; neither changes the model dynamics."
        ),
    )
    _p(
        doc,
        (
            "Limitations. All parameters are synthetic and uncalibrated, and the ±50% "
            "ranges are sensitivity ranges, not evidence-based ranges. Space is "
            "implicit, there is no interspecific competition or senescence, and "
            "three traits are inert. Policies are fixed rules, so nothing is claimed "
            "about optimised or belief-updating management, and the S7–S6 contrast "
            "bundles budget and movement. Many cells are indeterminate at 12 "
            "replicates. Welfare and utility weights are normative devices; the "
            "information effect under alternative weights is in Appendix A, Table A4."
        ),
    )
    _add_heading(doc, "5. Conclusions", 1)
    _p(
        doc,
        (
            "An ODD-documented IBM of a nine-node conservation network shows that "
            "wild–managed circulation is neither generally superior nor useless: "
            "which strategy retains more species depends on the timing of habitat "
            "loss, baseline suitability and movement costs, and circulation gains "
            "are mostly persistence outside the wild. A reduced criterion derived "
            "from the model's equations predicted the direction of determinate "
            "contrasts in a prospectively frozen evaluation within the shipped "
            "structure. The full specification is given so the model can be "
            "re-implemented, challenged and extended."
        ),
    )
    _add_heading(doc, "Declarations", 1)
    _p(doc, "Declaration of competing interest: none.")
    _p(doc, "Funding: this research received no specific grant.")
    _p(
        doc,
        (
            "Data and code availability: code, configuration, outputs, the values "
            "registries, the verification and confirmatory outputs, and the forensic "
            "reconstruction are available at "
            "https://github.com/bougtoir/agentic-conservation, release tag "
            f"{MIRROR_TAG} (commit {_mirror_commit(root)}). Random seeds and run "
            "manifests are part of the stored outputs. The repository holds "
            "aggregated GBIF counts and bibliographic metadata only, not individual "
            "occurrence records or article full texts. This is a substantially "
            "revised new submission referring to ECOMOD-26-2231."
        ),
    )
    _p(
        doc,
        (
            "Declaration of generative AI use: an AI coding assistant (Devin, "
            "Cognition AI) ran the computational pipeline and drafted text and "
            "document scaffolding under the author's direction. The author reviewed "
            "and is responsible for all content."
        ),
    )
    _add_heading(doc, "References", 1)
    for ref in _reference_text(
        lit.assign(_sort=lit.reference_authors.str.casefold()).sort_values(["_sort", "year"])
    ):
        _p(doc, ref)
    doc.save(out)
    _validate_office_file(out)
    _check_citations(out, lit)
    return out, n


def _doc_text(path: Path) -> str:
    return "\n".join(p.text for p in Document(path).paragraphs)


def _check_citations(path: Path, lit: pd.DataFrame) -> None:
    body = _doc_text(path).split("\nReferences\n", 1)[0]
    missing = sorted(c for c in lit.citation if c not in body)
    if missing:
        raise ValueError(f"references not cited: {missing}")


# ---------------------------------------------------------------- tracked
RED = RGBColor(0xC0, 0x00, 0x00)
BLUE = RGBColor(0x00, 0x33, 0xCC)


def _paragraphs(path: Path) -> list[str]:
    return [p.text for p in Document(path).paragraphs if p.text.strip()]


def _run(para, text: str, kind: str) -> None:
    run = para.add_run(text)
    if kind == "ins":
        run.font.color.rgb = RED
    elif kind == "del":
        run.font.color.rgb = BLUE
        run.font.strike = True


def build_tracked(root: Path, clean: Path) -> Path:
    """Colour-coded comparison against the submitted ECOMOD-26-2231 file:
    additions red, deletions blue with strikethrough. Paragraph text is
    compared; table bodies and figures are listed by caption only."""
    old = _paragraphs(root / "manuscript/EM_MANUSCRIPT.docx")
    new = _paragraphs(clean)
    out = root / OUT_DIR / "EM_ODD_REVISED_MANUSCRIPT_TRACKED_FINAL.docx"
    doc = Document()
    _configure_document(doc, TITLE + " (tracked)")
    note = doc.add_paragraph()
    note.add_run(
        "Comparison with the version submitted as ECOMOD-26-2231 "
        "(manuscript/EM_MANUSCRIPT.docx). Additions in red; deletions in blue "
        "with strikethrough. Body text is compared paragraph by paragraph and "
        "word by word; table bodies are not diffed (see the clean version)."
    ).italic = True
    sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for t in new[j1:j2]:
                doc.add_paragraph().add_run(t)
            continue
        olds, news = old[i1:i2], new[j1:j2]
        k = 0
        while k < max(len(olds), len(news)):
            a = olds[k] if k < len(olds) else None
            b = news[k] if k < len(news) else None
            para = doc.add_paragraph()
            if (
                a is not None
                and b is not None
                and (difflib.SequenceMatcher(a=a.split(), b=b.split()).ratio() > 0.4)
            ):
                aw, bw = re.findall(r"\S+\s*", a), re.findall(r"\S+\s*", b)
                for t2, x1, x2, y1, y2 in difflib.SequenceMatcher(
                    a=aw, b=bw, autojunk=False
                ).get_opcodes():
                    if t2 == "equal":
                        _run(para, "".join(bw[y1:y2]), "eq")
                    else:
                        if x2 > x1:
                            _run(para, "".join(aw[x1:x2]), "del")
                        if y2 > y1:
                            _run(para, "".join(bw[y1:y2]), "ins")
            else:
                if a is not None:
                    _run(para, a, "del")
                if b is not None:
                    para = doc.add_paragraph() if a is not None else para
                    _run(para, b, "ins")
            k += 1
    doc.save(out)
    _validate_office_file(out)
    return out


# ------------------------------------------------------- letters and appendix
def _letter(path: Path, title: str, paras: list[str]) -> Path:
    doc = Document()
    _configure_document(doc, title)
    _add_title(doc, title)
    for t in paras:
        _p(doc, t)
    doc.save(path)
    _validate_office_file(path)
    return path


def _mirror_commit(root: Path) -> str:
    f = root / "odd_resubmission/PUBLIC_MIRROR_COMMIT.txt"
    return f.read_text().strip()[:12] if f.exists() else "[to be inserted]"


def build_cover(root: Path, v: dict) -> Path:
    cf = conf(v)
    return _letter(
        root / OUT_DIR / "EM_ODD_COVER_LETTER_FINAL.docx",
        "Cover letter",
        [
            "Dear Dr Wang,",
            f"I submit \u201c{TITLE}\u201d as a substantially revised new submission "
            "to Ecological Modelling, referring to manuscript ECOMOD-26-2231, as the "
            "decision letter permitted. A detailed point-by-point response is "
            "attached (EDITOR_RESPONSE_ODD_FINAL).",
            "The Associate Editor, Dr Volker Grimm, found the work interesting but "
            "not acceptable as presented. He recommended the ODD protocol (Grimm et "
            "al. 2020), following the hints in its Supplement S1, and asked for the "
            "rationale underlying the equations and algorithms, because they contain "
            "important assumptions about processes and interactions. The decision "
            "letter listed no separate reviewer comments. I "
            "have rewritten the Methods as a complete ODD description in the "
            "protocol's order. Following Supplement S1, I added evaluation patterns, "
            "a state-variable table that identifies inert variables, scheduling and "
            "update semantics, all eleven design concepts, and one subsection per "
            "submodel. Each submodel states the process it approximates, why the "
            "form was chosen, the alternatives, its assumptions, how they can affect "
            "the conclusions, and the evidence available and missing.",
            "Writing the rationale led me to test three assumptions that could "
            "decide the main result, under a plan frozen before any run: the "
            "persistence endpoint, the climate trajectory, and ten uncalibrated "
            "coefficients. The habitat-first versus circulation ordering holds for "
            "individual, reproductive and wild persistence. It reverses, however, "
            "when climate exposure comes earlier for the same year-100 displacement, "
            "and when baseline suitability is higher. The paper now presents that "
            "ordering as a conditional, located result. The reversal under higher "
            "baseline suitability was found in the base design and was not "
            "re-evaluated on held-out cells; in held-out cells most of the "
            "circulation advantage is persistence outside wild habitat.",
            "What did not change: the model dynamics, parameter values, policies "
            "and the canonical numerical registries are those "
            "of ECOMOD-26-2231. The new analyses were added beside them, and the "
            "registries were not edited. The changes are in the description, the "
            "added verification and the corrected interpretation.",
            "I believe the paper suits Ecological Modelling because its subject is "
            "a mechanistic model of a conservation decision: when moving animals "
            "among wild, managed-care and biobank nodes, rather than investing in "
            "habitat, improves persistence under directional habitat decline. The "
            "contribution is the mechanism-level account of when the ordering "
            "flips (timing of climate exposure, baseline suitability, disease and "
            "engagement feedbacks) and a reduced criterion whose predictive use is "
            "tested prospectively, documented in ODD so that the assumptions can "
            "be examined and reused.",
            "I also found that the original held-out evaluation of the reduced "
            "criterion Ψ had been produced by an implementation that differed from "
            "the documented one. I withdraw the claim that it evaluated a frozen "
            "model, report it as historical, and base the predictive claim on a new "
            "evaluation frozen before any outcome was seen. In 60 untouched "
            f"configurations Ψ signed {cf.acc_det:.3f} of {int(cf.det_cells)} "
            "determinate cells correctly, with regret below either fixed policy, "
            "within the shipped structural assumptions.",
            "The remaining limitations are stated in the paper. The parameters are "
            "synthetic and uncalibrated, space is implicit, the S7–S6 contrast "
            "bundles budget and movement, and there is no external validation. The "
            "model dynamics were not changed; the code, registries and forensic "
            "reconstruction are public.",
            "Code, configuration, outputs and the forensic reconstruction are "
            "public at https://github.com/bougtoir/agentic-conservation, release "
            f"tag {MIRROR_TAG} (commit {_mirror_commit(root)}).",
            "The manuscript is not under consideration elsewhere. I declare no "
            "competing interests.",
            "Sincerely,",
            "Tatsuki Onishi",
        ],
    )


EDITORIAL_QUOTES = "odd_resubmission/editorial/response_quotes.json"


def _editorial_quotes(root: Path) -> list[str]:
    """Verbatim decision-letter excerpts; kept outside the public mirror."""
    return json.loads((root / EDITORIAL_QUOTES).read_text(encoding="utf-8"))["quotes"]


def build_response(root: Path, v: dict, n: Numbering) -> Path:
    cf = conf(v)
    note = (
        "Editorial comments are quoted verbatim from the decision letter on "
        "ECOMOD-26-2231 (original spelling retained). The letter lists comments "
        "from the Associate Editor; no separate reviewer reports were included, "
        "so the responses below address the Associate Editor and the "
        "Editor-in-Chief. The Associate Editor's comments form one continuous "
        "paragraph; I quote it in consecutive parts so that each request has "
        "its own answer. The responses describe what I changed; neither editor "
        "has seen or endorsed the revised manuscript."
    )
    points = [
        (
            "Point 1 (Associate Editor): use the ODD protocol (Grimm et al. 2020).",
            "I rewrote the Methods as a full ODD description in the protocol's "
            "order: Purpose and patterns (2.1), Entities, state variables and "
            "scales (2.2), Process overview and scheduling (2.3), Design concepts "
            "(2.4), Initialization (2.5), Input data (2.6) and Submodels (2.7). "
            f"New tables: {n.t('patterns')} (patterns) and {n.t('state')} (state "
            "variables, including inert variables). Algorithm 1 now states the "
            "update semantics.",
        ),
        (
            "Point 2 (Associate Editor): follow Supplement S1 explicitly.",
            "For each element I followed the S1 guidance. I stated a specific "
            "purpose and defined its terms, and gave testable general patterns "
            "with their reproduction status. I listed every state variable and "
            "marked the inert ones. I gave synchronous-update and order rules, "
            "addressed all eleven design concepts, and wrote one subsection per "
            "submodel. The essential description is in the main text, not in the "
            "repository.",
        ),
        (
            "Point 3 (Associate Editor): explain the ecological rationale of every "
            "consequential equation and algorithm.",
            "Each submodel in 2.7 (Eqs. 1–7, Algorithm 2) now has a rationale "
            "block: process, form, alternatives, assumptions, effect on "
            "conclusions, evidence and missing evidence. Where evidence is "
            "lacking, the form is labelled an exploratory structural assumption. "
            "Because rationale alone cannot show whether an assumption matters, I "
            "ran preregistered tests (2.9). "
            f"Endpoints: {n.t('q1')}. Climate trajectory: {n.t('q2')} and "
            f"{n.f('climate_forms')}. Coefficients: {n.t('q3')}. The climate "
            "trajectory and the suitability intercept proved load-bearing, and the "
            "conclusions were narrowed accordingly (Sections 3.3–3.5, 4).",
        ),
        (
            "Point 4 (Editor-in-Chief): a substantially revised new submission "
            "with detailed responses.",
            "This is a new submission referring to ECOMOD-26-2231. Beyond the "
            "presentation, two substantive corrections were made. First, the "
            "climate term is stated as implemented (Eq. 1). Second, the original "
            "held-out Ψ evaluation is withdrawn as evidence of a frozen-model test "
            "(2.10.2) and replaced by a prospectively frozen evaluation (2.10.3, "
            f"{n.t('psi')}): {cf.acc_det:.3f} determinate accuracy (Wilson 95% "
            f"{cf.acc_det_wilson_lo:.3f}–{cf.acc_det_wilson_hi:.3f}), regret "
            f"{cf.regret_psi:.4f}. I also corrected text that did not match the "
            "code: the funding shock is a one-year reduction, not a collapse "
            "(2.7.5); release events are counted before release mortality, not as "
            "successful reintroductions (2.7.6); engagement never decreases "
            "(2.7.5); and Algorithm 1 gives the implemented order of the annual "
            "step (2.3). Model dynamics are unchanged. The parameters remain "
            "synthetic and uncalibrated, and the limitations are stated in "
            "Section 4.",
        ),
    ]
    quotes = _editorial_quotes(root)
    points = [(q, a) for q, (_, a) in zip(quotes[:-1], points, strict=True)]
    points.append(
        (
            quotes[-1],
            "The cover letter (EM_ODD_COVER_LETTER_FINAL) refers to ECOMOD-26-2231 and "
            "summarises the revision; this document gives the detail. What was "
            "not changed: the model dynamics, the parameter values and the "
            "canonical results. The revision changes how the model is described "
            "and justified, adds preregistered structural tests, and narrows the "
            "claims where those tests or the provenance audit required it.",
        )
    )
    doc = Document()
    _configure_document(doc, "Response to the editors")
    _add_title(doc, "Response to the editors", "Reference: ECOMOD-26-2231")
    _p(
        doc,
        "Dear Editors, I thank the Associate Editor and the Editor-in-Chief "
        "for their decision and advice. My responses follow; section, table "
        "and figure numbers refer to the revised manuscript.",
    )
    _p(doc, note)
    for q, a in points:
        para = doc.add_paragraph()
        para.add_run(q).bold = True
        para = doc.add_paragraph()
        para.add_run("Response: ").bold = True
        para.add_run(a)
    _p(doc, "Tatsuki Onishi")
    out = root / OUT_DIR / "EDITOR_RESPONSE_ODD_FINAL.docx"
    doc.save(out)
    _validate_office_file(out)
    return out


APPENDIX_TABLES = [
    (
        "tables/table4_sensitivity.csv",
        "Latin-hypercube Spearman rank correlations between each varied parameter "
        "and each outcome, by policy",
        "128 designs × 4 replicates. Useful secondary evidence for Section 2.8.",
    ),
    (
        "tables/table4_sensitivity_interactions.csv",
        "Partial-rank interaction screens for parameter pairs",
        "Descriptive screen on the same designs as Table A1; not a test.",
    ),
    (
        "tables/table7_robustness.csv",
        "Ablation and adverse-condition outcomes (point estimates)",
        "Paired seeds per design as stated in Section 3.5; cited in Section 3.5.",
    ),
    (
        "tables/table8_information_weight_sensitivity.csv",
        "Perfect-current-state information effect on the utility index under "
        "alternative normative weights",
        "Columns survival_100 to mean_individual_welfare are the weights; estimate, "
        "lower and upper are the paired effect and its 95% interval; the comparator "
        "keeps the S7 rule (Section 3.7).",
    ),
    (
        "tables/table9_reversal_predictors.csv",
        "Historical (V0) held-out performance of Ψ and baselines B0–B2",
        "Historical result from implementation V0 (Section 2.10.2); not the "
        "prospective evaluation of Section 3.6.",
    ),
]


def _token_len(value: object) -> int:
    return max((len(t) for t in str(value).split()), default=1)


def _appendix_table(doc: Document, frame: pd.DataFrame, number: str, caption: str, note: str):
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches

    from agentic_conservation.documents import _format_cell, _repeat_header

    cap = doc.add_paragraph()
    cap.paragraph_format.space_before = Pt(10)
    cap.paragraph_format.space_after = Pt(4)
    cap.paragraph_format.keep_with_next = True
    cap.add_run(f"{number}. {caption}").bold = True
    cells = [[_format_cell(x) for x in row] for row in frame.itertuples(index=False)]
    heads = [str(c) for c in frame.columns]
    longest = [
        max([_token_len(h)] + [_token_len(r[k]) for r in cells]) for k, h in enumerate(heads)
    ]
    mean = [sum(len(r[k]) for r in cells) / max(len(cells), 1) for k in range(len(heads))]
    usable = 9.7
    font = 8.0

    def minimum(f: float) -> list[float]:
        return [n * f * 0.0085 + 0.16 for n in longest]

    while sum(minimum(font)) > usable and font > 6:
        font -= 0.5
    base = minimum(font)
    spare = max(usable - sum(base), 0)
    extra = [max(m - n, 0) + 1 for m, n in zip(mean, longest, strict=True)]
    widths = [w + spare * e / sum(extra) for w, e in zip(base, extra, strict=True)]
    table = doc.add_table(rows=1, cols=len(heads))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    table._tbl.tblPr.append(layout)
    _repeat_header(table.rows[0])
    for k, h in enumerate(heads):
        table.rows[0].cells[k].text = h
    for r in cells:
        row = table.add_row().cells
        for k, val in enumerate(r):
            row[k].text = val
    for row in table.rows:
        for k, cell in enumerate(row.cells):
            cell.width = Inches(widths[k])
            for para in cell.paragraphs:
                para.paragraph_format.space_after = Pt(0)
                para.paragraph_format.line_spacing = 1.0
                for run in para.runs:
                    run.font.size = Pt(font)
                    run.font.name = "Times New Roman"
                    run.font.color.rgb = RGBColor(0, 0, 0)
    for cell in table.rows[0].cells:
        for run in cell.paragraphs[0].runs:
            run.bold = True
    n = doc.add_paragraph()
    n.paragraph_format.line_spacing = 1.0
    n.paragraph_format.space_after = Pt(8)
    r = n.add_run(f"Note. {note}")
    r.font.size = Pt(9)


def build_appendix(root: Path) -> Path:
    from docx.enum.section import WD_ORIENT
    from docx.shared import Inches

    doc = Document()
    _configure_document(doc, "Appendix A")
    doc.core_properties.subject = "Appendix A"
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Inches(11), Inches(8.5)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Inches(0.65))
    _add_title(doc, "Appendix A. Supplementary tables", TITLE)
    intro = doc.add_paragraph(
        "Tables A1–A5 are secondary scientific evidence cited in the main text. "
        "Variable names are the column names of the public files in tables/. The "
        "GBIF coverage aggregates and bibliographic evidence levels used as "
        "context only are reproducibility material and are provided in the public "
        "repository (tables/table5_empirical_coverage.csv, "
        "tables/table6_empirical_evidence.csv)."
    )
    intro.paragraph_format.line_spacing = 1.0
    for i, (f, cap, note) in enumerate(APPENDIX_TABLES, 1):
        _appendix_table(doc, pd.read_csv(root / f), f"Table A{i}", cap, note)
    out = root / OUT_DIR / "EM_ODD_APPENDIX_A_FINAL.docx"
    doc.save(out)
    _validate_office_file(out)
    return out


def _force_times(path: Path) -> None:
    """Set every text run (body and tables) to Times New Roman."""
    from docx.oxml.ns import qn

    doc = Document(path)
    for r in doc.element.body.iter(qn("w:r")):
        rpr = r.get_or_add_rPr()
        fonts = rpr.find(qn("w:rFonts"))
        if fonts is None:
            fonts = rpr.makeelement(qn("w:rFonts"), {})
            rpr.insert(0, fonts)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            fonts.set(qn(a), "Times New Roman")
    doc.save(path)


def build_all(root: Path) -> dict[str, Path]:
    clean, n = build_clean(root)
    v = load_values(root)
    outs = {
        "clean": clean,
        "tracked": build_tracked(root, clean),
        "cover": build_cover(root, v),
        "appendix": build_appendix(root),
    }
    if (root / EDITORIAL_QUOTES).exists():
        outs["response"] = build_response(root, v, n)
    for p in outs.values():
        _force_times(p)
    fig_dir = root / OUT_DIR / "figures"
    fig_dir.mkdir(exist_ok=True)
    for label, src, _cap in n.figure_files:
        num = label.split()[1]
        (fig_dir / f"Figure_{num}{src.suffix}").write_bytes(src.read_bytes())
    return outs


if __name__ == "__main__":
    for k, p in build_all(Path(__file__).resolve().parents[2]).items():
        print(k, p)
