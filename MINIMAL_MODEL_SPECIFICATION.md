# MINIMAL MODEL SPECIFICATION

Companion executable: `src/agentic_conservation/minimal_model.py`.
Purpose: the smallest subsystem of the full IBM in which the S6
(habitat-first) vs S7 (hybrid/circulation) policy reversal can occur,
keeping identical parameter semantics, so a reversal condition can be
derived and then tested prospectively on the full model.

## Entities and state

- **Species**: every species in `config/species.json` is rolled forward
  independently (demographic density is species-local in the IBM —
  `simulation.py` line ~711 — so independent per-species rollouts share
  only environment and budget, matching the full model's coupling).
- **Cohorts per species**: known (movable) population `n_j` per node `j`,
  and a latent (undiscovered) population `ell` confined to the origin.
  `latent_fraction_proxy` marks the last `round(L * n_species)` species
  as latent, exactly as `run_simulation` does.
- **Environment**: node qualities `q_j` on all wild nodes; engagement
  `eta` driving budget `B_t = B0 * (0.82 + 0.24 eta_t)`.

## Per-year update (equation-to-code map)

| IBM equation | Minimal-model statement | Code site |
|---|---|---|
| E1 suitability | `s_j = q(0.72+0.28b) - spec(1-q)0.32` (+ captivity/migration terms on managed nodes) | `suitability()` |
| E2 survival | `1 - m*mu - (1-s)0.24 - anthro*sens*alpha*0.08 - (1-H)0.08 - inb*imb_pen (+ research 0.035 managed / - pred*pm*0.035 wild)` | `run_minimal_species` |
| E11/E12 births | `n * FEMALE_FRAC * (m+g)(0.5+f) s 5 (1-dens) [x (1+ex_b*exsitu/B_t) managed]` gated by `MIN_BREEDING_POP` | `run_minimal_species` |
| E14–E17 quality | `q <- clip(q - trend - climate_j(t) - E[hit] + habitat/B0 * e * restoration_j)` | quality loop |
| Engagement/budget | `eta <- clip(eta + coeff*(exposure + eng_share*0.2) + feedback*habitat_signal)`; `B_t = B0(0.82+0.24 eta)` | engagement block |
| Detection (EBD-lite) | `p_detect = min(0.60, bg + 0.06*survey/cost + habitat/1000)` | detection block |
| Movement (Alg. 2) | `quota_t = max(1, floor(cap_t / N_atrisk(t)))`; moved pay `tau` + transit-infection hit | move block |
| Target rule | argmax of suitability − 0.04 cost + 0.08 research + 0.08 restoration (+ origin fidelity 0.2) | `s7_target()` |

## Approximations (stated, with role)

1. **Mean-field constants**: `HEALTH = 0.70`, `INBREEDING = 0.08`,
   `FEMALE_FRAC = 0.25` replace stochastic per-agent draws.
2. **Mate-limitation proxy**: recruitment at a node is zero below
   `MIN_BREEDING_POP = 8` residents. This is the one fitted constant —
   chosen on the 125 development sweep cells (accuracy rose 0.61→0.90
   over candidates {2,4,6,8,12,20}) then frozen before holdout. It
   encodes the IBM's co-located mature female+male requirement that a
   dribble of 1–2 relocated individuals per year cannot satisfy.
3. **Shared rescue capacity**: IBM `cap = floor(rescue_spend/2.5)` is a
   TOTAL across species allocated in risk order; the minimal model uses
   an equal-share quota `cap_t // N_atrisk(t)` with `N_atrisk` from an
   environment-only pre-pass.
4. **Quasi-stationary infection**: endogenous prevalence is ~0 at every
   node (node.disease 0.07–0.14 < recovery 0.32), so only the transit
   infection term is kept: moved individuals lose `infect_p * 0.14`
   survival where `infect_p = d_risk (1 - coverage * quar_eff)` and
   `coverage = min(1, rescue_spend / (moves * quar_cost))`.
5. **Catastrophes**: quality hits only (as in the IBM), folded into an
   expected per-node drift `c * E[U(0.16,0.38)] / n_wild`.
6. **Metric**: `survival = mean_i n_i(T) / (n_i(T) + 0.05 n_i(0))`, a
   smoothed extant indicator mirroring `survival_100`.

## Deterministic limiting-case behaviour (tested)

- `habitat_deterioration=0`, stationary scenario, high protection
  efficiency → `Psi < 0` (habitat policy wins).
- Large `habitat_deterioration` + `climate_velocity` → `Psi > 0`.
- `latent_fraction_proxy -> 1` → circulation channel → 0, `Psi <= 0`.
- `movement_disabled=True` → circulation channel exactly 0.
- `relocation_mortality -> 1` → circulation channel negative.

## What the minimal model is NOT

Not a stochastic IBM (no seed variance, no finite-population noise), not
a species-interaction model (no shared density across species), not an
observation model (detection is a smooth rate). It is a **predictor**:
`Psi = log( M_S7 / M_S6 )` with `M` the pseudo-extant fraction;
predict S7 preferred iff `Psi > 0`.
