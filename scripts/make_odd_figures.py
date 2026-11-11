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


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    climate_forms_figure()
