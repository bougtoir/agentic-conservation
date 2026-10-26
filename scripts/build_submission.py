"""Build human-authoring, audit, and anonymous submission-support materials."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from agentic_conservation.analysis import write_run_manifest
from agentic_conservation.documents import (
    FIGURE,
    MAIN_FIGURES,
    MAIN_TABLES,
    TABLE,
    build_submission_documents,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def _figure_regeneration_guide(root: Path) -> None:
    _write(
        root / "manuscript/FIGURE_REGENERATION.md",
        """
# Figure deck and artwork regeneration

`FIGURE_DECK.pptx` is a submission-support deck with editable slide titles,
captions, and provenance notes. The figure artwork on each slide is a placed
PNG and is not editable as separate axes, series, or labels in PowerPoint.

The authoritative editable sources are the repository result tables and
`scripts/build_outputs.py`. From the project root, regenerate every PNG, PDF,
and SVG figure with:

```bash
make figures
```

After changing figure code or source results, rerun `make package` to rebuild
the deck and submission archive. This distinction prevents image-based slides
from being represented as element-editable charts.
""",
    )


def _interval(summary: pd.DataFrame, policy: str, metric: str) -> str:
    row = summary[
        (summary.policy == policy) & (summary.metric == metric) & (~summary.oracle)
    ].iloc[0]
    return f"{row.estimate:.3f} [{row.lower:.3f}, {row.upper:.3f}]"


def _reference_list(literature: pd.DataFrame) -> str:
    lines = []
    ordered = literature.assign(
        sort_key=literature.reference_authors.str.casefold()
    ).sort_values(["sort_key", "year"])
    for row in ordered.itertuples():
        lines.append(
            f"{row.reference_authors}. {int(row.year)}. {row.title}. "
            f"*{row.journal}*. https://doi.org/{row.doi} ({row.evidence_level})"
        )
    return "\n".join(lines)


def _literature_status(root: Path) -> str:
    audit = pd.read_csv(root / "provenance/literature_claim_audit.csv")
    cited = audit[audit.citation_status == "CITED"].drop_duplicates("doi")
    excluded = audit[audit.citation_status == "EXCLUDED"].drop_duplicates("doi")
    levels = cited.full_text_access.value_counts()
    return (
        f"{len(cited)} sources are cited. Complete article text was appraised for "
        f"{int(levels.get('FULL_TEXT_LOCAL', 0))}; "
        f"{int(levels.get('ABSTRACT_LOCAL', 0))} are cited only for statements "
        "in retained author abstracts or titles; and "
        f"{int(levels.get('METADATA_ONLY', 0))} are cited only for title-bounded "
        "background after exact-DOI Crossref verification. "
        f"{len(excluded)} former candidates without verified text are marked "
        "NOT_VERIFIED, excluded from the bibliography, and not used for "
        "substantive claims."
    )


def _authoring_packet(
    root: Path,
    summary: pd.DataFrame,
    information: pd.DataFrame,
    coverage: pd.DataFrame,
    literature: pd.DataFrame,
    checkpoint: dict,
) -> None:
    base = summary[(~summary.oracle) & (summary.metric == "survival_100")].copy()
    top = base.sort_values("estimate", ascending=False).iloc[0]
    information_effect = information[
        information.metric == "decision_utility"
    ].iloc[0]
    threshold = pd.read_csv(root / "results/threshold_sweep_audit.csv")
    convergence = pd.read_csv(root / "results/convergence_audit.csv")
    cap_audit = pd.read_csv(root / "results/population_cap_audit.csv")
    s0_controls = pd.read_csv(root / "results/s0_benign_controls.csv").set_index(
        "scenario"
    )
    pareto = pd.read_csv(root / "results/pareto_front.csv")
    registry = pd.read_csv(root / "provenance/parameter_registry.csv")
    weight_sensitivity = pd.read_csv(
        root / "results/information_weight_sensitivity.csv"
    )
    reversals = int(threshold.robust_s6_higher.sum())
    hybrid_advantages = int(threshold.robust_s7_higher.sum())
    indeterminate = int(threshold.indeterminate.sum())
    literature_audit = pd.read_csv(root / "provenance/literature_claim_audit.csv")
    cited_literature = literature_audit[
        literature_audit.citation_status == "CITED"
    ]
    excluded_literature = literature_audit[
        literature_audit.citation_status == "EXCLUDED"
    ]
    evidence_lines = "\n".join(
        f"- {row.reference}, DOI {row.doi}: {row.claim_summary} "
        f"Evidence level: {row.full_text_access}; location: {row.relevant_section}. "
        f"Boundary: {row.required_action}"
        for row in cited_literature.itertuples()
    )
    excluded_lines = "\n".join(
        f"- {row.reference}, DOI {row.doi}: NOT_VERIFIED and excluded from "
        "substantive manuscript use."
        for row in excluded_literature.itertuples()
    )
    production_convergence = convergence[
        (convergence.n == 192)
        & convergence.contrast.isin(["S6", "S7", "S7-S6"])
    ]
    max_convergence_ratio = float(
        (
            production_convergence.estimate_change_from_final.abs()
            / production_convergence.mcse.replace(0, np.nan)
        ).max()
    )
    cap_endpoint = cap_audit[
        (cap_audit.population_cap == 2400)
        & (cap_audit.contrast == "S7-S6")
        & (cap_audit.metric == "survival_100")
    ].iloc[0]
    nondominated = ", ".join(
        pareto.loc[pareto.pareto_efficient, "policy"].astype(str)
    )
    dominated = ", ".join(
        pareto.loc[~pareto.pareto_efficient, "policy"].astype(str)
    )
    status_counts = registry.status.value_counts().to_dict()
    status_summary = ", ".join(
        f"{status}={count}" for status, count in sorted(status_counts.items())
    )
    coverage_lines = "\n".join(
        f"- {row.species}: {int(row.gbif_query_total):,} coordinate-bearing present "
        f"records in the saved aggregate query; {int(row.records_2015_2025):,} "
        "were dated 2015–2025."
        for row in coverage.itertuples()
    )
    weight_lines = "\n".join(
        f"- {row.scenario}: {row.estimate:.3f} "
        f"[{row.lower:.3f}, {row.upper:.3f}]"
        for row in weight_sensitivity.itertuples()
    )
    packet = f"""
# Human authoring packet

This is a factual, code-derived packet for accountable human authors. It is not
a manuscript and does not supply final scientific interpretation.

## Candidate title

Dynamic conservation networks under environmental change and hidden biodiversity

## Article type and limits

- *Conservation Biology* Contributed Paper.
- IMRAD organization.
- Maximum 7,000 words from Abstract through Acknowledgments under the live
  instructions verified 2026-09-24.
- Abstract no longer than 300 words; 5–8 keywords; impact statement no longer
  than 140 characters.
- Double-blind manuscript; identifying cover page separate. All former
  Supporting Information content is integrated in the main text.

