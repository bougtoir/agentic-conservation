"""Figures for the ODD revision built only from preserved verification outputs."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from agentic_conservation.simulation import climate_increment  # noqa: E402

OUT = ROOT / "figures/odd"
FORMS = ["accelerating", "linear", "decelerating", "step"]


def climate_forms_figure() -> None:
    q2 = pd.read_csv(ROOT / "results/odd_verification/q2_summary.csv")
    q2 = q2[q2.endpoint == "survival_100"].set_index("climate_form").loc[FORMS]
    v, years = 0.012, 100
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    t = np.arange(1, years + 1)
    for form in FORMS:
        inc = [
            climate_increment({"climate_velocity": v, "climate_form": form}, y, years) for y in t
        ]
        axes[0].plot(
            t, np.cumsum(inc), label=f"{form} ({q2.loc[form].cumulative_exposure_disp_years:.1f})"
        )
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Cumulative origin-quality displacement")
    axes[0].legend(title="Form (cumulative exposure)", fontsize=7, title_fontsize=7)
    axes[0].set_title("(a) Same year-100 displacement", fontsize=9)
    y = q2.S7_minus_S6.to_numpy()
    e = 2 * q2.se.to_numpy()
    axes[1].errorbar(range(len(FORMS)), y, yerr=e, fmt="o", capsize=4, color="black")
    axes[1].axhline(0, color="grey", lw=0.8)
    axes[1].set_xticks(range(len(FORMS)), FORMS, fontsize=8)
    axes[1].set_ylabel("S7 − S6 year-100 survival (±2 SE)")
    axes[1].set_title("(b) Base-scenario policy contrast", fontsize=9)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"fig_q2_climate_forms.{ext}", dpi=300)
    plt.close(fig)


def network_figure() -> None:
    """Node schematic in which only living-animal nodes are connected by movement
    arrows; the biobank stores genetic material and is never a movement target."""
    nodes = pd.read_json(ROOT / "config/nodes.json")
    positions = {
        "origin": (0.10, 0.70),
        "alternative": (0.30, 0.84),
        "reserve": (0.30, 0.55),
        "zoo": (0.56, 0.85),
        "conservation_zoo": (0.78, 0.78),
        "breeding": (0.57, 0.58),
        "semiwild": (0.79, 0.49),
        "rehabilitation": (0.56, 0.32),
        "biobank": (0.82, 0.22),
    }
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.18, 0.97, "Wild environments", ha="center", weight="bold", fontsize=13)
    ax.text(
        0.68, 0.97, "Managed conservation environments", ha="center", weight="bold", fontsize=13
    )
    ax.axvline(0.43, ymin=0.12, color="#bbbbbb", lw=1.2, ls="--")
    for row in nodes.itertuples():
        x, y = positions[row.id]
        color = "#cfe8d5" if row.wild else "#d8e5f4"
        label = row.id.replace("_", " ").title()
        h = 0.09
        if row.type == "biobank":
            color, h = "#e7dcf4", 0.15
            label = "Biobank\n(stored genetic material;\nno animals)"
        ax.add_patch(
            FancyBboxPatch(
                (x - 0.09, y - h / 2),
                0.18,
                h,
                boxstyle="round,pad=0.012",
                facecolor=color,
                edgecolor="#333333",
                linewidth=1.1,
                linestyle="--" if row.type == "biobank" else "-",
            )
        )
        ax.text(x, y, label, ha="center", va="center", fontsize=9)
    edges = [
        ("origin", "alternative"),
        ("origin", "reserve"),
        ("origin", "rehabilitation"),
        ("alternative", "semiwild"),
        ("reserve", "semiwild"),
        ("zoo", "conservation_zoo"),
        ("conservation_zoo", "breeding"),
        ("breeding", "semiwild"),
        ("rehabilitation", "semiwild"),
        ("semiwild", "origin"),
        ("semiwild", "alternative"),
    ]
    for source, target in edges:
        ax.add_patch(
            FancyArrowPatch(
                positions[source],
                positions[target],
                arrowstyle="-|>",
                mutation_scale=11,
                color="#555555",
                alpha=0.65,
                linewidth=1.1,
                connectionstyle="arc3,rad=0.07",
                shrinkA=34,
                shrinkB=34,
            )
        )
    ax.text(
        0.5,
        0.045,
        "Arrows: example pathways along which living animals can be moved "
        "(optional, resource-limited, not recommendations).\nThe biobank "
        "receives budget, not animals, and is never a movement target.",
        ha="center",
        fontsize=10,
    )
    fig.savefig(OUT / "fig1_network_living_nodes.png", dpi=320, bbox_inches="tight")
    plt.close(fig)


def psi_historical_figure() -> None:
    """Historical held-out Psi (implementation V0) against the observed contrast."""
    m = pd.read_csv(ROOT / "results/reversal/holdout_metrics.csv")
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.axvline(0, color="#777777", lw=1.0, ls="--")
    ax.axhline(0, color="#777777", lw=1.0, ls="--")
    for sign, colour in [(1, "#2878b5"), (-1, "#c1443c")]:
        d = m[m.obs_sign == sign]
        ax.scatter(d.psi, d.mean_diff, c=colour, s=42, edgecolor="black", linewidth=0.4, zorder=3)
    ind = m[m.obs_sign == 0]
    ax.scatter(ind.psi, ind.mean_diff, c="#bbbbbb", s=34, marker="x", linewidth=1.4, zorder=2)
    ax.set_xscale("symlog", linthresh=0.5)
    ax.set(
        xlabel="Reduced reversal criterion \u03a8, implementation V0 (symlog scale)",
        ylabel="Observed S7 \u2212 S6 year-100 survival difference",
        title="Historical held-out evaluation of \u03a8 (implementation V0)",
    )
    ax.grid(alpha=0.25)
    handles = [
        Line2D(
            [],
            [],
            marker="o",
            ls="",
            color="#2878b5",
            markeredgecolor="black",
            label="determinate, S7 higher (|mean diff| > 2 MC SE)",
        ),
        Line2D(
            [],
            [],
            marker="o",
            ls="",
            color="#c1443c",
            markeredgecolor="black",
            label="determinate, S6 higher (|mean diff| > 2 MC SE)",
        ),
        Line2D([], [], marker="x", ls="", color="#bbbbbb", label="indeterminate"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=9)
    fig.savefig(OUT / "fig_psi_historical_v0.png", dpi=320, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    if "--all" in sys.argv:
        climate_forms_figure()
    network_figure()
    psi_historical_figure()
