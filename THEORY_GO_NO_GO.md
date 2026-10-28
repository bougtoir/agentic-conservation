# THEORY GO/NO-GO GATE — FROZEN BEFORE HOLDOUT INSPECTION

Date frozen: 2026-10-27. Branch: devin/1793300000-reversal-theory.
Baseline: df40a91fd3efd2d2cd6604c60fea4d83225a759f (merge of PR #733).

This file is written BEFORE any holdout configuration is run. The
acceptance criteria below are the contract for the final verdict.

## Frozen theory artifacts

- Minimal model: `src/agentic_conservation/minimal_model.py`
  (per-species deterministic mean-field; E1/E2/E11/E12/E14–E17 semantics;
  shared rescue capacity; mate-limitation proxy; latent cohort; engagement
  budget feedback).
- Derived condition index: `Psi = log( M_S7-rule / M_S6-rule )` where
  M = fraction of pseudo-cohorts extant at T (IBM survival_100 analog).
  Channels: habitat_channel (S7-budget no-move vs S6-budget) and
  circulation_channel (S7-budget move vs no-move).
- Frozen nuisance constant: `MIN_BREEDING_POP = 8`
  (co-located mate availability proxy; selected on the 125 development
  sweep cells, then FROZEN — never retuned on holdout data).
- Frozen decision rule: predict "S7 preferred" iff `Psi > theta_0 = 0`,
  else "S6 preferred". Theta was NOT tuned on dev (theta_0 = 0 a priori).
- Dev-set performance (125 sweep cells, informational only):
  sign accuracy 0.896; per-sweep 0.84–0.96.

## Holdout design (frozen)

56 new configurations, none of which appear in the dev sweep grid:

- 12 in-domain: interior midpoints of existing sweep grids.
- 16 shifted-domain: parameter values beyond dev ranges
  (deterioration 0.030–0.038, relocation_mortality 0.30–0.45,
  climate_velocity 0.055–0.070, ex_situ_benefit 0.70–0.90,
  captivity_penalty 0.65–0.80, latent_fraction 0.70–0.85,
  survey_cost 80–100, engagement -0.25–0.35,
  protection_efficiency 0.10–0.14, relocation_stress 0.70–0.90).
- 12 joint/interaction: 2–3 parameter combinations not separable into
  any single dev sweep axis.
- 8 out-of-domain: scenario=rapid_deterioration, years in {50, 150},
  mortality_multiplier 1.5, origin_quality_override 0.45,
  initial_budget 60, catastrophe_probability 0.08,
  slow_deterioration + climate 0.04, predation_multiplier 3.0.
- 8 hostile: stable origin (stationary, d=0, c=0); relocation_mortality
  0.50 + disease risk 0.20; protection_efficiency 0.15 + det 0.01;
  ex_situ_benefit 0 + relocation mortality 0.02; latent 0.90 + survey
  cost 100; engagement -0.30 + captivity 0.60; predation_multiplier 3.0;
  anthropogenic_multiplier 2.0.

Replicates: 12 seeds per config per policy (paired across policies).
Estimator: mean S7 − S6 on survival_100 with MC SE; a cell's actual sign
is +1 if mean > +2 MCSE, -1 if mean < -2 MCSE, else 0 (indeterminate).
Primary sign-evaluation uses robust cells (|mean| > 2 MCSE);
indeterminate cells are reported but excluded from accuracy denominators.

## Baselines (fit on dev only, frozen)

- B0 null rule: always predict S6 (dev-majority sign).
- B1 single-parameter threshold: the parameter+threshold pair that
  maximizes dev sign accuracy (exhaustive search over swept params).
- B2 logistic surrogate: L2 logistic regression on the full override
  vector (standardized), fit on dev cells only.

## Acceptance criteria

- **Gate A — STRONG THEORY**: on robust holdout cells, sign accuracy
  >= 0.85 AND balanced accuracy >= 0.80 AND Psi beats every baseline by
  >= 0.10 sign-accuracy points AND mean decision regret <= 0.03
  (regret = best-policy survival minus chosen-policy survival per cell).
- **Gate B — LIMITED THEORY**: sign accuracy >= 0.70 AND beats B0 (null)
  AND regret <= 0.06, with the failing region characterized (which
  sweeps/parameters break the condition). Mechanism ladder must identify
  at least one omission that accounts for a failure region.
- **Gate C — NO GENERAL REDUCTION**: otherwise. The reversal is reported
  as a parameter-sweep phenomenon without a portable mechanistic
  condition; the manuscript keeps its current claims plus a bounded
  negative finding.

## Attribution contract (Phase 4, frozen)

S7 − S6 is decomposed on dev cells via the factorial comparators
- total package contrast: S7 vs S6
- circulation main effect: (S6-alloc + S7-rule) vs S6
- allocation main effect: S7_NC (S7-alloc, no movement) vs S6
- interaction: (S7 vs S7_NC) vs (S6_C vs S6)

If |circulation effect| < |allocation effect| on the dev median, we do
NOT call S7–S6 a causal effect of circulation; we report a budget-bundle
effect instead. Labels used in reports: "total-package contrast",
"marginal circulation contrast", "allocation contrast", "interaction".

---

## Recorded verdict (post-holdout): B — LIMITED

Computed from `results/reversal/holdout_metrics.csv`:

| criterion | threshold | observed | pass |
|---|---|---|---|
| determinate sign accuracy | ≥ 0.70 | 0.846 (17 S7 + 5/9 S6 of 26) | yes |
| beats null (B0) | acc > B0 | 0.393 vs 0.161 all-cells; 0.846 vs 0.000 determinate | yes |
| beats B1/B2 | — | 0.304 / 0.161 all-cells | yes |
| decision regret | ≤ 0.06 | 0.045 | yes |
| failure region characterized | required | abstention absent; |Ψ|<0.2 coin-flip; captivity/all-latent hostile cells fail | yes |

Gate A failed on all three remaining criteria (sign acc 0.393 < 0.85,
3-class bacc 0.519 < 0.80, regret 0.045 > 0.03).

**Manuscript consequence**: Phase 9 integration is allowed only as a bounded
conditional claim — "the sign of strong S6↔S7 reversals is predicted by a
mechanistic two-channel index Ψ at ≈85% accuracy on determinate cells, with a
characterized near-boundary failure region; circulation alone does not cause the
S7–S6 difference (allocation shift dominates S6-favored cells)." The unqualified
"predictive theory" claim is not permitted. Negative/bounded-findings wording for
the abstention gap is required.