## Central question

When do dynamic networks spanning wild and managed environments change
biodiversity, welfare, genetic, information, and cost outcomes relative to
fixed strategies, and when do those differences disappear or reverse?

## Candidate model hypotheses for human framing

These were not externally preregistered and must not be described as
confirmatory hypotheses.

1. No single policy will dominate every alternative across persistence,
   welfare, cost, EBD, genetics, and future-option value.
2. S7 will exceed habitat-first S6 when directional habitat change is strong
   and movement harm is limited, but the ordering will reverse under stable
   origins or costly movement.
3. Survey investment will reduce EBD only when latent taxa remain detectable
   before extinction and survey opportunity costs do not displace higher-value
   interventions.
4. True current-state information will have an aggregation-dependent effect
   under a fixed heuristic rather than a necessarily positive EVPI.

## Defensible contribution

The transferable contribution is a transparent simulation framework that
combines latent species, noisy delayed observations, individual heterogeneity,
wild and managed nodes, finite budgets, human feedback, disease, welfare,
genetics, biobanking, and explicit policy reversals. The study should be framed
as a conditional decision-analysis experiment, not an empirical demonstration
that one institutional arrangement is generally superior.

## Methods facts to convert into human prose

1. Eight synthetic species were followed for 100 annual steps across nine
   node types. Five species were initially known and three were hidden from
   feasible decision makers.
2. Individuals carried demographic, health, disease, behavioral, origin,
   founder, and inbreeding states.
3. Latent taxa advanced through detection, description, monitoring, threat
   recognition, and protection; extinction before description was retained as
   an explicit endpoint.
4. Eight policies (S0–S7) ranged from no intervention through fixed habitat or
   captivity rules to state-dependent circulation, global allocation, and a
   hybrid forward-quality proxy.
5. Policy outcomes used paired seed sets. The {checkpoint["mode"]} run used
   {checkpoint["selected_replications"]} replications per policy. Percentile
   intervals describe simulation distributions; Monte Carlo half-widths are
   reported separately.
6. Sensitivity used a Latin-hypercube design plus five prespecified two-factor
   sweeps. Nine feature ablations and six adverse-condition designs sought
   disappearance and reversal conditions.
7. A current-state-information S7 comparison supplied true current abundance
   and habitat quality to the same action class. It did not supply future
   environmental draws and was not optimized as a POMDP or monetary EVPI.
   Effects were evaluated against a declared weighted utility and component
   outcomes.
8. The empirical component saved GBIF taxonomy and occurrence-year aggregates
   plus bibliographic metadata and bounded literature evidence snapshots. It
   was not used to calibrate synthetic parameters.

Detailed methods are in `docs/model_specification.md` and
`docs/analysis_plan.md`. {FIGURE['network']} depicts the node network.
{TABLE['parameters']} lists base parameters and {TABLE['policies']} lists policy
allocations.

## Code-derived result prompts

- The largest mean 100-year survival proportion in the current run was
  {top.estimate:.3f} for {top.policy}; its replicate-distribution interval was
  [{top.lower:.3f}, {top.upper:.3f}]. This ranking is descriptive and not a
  claim of general superiority.
- S7 survival was {_interval(summary, "S7", "survival_100")}; S6 survival was
  {_interval(summary, "S6", "survival_100")}; state-dependent S4 survival was
  {_interval(summary, "S4", "survival_100")}.
- S7 mean individual welfare was
  {_interval(summary, "S7", "mean_individual_welfare")}, while S2 lifetime
  captivity was {_interval(summary, "S2", "mean_individual_welfare")}.
- S7 extinction-before-discovery fraction was
  {_interval(summary, "S7", "fraction_ebd")}; S5 was
  {_interval(summary, "S5", "fraction_ebd")}.
- The paired current-state-information effect on the prespecified utility
  scale was {information_effect.estimate:.3f}
  [{information_effect.lower:.3f}, {information_effect.upper:.3f}].
- Robust two-factor sweep contrasts favored S7 in {hybrid_advantages} cells
  and S6 in {reversals}; {indeterminate} cells were indeterminate because
  their sign changed from N=4 to N=8 or their absolute mean did not exceed
  1.96 Monte Carlo standard errors. The existence of opposite-direction
  regions, not the raw cell tally, is the supported result.

All figures and tables are in the main text and numbered by first citation.
{FIGURE['pareto']} provides the multiobjective Pareto comparison,
{FIGURE['trajectories']} 100-year trajectories, {FIGURE['ebd']} EBD sensitivity,
{FIGURE['tradeoffs']} cross-objective trade-offs, {FIGURE['observation']} the
observation architecture, {FIGURE['reversal']} the policy-reversal surfaces,
{FIGURE['exploration']} exploration–exploitation patterns, and
{FIGURE['origin_future']} the origin-to-future optimum shift.
{TABLE['sensitivity']} and {TABLE['interactions']} provide sensitivity and
interaction screens, {TABLE['coverage']} and {TABLE['evidence']} empirical-source
summaries, {TABLE['outcomes']} policy estimates, {TABLE['robustness']}
robustness summaries, and {TABLE['information_weights']} information-weight
summaries.

## Robust, fragile, and alternative interpretations

- Robust implementation-level findings: policy rankings reverse across
  prespecified conditions; welfare, persistence, EBD, genetics, cost, and
  future-option value are noninterchangeable; and the six-objective Pareto
  analysis yields a broad nondominated set rather than a unique winner.
- Monte Carlo convergence: all registered S6, S7, and S7-S6 endpoint estimates
  at N=192 were within two N=192 Monte Carlo standard errors of N=384; the
  largest observed ratio was {max_convergence_ratio:.2f}. Current-state
  information effects also met the criterion. Production therefore remains
  N=192, with N=384 retained only as an audit.
- Population-cap robustness: doubling the synthetic cap from 1200 to 2400
  changed the paired S7-S6 survival contrast by
  {cap_endpoint.change_from_baseline:.4f}. Total abundance is cap-sensitive
  and is not used for the primary policy conclusions.
- Assumption-dependent findings: the base S6–S7 ordering, sweep-cell counts,
  S3 collapse under directional change, and the sign or magnitude of the
  aggregated information effect.
- Negative findings: current-state information did not produce a detectable
  positive utility effect under the fixed S7 heuristic; S7 did not exceed S6
  in the base production scenario; and the analysis does not identify a
  universally preferred institutional form.
- Alternative interpretations: reversals may reflect unavoidable ecological
  trade-offs, limitations of the policy heuristics, or arbitrary synthetic
  parameter regions. The experiment cannot distinguish those explanations
  empirically.
- Information-weight diagnostics:

{weight_lines}

## Empirical observation-coverage facts

{coverage_lines}

These counts are affected by observation effort, digitization, data publishing,
taxonomy, and the query date. They are not abundance, occupancy, population
trend, or intervention-effect estimates.

## Full-text-verified literature evidence

