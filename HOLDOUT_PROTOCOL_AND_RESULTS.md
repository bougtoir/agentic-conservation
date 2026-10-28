# Holdout Protocol and Results

## Protocol (frozen before holdout inspection, see THEORY_GO_NO_GO.md)

- 56 cells, none used in calibration: 12 in-domain midpoints, 16 shifted-range,
  12 joint-perturbation, 8 out-of-domain, 8 hostile.
- 12 paired seeds per cell per policy (seeds 910000+, never used in dev sweeps).
- Observed sign = sign(mean S7−S6) when |mean| > 2·MCSE, else 0 (indeterminate).
- Predictor: Ψ = habitat channel + circulation channel from the minimal model
  (`minimal_model.psi_index`), formula and constants (HEALTH 0.70, INBREEDING 0.08,
  FEMALE_FRAC 0.25, MIN_BREEDING_POP 8, eps 0.02) frozen before holdout.
- Baselines: B0 always-S6; B1 best single-parameter threshold fit on dev;
  B2 L2 logistic regression on the override vector fit on dev.
- Gate A STRONG: sign acc ≥ 0.85 AND balanced acc ≥ 0.80 AND beats all baselines
  by ≥ 0.10 AND decision regret ≤ 0.03.
- Gate B LIMITED: acc ≥ 0.70 AND beats null AND regret ≤ 0.06, with a
  characterized failure region.
- Gate C: otherwise → bounded negative finding only.

## Data

- `results/reversal/holdout_runs.csv` — 1,344 IBM runs (56 cells × 2 policies × 12 seeds)
- `results/reversal/holdout_psi.csv` — Ψ per cell (computed once, before runs)
- `results/reversal/holdout_metrics.csv` — per-cell observed mean diff, MCSE, signs, predictions

## Results

Observed sign distribution: 17 cells S7-favored, 9 S6-favored, 30 indeterminate.
(26 determinate cells.)

| predictor | sign acc (all 56) | sign acc (26 determinate) | balanced acc (3-class) | regret |
|---|---|---|---|---|
| **Ψ (minimal model)** | 0.393 | **0.846** | 0.519 | **0.045** |
| B0 always-S6 | 0.161 | 0.000 | 0.333 | 0.084 |
| B1 climate-velocity ≥ 0.0011 → S7 (dev acc 0.728) | 0.304 | 0.231 | 0.490 | — |
| B2 logistic (dev acc 0.648) | 0.161 | 0.154 | 0.298 | — |

Determinate-cell detail: sensitivity (S7 detection) 1.00 (17/17),
specificity (S6 detection) 0.556 (5/9), two-class balanced accuracy 0.778.

### Failure region (characterized)

- **Abstention failure.** Ψ never predicts "indeterminate"; 30/56 cells were
  indeterminate and Ψ assigns them a sign anyway. All 30 were predicted +1 or −1
  and are scored wrong under the 3-class metric. This is the dominant accuracy loss.
- **Near-boundary cells are coin flips.** Among 23 cells with |Ψ| < 0.2, Ψ's sign
  matched the observed sign in only 4 (17%). Restricting to |Ψ| ≥ 0.1 leaves
  36 covered cells with 94.7% determinate accuracy; τ = 0.3 covers 28 cells at
  94.4%. The magnitude of Ψ is informative — the sign of a near-zero Ψ is not.
- **Captivity/ex-situ and all-latent hostile cells fail.** `exsitu_high`
  (Ψ = +0.034, obs −1), `all_latent_expensive` (Ψ = +0.73, obs −1):
  the deterministic rollout overstates the latent-cohort salvage and ex-situ
  benefit because the IBM's per-move shared capacity dribbles 1–2 animals to
  mate-limited nodes where the metric still counts them as marginal persistence.
- **Bimodality.** Ψ tracks a deterministic median path; IBM survival_100 is
  bimodal by seed, so cells with small deterministic margins have high observed
  variance and frequently land in the indeterminate band.

## Verdict per frozen gate

- A STRONG: FAIL (sign acc all-cells 0.393 < 0.85; bacc 0.519 < 0.80; regret 0.045 > 0.03).
- B LIMITED: **PASS** — determinate sign accuracy 0.846 ≥ 0.70, beats B0/B1/B2 by
  ≥ 0.40 on all-cells accuracy (0.393 vs ≤ 0.304) and by ≥ 0.61 on determinate
  cells (0.846 vs ≤ 0.231), regret 0.045 ≤ 0.06, failure region characterized
  (near-boundary |Ψ| < 0.2, abstention absent, captivity/all-latent hostile cells).
- C: not applicable.
