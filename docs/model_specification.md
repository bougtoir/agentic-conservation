# Model specification

## Purpose and interpretation

The model is an individual-based, annual-step simulation over 100 years. It
compares eight prespecified conservation policies under changing habitat,
partial observability, stochastic events, latent species, finite budgets, and
multiple outcomes. It is deliberately intermediate in complexity: more
mechanistic than a payoff table, but not a taxon-specific population viability
analysis or an exact partially observable Markov decision process.

The primary estimand is a policy contrast conditional on the model and
parameter distribution. No output is an empirical causal effect.

## State

The true state \(X_t\) includes individual species, sex, age, origin, current
node, founder lineage, inbreeding proxy, health, S/I/R disease state, wildness,
human habituation, stress tolerance, foraging competence, release readiness,
and survival. Species traits include growth, mortality, niche breadth, habitat
specificity, climate and anthropogenic sensitivity, dispersal, detectability,
fertility, social dependence, migration need, and captivity tolerance.

The node network includes original habitat, alternative habitat, reserve,
conventional zoo, conservation zoo, breeding center, semi-wild facility,
rehabilitation facility, and biobank.

## Partial observability and latent biodiversity

Non-oracle policies receive \(O_t\), not \(X_t\). Observed abundance is
lognormally noisy for species at or beyond description stage; habitat quality
is delayed one year and measured with additive noise. The oracle receives true
abundance and current quality.

Initially latent species progress stochastically through:

1. exist;
2. detect;
3. describe;
4. monitor;
5. recognize threat;
6. protect.

Survey spending, detectability, habitat access, and stage affect transition
probability. A latent species that becomes extinct before description is
recorded as extinction before discovery (EBD).

## Environment

Wild-node quality changes through deterioration or restoration, directional
climate displacement from origin toward alternative habitat, habitat
investment, and stochastic wildfire, flood, or heatwave shocks. Supported
scenario labels are stationary, slow deterioration, rapid deterioration,
restoration, directional change, and abrupt origin collapse.

Species-node suitability combines current quality, niche breadth, habitat
specificity, captivity tolerance, and migration need. Thus historical origin
and the future best node can differ.

## Demography, welfare, genetics, and disease

Annual survival depends on species mortality, suitability, anthropogenic
pressure, predation, managed-node research support, infection, relocation,
release risk, and individual health. Density-dependent reproduction requires
adult females and males in the same node. Managed reproduction can benefit
from ex-situ investment.

Welfare is calculated independently of the wild/managed label from node space,
social support, naturalistic opportunity, food security, disease,
anthropogenic disturbance, relocation stress tolerance, and migration-related
habituation. Both mean individual welfare and welfare-person-years are retained
so that quality of life is not silently conflated with population persistence.

Genetic outputs include effective founder representation, inbreeding, and a
heterozygosity proxy. Genetic investment enables diversity-aware mating.

Disease uses individual susceptible, infected, and recovered states. Local
prevalence and movement-associated exposure generate infection; recovery is
stochastic, and infection reduces survival and welfare.

## Biobank and human feedback

The biobank endpoint is a simplified species-level coverage index representing
the combined future option from stored sperm, ova, embryos, somatic cells, or
DNA. It accounts for investment, viability decay, and future value but does not
model material-specific laboratory protocols.

Visitor exposure, habitat signal, and engagement spending alter a bounded
engagement index that feeds the next annual budget. Sensitivity designs include
positive, zero, and negative engagement coefficients.

## Budget

Each nonzero policy allocates an annual budget among habitat, survey, rescue,
ex-situ management, genetics, biobank, and engagement. Allocations cannot
exceed the available budget. Funding collapse can reduce subsequent budgets.
Both expenditure and cumulative available budget are recorded.

## Policies and decision engines

- S0: no intervention.
- S1: ex-situ phase-down and wild-node transfer where applicable.
- S2: conventional lifetime captivity.
- S3: return to origin when feasible.
- S4: state-dependent circulation among conservation nodes.
- S5: greedy current expected-utility allocation without origin privilege.
- S6: habitat-first with no active circulation.
- S7: hybrid portfolio with a simple forward-quality proxy.

S3, S4, and S7 can include positive origin fidelity
\(\lambda_{\mathrm{origin}}>0\); S5 uses
\(\lambda_{\mathrm{origin}}=0\). An origin-fidelity ablation sets the parameter
to zero.

## Current-state information comparison

S7 is rerun with true current abundance and habitat quality, but without future
environmental realizations. Paired current-state-information effects are
reported for survival, future option value, EBD, and a transparent
decision utility:

\[
U = 0.35S + 0.20F + 0.15H + 0.15(1-E) + 0.15W ,
\]

where \(S\) is species survival, \(F\) future option value, \(H\) habitat
integrity, \(E\) EBD fraction, and \(W\) mean individual welfare. These weights
are illustrative normative choices, not empirically estimated preferences.
The utility difference is an information effect in index units, not currency,
theoretical EVPI, or the value of a solved POMDP.

## Analysis

Policies share keyed process/year seed streams for paired contrasts. Full
production uses 192 replications per policy and retains a nested convergence
audit through 384. Latin-hypercube sensitivity covers 12 parameters with 128
designs and four stochastic replicates; replicates are averaged before
design-level association and interaction screening. Five two-factor grids use
eight paired replicates per cell. Nine ablations and six adverse-condition
designs actively seek reversal and disappearance conditions.

Percentile intervals describe replicate distributions. Monte Carlo half-widths
quantify simulation error. They are not population confidence intervals.
