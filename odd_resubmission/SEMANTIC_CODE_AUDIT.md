# Semantic code audit (simulation.py at branch base 14d726d90)

Passing tests (43) and a clean Ruff run are not evidence of scientific correctness. Each item below was checked by reading the code. Items marked "run" were also checked by running the model.

## A. Computational reproducibility
- **PASS (run).** The current code reproduces `results/policy_outcomes.csv` exactly for S3, S5, S6, and S7 at seeds 200000 and 200001. All seven compared endpoints match to within 1e-9.
- Between the results commit (51ea91f23) and HEAD, `simulation.py` changed only in formatting, in the default-off `decision_rule_override`/`movement_disabled` hooks, and in engine labels. The `engine` column in older CSVs is therefore a stale label only. It is cosmetic and should be relabelled.

## B. Estimands and denominators
| ID | Finding | Severity | Effect on conclusions |
|---|---|---|---|
| S1 | `survival_100` is the fraction of the 8 species with at least one living individual anywhere, including captive-only and single-sex remnants. It is not a viability or quasi-extinction endpoint. | HIGH | The primary S6/S7 contrast and Ψ are defined on this endpoint. A viability-based endpoint could change the sign in cells where S7 keeps small captive remnants. |
| S2 | `successful_reintroductions` is incremented at release, before release mortality. S3's "successful returns" figure (25.43) is in fact origin-return events. | MEDIUM | Wording only. Rename to "release events". |
| S3 | `mean_individual_welfare` averages over the individuals alive at year 100. Survivor bias favours policies that lose low-welfare animals. | LOW | Caveat |
| S4 | The EBD denominator is the latent cohort (3 species). Proportions move in steps of 1/3. | LOW | Already reported as a count |

## C. Signs, units, and directions
| ID | Finding | Severity |
|---|---|---|
| S5 | Climate: each year the origin quality is reduced by v·t/T. The decrement grows with t, so cumulative displacement is quadratic, reaching about 0.61 at year 100 when v = 0.012. Node 1 gains 0.65× that amount. The manuscript formula can be read as a linear shift. | HIGH (this is the reversal driver) |
| S6 | "Funding collapse" multiplies the budget by 0.72 in step 1, but step 13 resets the budget every year for non-S0 policies. The event is therefore a one-year shock, not a collapse. | MEDIUM (wording/mechanism) |
| S7 | With the default positive coefficients, engagement never decreases (every increment is ≥ 0, capped at 1.5). The budget drifts upward from about 94 to about 118. The S7/S6 budget difference comes from visitor exposure. | MEDIUM |
| S8 | Density dependence uses the species' own count divided by the whole node capacity. There is no interspecific competition, and each species can individually fill a node. | MEDIUM |
| S9 | Age matters only for maturity (≥ 2). There is no senescence or age-specific survival. | MEDIUM |

## D. Description–code contradictions
| ID | Finding | Severity |
|---|---|---|
| S10 | Several traits are declared and described as species differences but never read by the IBM dynamics: `climate_sensitivity`, `dispersal`, `social_dependence`, node `connectivity`, the individual `foraging` variable, `wildness` (updated but never read), and `biobank_future_value`. Movement ignores network topology: any node can be reached from any node. | HIGH (reporting); scientific effect: species respond to climate only through habitat breadth and specificity |
| S11 | Under the population cap, births are truncated in species-index order, so latent species come last. The cap audit at 1200 vs 2400 leaves survival unchanged. | LOW |
| S12 | The literals in E1, E6, E11, and E12 (0.72, 0.28, 0.32, 0.25, 0.24, 0.58, 20% take, 0.14, 0.035, 5.0) are never varied. The LHS covers 12 configuration parameters only. | HIGH (functional-form robustness unknown) |

## E. Split integrity and inference unit
- The holdout and development grids come from separate generator streams and seeds. The registry values (56 holdout cells, 26 determinate, accuracy 0.846 on determinate cells, 0.393 on all cells) were re-read from `results/reversal/manuscript_reversal_values.csv`. No leakage was found in the code path. The abstention threshold is post hoc and is already labelled as such.
- The inference unit is the paired seed (common random numbers across policies). The intervals are Monte Carlo intervals only and do not express parameter uncertainty.

## F. Scientific interpretation
- The S7−S6 contrast bundles allocation, movement rule, and target scoring. The factorial attribution exists but must stay bundled in the text.
- The reduced model (M1–M4) is a deterministic surrogate with fixed constants (HEALTH 0.70, INBREEDING 0.08, FEMALE_FRAC 0.25, MIN_BREEDING_POP 4 in code, documented elsewhere as a frozen 8). It is a heuristic criterion, not a derivation from the IBM. The stored held-out Ψ is not reproducible from committed code (see PSI_PROVENANCE_AUDIT.md).
