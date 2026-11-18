# FINAL INLINE FIGURE CONTENT REVIEW

Each embedded image was viewed at full resolution and compared with its
caption, its generating code and its data. Placement data (page, inline
shape, aspect ratio, caption adjacency, first citation) are in
FINAL_INLINE_FIGURE_QC.md.

| Fig. | File (embedded unchanged) | First cited | PDF page | What the image shows | Caption check | Generator / data |
|---|---|---|---|---|---|---|
| 1 | figures/odd/fig1_network_living_nodes.png (new variant) | 2.2 | 6 | Nine nodes; wild (green), managed (blue), semi-wild green on the managed side, biobank purple dashed "stored genetic material; no animals"; movement arrows only among living-animal nodes | Matches; states that the biobank never holds or receives animals and that arrows are example pathways (any living-animal node can be a target) | `scripts/make_odd_figures.py::network_figure`; `config/nodes.json`; rule in `simulation.py::_target_node` (biobank score −1) |
| 2 | figures/fig7_partial_observation_architecture.png | 2.4 Sensing | 10 | True state → observed state (noise, one-year delay, undetected species) → action → outcomes; oracle replaces O with X | Matches; `observation_delay` = 1 in `config/base.json` | `scripts/build_outputs.py::_figure_observation_architecture` (schematic) |
| 3 | figures/fig9_origin_future_optimum.png | 2.7.1 | 12 | Mean suitability of origin vs alternative habitat, deterministic directional component; crossing marked | Matches; caption no longer hard-codes the crossing year | `_figure_origin_future` |
| 4 | figures/fig2_century_trajectories.png | 3.1 | 23 | Species retained and living individuals for the eight policies | Corrected: one replicate (seed 314159), not means; points to Table 5 for means | `results/trajectories.csv` (one seed) |
| 5 | figures/fig3_pareto_outcomes.png | 3.1 | 24 | Cost vs survival; circles non-dominated, crosses S2 and S5; size = welfare | Matches; dominated set read from `results/pareto_front.csv` | `_figure_pareto` |
| 6 | figures/fig6_objective_tradeoffs.png | 3.1 | 25 | Min–max normalised means on six objectives; EBD and cost reversed | Matches; S0 = 1 on cost efficiency explained | `_figure_tradeoffs` |
| 7 | figures/fig4_policy_reversal_thresholds.png | 3.2 | 26 | Two sweeps (deterioration × relocation stress; captivity penalty × breeding benefit), S7 − S6 cell means | Corrected: two of five sweeps; 8 replicates per cell; colour = mean only, per-panel scale | `_figure_thresholds`; `results/threshold_sweeps.csv` |
| 8 | figures/odd/fig_q2_climate_forms.png | 3.4 | 28 | (a) cumulative displacement, legend with cumulative exposure 20.6/30.6/40.6/30.9; (b) S7 − S6 ± 2 SE | Matches Table 7 values (−0.055, +0.104, +0.248, +0.389); step = one-year pulse at year 50 | `scripts/make_odd_figures.py::climate_forms_figure` (file not regenerated) |
| 9 | figures/odd/fig_psi_historical_v0.png (new variant) | 3.6 | 34 | V0 Ψ (symlog) vs observed S7 − S6 in 56 held-out cells; blue/red determinate, grey crosses indeterminate | Matches; labelled historical V0, not confirmatory; former in-figure "Psi frozen before holdout" removed | `psi_historical_figure`; `results/reversal/holdout_metrics.csv` (Ψ = stored holdout Ψ) |
| 10 | figures/fig5_extinction_before_discovery.png | 3.7 | 36 | S7 fraction EBD over latent fraction × survey cost | Corrected: S7 only; 8 replicates per cell; zero-latent column recorded as 0 | `_figure_latent_survey` |

No plotted value or axis label of an existing figure file was changed; the
two new variants reuse the same data and differ only in the elements listed.
Text legibility at the embedded width (6.3 in) was checked in the PDF.
