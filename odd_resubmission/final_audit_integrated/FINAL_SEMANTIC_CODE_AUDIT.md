# FINAL SEMANTIC CODE AUDIT (integrated, appendix-free version)

Scope: code that turns preserved outputs into the numbers, tables, figures
and sentences that are new or moved in this version. The model code
(`simulation.py`, `minimal_model.py`, `analysis.py`), configuration and all
registries are unchanged (QC: no modified or deleted file in protected paths
against the branch base). No simulation was run.

| # | Item | Estimand / quantity | Source → output → text | Direction, units, aggregation, denominator | Uncertainty | Verdict |
|---|---|---|---|---|---|---|
| 1 | Table 10 point values | Mean over 12 paired seeds of survival_100 (proportion of 8 species retained at year 100), fraction_ebd (latent species extinct before discovery / latent species, 0 when none), mean_individual_welfare (0–1) per design × policy | `tables/table7_robustness.csv` (= means of `results/ablations.csv`, `results/adverse_conditions.csv`; max abs. difference 5.6e-17) → `_robustness_frame` → Table 10 | Proportions; mean over seeds; denominators 8 species and latent count (`simulation.py` line 993, `max(latent_count, 1)`) | none in canonical table | PASS; all 45 × 3 values shown, rounded to 3 decimals |
| 2 | Table 10 S7 − S6 column | Paired difference of survival_100, S7 minus S6, same seed | per-seed records, pivot on (design, seed) | Sign: positive = S7 higher. Checked against canonical means (difference of means = mean of differences) | SE = SD of 12 paired differences / √12 (new derived quantity, labelled in the note) | PASS |
| 3 | "only 4 of 15 exceed 2 paired SE" | Count of designs with |diff| > 2 SE | derived from item 2 | disease (+0.188, SE 0.078), efficient_restoration (−0.115, 0.024), excellent_origin (−0.135, 0.036), high_relocation_harm (−0.260, 0.066) | 2-SE rule matches the determinate rule used elsewhere | PASS; this weakens the previous wording ("S6 kept a clear advantage", "disease and engagement feedbacks reverse it"), which was corrected in the manuscript and cover letter |
| 4 | Table 9 LHS profile | Spearman correlation across 128 design means (4 replicates each) between a sampled parameter and an outcome, per policy | `results/sensitivity_associations.csv` → `tables/table4_sensitivity.csv` → `_lhs_frame` (top 2 by |ρ|) | Signed ρ; per policy | none (descriptive) | PASS; text claim "strongest association is deterioration or protection efficiency for persistence, welfare, future option" is enforced by an assertion in the generator |
| 5 | Interaction screen text | Correlation of outcome-rank residual with residual of the product of two parameter ranks after removing both main effects (`analysis.py` lines 419–446) | `results/sensitivity_interactions.csv` (792 rows) | 66 pairs × 12 policy–outcome; max |score| 0.309 | none; called exploratory, not a test | PASS |
| 6 | Alternative weights sentence | Paired perfect-current-state minus S7 effect on the utility index under each weight vector | `tables/table8_information_weight_sensitivity.csv` | estimate range −0.0063 to +0.0009 over five alternatives; "lower/upper" are 2.5/97.5% replicate quantiles (`analysis.py` lines 172–174), MC half-width separately | max MC half-width 0.016; n = 192 | PASS; wording "no detectable improvement under this rule and model specification", not "zero value" |
| 7 | Table 11 historical baselines | Sign agreement of B0 (always S6), B1, B2 with observed sign | `results/reversal/holdout_metrics.csv` (`obs_sign`, `pred_B1`, `pred_B2`) | determinate accuracy over 26 determinate cells; all-cell over 56 | B0 regret from canonical table (0.084, 3 decimals as stored); B1/B2 regret not computed historically, shown "—" | PASS; canonical B0 determinate accuracy 0.0 is a literal in `scripts/build_outputs.py` and is wrong (0.346); not edited, documented in the crosswalk |
| 8 | Table 11 prospective rows | Determinate accuracy with Wilson 95% (z = 1.96), all-cell accuracy, regret, best fixed-policy regret | `results/psi_confirmatory/metrics.csv` | 33/34; 0.971 [0.851, 0.995]; 0.550; 0.0095 vs 0.0759 | Wilson as frozen | PASS; unchanged from the previous version |
| 9 | Figure 1 | Schematic; movement targets | `_target_node` sets score[8] (biobank) to −1; S2/S3/S6 targets zoo/origin; biobank coverage from budget (`simulation.py` lines 821–835) | — | — | PASS after correction (no arrow into the biobank) |
| 10 | Figure 4 caption | Single replicate | `results/trajectories.csv` has one seed (314159) | — | — | PASS after correction (previous caption said "mean") |
| 11 | Figure 9 | V0 Ψ vs observed contrast | `holdout_metrics.csv` Ψ equals stored `holdout_psi.csv` (max diff 3.6e-15); colours by `obs_sign` | determinate = |mean| > 2 MC SE | — | PASS; "frozen before holdout" note removed |
| 12 | Figure 7, 10 captions | Cell means, 8 paired replicates per cell | `results/threshold_sweeps.csv` (min group size 8) | Figure 10: S7, latent_survey sweep | — | PASS |
| 13 | Seeds and partitions | Base 192 paired seeds; held-out 56 cells × 12; prospective 60 cells × 12 untouched seeds | unchanged registries | — | — | PASS; nothing re-run |
| 14 | Equations | Same symbols and coefficients | linear strings unchanged; rendered as structured OMML with sub/superscripts; long equations split at top-level operators; `clip(argument; lo, hi)` written with an auxiliary z for the unclipped argument (Eqs. 1, 2, 6); "~" written as "∼" | — | — | PASS; presentation only, no change in mathematics |

Consistency of numbers that did not change: `scripts/final_numeric_audit.py`
(independent recomputation of Q1–Q3, historical V0 Ψ and prospective Ψ):
157/157 checks match, both in the working tree and in a clean clone of the
public release tag.
