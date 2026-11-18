# APPENDIX ELIMINATION CROSSWALK

Scope: the inline-figure, appendix-free version of the ODD 2020 revision
(new submission referring to ECOMOD-26-2231). The former Appendix A
(`odd_resubmission/submission/EM_ODD_APPENDIX_A_FINAL.docx`, built by the
previous generator) is not part of the new package. It stays unchanged in the
repository and in release tag `odd-2020-revision-v2` as the predecessor
version. No `EM_ODD_APPENDIX_A_FINAL.docx` is produced by the current
generator.

## Former appendix tables

| Former | Content | Canonical source (unchanged) | Where it is now | What the reader sees in the article |
|---|---|---|---|---|
| A1 | Latin-hypercube Spearman rank correlations, 12 parameters × 4 outcomes × 3 policies (144 rows) | `tables/table4_sensitivity.csv` (from `results/sensitivity_associations.csv`) | Section 2.8 (design), Section 3.5 text and **Table 9** | Definition of the quantity (Spearman correlation across 128 designs × 4 replicates between a sampled parameter and the design-mean outcome, per policy); the two strongest associations for every outcome × policy with their coefficients; label "descriptive sensitivity profiles, not calibrated or causal effects". Complete 144-row table in the repository. |
| A2 | Partial-rank interaction screen, three strongest pairs per policy × outcome (36 rows) | `tables/table4_sensitivity_interactions.csv`; all 792 scores in `results/sensitivity_interactions.csv` | Section 3.5 text | Definition of the score, number of scores (66 pairs × 12 policy–outcome combinations = 792), largest absolute score with its terms (−0.309, ex_situ_breeding_benefit × habitat_protection_efficiency, S4, mean_individual_welfare), and the statement that it is an exploratory screen, not a significance test or mechanistic proof. |
| A3 | Ablation and adverse-condition outcomes (45 rows: 15 designs × S4/S6/S7; survival_100, fraction_ebd, mean_individual_welfare) | `tables/table7_robustness.csv`; per-seed records `results/ablations.csv`, `results/adverse_conditions.csv` | **Table 10** (landscape section, two-row header, repeated header rows) and Section 3.5 text | All 45 rows × 3 outcomes, rounded to three decimals, with design labels and the parameter change of each design read from `ABLATIONS`/`ADVERSE` in `analysis.py`. Added column: S7 − S6 survival with paired SE computed from the per-seed records (new derived quantity; flagged in the table note). The text states that only 4 of 15 differences exceed 2 paired SE (disease ablation; efficient_restoration, excellent_origin, high_relocation_harm). |
| A4 | Perfect-current-state information effect under six weight vectors | `tables/table8_information_weight_sensitivity.csv` | Section 3.7 text (new paragraph); Limitations sentence updated | Range of the five alternative-weight effects (−0.0063 to +0.0009), maximum Monte Carlo half-width (0.016), 192 paired seeds, every replicate interval contains zero; wording "no detectable improvement under this rule and model specification; not evidence that information has zero value". Full weight vectors in the repository. |
| A5 | Historical (V0) held-out Ψ performance and baselines B0–B2 | `tables/table9_reversal_predictors.csv`; per-cell record `results/reversal/holdout_metrics.csv` | **Table 11** (three added historical-baseline rows and a table note) and Section 3.6 text | Historical V0 row (0.846 determinate, 0.393 all-cell, regret 0.0450), V1 same-cell row (exploratory), prospective rows (0.971 [0.851, 0.995], 33/34; all-cell 0.550; regret 0.0095 vs 0.0759/0.0807), and B0–B2 recomputed from the per-cell record. |
| A6 (already moved earlier) | GBIF coverage aggregates | `tables/table5_empirical_coverage.csv` | Repository; cited in Section 2.6 and the Data availability statement | Context only, not calibration or validation. |
| A7 (already moved earlier) | Bibliographic evidence levels | `tables/table6_empirical_evidence.csv` | Repository; cited in Section 2.6 and the Data availability statement | Context only. |

## Discrepancy found while integrating A5

`tables/table9_reversal_predictors.csv` lists B0 (always-S6) determinate
accuracy as 0.0. The per-cell record gives 9 of 26 determinate held-out cells
with S6 higher, so always-S6 is correct in 0.346 of determinate cells. The
value 0.0 is a literal in `scripts/build_outputs.py` (`"determinate_accuracy":
0.0`), not a computed value. The canonical table was not edited. Table 11
reports the value recomputed from `results/reversal/holdout_metrics.csv`
(0.346), and the all-cell value (0.161) agrees with the canonical table. This
discrepancy concerns a historical comparator only; it does not change any Ψ
result.

## Table numbering, previous version → this version

| Previous (with Appendix) | This version | Content |
|---|---|---|
| Table 1 | Table 1 | Evaluation patterns |
| Table 2 | Table 2 | Entities and state variables |
| Table 3 | Table 3 | Base parameter values (now also cited in Section 2.2 before it appears) |
| Table 4 | Table 4 | Policies and allocation shares |
| Table 5 | Table 5 | Base-scenario policy outcomes |
| Table 6 | Table 6 | Q1 endpoints |
| Table 7 | Table 7 | Q2 climate trajectories |
| Table 8 | Table 8 | Q3 coefficient perturbations |
| Appendix Table A1 | Table 9 (summary) | Latin-hypercube profile |
| Appendix Table A3 | Table 10 | Ablations and adverse conditions |
| Table 9 | Table 11 | Predictive performance of Ψ (now with historical baselines, former A5) |
| Appendix Tables A2, A4 | text of Sections 3.5 and 3.7 | Interaction screen; alternative weights |

Numbers are assigned by the generator in order of first citation; the QC
script confirms that tables are cited in order 1–11 and each is cited before
it appears.

## Figure numbering

Unchanged (Figures 1–10, numbered by first citation). Two figure files were
replaced by corrected variants generated from the same data
(`scripts/make_odd_figures.py`); the original files are unchanged:

| Figure | Previous file | Current file | Reason |
|---|---|---|---|
| 1 | `figures/fig1_conservation_network.png` | `figures/odd/fig1_network_living_nodes.png` | The previous schematic drew movement arrows into the biobank. In the model the biobank is never a movement target (`_target_node` sets its score to −1; it accumulates coverage from budget, `simulation.py`). The new version draws movement arrows only among living-animal nodes and labels the biobank "stored genetic material; no animals". |
| 9 | `figures/fig10_reversal_psi.png` | `figures/odd/fig_psi_historical_v0.png` | The previous plot carried the in-figure note "Psi frozen before holdout", which contradicts the withdrawn frozen-model claim (Section 2.10.2), and its legend did not explain red points. Same data (`results/reversal/holdout_metrics.csv`, V0 Ψ = stored `holdout_psi.csv`, max difference 3.6e-15); new title "Historical held-out evaluation of Ψ (implementation V0)" and a three-entry legend. |

Caption corrections without changes to the image: Figure 4 is a single
replicate (seed 314159), not a mean trajectory as the previous caption said;
Figure 7 shows two of the five sweeps and colour shows cell means only;
Figure 10 is S7 only and the zero-latent column is recorded as 0.
