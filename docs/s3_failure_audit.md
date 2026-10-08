# S3 failure audit

## Defects corrected

The previous implementation initialized every individual at the origin and then
allowed S3 to move only individuals already outside the origin. S3 therefore
had no initial candidates and was not a meaningful return policy. Movement
mortality and release mortality were also applied as diffuse population-wide
penalties rather than to moved and released individuals. The corrected S3 is a
refuge-and-return archetype: it evacuates visible populations when observed
origin suitability falls below a configured trigger and returns eligible
individuals after observed suitability recovers. Movement and release hazards
now apply only to exposed individuals, and node capacity is enforced per
species, consistently with density dependence.

## Conditional results

Across the registered audit seeds, base directional change retained
2.458 species on average with survival
0.307. Under a stable excellent origin, S3 retained
7.500 species with survival
0.938. In the restoration design, mean refuge moves
were 123.083 and mean returns to origin were
220.125.

S3 failure is therefore not interpreted as evidence that return-oriented
conservation is generally ineffective. It is a conditional result produced by
directional origin deterioration, the timing thresholds, finite budgets,
movement hazards, and demographic stochasticity. Exact scenario definitions
are versioned in `config/audit_designs.json`; replicate-level outcomes are in
`results/s3_failure_outcomes.csv`.

## Interpretation

S3 remains a synthetic policy archetype, not a representation of any named
reintroduction program. Stable-origin, restored-origin, zero-harm, larger-budget,
and alternative-timing scenarios are retained even when they weaken the
manuscript's base contrast.
