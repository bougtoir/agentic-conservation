"""Generate publication figures, result tables, and derived registries."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from agentic_conservation.simulation import (
    Project,
    _quality_update,
    _species_node_suitability,
    load_project,
)

POLICY_NAMES = {
    "S0": "No intervention",
    "S1": "Ex-situ phase-down",
    "S2": "Lifetime captivity",
    "S3": "Return to origin",
    "S4": "State-dependent circulation",
    "S5": "Dynamic global allocation",
    "S6": "Habitat-first",
    "S7": "Hybrid portfolio",
}
COLORS = {
    "S0": "#777777",
    "S1": "#2a9d8f",
    "S2": "#9c6644",
    "S3": "#e9c46a",
    "S4": "#e76f51",
    "S5": "#8e5ea2",
    "S6": "#264653",
    "S7": "#2878b5",
}


def _save_figure(fig: plt.Figure, figures: Path, stem: str) -> None:
    figures.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf", "svg"):
        kwargs = {"dpi": 320} if suffix == "png" else {}
        path = figures / f"{stem}.{suffix}"
        fig.savefig(path, bbox_inches="tight", **kwargs)
        if suffix == "svg":
            lines = path.read_text(encoding="utf-8").splitlines()
            path.write_text(
                "\n".join(line.rstrip() for line in lines) + "\n",
                encoding="utf-8",
            )
    plt.close(fig)


def _write_markdown_table(frame: pd.DataFrame, path: Path) -> None:
    values = frame.fillna("").astype(str)
    widths = [
        max(len(str(column)), *(len(item) for item in values[column]))
        for column in values.columns
    ]
    lines = [
        "| " + " | ".join(str(column).ljust(width) for column, width in zip(values, widths)) + " |",
        "| " + " | ".join("-" * width for width in widths) + " |",
    ]
    for _, row in values.iterrows():
        lines.append(
            "| " + " | ".join(str(item).ljust(width) for item, width in zip(row, widths)) + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _figure_network(root: Path, figures: Path) -> None:
    nodes = pd.read_json(root / "config/nodes.json")
    positions = {
        "origin": (0.08, 0.70),
        "alternative": (0.30, 0.84),
        "reserve": (0.30, 0.55),
        "zoo": (0.56, 0.85),
        "conservation_zoo": (0.76, 0.78),
        "breeding": (0.57, 0.58),
        "semiwild": (0.77, 0.49),
        "rehabilitation": (0.56, 0.32),
        "biobank": (0.78, 0.22),
    }
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.18, 0.97, "Wild environments", ha="center", weight="bold", fontsize=13)
    ax.text(
        0.68,
        0.97,
        "Managed conservation environments",
        ha="center",
        weight="bold",
        fontsize=13,
    )
    ax.axvline(0.43, color="#bbbbbb", lw=1.2, ls="--")
    for row in nodes.itertuples():
        x, y = positions[row.id]
        color = "#cfe8d5" if row.wild else "#d8e5f4"
        if row.type == "biobank":
            color = "#e7dcf4"
        box = FancyBboxPatch(
            (x - 0.08, y - 0.045),
            0.16,
            0.09,
            boxstyle="round,pad=0.012",
            facecolor=color,
            edgecolor="#333333",
            linewidth=1.1,
        )
        ax.add_patch(box)
        label = row.id.replace("_", " ").title()
        ax.text(x, y, "\n".join(textwrap.wrap(label, 18)), ha="center", va="center", fontsize=9)
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
        ("conservation_zoo", "biobank"),
        ("breeding", "biobank"),
    ]
    for source, target in edges:
        start = positions[source]
        end = positions[target]
        arrow = FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=11,
            color="#555555",
            alpha=0.65,
            linewidth=1.1,
            connectionstyle="arc3,rad=0.07",
            shrinkA=34,
            shrinkB=34,
        )
        ax.add_patch(arrow)
    ax.text(
        0.5,
        0.06,
        "Movement is optional and resource-limited; arrows denote feasible pathways,\n"
        "not recommendations.",
        ha="center",
        fontsize=10,
    )
    _save_figure(fig, figures, "fig1_conservation_network")


def _figure_trajectories(root: Path, figures: Path) -> None:
    trajectories = pd.read_csv(root / "results/trajectories.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharex=True)
    for policy, frame in trajectories.groupby("policy"):
        axes[0].plot(frame.year, frame.species_retained, label=policy, color=COLORS[policy])
        axes[1].plot(frame.year, frame.total_abundance, label=policy, color=COLORS[policy])
    axes[0].set(ylabel="Species retained", xlabel="Year", title="Species persistence")
    axes[1].set(ylabel="Living individuals", xlabel="Year", title="Total abundance")
    axes[0].set_ylim(bottom=0)
    axes[1].set_ylim(bottom=0)
    for ax in axes:
        ax.grid(alpha=0.25)
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, [f"{x}: {POLICY_NAMES[x]}" for x in labels], loc="lower center", ncol=4)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    _save_figure(fig, figures, "fig2_century_trajectories")


def _figure_pareto(root: Path, figures: Path) -> None:
    pareto = pd.read_csv(root / "results/pareto_front.csv")
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    size = 40 + 230 * pareto.welfare / max(pareto.welfare.max(), 1)
    for row, point_size in zip(pareto.itertuples(), size, strict=True):
        ax.scatter(
            row.cost,
            row.survival,
            s=point_size,
            color=COLORS[row.policy],
            marker="o" if row.pareto_efficient else "X",
            edgecolor="black",
            linewidth=0.7,
            alpha=0.88,
        )
        ax.annotate(row.policy, (row.cost, row.survival), xytext=(5, 5), textcoords="offset points")
    ax.set(
        xlabel="Mean 100-year cost (budget units)",
        ylabel="Mean proportion of species retained",
        title="Multiobjective policy outcomes",
    )
    ax.grid(alpha=0.25)
    ax.text(
        0.02,
        0.98,
        "Circle: Pareto-efficient across six tracked objectives\n"
        "Marker size: mean individual welfare",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
    )
    _save_figure(fig, figures, "fig3_pareto_outcomes")


def _heatmap(
    ax: plt.Axes,
    frame: pd.DataFrame,
    *,
    title: str,
    x_label: str,
    y_label: str,
) -> None:
    matrix = frame.pivot(index="y", columns="x", values="difference").sort_index(ascending=False)
    values = matrix.to_numpy()
    vmax = max(abs(np.nanmin(values)), abs(np.nanmax(values)), 1e-6)
    image = ax.imshow(values, cmap="RdBu", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(matrix.columns)), [f"{x:.3g}" for x in matrix.columns])
    ax.set_yticks(range(len(matrix.index)), [f"{y:.3g}" for y in matrix.index])
    ax.set(xlabel=x_label, ylabel=y_label, title=title)
    plt.colorbar(image, ax=ax, label="S7 minus S6 survival")


def _figure_thresholds(root: Path, figures: Path) -> None:
    sweeps = pd.read_csv(root / "results/threshold_sweeps.csv")
    aggregate = (
        sweeps.groupby(["sweep", "x", "y", "policy"], as_index=False)
        .survival_100.mean()
        .pivot(index=["sweep", "x", "y"], columns="policy", values="survival_100")
        .reset_index()
    )
    aggregate["difference"] = aggregate["S7"] - aggregate["S6"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    deterioration = aggregate[aggregate.sweep == "deterioration_relocation"]
    _heatmap(
        axes[0],
        deterioration,
        title="Habitat deterioration × relocation stress",
        x_label="Annual deterioration",
        y_label="Relocation stress",
    )
    captivity = aggregate[aggregate.sweep == "captivity_breeding"]
    _heatmap(
        axes[1],
        captivity,
        title="Captivity burden × breeding benefit",
        x_label="Captivity welfare penalty",
        y_label="Ex-situ breeding benefit",
    )
    fig.text(
        0.5,
        0.01,
        "Red: S6 survival is higher   |   White: tie   |   Blue: S7 survival is higher",
        ha="center",
        fontsize=10,
        weight="bold",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _save_figure(fig, figures, "fig4_policy_reversal_thresholds")


def _figure_latent_survey(root: Path, figures: Path) -> None:
    sweeps = pd.read_csv(root / "results/threshold_sweeps.csv")
    frame = sweeps[
        (sweeps.sweep == "latent_survey") & (sweeps.policy == "S7")
    ].copy()
    aggregate = frame.groupby(["x", "y"], as_index=False).fraction_ebd.mean()
    matrix = aggregate.pivot(index="y", columns="x", values="fraction_ebd").sort_index(
        ascending=False
    )
    fig, ax = plt.subplots(figsize=(7.5, 5.3))
    image = ax.imshow(matrix.to_numpy(), cmap="magma", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(matrix.columns)), [f"{x:.2f}" for x in matrix.columns])
    ax.set_yticks(range(len(matrix.index)), [f"{y:.1f}" for y in matrix.index])
    ax.set(
        xlabel="Latent-species fraction",
        ylabel="Survey cost",
        title="Extinction before discovery under the hybrid portfolio",
    )
    plt.colorbar(image, ax=ax, label="Fraction extinct before discovery")
    _save_figure(fig, figures, "fig5_extinction_before_discovery")


def _figure_tradeoffs(root: Path, figures: Path) -> None:
    pareto = pd.read_csv(root / "results/pareto_front.csv").set_index("policy")
    normalized = pareto[
        ["survival", "welfare", "genetics", "ebd", "cost", "future_option"]
    ].copy()
    normalized["ebd"] = -normalized.ebd
    normalized["cost"] = -normalized.cost
    metrics = list(normalized.columns)
    display = [
        "Survival",
        "Welfare",
        "Genetics",
        "EBD avoidance",
        "Cost efficiency",
        "Future option",
    ]
    for metric in metrics:
        low = normalized[metric].min()
        high = normalized[metric].max()
        normalized[metric] = (normalized[metric] - low) / max(high - low, 1e-12)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(metrics))
    width = 0.095
    for offset, policy in enumerate(POLICY_NAMES):
        ax.bar(
            x + (offset - 3.5) * width,
            normalized.loc[policy],
            width,
            label=policy,
            color=COLORS[policy],
        )
    ax.set_xticks(x, display)
    ax.set(ylabel="Within-metric normalized outcome", title="No policy dominates every objective")
    ax.set_ylim(0, 1.08)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    _save_figure(fig, figures, "fig6_objective_tradeoffs")


def _figure_observation_architecture(figures: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    boxes = {
        "truth": (0.05, 0.56, 0.23, 0.26, "#d9ead3"),
        "observation": (0.38, 0.56, 0.23, 0.26, "#fff2cc"),
        "decision": (0.71, 0.56, 0.23, 0.26, "#cfe2f3"),
        "outcomes": (0.38, 0.12, 0.23, 0.22, "#eadcf8"),
    }
    labels = {
        "truth": "True state $X_t$\nIndividuals, species,\nhabitat, latent taxa",
        "observation": "Observed state $O_t$\nNoise, one-year delay,\nundetected species",
        "decision": "Policy action $A_t$\nBudget allocation,\nmovement, protection",
        "outcomes": "Outcomes\nSurvival, welfare,\ngenetics, EBD, cost",
    }
    for key, (x, y, width, height, color) in boxes.items():
        patch = FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.015",
            facecolor=color,
            edgecolor="#333333",
            linewidth=1.2,
        )
        ax.add_patch(patch)
        ax.text(
            x + width / 2,
            y + height / 2,
            labels[key],
            ha="center",
            va="center",
            fontsize=11,
        )

    def arrow(start: tuple[float, float], end: tuple[float, float], label: str) -> None:
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=15,
                linewidth=1.5,
                color="#555555",
            )
        )
        ax.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2 + 0.035,
            label,
            ha="center",
            fontsize=9,
        )

    arrow((0.28, 0.69), (0.38, 0.69), "detect / measure")
    arrow((0.61, 0.69), (0.71, 0.69), "infer / allocate")
    arrow((0.83, 0.56), (0.60, 0.32), "intervene")
    arrow((0.38, 0.23), (0.23, 0.56), "state transition")
    ax.text(
        0.5,
        0.94,
        "Partial-observation decision architecture",
        ha="center",
        fontsize=16,
        weight="bold",
    )
    ax.text(
        0.5,
        0.04,
        "The oracle replaces $O_t$ with $X_t$; feasible policies never observe latent-state truth.",
        ha="center",
        fontsize=10,
    )
    _save_figure(fig, figures, "fig7_partial_observation_architecture")


def _figure_exploration(root: Path, figures: Path) -> None:
    sweeps = pd.read_csv(root / "results/threshold_sweeps.csv")
    frame = sweeps[
        (sweeps.sweep == "latent_survey") & (sweeps.policy == "S7")
    ].copy()
    aggregate = (
        frame.groupby(["x", "y"], as_index=False)
        .agg(
            fraction_ebd=("fraction_ebd", "mean"),
            survival=("survival_100", "mean"),
            future_option=("future_option_value", "mean"),
        )
        .sort_values(["x", "y"])
    )
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    for latent, group in aggregate.groupby("x"):
        label = f"Latent fraction {latent:.2f}"
        axes[0].plot(group.y, group.fraction_ebd, marker="o", label=label)
        axes[1].plot(group.y, group.future_option, marker="o", label=label)
    axes[0].set(
        xlabel="Survey cost",
        ylabel="Fraction extinct before discovery",
        title="Exploration outcome",
    )
    axes[1].set(
        xlabel="Survey cost",
        ylabel="Future option value",
        title="Portfolio consequence",
    )
    for ax in axes:
        ax.grid(alpha=0.25)
    axes[1].legend(loc="best", fontsize=9)
    fig.suptitle("Exploration–exploitation trade-offs under hidden biodiversity")
    fig.tight_layout()
    _save_figure(fig, figures, "fig8_exploration_exploitation")


def _figure_origin_future(root: Path, figures: Path) -> None:
    loaded = load_project(root)
    config = dict(loaded.config)
    config["catastrophe_probability"] = 0.0
    project = Project(config=config, species=loaded.species, nodes=loaded.nodes)
    quality = project.nodes.base_quality.to_numpy(dtype=float)
    rng = np.random.default_rng(90817)
    rows = []
    for year in range(1, config["years"] + 1):
        quality, _ = _quality_update(quality, year, project, rng, habitat_spend=0.0)
        suitability = _species_node_suitability(project, quality)
        rows.append(
            {
                "year": year,
                "origin": float(suitability[:, 0].mean()),
                "alternative": float(suitability[:, 1].mean()),
            }
        )
    frame = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(frame.year, frame.origin, label="Historical origin", color="#2a9d8f", lw=2.2)
    ax.plot(
        frame.year,
        frame.alternative,
        label="Alternative wild habitat",
        color="#e76f51",
        lw=2.2,
    )
    better = frame[frame.alternative > frame.origin]
    if not better.empty:
        crossing = int(better.year.iloc[0])
        ax.axvline(crossing, color="#555555", ls="--", lw=1.2)
        ax.text(crossing + 2, 0.52, f"Mean ranking reverses\nat year {crossing}", fontsize=9)
    ax.set(
        xlabel="Year",
        ylabel="Mean synthetic-species suitability",
        title="Historical origin need not remain the future optimum",
        ylim=(0, 1),
    )
    ax.grid(alpha=0.25)
    ax.legend()
    ax.text(
        0.02,
        0.03,
        "Directional-change component only; no intervention or stochastic shock.",
        transform=ax.transAxes,
        fontsize=9,
    )
    _save_figure(fig, figures, "fig9_origin_future_optimum")


def _build_tables(root: Path, tables: Path) -> None:
    tables.mkdir(parents=True, exist_ok=True)
    config = json.loads((root / "config/base.json").read_text())
    parameters = pd.DataFrame(
        [
            {"parameter": key, "base_value": value}
            for key, value in config.items()
            if key != "policy_allocations"
        ]
    )
    parameters.to_csv(tables / "table1_model_parameters.csv", index=False)
    _write_markdown_table(parameters, tables / "table1_model_parameters.md")

    policy_rows = []
    engines = {
        "S0": "none",
        "S1": "rule",
        "S2": "rule",
        "S3": "rule",
        "S4": "state-dependent rule",
        "S5": "greedy expected utility",
        "S6": "rule",
        "S7": "forward-rollout proxy",
    }
    for policy, allocation in config["policy_allocations"].items():
        row = {
            "policy": policy,
            "name": POLICY_NAMES[policy],
            "engine": engines[policy],
            **allocation,
        }
        policy_rows.append(row)
    policies = pd.DataFrame(policy_rows)
    policies.to_csv(tables / "table2_policies.csv", index=False)
    _write_markdown_table(policies.round(3), tables / "table2_policies.md")

    summary = pd.read_csv(root / "results/policy_summary.csv")
    selected_metrics = [
        "survival_100",
        "species_retained_100",
        "fraction_ebd",
        "mean_individual_welfare",
        "founder_effective",
        "cost",
        "future_option_value",
    ]
    outcome = summary[(~summary.oracle) & summary.metric.isin(selected_metrics)].copy()
    outcome["estimate_95_interval"] = outcome.apply(
        lambda row: f"{row.estimate:.3f} [{row.lower:.3f}, {row.upper:.3f}]", axis=1
    )
    outcome = outcome.pivot(index="policy", columns="metric", values="estimate_95_interval")
    outcome = outcome.reset_index()
    outcome.to_csv(tables / "table3_policy_outcomes.csv", index=False)
    _write_markdown_table(outcome, tables / "table3_policy_outcomes.md")

    sensitivity_table = pd.read_csv(root / "results/sensitivity_associations.csv")
    sensitivity_table.to_csv(tables / "table4_sensitivity.csv", index=False)
    strongest = (
        sensitivity_table.assign(abs_rho=lambda x: x.spearman_rho.abs())
        .sort_values(["policy", "metric", "abs_rho"], ascending=[True, True, False])
        .groupby(["policy", "metric"], as_index=False)
        .head(3)
        .drop(columns="abs_rho")
        .round(3)
    )
    _write_markdown_table(strongest, tables / "table4_sensitivity.md")
    interactions = pd.read_csv(root / "results/sensitivity_interactions.csv")
    strongest_interactions = (
        interactions.assign(
            absolute=lambda frame: frame.partial_rank_interaction.abs()
        )
        .sort_values(
            ["policy", "metric", "absolute"], ascending=[True, True, False]
        )
        .groupby(["policy", "metric"], as_index=False)
        .head(3)
        .drop(columns="absolute")
        .round(3)
    )
    strongest_interactions.to_csv(
        tables / "table4_sensitivity_interactions.csv", index=False
    )
    _write_markdown_table(
        strongest_interactions,
        tables / "table4_sensitivity_interactions.md",
    )

    coverage = pd.read_csv(root / "data/processed/gbif_coverage_summary.csv")
    coverage.to_csv(tables / "table5_empirical_coverage.csv", index=False)
    _write_markdown_table(coverage, tables / "table5_empirical_coverage.md")

    literature = pd.read_csv(root / "data/processed/selected_literature.csv")
    literature_audit = pd.read_csv(root / "provenance/literature_claim_audit.csv")
    literature = literature.merge(
        literature_audit[
            ["doi", "full_text_access", "support_level", "required_action"]
        ],
        on="doi",
        how="left",
    )
    literature.to_csv(tables / "table6_empirical_evidence.csv", index=False)
    _write_markdown_table(
        literature[
            [
                "species",
                "year",
                "title",
                "doi",
                "full_text_access",
                "support_level",
            ]
        ],
        tables / "table6_empirical_evidence.md",
    )

    robustness_rows = []
    for source, design_column in [
        ("ablations", "ablation"),
        ("adverse_conditions", "condition"),
    ]:
        frame = pd.read_csv(root / f"results/{source}.csv")
        frame = frame.rename(columns={"name": design_column})
        aggregate = (
            frame.groupby([design_column, "policy"], as_index=False)
            .agg(
                survival_100=("survival_100", "mean"),
                fraction_ebd=("fraction_ebd", "mean"),
                mean_individual_welfare=("mean_individual_welfare", "mean"),
            )
            .rename(columns={design_column: "design"})
        )
        aggregate.insert(0, "analysis", source)
        robustness_rows.append(aggregate)
    robustness = pd.concat(robustness_rows, ignore_index=True)
    robustness.to_csv(tables / "table7_robustness.csv", index=False)
    _write_markdown_table(
        robustness.round(3), tables / "table7_robustness.md"
    )
    information_weights = pd.read_csv(
        root / "results/information_weight_sensitivity.csv"
    )
    information_weights.to_csv(
        tables / "table8_information_weight_sensitivity.csv", index=False
    )
    _write_markdown_table(
        information_weights.round(3),
        tables / "table8_information_weight_sensitivity.md",
    )


def _append_derived_values(root: Path) -> None:
    registry = pd.read_csv(root / "results/manuscript_values.csv")
    registry = registry[
        ~registry.analysis.isin(
            [
                "gbif_observation_coverage",
                "information_weight_sensitivity",
                "normative_assumption",
                "budget_diagnostic_assumption",
                "two_factor_thresholds",
                "monte_carlo_convergence",
                "pareto_assessment",
            ]
        )
    ]
    coverage = pd.read_csv(root / "data/processed/gbif_coverage_summary.csv")
    rows = []
    for row in coverage.itertuples():
        values = row._asdict()
        slug = row.species.lower().replace(" ", "_").replace("'", "")
        for field, unit in [
            ("gbif_query_total", "occurrence_records"),
            ("records_2000_2025", "occurrence_records"),
            ("records_2015_2025", "occurrence_records"),
        ]:
            rows.append(
                {
                    "value_id": f"{slug}_{field}",
                    "analysis": "gbif_observation_coverage",
                    "estimate": values[field],
                    "lower": np.nan,
                    "upper": np.nan,
                    "unit": unit,
                    "source_file": "data/processed/gbif_coverage_summary.csv",
                    "source_code": "scripts/analyze_empirical.py",
                    "seed/config": (
                        "persisted GBIF query snapshot; see provenance/source_ledger.csv"
                    ),
                }
            )
    utility_weights = json.loads((root / "config/analysis.json").read_text())[
        "information_utility_weights"
    ]
    for outcome, weight in utility_weights.items():
        rows.append(
            {
                "value_id": f"information_utility_weight_{outcome}",
                "analysis": "normative_assumption",
                "estimate": weight,
                "lower": np.nan,
                "upper": np.nan,
                "unit": "proportion",
                "source_file": "config/analysis.json",
                "source_code": "src/agentic_conservation/analysis.py",
                "seed/config": "information_utility_weights",
            }
        )
    diagnostic_weights = json.loads(
        (root / "config/audit_designs.json").read_text()
    )["budget_robustness"]["diagnostic_utility_weights"]
    for outcome, weight in diagnostic_weights.items():
        rows.append(
            {
                "value_id": f"budget_diagnostic_utility_weight_{outcome}",
                "analysis": "budget_diagnostic_assumption",
                "estimate": weight,
                "lower": np.nan,
                "upper": np.nan,
                "unit": "proportion",
                "source_file": "config/audit_designs.json",
                "source_code": "src/agentic_conservation/audits.py",
                "seed/config": "budget_robustness.diagnostic_utility_weights",
            }
        )
    weight_sensitivity = pd.read_csv(
        root / "results/information_weight_sensitivity.csv"
    )
    for row in weight_sensitivity.itertuples():
        rows.append(
            {
                "value_id": f"information_weight_sensitivity_{row.scenario}",
                "analysis": "information_weight_sensitivity",
                "estimate": row.estimate,
                "lower": row.lower,
                "upper": row.upper,
                "unit": "weighted_utility_index",
                "source_file": "results/information_weight_sensitivity.csv",
                "source_code": "src/agentic_conservation/analysis.py",
                "seed/config": "config/analysis.json",
            }
        )
    threshold = pd.read_csv(root / "results/threshold_sweep_audit.csv")
    for row in threshold.itertuples():
        for field in [
            "robust_s7_higher",
            "robust_s6_higher",
            "indeterminate",
        ]:
            rows.append(
                {
                    "value_id": f"{row.sweep}_{field}",
                    "analysis": "two_factor_thresholds",
                    "estimate": row._asdict()[field],
                    "lower": np.nan,
                    "upper": np.nan,
                    "unit": "grid_cells",
                    "source_file": "results/threshold_sweep_audit.csv",
                    "source_code": "src/agentic_conservation/analysis.py",
                    "seed/config": (
                        "paired sweep seeds; stable N=4 to N=8 and "
                        ">1.96 Monte Carlo SE"
                    ),
                }
            )
    pareto = pd.read_csv(root / "results/pareto_front.csv")
    rows.append(
        {
            "value_id": "pareto_nondominated_policy_count",
            "analysis": "pareto_assessment",
            "estimate": int(pareto.pareto_efficient.sum()),
            "lower": np.nan,
            "upper": np.nan,
            "unit": "policies",
            "source_file": "results/pareto_front.csv",
            "source_code": "src/agentic_conservation/analysis.py",
            "seed/config": "six registered objectives",
        }
    )
    for row in pareto.itertuples():
        rows.append(
            {
                "value_id": f"pareto_efficient_{row.policy}",
                "analysis": "pareto_assessment",
                "estimate": int(row.pareto_efficient),
                "lower": np.nan,
                "upper": np.nan,
                "unit": "binary_indicator",
                "source_file": "results/pareto_front.csv",
                "source_code": "src/agentic_conservation/analysis.py",
                "seed/config": "six registered objectives",
            }
        )
    convergence_path = root / "results/convergence_audit.csv"
    if convergence_path.exists():
        convergence = pd.read_csv(convergence_path)
        final = convergence[
            (convergence.contrast == "S7-S6")
            & (convergence.n == convergence.n.max())
        ]
        for row in final.itertuples():
            rows.append(
                {
                    "value_id": f"convergence_s7_s6_{row.metric}",
                    "analysis": "monte_carlo_convergence",
                    "estimate": row.estimate,
                    "lower": row.lower,
                    "upper": row.upper,
                    "unit": "endpoint_scale",
                    "source_file": "results/convergence_audit.csv",
                    "source_code": "src/agentic_conservation/audits.py",
                    "seed/config": "nested paired prefixes through N=384",
                }
            )
    registry = pd.concat([registry, pd.DataFrame(rows)], ignore_index=True)
    duplicates = registry.loc[
        registry.value_id.duplicated(keep=False),
        "value_id",
    ].unique()
    if len(duplicates):
        raise ValueError(
            "Duplicate manuscript value IDs: "
            + ", ".join(sorted(duplicates))
        )
    registry.to_csv(root / "results/manuscript_values.csv", index=False)


def _verify_pareto_consistency(root: Path) -> None:
    pareto = pd.read_csv(root / "results/pareto_front.csv").set_index("policy")
    summary = pd.read_csv(root / "results/policy_summary.csv")
    summary = summary[~summary.oracle].set_index(["policy", "metric"])
    table = pd.read_csv(root / "tables/table3_policy_outcomes.csv").set_index(
        "policy"
    )
    values = pd.read_csv(root / "results/manuscript_values.csv").set_index(
        "value_id"
    )
    metric_map = {
        "survival": "survival_100",
        "welfare": "mean_individual_welfare",
        "genetics": "founder_effective",
        "ebd": "fraction_ebd",
        "cost": "cost",
        "future_option": "future_option_value",
    }
    for policy, row in pareto.iterrows():
        for objective, metric in metric_map.items():
            expected = float(summary.loc[(policy, metric), "estimate"])
            if not np.isclose(row[objective], expected):
                raise ValueError(
                    f"Pareto {policy} {objective} differs from policy summary"
                )
            table_estimate = float(str(table.loc[policy, metric]).split()[0])
            if not np.isclose(table_estimate, expected, atol=0.0005):
                raise ValueError(
                    f"Table 3 {policy} {metric} differs from policy summary"
                )
        value_id = f"pareto_efficient_{policy}"
        if int(values.loc[value_id, "estimate"]) != int(row.pareto_efficient):
            raise ValueError(f"{value_id} differs from Pareto output")
    count = int(values.loc["pareto_nondominated_policy_count", "estimate"])
    if count != int(pareto.pareto_efficient.sum()):
        raise ValueError("Pareto nondominated count differs from value registry")
    pairs = pd.read_csv(root / "results/pareto_dominance.csv")
    if not (pairs.filter(like="_advantage") >= -1e-12).all(axis=None):
        raise ValueError("A recorded Pareto dominance pair is directionally invalid")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "results/policy_summary.csv",
        root / "results/threshold_sweeps.csv",
        root / "results/sensitivity_outcomes.csv",
        root / "results/sensitivity_associations.csv",
        root / "results/sensitivity_interactions.csv",
        root / "results/threshold_sweep_audit.csv",
        root / "results/threshold_cell_stability.csv",
        root / "results/information_weight_sensitivity.csv",
        root / "data/processed/selected_literature.csv",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required pipeline outputs: {missing}")
    figures = root / "figures"
    tables = root / "tables"
    _figure_network(root, figures)
    _figure_trajectories(root, figures)
    _figure_pareto(root, figures)
    _figure_thresholds(root, figures)
    _figure_latent_survey(root, figures)
    _figure_tradeoffs(root, figures)
    _figure_observation_architecture(figures)
    _figure_exploration(root, figures)
    _figure_origin_future(root, figures)
    _build_tables(root, tables)
    _append_derived_values(root)
    _verify_pareto_consistency(root)
    print("Generated nine figures in PNG/PDF/SVG and seven result tables")


if __name__ == "__main__":
    main()