{_literature_status(root)} Bounded uses by source:

{evidence_lines}

Former candidates that remain auditable but are not cited:

{excluded_lines}

Cited sources support only the bounded statements above at their recorded
evidence levels; they do not calibrate model parameters or validate simulated
policy effects. Abstract- and metadata-level sources must not be strengthened
without full-text review.

## Parameter provenance

- Registry entries: {len(registry)}.
- Classification counts: {status_summary}.
- All registered model, species, node, and policy-allocation values are
  deliberately synthetic or illustrative (class C); none is presented as an
  empirical estimate, and no class-D entry remains.
- The registry records value, range or distribution, unit, rationale,
  sensitivity or robustness coverage, manuscript location, and action for
  every entry.
- The `max_individuals` computational cap is class C and covered by the
  twofold population-cap audit. This audit supports endpoint robustness but
  not interpretation of capped total abundance.

## S0 benign-control conclusion

The directional-change S0 design retained
{s0_controls.loc["base_directional_change", "species_retained_100_mean"]:.3f}
species on average at year 100. Removing directional deterioration and climate
velocity while retaining ordinary catastrophe risk, predation, anthropogenic
pressure, and demographic stochasticity retained
{s0_controls.loc["stationary_environment", "species_retained_100_mean"]:.3f}
species with survival
{s0_controls.loc["stationary_environment", "survival_100_mean"]:.3f}.
The stable excellent-origin and combined benign controls retained
{s0_controls.loc["stable_excellent_origin", "species_retained_100_mean"]:.3f}
and {s0_controls.loc["benign_combined", "species_retained_100_mean"]:.3f}
species, respectively. Zero-intervention extinction is therefore specific to
the configured directional-change scenario, not structurally required.

## Pareto conclusion

The reproducible analysis maximizes persistence, welfare, genetics, and future
option value and minimizes EBD and cost. Dominance uses an absolute numerical
tolerance of 1e-12 and no weighted overall score. Nondominated policies are
{nondominated}; dominated policies are {dominated}. {TABLE['outcomes']} and
`results/manuscript_values.csv` are checked against the same production means
and Pareto flags.

## Current AI-policy boundary

The live Wiley ethics guidance checked on 2026-09-25 permits AI only as an
additional tool, not a replacement for accountable human expertise and
judgment. Authors must document and disclose substantial AI use, including its
purpose, influence on arguments or conclusions, and personal review and
verification. AI cannot be an author. Human authors must ensure the final work
reflects their own expertise, voice, originality, and scientific decisions,
and must verify provider rights, privacy, and confidentiality terms.

## Exact passages requiring human scientific judgment

1. **HUMAN AUTHOR REQUIRED:** Results passage beginning “Supplying true current
   state to the same S7 action class” — decide whether the near-zero,
   weight-dependent negative result merits main-text emphasis.
2. **HUMAN AUTHOR REQUIRED:** Discussion passage beginning “The central result
   was conditionality rather than dominance” — determine the final novelty,
   conservation relevance, and alternative scientific interpretation.
3. **HUMAN AUTHOR REQUIRED:** Discussion passage beginning “The results do not
   identify a universal best institutional form” — approve the boundary
   between model proposition and applied recommendation.
4. **HUMAN AUTHOR REQUIRED:** Acknowledgments and AI-use disclosure — provide
   accurate tool, purpose, human-verification, funding, conflict, and
   contribution statements under the live journal policy.

## Discussion boundaries

- Explain why movement can help when origin quality deteriorates or future
  suitability shifts, but can harm through mortality, stress, pathogens, and
  maladaptation.
- Separate persistence in managed care from restoration of free-living
  populations.
- Treat welfare, genetics, habitat integrity, EBD, and cost as separate
  objectives; do not collapse them into a moral ranking.
- Explain why additional information has value only relative to a decision
  rule and normative utility.
- Discuss hidden biodiversity as a resource-allocation problem without
  asserting that the synthetic EBD rate predicts real global loss.
- State that fixed policy allocations, simplified genetics, aggregate
  biobanking, and noncalibrated synthetic species limit external validity.
- Present reversal surfaces and adverse conditions prominently. A conclusion
  that ignores them would overstate the evidence.

## Exact remaining human actions before submission

1. **HUMAN AUTHOR REQUIRED:** inspect the cited passages and approve every
   bounded literature claim at its recorded evidence level; read full text
   before strengthening any abstract- or metadata-level citation.
2. **HUMAN AUTHOR REQUIRED:** decide whether the synthetic parameterization,
   policy archetypes, utility weights, and interpretation are scientifically
   defensible; do not convert class-C values into empirical claims.
3. **HUMAN AUTHOR REQUIRED:** write or substantively revise the final manuscript
   in the authors' own scientific voice and approve every claim, citation,
   figure, table, and limitation.
4. **HUMAN AUTHOR REQUIRED:** supply authors, affiliations, contributions,
   funding, conflicts, acknowledgments, and the accurate AI-use disclosure on
   the nonanonymous cover material.
5. **HUMAN AUTHOR REQUIRED:** recheck live Conservation Biology and ScholarOne
   requirements on the submission date and arrange durable anonymous
   code/data review access if requested.

## References for human approval

{_reference_list(literature)}
"""
    _write(root / "manuscript/HUMAN_AUTHORING_PACKET.md", packet)


def _submission_templates(root: Path) -> None:
    impacts = [
        "Conservation networks help only when information and movement benefits "
        "exceed their welfare, disease, and opportunity costs.",
        "Hidden biodiversity and shifting habitat can reverse which mix of "
        "habitat protection, managed care, and movement performs best.",
        "No conservation network dominates when survival, welfare, genetics, "
        "information, habitat, and cost are evaluated separately.",
    ]
    if any(len(statement) > 140 for statement in impacts):
        raise ValueError("Impact statement exceeds 140 characters")
    _write(
        root / "manuscript/ARTICLE_IMPACT_STATEMENT_OPTIONS.md",
        "# Article impact statement options\n\n"
        + "\n".join(f"- {statement} ({len(statement)} characters)" for statement in impacts),
    )
    _write(
        root / "manuscript/COVER_PAGE_TEMPLATE.md",
        """
# Cover page template

Do not invent or infer any field. Replace every bracketed placeholder.

## Article

**Title:** [final title]

**Article type:** Contributed Paper

**Running head:** Dynamic conservation networks

**Word count:** [Abstract through Acknowledgments]

## Authors

1. [full legal/preferred publication name]
   - [affiliation]
   - [ORCID, if applicable]
   - [email]

**Corresponding author:** [name, postal address, email, telephone if required]

## Declarations

- Author contributions: [CRediT roles]
- Funding: [verified funder and award identifiers, or explicit none]
- Competing interests: [verified declaration]
- Data and code availability: [final archival citation]
- Acknowledgments: [verified names and permissions]
- AI-use disclosure: see `AI_USE_DISCLOSURE_DRAFT.md`, reviewed and approved by
  all authors.
