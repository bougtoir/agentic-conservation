# Hostile but fair pre-submission review

The review separates manuscript logic, statistical design, figures/tables,
reproducibility, and claim strength. Priorities reflect likely editorial
consequence, scientific benefit, and feasibility with the existing evidence.

## Prioritization matrix

| Issue | Domain | Editorial risk | Corrective benefit | Feasibility | Required correction |
|---|---|---|---|---|---|
| Full-text evidence boundary | claim strength | desk reject if overstated | high | completed computationally; human approval required | retain only evidence-level-bounded claims |
| Synthetic external validity | manuscript | desk reject / major revision | high | feasible now by reframing; calibration requires new data | present conditional model propositions, not general effect sizes |
| Normative utility weights | statistical design | major revision | high | completed computationally; prose revision feasible | report components and weight sensitivity |
| Accountable authorship and verification | reproducibility | integrity / desk reject | high | human review required | inspect and approve every artifact and claim |
| Monte Carlo precision | statistical design | major revision | medium | completed | report nested convergence and MCSE |
| RNG pairing qualification | statistical design | major revision | medium | feasible now | describe keyed process-year streams and their limit |
| S7 construction advantage | manuscript / design | major revision | high | completed with active comparators and reversals | foreground reversal regions and avoid winner language |
| Dependent individuals | statistical design | major revision | high | feasible now | treat simulation replication as the analysis unit |
| Multiple exploratory outcomes | statistical design | major revision | medium | feasible now | emphasize effect patterns and uncertainty, not binary significance |
| Pareto interpretation | figures/tables | major revision | medium | completed | report nondominance without cardinal ranking |
| Welfare value dependence | claim strength | major revision | medium | completed computationally; human framing required | distinguish burden definitions and normative weights |
| Policy-budget confounding | statistical design | major revision | high | robustness audit completed | report allocation sensitivity and avoid tuned-versus-handicapped comparisons |
| GBIF observation coverage | claim strength | desk reject if overstated | high | feasible now | do not infer abundance, occupancy, trend, or intervention effect |

## Most urgent — mandatory before submission

1. **Claim strength — evidence boundary (desk-reject risk if overstated; high
   impact; completed computationally, human approval required).**
   40 sources are cited. Complete article text was appraised for 4; 31 are cited only for statements in retained author abstracts or titles; and 5 are cited only for title-bounded background after exact-DOI Crossref verification. 5 former candidates without verified text are marked NOT_VERIFIED, excluded from the bibliography, and not used for substantive claims. Human authors
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
   estimate is -0.003 utility units. Present
   component outcomes and weight sensitivity; do not call it theoretical or
   monetary EVPI.
4. **Reproducibility and authorship (integrity risk; high impact; mandatory).**
   Accountable authors must inspect code, raw snapshots, model behavior,
   citations, figures, tables, and every sentence; then write and approve the
   final manuscript.

## High priority

1. **Statistical design — Monte Carlo precision.** The nested audit through
   384 paired replications gives an S7-minus-S6 survival
   contrast of -0.057 with MCSE
   0.016. At the production count of
   192, the sign is unchanged. Report the complete
   convergence table rather than implying that simulation error is absent.
2. **Statistical design — random-number qualification.** Policies share keyed
   process-year streams, but diverging populations prevent exact
   individual-level pairing within later demographic arrays. Describe these
   as keyed process-year streams, not mathematically exact common random
   numbers.
3. **Manuscript — construction bias.** S7 contains future-quality and research terms. Report
   S6 and simpler dynamic policies as active comparators and show reversals.
   Robust cell-level contrasts favored S6 in 26 tested
   two-factor cells; directionally indeterminate cells are not counted as
   reversals.
4. **Statistical design — analysis unit and independence.** Replications are the inferential unit.
   Individuals within one simulation are dependent and must not be treated as
   independent observations.
5. **Claim strength — multiplicity.** The study is exploratory across many outcomes and
   scenarios. Emphasize effect patterns, intervals, and robustness rather than
   binary significance claims.
6. **Figures/tables — Pareto interpretation.** 6 of
   8 policies are nondominated under the six registered objectives;
   the dominated policies are S2, S5. Figure 2 therefore shows
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
