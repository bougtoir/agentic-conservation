# Ψ confirmatory validation plan (prospective; frozen before any outcome)

This plan is committed **together with** the configuration set and the Ψ predictions, **before** any IBM run on these configurations. The commit SHA and UTC freeze time are recorded in `PSI_CONFIRMATORY_FREEZE_RECORD.md` in the next commit. Nothing below may be changed after the IBM stage starts. Any deviation must be appended as a dated amendment and reported.

## 1. Frozen Ψ specification
- Implementation: `psi_index` in `src/agentic_conservation/minimal_model.py` at the freeze commit. This is the committed model **V1** (whole-cohort latent discovery, `eps = 0.02`, `MIN_BREEDING_POP = 4.0` default, `STRUCTURAL_DEFAULTS` at shipped values, shipped accelerating climate).
- Allocations: `config/base.json` `policy_allocations` S7 (circulation arm) vs S6 (habitat arm).
- Decision rule: predict S7-favoured iff Ψ > 0; otherwise S6-favoured. θ₀ = 0, fixed a priori. Ψ never abstains.
- Why V1 and not V0: V1 is the committed and documented implementation. V0's development accuracy was 0.608. V1 is frozen **as is**: no constant, threshold, or formula is changed for this evaluation. This choice is made before any confirmatory outcome exists.

## 2. Configuration generation rule (untouched configurations)
- Script: `scripts/psi_confirmatory.py design`. RNG `SeedSequence(20261110)`.
- Parameter space: the 10 development-sweep parameters in `analysis.SWEEPS`, each with its dev range.
- Stratum A, **in-domain joint** (40 cells): 3 distinct parameters per cell, each drawn uniformly within its dev range. Joint 3-parameter perturbations never appear in the dev grid.
- Stratum B, **shifted** (20 cells): 1–2 parameters per cell, each drawn uniformly from `[hi, hi + 0.5·(hi − lo)]`, i.e. beyond the dev range. All values remain valid (fractions and probabilities < 1).
- Exclusion at generation: a configuration that equals (within 1e-6) any dev-grid cell or any of the 56 original holdout cells is re-drawn by the same RNG stream. No configuration is ever excluded because of its Ψ value or its outcome.
- The output `results/psi_confirmatory/designs.csv` is committed at the freeze.

## 3. Outcome generation (after freeze only)
- IBM: `run_simulation` at the freeze commit, S6 and S7, 12 paired seeds per cell, `seed = 5_000_000 + 100·cell + rep`. These seeds are unused anywhere in the repository (the largest existing seed is 980047). Total 1,440 runs.
- Primary endpoint: `survival_100`, the endpoint Ψ was derived for. Secondary endpoints, reported without gate: `viable_persistence_100` and `wild_persistence_100`.
- Cell sign: `d = Y(S7) − Y(S6)` per seed. The sign is that of the mean of `d` if `|mean d| > 2·SE`; otherwise the cell is indeterminate (0). This is the same rule as the original holdout and Q1–Q3.

## 4. Metrics (all reported, by stratum and pooled)
- Counts of S7-favoured, S6-favoured and indeterminate cells.
- Accuracy on determinate cells, with a Wilson 95% CI. All-cell accuracy, in which every indeterminate cell counts as an error because Ψ never abstains.
- Decision regret `mean(max(S6,S7) − value of Ψ's pick)`, compared with always-S6 and always-S7.

## 5. Pre-specified pass criteria (primary endpoint, pooled 60 cells)
The Ψ validation gate **passes** only if all three hold:
1. Determinate-cell accuracy ≥ 0.75, and the Wilson 95% lower bound > 0.50.
2. Ψ regret < min(always-S6 regret, always-S7 regret).
3. At least 15 determinate cells. If fewer, the result is **inconclusive**, not a pass.

All-cell accuracy, the indeterminate fraction, the per-stratum results and the secondary endpoints are reported descriptively. They must appear in the manuscript whether favourable or not.

## 6. Use restrictions
- The confirmatory set is not used for model selection, threshold tuning, formula revision or constant refitting. If Ψ fails, the failure is reported as the confirmatory result. Any revised Ψ would need a new, separately frozen evaluation.
- The original holdout (V0) and the exploratory V1-on-old-holdout numbers stay labelled as historical and exploratory, respectively.
- No canonical registry (`results/*.csv`, `results/reversal/*`) is modified. Outputs go only to `results/psi_confirmatory/`.

## 7. Execution order
1. Freeze commit: this plan, `scripts/psi_confirmatory.py`, `designs.csv`, `psi_predictions.csv`.
2. Freeze record commit (SHA and time).
3. After the Q1–Q3 runs finish (single VM): `ibm`, then `evaluate`.
4. The gate decision is recorded in UPDATED_SCIENTIFIC_GATE_DECISION.md.