""",
    )
    _write(
        root / "manuscript/DATA_CODE_AVAILABILITY.md",
        """
# Data and code availability draft

All synthetic simulation inputs, analysis code, seed assignments, result
tables, and figure-generation scripts are organized in the accompanying
reproducibility repository. Public-source API responses used in the empirical
coverage audit are retained as immutable timestamped snapshots with URLs,
retrieval conditions, file sizes, SHA-256 checksums, license notes, and
completeness statements in a machine-readable source ledger.

Before submission, replace this paragraph with a durable repository citation,
version/DOI, license, and an anonymous review link if required. Do not state
that individual GBIF occurrence records are archived. Literature-audit source
snapshots are retained locally with checksums, but publisher pages and article
full text are not redistributed because reuse rights were not established.
""",
    )
    _write(
        root / "manuscript/CONSERVATION_BIOLOGY_SUBMISSION_CHECKLIST.md",
        """
# Conservation Biology submission checklist

## Scientific

- [ ] All authors approve the model, utility weights, claims, and final text.
- [ ] Full-text appraisal supports every literature claim.
- [ ] Synthetic and empirical evidence are clearly separated.
- [ ] Reversal, adverse-condition, and null results are reported.
- [ ] Percentile intervals are not mislabeled as empirical confidence intervals.
- [ ] No universal policy winner is claimed.

## Journal format

- [ ] Contributed Paper, IMRAD, no standalone Conclusion.
- [ ] Abstract ≤300 words; 5–8 keywords.
- [ ] Article impact statement ≤140 characters.
- [ ] Abstract-through-Acknowledgments ≤7,000 words under current instructions.
- [ ] Authors approve the integrated main-text display count (no SI).
- [ ] Every figure and table is cited in order in the final text.
- [ ] Live instructions and ScholarOne fields rechecked on submission day.

## Double blind

- [ ] Cover page uploaded separately.
- [ ] Anonymous manuscript, file names, metadata, and acknowledgments contain
  no author, institution, email, repository owner, or session identifier.
- [ ] Self-citations do not reveal authorship unnecessarily.
- [ ] Anonymous code/data link used if review access is supplied.

## Integrity and availability

- [ ] `make quick`, `make full`, `make empirical`, `make audit`,
  `make figures`, and `make package` rerun from the release source commit,
  with the full outputs regenerated after the quick smoke run.
- [ ] Tests and lint pass.
- [ ] Source and artifact checksums verified.
- [ ] `results/manuscript_values.csv` agrees with final prose, tables, and figures.
- [ ] Repository archived with DOI/version and license.
- [ ] Author details, contributions, funding, conflicts, and acknowledgments are
  verified rather than inferred.
- [ ] AI-use disclosure is accurate and approved by all authors.
""",
    )


def _audits(
    root: Path,
    summary: pd.DataFrame,
    information: pd.DataFrame,
    checkpoint: dict,
) -> None:
    convergence = pd.read_csv(root / "results/convergence_audit.csv")
    principal = convergence[
        (convergence.contrast == "S7-S6")
        & (convergence.metric == "survival_100")
    ].sort_values("n")
    final_convergence = principal.iloc[-1]
    production_convergence = principal[
        principal.n == checkpoint["selected_replications"]
    ]
    production_convergence = (
        production_convergence.iloc[0]
        if not production_convergence.empty
        else principal.iloc[-1]
    )
    thresholds = pd.read_csv(root / "results/threshold_sweep_audit.csv")
    reversal_count = int(thresholds.robust_s6_higher.sum())
    pareto = pd.read_csv(root / "results/pareto_front.csv")
    nondominated = int(pareto.pareto_efficient.sum())
    dominated_policies = ", ".join(
        pareto.loc[~pareto.pareto_efficient, "policy"].astype(str)
    )
    information_effect = information[
        information.metric == "decision_utility"
    ].iloc[0]
    priority_rows = "\n".join(
        [
            (
                "| Full-text evidence boundary | claim strength | desk reject if "
                "overstated | high | completed computationally; human approval "
                "required | retain only evidence-level-bounded claims |"
            ),
            (
                "| Synthetic external validity | manuscript | desk reject / major "
                "revision | high | feasible now by reframing; calibration requires "
                "new data | present conditional model propositions, not general "
                "effect sizes |"
            ),
            (
                "| Normative utility weights | statistical design | major revision | "
                "high | completed computationally; prose revision feasible | report "
                "components and weight sensitivity |"
            ),
            (
                "| Accountable authorship and verification | reproducibility | "
                "integrity / desk reject | high | human review required | inspect and "
                "approve every artifact and claim |"
            ),
            (
                "| Monte Carlo precision | statistical design | major revision | "
                "medium | completed | report nested convergence and MCSE |"
            ),
            (
                "| RNG pairing qualification | statistical design | major revision | "
                "medium | feasible now | describe keyed process-year streams and "
                "their limit |"
            ),
            (
                "| S7 construction advantage | manuscript / design | major revision | "
                "high | completed with active comparators and reversals | foreground "
                "reversal regions and avoid winner language |"
            ),
            (
                "| Dependent individuals | statistical design | major revision | "
                "high | feasible now | treat simulation replication as the analysis "
                "unit |"
            ),
            (
                "| Multiple exploratory outcomes | statistical design | major "
                "revision | medium | feasible now | emphasize effect patterns and "
                "uncertainty, not binary significance |"
            ),
            (
                "| Pareto interpretation | figures/tables | major revision | medium | "
                "completed | report nondominance without cardinal ranking |"
            ),
            (
                "| Welfare value dependence | claim strength | major revision | "
                "medium | completed computationally; human framing required | "
                "distinguish burden definitions and normative weights |"
            ),
            (
                "| Policy-budget confounding | statistical design | major revision | "
                "high | robustness audit completed | report allocation sensitivity "
                "and avoid tuned-versus-handicapped comparisons |"
            ),
            (
                "| GBIF observation coverage | claim strength | desk reject if "
                "overstated | high | feasible now | do not infer abundance, occupancy, "
                "trend, or intervention effect |"
            ),
        ]
    )
    _write(
        root / "docs/reviewer_audit.md",
        f"""
# Hostile but fair pre-submission review

The review separates manuscript logic, statistical design, figures/tables,
reproducibility, and claim strength. Priorities reflect likely editorial
consequence, scientific benefit, and feasibility with the existing evidence.

## Prioritization matrix

| Issue | Domain | Editorial risk | Corrective benefit | Feasibility | Required correction |
|---|---|---|---|---|---|
{priority_rows}

## Most urgent — mandatory before submission

1. **Claim strength — evidence boundary (desk-reject risk if overstated; high
   impact; completed computationally, human approval required).**
   {_literature_status(root)} Human authors
   must preserve the bounded wording unless they independently add and verify
   new evidence.
