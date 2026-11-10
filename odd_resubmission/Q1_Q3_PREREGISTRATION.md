# Q1–Q3 frozen analysis plan (written and committed before any Q1–Q3 run)

Authorised by the author on 2026-11-10 (Gate 1 = B). The shipped dynamics, the canonical registries (`results/*.csv`, `results/reversal/*`) and the submitted manuscript (`manuscript/EM_MANUSCRIPT.docx`, sha256 8ff06f53…95b1de) are immutable baselines. New outputs go only to `results/odd_verification/`.

## Implementation hooks (no change to default dynamics)
- `simulation.py`: `STRUCTURAL_DEFAULTS` (10 literals at shipped values), `climate_increment` (default `accelerating` = shipped v·t/T), observer outputs `viable_persistence_100`, `wild_persistence_100`, `origin_quality_mean` (no RNG draws).
- `minimal_model.py` reads the same hooks so that Ψ can be recomputed under the same alternative.
- Regression gate (must pass before any run): pytest + Ruff; exact reproduction of `policy_outcomes.csv` (8 policies × 3 seeds, 9 endpoints), 12 random `holdout_runs.csv` rows, and all 56 `holdout_psi.csv` Ψ values (|ΔΨ| = 0).

## Common definitions (identical to the canonical registry)
- Paired contrast per seed: d = Y(S7) − Y(S6). Cell sign = sign(mean d) if |mean d| > 2·SE (SE = sd/√n), otherwise 0 (indeterminate).
- Ψ metrics on the 56 frozen held-out cells (seeds 910000 + 100·cell + rep, 12 reps): determinate-cell sign accuracy, all-cell accuracy, number of S7-favoured, S6-favoured and indeterminate cells, and decision regret = mean over cells of (best policy mean − mean of the Ψ-picked policy), computed on the endpoint under study.
- Base scenario: `config/base.json`, seeds 200000–200191 (192 paired seeds, the same ones as `policy_outcomes.csv`).
- Policy ranking: order of the 8 policies by mean endpoint. Rank agreement is Kendall τ against the individual-persistence ranking.
- Two sensitivities are always reported separately:
  - (a) **Policy contrast**: the S7−S6 sign, magnitude and determinacy in the IBM.
  - (b) **Reduced Ψ criterion**: (b1) the frozen original Ψ scored against the new IBM signs; (b2) Ψ recomputed under the same alternative, scored against the new IBM signs; (b3) the number of held-out cells whose Ψ sign flips.

## Q1: endpoints (highest priority)
- **Endpoints**:
  - E-ind: `survival_100`, ≥ 1 living individual anywhere (the canonical endpoint).
  - E-rep: `viable_persistence_100`, ≥ 1 mature (age ≥ 2) female and ≥ 1 mature male co-located in the same non-biobank node. This is a reproductive co-location proxy, not a guarantee of long-term viability.
  - E-wild: `wild_persistence_100`, ≥ 1 living individual in a wild node.
- **Runs**: base scenario, 8 policies × 192 seeds (1,536 runs); held-out grid, S6/S7 × 56 cells × 12 reps (1,344 runs). Both use the canonical seeds, so E-ind must reproduce the registry exactly.
- **Reported per endpoint**: base means for all 8 policies, the S7−S6 paired mean ± SE with its sign, Kendall τ, and the held-out Ψ metrics. Ψ itself is not recomputed under Q1, because the reduced model has no sex or wild-only structure. Original Ψ is scored against each endpoint (b1 only).
- **Finding rule**: a sign or ranking change between endpoints is reported as an endpoint-conditional finding. On its own it is not a model failure.

