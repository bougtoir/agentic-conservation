# THEORY DERIVATION — a mechanistic condition for the S6/S7 reversal

Status: derivation + transparent approximation. The full condition is
evaluated numerically by the deterministic minimal model
(`minimal_model.py`); the closed-form expressions below expose what the
condition *is* and which quantities it needs — all measurable before
running the full policy comparison.

## 1. Setup

Per-capita annual growth multiplier of species i at node j
(mean-field of E1+E2+E11/E12):

    g_j(s) = surv_j(s) + b_j(s)
    surv_j = 1 - m mu - (1 - s) 0.24 - a_j sens alpha 0.08
             - (1 - H) 0.08 - inb imb_pen
             + (managed: research_j 0.035 | wild: - pred_j pm 0.035)
    b_j    = FF (m + g)(0.5 + f) s 5 (1 - n_j/K_j) (1 + ex_b e_j/B_t)
             [managed only] * 1[n_j >= B*]

with `s = s(q) = q(0.72+0.28b_i) - spec_i(1-q)0.32` (E1) and `B* = 8`
the co-located mate-availability proxy (fitted on dev, frozen).

Origin quality trajectory under allocation share h (E14–E17,
deterministic part):

    q_O(t) ≈ q_O(0) + rho(h) t - kappa t^2,
    rho(h) = h e r_O - delta - e_hit,   kappa = chi / (2T)

where `e` = habitat_protection_efficiency, `r_O` = origin restoration
response, `delta` = deterioration trend, `chi` = climate_velocity,
`e_hit` = expected catastrophe drift. **The whole S6-vs-S7 habitat
difference enters through rho(h_S6) - rho(h_S7) = (0.68-0.35) e r_O.**

## 2. The marginal circulation condition (non-tautological)

For one at-risk individual relocated at year t, the expected
next-year contribution to population is

    circ_payoff(t) = (1 - tau)(1 - phi_d) g_A(s_A(t)) - g_O(s_O(t))

where `tau` = relocation mortality, `phi_d` = effective transit
infection burden `d_risk (1 - coverage quar_eff) * 0.14`. Circulation
pays at the margin iff `circ_payoff(t) > 0`. This is a condition on
**measurable pre-simulation quantities** — node qualities/suitabilities,
transit hazard, breeding and mortality parameters — not a restatement
of `survival_S7 > survival_S6`.

## 3. The package condition (what S7-vs-S6 actually is)

S7 is not "circulation" — it is a budget bundle. Write

    Psi = log M(S7) - log M(S6) = H + C (+ I)

    H = log M(S7-alloc, no-move) - log M(S6-alloc)        <= 0 always
    C = log M(S7-alloc, move)    - log M(S7-alloc, no-move)
    I = residual interaction (reported separately)

Predict a reversal iff `Psi > 0`, i.e. `C > -H`. Each channel maps to
interpretable leverage terms:

    C ≈ sum_i w_i * C_res_i * [ (1-tau)(1-phi_d) g_Ai - g_Oi ] * T_eff
        - mu_i   (mate-limitation discount: relocated dribbles cannot
                  breed below B* residents)
    H ≈ sum_i w_i * (h_S7 - h_S6) e r_O * (d g_Oi / d q_O)|borderline * T_eff
        <= 0
    latent penalty: species with known=0 contribute 0 to C under any
        allocation; under S7-alloc their origin persists only if
        rho(h_S7) >= 0 — an additive penalty absorbed into H.

Dimensionless ratios carrying the condition:

    R1 = (1 - tau)(1 - phi_d) g_A / g_O       (transit-adjusted target/origin fitness)
    R2 = C_res * T_eff / n0                   (rescuable fraction of the population)
    R3 = (h_S6 - h_S7) e r_O T / q_O(0)       (relative quality foregone)

`Psi > 0` empirically coincides with R1 > 1 AND R2 large enough that
rescue volume beats the R3 habitat loss; the deterministic model
evaluates the exact balance.

## 4. Interactions, finiteness, uncertainty

- **Non-additivity**: C depends on S7's habitat share (at-risk
  threshold s_O < 0.58 is reached sooner under weaker restoration) —
  C and H are not independent; the factorial design separates them
  (POLICY_ATTRIBUTION_AUDIT.md).
- **Finite horizon**: T_eff = time remaining once s_O(t) < 0.58; late
  onset makes dribble relocation useless (B* never reached) — the
  horizon enters through T_eff, not through T directly.
- **Demographic stochasticity**: the IBM's species-level survival is
  bimodal (paired seeds show 0 vs 0.875); the deterministic model
  tracks the median path. Boundary cells are therefore expected to
  disagree — the gate measures whether misses cluster systematically.
- **Uncertainty in Psi**: none at the model level (deterministic);
  the honest uncertainty statement is the holdout error rate, not a
  posterior on parameters.

## 5. Validity domain and counterexamples (expected)

Valid where the reversal is driven by origin degradation vs target
refuge: deterioration, climate, relocation-hazard axes (dev accuracy
0.84–0.92). Expected failures, i.e. documented boundary cases:

- `latent_fraction -> 1`: all species unmovable → C -> 0 → S6; the
  model handles this but detection-rate timing makes the boundary soft.
- Very high `relocation_mortality`: R1 < 1, S6.
- Efficient restoration (`e` large): rho(h_S6) >> 0, origin saved
  outright, S6 — and H→0 fast because M saturates at 1.
- Stable origin (stationary, delta = 0): no at-risk trigger, C = 0, S6.
- Captivity/ex-situ sweeps: reversal driven by the ex-situ channel in
  the allocation bundle, partially inside H — reported as a
  bundle-vs-circulation attribution issue, not a theory failure per se.

If an exact closed-form Psi were possible it would still be
approximate; the evaluated object is the deterministic model itself,
whose remainder vs the IBM is quantified by the holdout hit rate.