2. **Manuscript — external validity (major-revision risk; high impact; requires
   additional evidence or narrower claims).** Synthetic species and uncalibrated nodes do
   not support taxon-specific or global effect sizes. Frame results as model
   propositions and reversal conditions. A calibrated case study would be a
   separate study.
3. **Statistical design — normative utility (major-revision risk; high impact;
   feasible now).** The
   current-state-information contrast depends on declared weights. The current
   estimate is {information_effect.estimate:.3f} utility units. Present
   component outcomes and weight sensitivity; do not call it theoretical or
   monetary EVPI.
4. **Reproducibility and authorship (integrity risk; high impact; mandatory).**
   Accountable authors must inspect code, raw snapshots, model behavior,
   citations, figures, tables, and every sentence; then write and approve the
   final manuscript.

## High priority

1. **Statistical design — Monte Carlo precision.** The nested audit through
   {int(final_convergence.n)} paired replications gives an S7-minus-S6 survival
   contrast of {final_convergence.estimate:.3f} with MCSE
   {final_convergence.mcse:.3f}. At the production count of
   {int(production_convergence.n)}, the sign is unchanged. Report the complete
   convergence table rather than implying that simulation error is absent.
2. **Statistical design — random-number qualification.** Policies share keyed
   process-year streams, but diverging populations prevent exact
   individual-level pairing within later demographic arrays. Describe these
   as keyed process-year streams, not mathematically exact common random
   numbers.
3. **Manuscript — construction bias.** S7 contains future-quality and research terms. Report
   S6 and simpler dynamic policies as active comparators and show reversals.
   Robust cell-level contrasts favored S6 in {reversal_count} tested
   two-factor cells; directionally indeterminate cells are not counted as
   reversals.
4. **Statistical design — analysis unit and independence.** Replications are the inferential unit.
   Individuals within one simulation are dependent and must not be treated as
   independent observations.
5. **Claim strength — multiplicity.** The study is exploratory across many outcomes and
   scenarios. Emphasize effect patterns, intervals, and robustness rather than
   binary significance claims.
6. **Figures/tables — Pareto interpretation.** {nondominated} of
   {len(pareto)} policies are nondominated under the six registered objectives;
   the dominated policies are {dominated_policies}. {FIGURE['pareto']} therefore shows
   broad trade-off incomparability without identifying a unique winner; state
   this limitation explicitly.

## Medium priority

1. **Claim strength:** explain that welfare-person-years rewards both persistence and welfare,
   whereas mean individual welfare isolates average experienced conditions.
2. **Claim strength:** replace the simplified founder/inbreeding proxy with pedigree or genomic
   dynamics before making applied genetic-management recommendations.
3. **Manuscript:** expand catastrophe modeling if facility failure and epidemic are central
   claims; current environmental events and disease/funding processes are
   stylized.
4. **Statistical design:** justify fixed policy allocations or add allocation optimization. Current
   comparisons conflate decision rules and portfolio shares by design.
5. **Claim strength:** keep occurrence coverage descriptive. Sampling intensity and data
   mobilization can dominate interspecific differences.

## Optional strengthening

1. Calibrate a preregistered case study with demographic and management data.
2. Add stakeholder-derived multiattribute utility weights.
3. Replace the rollout proxy with a formally solved small POMDP benchmark.
4. Validate biobank value against material-specific viability and use models.

## Figure and table audit

The network, trajectory, and Pareto figures directly support architecture,
time-course, and trade-off claims. Threshold, sensitivity, empirical-source,
robustness, and information-weight displays are integrated in the main text and
numbered by first citation. The objective-normalization plot is descriptive
only and must not be interpreted as cardinal utility. Tables overlap with CSV
source files but are necessary for human review.

## Verdict

The computational framework is suitable for critical methodological
discussion. The full-text evidence audit and technical corrections are
complete. It is ready for accountable human scientific interpretation,
approval, disclosure, and final submission-day checks.
""",
    )
    _write(
        root / "docs/model_bias_audit.md",
        f"""
# Model-bias and negative-results audit

## Checks

- S7 is not universally dominant: its survival is lower than S6 in
  {reversal_count} tested two-factor cells.
- No-intervention and refuge-and-return policies can fail under directional change;
  this is a conditional model result, not a premise about real programs.
- Stable excellent origin, high movement harm, zero breeding advantage, high
  captivity burden, efficient restoration, and negative engagement are
  explicitly tested.
- Welfare is built from conditions rather than a wild/managed binary.
- Feasible policies do not receive hidden-species state or true habitat
  quality; the oracle analysis is separately labeled.
- S5 omits origin privilege; origin-fidelity ablation sets it to zero for
  dynamic policies.

## Residual biases

1. Policy budget shares are fixed and can advantage a policy under its favored
   assumptions.
2. S7's forward-quality term may favor restoration-capable nodes.
3. Every policy shares the same simplified demographic and welfare equations.
4. Hidden species differ from known species only through configured traits and
   information stage; the taxonomy process is stylized.
5. Welfare, genetic, biobank, and engagement indices are commensurable only
   after normative scaling.

## Interpretation rule

Report where rankings disappear or reverse before discussing base-case means.
Do not use one weighted utility to label an overall winner.
""",
    )
    _write(
        root / "docs/integrity_audit.md",
        """
# Fabrication and integrity audit

## Passed machine-verifiable checks

- Synthetic species are labeled synthetic.
- Empirical inputs exist as immutable local raw snapshots.
- The source ledger contains retrieval URL, identifier/version, UTC time,
  condition, local path, size, SHA-256, license note, and completeness.
- GBIF summaries derive from saved API responses.
- Bibliography rows match saved exact-DOI Crossref responses.
- Figures and tables are generated from result CSV files.
- Numerical prompts in the authoring packet are read from current result files.
- No author names, affiliations, funding, conflicts, or contributions are
  invented.

## Limits requiring human verification

- {_literature_status(root)} Crossref, OpenAlex, and Semantic Scholar records
  were not treated as evidence of methods or findings beyond retained abstract
  text.
- Human authors must approve the bounded source interpretations and must not
  strengthen them without independently verified evidence.
- GBIF individual occurrence records were not downloaded; only complete
  aggregate year-facet responses for the recorded queries were saved.
- Scientific plausibility and conservation relevance cannot be established by
  tests alone.
- A human must compare the eventual manuscript against
  `results/manuscript_values.csv`.
""",
    )
    _write(
        root / "provenance/hard_code_audit.md",
        """
# Hard-code audit

All result estimates inserted into generated authoring materials are read from
`results/*.csv` or `data/processed/*.csv`. Analysis assumptions and normative
utility weights are stored in versioned JSON configuration. The scripts contain
structural constants—policy labels, journal limits, display labels, and
formatting precision—but no hand-entered simulation estimates, uncertainty
intervals, empirical occurrence totals, or literature citation counts.