## Q2: climate trajectory with equal year-100 displacement
- **Forms**: `accelerating` (shipped), `linear`, `decelerating`, and `step` (all at mid-run). The IBM total displacement over years 1–100 is 0.606 for v = 0.012; the reduced model's total over t = 0–99 is 0.594.
- **Cumulative exposure** = Σ_t (cumulative displacement through year t), in displacement-years, at v = 0.012: accelerating 20.60, linear 30.60, decelerating 40.60, step 30.91. Equal endpoint displacement is therefore **not** equal ecological exposure. The alternatives impose 1.49–1.97× the shipped exposure. The realised mean origin quality (`origin_quality_mean`, after clipping and restoration) is reported per form.
- **Runs**: base S6/S7 × 192 seeds and held-out S6/S7 × 56 × 12, for each of the 3 alternatives (3 × 1,728 = 5,184 runs), on E-ind and E-rep.
- **Reported per form**: the base contrast; agreement between determinate held-out cell signs and the shipped form; and Ψ metrics (b1), (b2), (b3).
- **Pre-stated reading** (not a gate rule): ≥ 80 % agreement means the reversal location is robust to the trajectory shape. Below 80 % means the reversal location depends on climate timing and exposure, and must be stated as conditional on the trajectory.

## Q3: one-at-a-time literal perturbations (±50 %)
- **Literals**: E1 intercept 0.72, breadth slope 0.28, specificity penalty 0.32, tolerance bonus 0.25, migration penalty 0.24; E6 eligibility threshold 0.58, take fraction 0.20; E11 habitat mortality 0.24, pressure mortality 0.08; E12 birth scale 5.0. That gives 20 perturbations.
- **Domain constraints**: every perturbed value lies inside its domain. Thresholds and fractions stay in (0, 1), with 0.87 and 0.30 as the maxima. Survival probabilities remain clipped to [0.05, 0.995] and suitability to [0.02, 0.99], as shipped. No perturbation needs truncation, so none is truncated.
- **Stage 1 (all 20)**: base S6/S7 × 48 seeds (200000–200047) on E-ind and E-rep (1,920 runs). Ψ is recomputed on all 56 held-out cells, giving the count of Ψ sign flips (b3). Each run also gets the reference with shipped literals on the same seeds.
- **Material** (frozen): any of (i) the base S7−S6 sign changes (determinate in the opposite direction, or determinate ↔ indeterminate); (ii) |Δ mean contrast| > 2·SE of the shipped contrast; (iii) Ψ sign flips in ≥ 5 of 56 held-out cells.
- **Stage 2**: full held-out re-runs (1,344 runs each) for the material perturbations, ranked by (iii) then (ii), capped at 6. Any material perturbation beyond the cap is listed as "material, held-out not evaluated". For each, report the policy contrast, the held-out sign distribution, and Ψ metrics (b1) and (b2), including regret.

## Revised gate rules (frozen; following the author's instruction 4)
- **C**: only if a central conclusion depends on a scientifically indefensible assumption, or a fundamental model–implementation contradiction is found. Ranking or sign changes on their own are not grounds for C.
- **B**: if a material dependency is found whose scientific interpretation cannot be stated without further analysis (e.g. the held-out results are dominated by indeterminate cells, or the dependency is on a literal with no defensible range), or if Q1 shows that the central conclusion holds on none of the three endpoints and no conditional restatement is defensible.
- **A**: otherwise. Every dependency is then reported as a bounded, conditional result, with its rationale written into the ODD Submodels section.
- Unfavourable results are reported in full. No threshold above may be changed after the runs.

## Amendment A1 (before any Q run; see PSI_PROVENANCE_AUDIT.md)
- The regression gate passed for the IBM (exact) and for development Ψ (exact). The stored held-out Ψ is not reproducible from committed code.
- (b1) is evaluated for both Ψ_reg (stored) and Ψ_code (committed code, shipped settings). (b2) and (b3) use Ψ_code under the alternative and compare against Ψ_code at the shipped settings.
- Criterion (iii) in Q3 counts sign flips relative to Ψ_code at the shipped settings.
- No criterion or threshold has otherwise changed.
