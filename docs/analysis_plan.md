# Prespecified analysis plan

## Primary comparisons

Compare S0–S7 at 100 years for:

- proportion and number of species retained;
- wild and total abundance;
- extinction before discovery;
- mean individual welfare and welfare-person-years;
- founder-effective representation, inbreeding, and heterozygosity proxy;
- habitat integrity and future option value;
- disease prevalence and relocation burden;
- cost and cost per species retained.

No single weighted endpoint selects a universal winner. Pareto efficiency is
reported across persistence, mean individual welfare, cost, EBD, genetics,
and future option value.

## Monte Carlo

1. Pilot each policy with paired seed sets as a diagnostic.
2. Audit survival, EBD, welfare, and policy contrasts at nested prefixes
   through 384 replications.
3. Use the versioned full-production count of 192 replications per policy,
   retaining the 384-replication convergence audit for precision assessment.
4. Pair S7 feasible-information and oracle runs by seed.

The production count is a computational design choice justified by stable
principal-contrast direction and small 192-to-384 changes, not a claim of zero
Monte Carlo error.

## Global and threshold sensitivity

Latin-hypercube inputs:

- habitat deterioration;
- climate velocity;
- relocation mortality and stress;
- breeding benefit;
- release-survival penalty;
- movement disease;
- captivity welfare penalty;
- survey cost;
- engagement coefficient;
- budget;
- habitat-protection efficiency.

The full design uses 128 Latin-hypercube points and four stochastic replicates
per point for S4, S6, and S7. Replicates are averaged within a design before
Spearman rank associations are calculated. Pairwise partial-rank interaction
screens residualize both the outcome and product term against the two main
effects. Morris screening is omitted because the requested interaction
assessment requires a separate pairwise design-level analysis.

Structured two-factor designs:

1. habitat deterioration × relocation stress;
2. latent-species fraction × survey cost;
3. climate velocity × assisted-colonization mortality;
4. captivity welfare penalty × ex-situ breeding benefit;
5. engagement effect × habitat-protection efficiency.

Each full-production grid contains 25 cells and eight paired stochastic
replicates per cell. Cell signs are checked at nested replicate prefixes.

## Ablations

Remove human feedback, latent species, genetics, climate, biobank, disease,
welfare, partial-observation noise, and origin fidelity one at a time.

## Adverse conditions

Actively test excellent stable origin, high relocation/pathogen harm, zero
breeding advantage, high captivity burden, efficient restoration, and negative
engagement. A result in which circulation always wins triggers a construction
bias review rather than a favorable conclusion.

## Empirical component

The empirical component is a reproducibility and observation-coverage audit,
not model calibration. For Przewalski's horse, scimitar-horned oryx, and
California condor:

- resolve accepted taxonomy through GBIF;
- save complete year-facet responses for present, georeferenced occurrences;
- summarize temporal coverage;
- retrieve Crossref metadata for intervention and decision-theory literature;
- keep only DOI-verified selected records for the evidence table.

GBIF occurrence counts must not be interpreted as abundance or trend.