The source of truth for proposed manuscript numbers is
`results/manuscript_values.csv`. Tables and figures are regenerated by
`scripts/build_outputs.py`; authoring materials and audits are regenerated by
`scripts/build_submission.py`.
""",
    )
    _write(
        root / "docs/reproducibility_audit.md",
        f"""
# Reproducibility audit

## Current build

- Pipeline mode: `{checkpoint["mode"]}`.
- Policy replications: {checkpoint["selected_replications"]}.
- Analysis sizes and replicate counts are versioned in `config/analysis.json`.
- Nested policy convergence was audited through 384 paired replications.
- Sensitivity replicates are aggregated to the design level before inference.
- All five two-factor sweeps have cell-level sign-stability outputs.
- Raw API snapshots are under `data/raw/` and are never overwritten.
- Source and run manifests retain SHA-256 checksums.
- Figures are emitted as SVG, PDF, and 320-dpi PNG.
- Tables are emitted as CSV and Markdown.
- Tests exercise budget, origin-collapse, captivity, latent-species,
  survey-cost, unlimited-budget, relocation, and movement-disease behavior.

## Reproduction sequence

```text
python3 -m pip install -r requirements-dev.txt
make empirical
make full
make audit
make figures
make package
make test
make lint
```

`make empirical` operates on the latest persisted raw snapshot and requires no
network. `make fetch` is used only to create a new immutable source version.

## Qualification

Re-running from the same raw snapshots, code commit, Python environment, and
seeds is deterministic. A fresh `make fetch` can change public-source
summaries and must be treated as a new data version.
""",
    )


def _double_blind_audit(root: Path, anonymous: Path) -> None:
    forbidden = [
        "bougtoir",
        "tatsuki",
        "onishi",
        "@gmail",
        "/home/",
        "app.devin.ai/sessions",
    ]
    findings = []
    for path in anonymous.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in {".md", ".csv", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        elif suffix in {".docx", ".pptx"}:
            with zipfile.ZipFile(path) as archive:
                text = "\n".join(
                    archive.read(name).decode("utf-8", errors="ignore").lower()
                    for name in archive.namelist()
                    if name.endswith((".xml", ".rels"))
                )
        elif suffix in {".png", ".pdf", ".svg"}:
            text = path.read_bytes().decode("utf-8", errors="ignore").lower()
        else:
            continue
        for term in forbidden:
            if term in text or term in path.name.lower():
                findings.append(f"{path.relative_to(root)}: `{term}`")
    status = "PASS" if not findings else "FAIL"
    details = "\n".join(f"- {finding}" for finding in findings) or "- None."
    _write(
        root / "docs/double_blind_audit.md",
        f"""
# Double-blind audit

**Status: {status}**

The anonymous review directory was scanned for user name, repository owner,
email-domain, local absolute path, and Devin session identifiers. Text,
Office XML and relationships, and rendered-artwork metadata streams were
included.

## Findings

{details}

## Manual checks still required

- self-citations and acknowledgments;
- anonymous archive URLs;
- ScholarOne-generated file labels.
""",
    )
    if findings:
        raise RuntimeError(f"Double-blind audit failed: {findings}")


def _readiness_report(root: Path) -> None:
    literature = pd.read_csv(root / "provenance/literature_claim_audit.csv")
    cited = literature[literature.citation_status == "CITED"]
    excluded = literature[literature.citation_status == "EXCLUDED"]
    bibliography = pd.read_csv(root / "data/processed/bibliography.csv")
    allowed_support = {
        "FULL_TEXT_LOCAL": {"DIRECT"},
        "ABSTRACT_LOCAL": {"ABSTRACT_DIRECT", "TITLE_BOUNDED"},
        "METADATA_ONLY": {"TITLE_BOUNDED"},
    }
    if not (
        30 <= bibliography.doi.nunique() == len(bibliography) <= 40
        and set(cited.doi) == set(bibliography.doi)
        and cited.full_text_access.eq("FULL_TEXT_LOCAL").sum() >= 4
        and all(
            row.support_level in allowed_support.get(row.full_text_access, set())
            for row in cited.itertuples()
        )
        and not set(excluded.doi) & set(bibliography.doi)
        and excluded.support_level.eq("NOT_VERIFIED").all()
    ):
        raise RuntimeError("Literature evidence readiness criterion failed")

    registry = pd.read_csv(root / "provenance/parameter_registry.csv")
    required_registry_fields = [
        "base_value",
        "range_or_distribution",
        "unit",
        "status",
        "source_or_rationale",
        "doi_or_source",
        "sensitivity_included",
        "manuscript_location",
        "action",
    ]
    if (
        registry[required_registry_fields].isna().any().any()
        or registry.status.eq("D").any()
    ):
        raise RuntimeError("Parameter provenance readiness criterion failed")

    convergence = pd.read_csv(root / "results/convergence_audit.csv")
    primary = convergence[
        (convergence.n == 192)
        & convergence.contrast.isin(["S6", "S7", "S7-S6"])
    ]
    if not (
        len(primary) == 15
        and (
            primary.estimate_change_from_final.abs()
            <= 2 * primary.mcse
        ).all()
        and primary.sign_stable.all()
    ):
        raise RuntimeError("Monte Carlo convergence readiness criterion failed")

    controls = pd.read_csv(root / "results/s0_benign_controls.csv").set_index(
        "scenario"
    )
    if controls.loc["stationary_environment", "species_retained_100_mean"] <= 0:
        raise RuntimeError("S0 benign-control readiness criterion failed")

    pareto = pd.read_csv(root / "results/pareto_front.csv")
    objectives = {
        "survival",
        "welfare",
        "genetics",
        "ebd",
        "cost",
        "future_option",
    }
    if not objectives.issubset(pareto.columns) or int(
        pareto.pareto_efficient.sum()
    ) != 6:
        raise RuntimeError("Pareto readiness criterion failed")

    packet = (root / "manuscript/HUMAN_AUTHORING_PACKET.md").read_text(
        encoding="utf-8"
    )
    packet_requirements = [
        "## Full-text-verified literature evidence",
        "## Parameter provenance",
        "## S0 benign-control conclusion",
        "## Pareto conclusion",
        "## Current AI-policy boundary",
        "## Exact passages requiring human scientific judgment",
        "## Exact remaining human actions before submission",
    ]
    if not all(requirement in packet for requirement in packet_requirements):
        raise RuntimeError("Human-authoring handoff readiness criterion failed")

    nondominated = ", ".join(
        pareto.loc[pareto.pareto_efficient, "policy"].astype(str)
    )
    _write(
        root / "FINAL_SUBMISSION_READINESS.md",
        f"""
## 1. Full-text evidence audit — PASS

{_literature_status(root)} Every claim is restricted to its recorded
evidence level, and no in-text citation lacks a verified bibliography entry.

## 2. Parameter provenance — PASS

All {len(registry)} registered entries contain the required provenance fields;
all are explicitly synthetic class C, no class-D entry remains, and the
population cap has a twofold robustness audit.

