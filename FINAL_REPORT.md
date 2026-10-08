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

- S6 mean year-100 survival was 0.529; S7 was
  0.473.
- Across registered sweep cells, robust contrasts favored S7 in 35
  and S6 in 26; 64 cells were directionally
  indeterminate under the registered stability and Monte Carlo error rule.
- The registered current-state-information effect was
  -0.003
  [-0.112, 0.131].
- 6 of 8 policies were Pareto-nondominated under the
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

At N=384, the paired S7-minus-S6 survival contrast was
-0.057 with MCSE 0.016. Its
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
model. 40 sources are cited. Complete article text was appraised for 4; 31 are cited only for statements in retained author abstracts or titles; and 5 are cited only for title-bounded background after exact-DOI Crossref verification. 5 former candidates without verified text are marked NOT_VERIFIED, excluded from the bibliography, and not used for substantive claims. Latest recorded public-source
retrieval: 2026-10-07T06:02:25+00:00.

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

- Analysis code commit recorded by the run: `60493965c52bce6a16f300395c6094ce1b0de057`.
- Output hashes: 195.
- Input hashes: 259.
- Submission-support archive SHA-256:
  `0864ca4a301de4cd0e7cc3a654f3f85b0ffed1397fba20641d8afcac1a0e2ba2`.

## Reproducibility and test status

- `full` policy replications:
  192 per policy.
- 9 figures in SVG/PDF/320-dpi
  PNG and 9 tables in
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
