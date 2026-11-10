# Gate 1 decision: B — TARGETED SCIENTIFIC VERIFICATION REQUIRED

| Dimension | Status | Basis |
|---|---|---|
| Computational reproducibility | PASS | 43 tests and Ruff clean; current code reproduces `policy_outcomes.csv` exactly (sampled seeds); the reversal registry is present and consistent |
| Reporting completeness (ODD 2020/S1) | FAIL, repairable | crosswalk: 8 FAIL, 12 PARTIAL, 0 PASS; Patterns, state-variable table, schedule semantics, 5 design concepts, and most submodels are missing |
| Scientific validity | UNRESOLVED | three questions (below) bear directly on the S6/S7 reversal and on Ψ |
| Empirical validity | NOT CLAIMED | synthetic system; GBIF is context only; no calibration or external validation |

Why not A: three construction choices decide the main result and have never been tested. Text alone cannot show that the result comes from the ecology rather than from these choices.
Why not C: no central mechanism is indefensible in direction. The code is faithful and reproducible, and each open question can be settled with a bounded analysis.

## Required analyses
None of these changes the default dynamics. They add observer outputs and run alternative-form sensitivity configurations. Cost is estimated at about 1 s per run on 2 cores (measured 1.8 s per run per core).

| Q | Unresolved question | Minimum analysis | Approx. cost | Decision criterion | Possible effect |
|---|---|---|---|---|---|
| Q1 | Does the S6/S7 conclusion hold when "persistence" means a viable population rather than ≥ 1 individual anywhere? | Observer-only outputs: (a) species with ≥ 1 mature female and ≥ 1 mature male co-located in a non-biobank node at year 100; (b) wild-node persistence. Base scenario, all 8 policies × 192 paired seeds; S6/S7 on the 56 holdout cells | about 30–60 min | Conclusion retained if the sign of the base S7−S6 contrast and the determinate-cell sign accuracy (≥ 0.75) hold under the viable endpoint | If the sign changes: the conclusions must be restated per endpoint, or Gate C |
| Q2 | Is the reversal an artefact of quadratic cumulative climate displacement? | Alternative forms with equal year-100 displacement: (i) linear cumulative (constant annual decrement); (ii) step at T/2. S6/S7 × 192 seeds plus holdout cells | about 30–45 min | Base sign unchanged, and ≥ 80 % agreement of determinate holdout cell signs | If agreement < 80 %: the reversal location depends on form, so the claim becomes conditional |
| Q3 | Are the conclusions robust to the untested literals (E1 0.72/0.28/0.32/0.25/0.24; E6 0.58, 20 % take; E11 0.24/0.08; E12 5.0)? | One-at-a-time ±50 % perturbation, S6/S7 × 48 seeds (20 perturbations) | about 35 min | Sign of S7−S6 unchanged in ≥ 18 of 20 perturbations; flipping literals reported | If a literal flips the sign: it is reported as a load-bearing assumption with its rationale, or Gate C |

Total: about 2–3 h of compute in one VM, with no new large Monte Carlo campaign. All results will be reported whatever they show. The canonical registry is not changed. New values go into a separate `results/odd_verification/` registry.

## Reporting corrections required in every case (text only)
- Remove or label the inert traits and variables.
- State the climate form exactly.
- Rename "funding collapse" to "one-year funding shock" and "successful reintroductions" to "release events".
- State that engagement is non-decreasing.
- State the exclusions: no topology, no interspecific competition, no senescence.
- Add the ODD Patterns, state-variable table, schedule semantics, and all 11 design concepts.
- Write one ODD 7 subsection per submodel.