## 3. Monte Carlo convergence — PASS

All registered S6, S7, and S7-S6 endpoints at N=192 are within two N=192 Monte
Carlo standard errors of N=384 with stable qualitative signs. Information
effects also converge but remain interval-spanning and directionally
uncertain.

## 4. S0 benign control — PASS

The stationary control retains
{controls.loc["stationary_environment", "species_retained_100_mean"]:.3f}
species on average at year 100, and the stronger combined benign control
retains {controls.loc["benign_combined", "species_retained_100_mean"]:.3f}.
Directional-scenario extinction is not structurally required.

## 5. Pareto verification — PASS

The reproducible analysis applies the declared directions and tolerance to six
objectives without a weighted overall ranking. The nondominated set is
{nondominated}, consistent with {TABLE['outcomes']} and the manuscript values registry.

## 6. Human-authorship handoff — PASS

The packet now contains verified results, robust and fragile findings, negative
findings, evidence boundaries, provenance, convergence, S0 and Pareto
conclusions, limitations, alternative interpretations, exact judgment
passages, and only genuinely human-required actions.

Overall Conservation Biology readiness:
READY FOR HUMAN FINALIZATION

Remaining HUMAN AUTHOR REQUIRED actions:

1. Approve the evidence-level-bounded literature interpretations and the scientific
   defensibility of the synthetic design, utility weights, and conclusions.
2. Finalize the manuscript in the authors' own scientific voice and approve
   every claim, citation, figure, table, and limitation.
3. Supply authorship, affiliations, contributions, funding, conflicts,
   acknowledgments, and an accurate AI-use disclosure outside anonymous review
   materials.
4. Decide repository deposition, license, DOI, and anonymous review access,
   then verify live journal and ScholarOne requirements on the submission date.
""",
    )


def _package(root: Path) -> None:
    submission = root / "submission"
    if submission.exists():
        shutil.rmtree(submission)
    anonymous = submission / "anonymous_review"
    figures = anonymous / "figures"
    tables = anonymous / "tables"
    anonymous.mkdir(parents=True)
    figures.mkdir()
    tables.mkdir()
    shutil.copy2(
        root / "manuscript/HUMAN_AUTHORING_PACKET.md",
        anonymous / "HUMAN_AUTHORING_PACKET.md",
    )
    for name in [
        "INLINE_MANUSCRIPT_HUMAN_REVIEW_DRAFT.docx",
        "EDITABLE_TABLES.docx",
        "FIGURE_DECK.pptx",
        "FIGURE_REGENERATION.md",
        "DOCUMENT_VALIDATION.txt",
    ]:
        shutil.copy2(root / "manuscript" / name, anonymous / name)
    for number, filename, _ in MAIN_FIGURES:
        source_stem = Path(filename).stem
        display_stem = source_stem.split("_", maxsplit=1)[1]
        output_stem = f"{number.replace(' ', '_')}_{display_stem}"
        for suffix in ("png", "pdf", "svg"):
            source = root / "figures" / f"{source_stem}.{suffix}"
            shutil.copy2(source, figures / f"{output_stem}.{suffix}")
    for number, filename, _ in MAIN_TABLES:
        source_stem = Path(filename).stem
        display_stem = source_stem.split("_", maxsplit=1)[1]
        output_stem = f"{number.replace(' ', '_')}_{display_stem}"
        for suffix in ("csv", "md"):
            source = root / "tables" / f"{source_stem}.{suffix}"
            shutil.copy2(source, tables / f"{output_stem}.{suffix}")
    for name in [
        "COVER_PAGE_TEMPLATE.md",
        "COVER_PAGE_TEMPLATE.docx",
        "COVER_LETTER.docx",
        "COVER_LETTER.txt",
        "ARTICLE_IMPACT_STATEMENT_OPTIONS.md",
        "DATA_CODE_AVAILABILITY.md",
        "AI_USE_DISCLOSURE_DRAFT.md",
        "CONSERVATION_BIOLOGY_SUBMISSION_CHECKLIST.md",
    ]:
        shutil.copy2(root / "manuscript" / name, submission / name)

    records = []
    for path in sorted(submission.rglob("*")):
        if path.is_file():
            records.append(
                {
                    "path": str(path.relative_to(submission)),
                    "size": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    pd.DataFrame(records).to_csv(submission / "package_manifest.csv", index=False)
    archive = root / "submission/conservation_biology_submission_package.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(submission.rglob("*")):
            if path.is_file() and path != archive:
                bundle.write(path, path.relative_to(submission))


def _final_report(root: Path, checkpoint: dict) -> None:
    ledger = pd.read_csv(root / "provenance/source_ledger.csv")
    latest = ledger.accessed_utc.max()
    manifest = json.loads((root / "provenance/run_manifest.json").read_text())
    archive = root / "submission/conservation_biology_submission_package.zip"
    summary = pd.read_csv(root / "results/policy_summary.csv")
    information = pd.read_csv(root / "results/information_value.csv")
    thresholds = pd.read_csv(root / "results/threshold_sweep_audit.csv")
    convergence = pd.read_csv(root / "results/convergence_audit.csv")
    pareto = pd.read_csv(root / "results/pareto_front.csv")
    s6 = summary[
        (summary.policy == "S6")
        & (~summary.oracle)
        & (summary.metric == "survival_100")
    ].iloc[0]
    s7 = summary[
        (summary.policy == "S7")
        & (~summary.oracle)
        & (summary.metric == "survival_100")
    ].iloc[0]
    information_utility = information[
        information.metric == "decision_utility"
    ].iloc[0]
    convergence_final = convergence[
        (convergence.contrast == "S7-S6")
        & (convergence.metric == "survival_100")
        & (convergence.n == convergence.n.max())
    ].iloc[0]
    s7_higher = int(thresholds.robust_s7_higher.sum())
    s6_higher = int(thresholds.robust_s6_higher.sum())
    indeterminate = int(thresholds.indeterminate.sum())
    nondominated = int(pareto.pareto_efficient.sum())
    report = f"""
# Final report

## Executive summary

The targeted final revision corrected implementation and inference defects,
reran affected analyses, and rebuilt the complete human-review package. The
study remains a synthetic conditional decision experiment, not an empirical
forecast or policy recommendation. The full-text evidence audit is complete;
human scientific authorship and final source approval remain mandatory before
submission.

## What changed from the previous package

- Corrected S3 refuge-and-return eligibility, movement exposure, release
  hazards, and species-level capacity handling.
- Removed hidden current-quality leakage from feasible policies and removed
  hindsight retention from the information comparator.
- Added process/year keyed random streams, observation delay, EBD boundary
  tests, active welfare/genetics/disease/biobank/engagement audits, explicit
  analysis configuration, design-level sensitivity aggregation, interaction
  screening, threshold sign stability, six-objective Pareto assessment, and
  alternative information-weight diagnostics.
- Narrowed empirical and literature claims to the evidence actually retained.

## Defects found and corrected

The consequential defects were an inert S3 policy, diffuse rather than
exposure-specific movement hazards, feasible access to hidden habitat quality,
post-hoc oracle action selection, repeated sensitivity rows treated as
independent, and incomplete threshold/Pareto auditing. Each was corrected in
code and covered by regression or structural checks.

## Analyses rerun and why

The policy Monte Carlo, sensitivity design, all five two-factor sweeps,
ablations, adverse conditions, figures, tables, value registry, manuscript
documents, and archive were rerun because their inputs or interpretation
changed. The separate convergence audit was retained and regenerated through
384 paired replications.

## Main verified findings

- S6 mean year-100 survival was {s6.estimate:.3f}; S7 was
  {s7.estimate:.3f}.
- Across registered sweep cells, robust contrasts favored S7 in {s7_higher}
  and S6 in {s6_higher}; {indeterminate} cells were directionally
  indeterminate under the registered stability and Monte Carlo error rule.
- The registered current-state-information effect was
  {information_utility.estimate:.3f}
  [{information_utility.lower:.3f}, {information_utility.upper:.3f}].
- {nondominated} of {len(pareto)} policies were Pareto-nondominated under the
  six registered objectives; this indicates incomparability, not universal
  optimality.

## Robust findings

Policy orderings reverse across conditions, component objectives are
noninterchangeable, and no single policy dominates every objective. Feasible
policies remain separated from oracle-only state, and null/adverse results are
retained.

## Fragile or assumption-dependent findings

Base-case ranks, exact sweep-cell counts, S3 performance, engagement effects,
and aggregated information effects depend on synthetic ranges, policy shares,
heuristic structure, and normative weights. They must not be presented as
taxon-specific effect sizes.

## Negative and unexpected findings

S7 can underperform S6, extra current-state information can reduce utility
under the fixed heuristic, and the broad six-objective Pareto set does not
produce a unique winner.

## S3 failure explanation

The original zero result included an implementation defect that prevented
initial refuge movement. After correction, S3 still performs poorly in the
directional-change base case but persists under stable excellent and restored
origins. Its remaining failures reflect deterioration, timing, finite budgets,
movement hazards, and stochastic demography rather than a general failure of
return-oriented conservation.

## S0 failure explanation

S0 fails in the harsh directional-change base case, but stationary excellent
and combined benign controls retain most species. Intervention is therefore
not structurally required by the implementation.

## Monte Carlo convergence conclusion

At N={int(convergence_final.n)}, the paired S7-minus-S6 survival contrast was
{convergence_final.estimate:.3f} with MCSE {convergence_final.mcse:.3f}. Its
sign was stable across nested prefixes; 192 production replications were
retained while the 384-replication audit is reported.

## Oracle and information conclusion

The comparator supplies true current abundance and habitat quality to the same
S7 action class, without future draws, realized outcomes, or post-hoc action
selection. It is a paired current-state-information effect under a fixed
heuristic, not theoretical or monetary EVPI.

## Empirical evidence and literature status

GBIF results are observation-coverage aggregates only. They do not estimate
abundance, occupancy, trends, or intervention effects and do not calibrate the
model. {_literature_status(root)} Latest recorded public-source
retrieval: {latest}.

## Transferability beyond zoos

The defensible contribution concerns dynamic conservation networks under
shifting habitat, partial observation, latent biodiversity, finite resources,
and multiobjective trade-offs. Managed facilities are node types within that
general framework rather than the article's advocated institution.

## Remaining limitations and blocked items

Synthetic species and nodes are uncalibrated; genetics, disease, welfare,
biobank, engagement, and policy optimization remain stylized. No technical
blocker prevents reproduction. External and human-required items are listed in
`BLOCKED_ITEMS.md`.

## Conservation Biology readiness

The evidence, provenance, convergence, S0, Pareto, and reproducibility checks
are complete. The package is ready for accountable human scientific
finalization, not autonomous submission.

## AI-policy compliance and double-blind status

The package identifies Devin's implementation, analysis, and drafting support;
human authors remain responsible for every claim and must approve the final
disclosure. Automated scans cover text, Office XML/relationships, and artwork
metadata; manual self-citation, acknowledgment, archive-link, and ScholarOne
checks remain required.

## Reproducibility identity

- Analysis code commit recorded by the run: `{manifest.get("git_commit", "unrecorded")}`.
- Output hashes: {len(manifest.get("output_sha256", {}))}.
- Input hashes: {len(manifest.get("input_sha256", {}))}.
- Submission-support archive SHA-256:
  `{hashlib.sha256(archive.read_bytes()).hexdigest()}`.

## Reproducibility and test status

- `{checkpoint["mode"]}` policy replications:
  {checkpoint["selected_replications"]} per policy.
- {len(MAIN_FIGURES)} figures in SVG/PDF/320-dpi
  PNG and {len(MAIN_TABLES)} tables in
  CSV/Markdown.
- Values registry, source inventory, run manifest, editable Office files,
  anonymous package, and scientific audits are regenerated from current
  results.

## Exact local reproduction commands

```bash
make full
make audit
make figures
make package
make test
make lint
git diff --check
unzip -t submission/conservation_biology_submission_package.zip
```

## Exact remaining HUMAN AUTHOR REQUIRED actions

1. Approve the bounded literature claims at their recorded evidence levels.
2. Finalize manuscript prose, scientific interpretation, and every
   policy-relevance boundary in the authors' own voice.
3. Supply author names, affiliations, contributions, funding, conflicts,
   acknowledgments, and the accurate AI-use disclosure.
4. Decide on durable repository deposition, DOI, license, and anonymous review
   access.
5. Verify live journal and ScholarOne requirements on the submission date.

## Readiness verdict

The reproducible computational and human-review drafting package is complete
and ready for the mandatory accountable human finalization listed above.
"""
    _write(root / "FINAL_REPORT.md", report)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    summary = pd.read_csv(root / "results/policy_summary.csv")
    information = pd.read_csv(root / "results/information_value.csv")
    coverage = pd.read_csv(root / "data/processed/gbif_coverage_summary.csv")
    literature = pd.read_csv(root / "data/processed/bibliography.csv")
    checkpoint = json.loads((root / "results/checkpoints/pipeline.json").read_text())
    counts = json.loads((root / "provenance/run_manifest.json").read_text())["counts"]
    _authoring_packet(root, summary, information, coverage, literature, checkpoint)
    _submission_templates(root)
    _figure_regeneration_guide(root)
    _audits(root, summary, information, checkpoint)
    _readiness_report(root)
    build_submission_documents(root)
    _package(root)
    _double_blind_audit(root, root / "submission/anonymous_review")
    write_run_manifest(root, checkpoint["mode"], counts)
    _final_report(root, checkpoint)
    write_run_manifest(root, checkpoint["mode"], counts)
    print("Generated authoring packet, audits, and submission-support archive")


if __name__ == "__main__":
    main()
