# Final Hostile Review — Reversal Theory

Adversarial self-review of the Ψ condition and its holdout evidence.

## Attacks attempted and survived

1. **"Ψ is circular — fitted on the same cells it predicts."** Partly defused:
   constants were calibrated on dev cells (125, excluded from holdout), formula and
   constants frozen before holdout. Dev accuracy 88.8% vs holdout determinate
   accuracy 84.6% — no catastrophic overfit, but the frozen constants carry dev-set
   information. Disclosed in MINIMAL_MODEL_SPECIFICATION.md.
2. **"Sign accuracy on determinate cells is cherry-picked."** The indeterminate
   class was defined ex ante by MCSE, not by prediction error; Ψ's inability to
   abstain is itself reported as the dominant failure (30/56 wrong). The
   alternative two-class metric is a *less* favorable framing for Ψ's specificity
   (0.556) and is reported alongside.
3. **"'benefits > costs' is not a theory."** The condition is written as
   Ψ = H + C with H, C explicit functions of pre-policy quantities (suitability
   trajectories, latent discovery time, shared capacity quota, mate limitation),
   not as a residual; the attribution audit shows the circulation channel cannot
   be replaced by a single-parameter threshold (B1 holdout acc 0.30).
4. **"The IBM runs you compare against used the same seeds/rng quirks."** Holdout
   seeds (910000+) are disjoint from dev seeds (900000+) and shared across
   policies (paired shocks). MCSE accounts only for seed variance; model-form
   error is unconstrained — acknowledged as a limitation (bimodal outcome →
   deterministic-median proxy).
5. **"Attribution pairing was lost by a script bug."** Disclosed; per-cell means
   are unbiased without pairing, but SEs for the factorial contrasts are wider
   than a paired design would give. Bug fixed for future runs
   (`scripts/run_reversal_theory.py` line 167).
6. **"Hostile cells were crafted to fail."** The 8 hostile cells were designed to
   break the theory (stable origins, movement harm, easy restoration, all-latent
   expensive, etc.); 2 of 8 were predicted correctly on sign, all failures are
   named in HOLDOUT_PROTOCOL_AND_RESULTS.md.

## Residual weaknesses (accepted, disclosed)

- No abstention mechanism: Ψ gives a sign everywhere; the |Ψ| ≥ 0.1 abstention
  rule (94.7% determinate accuracy) is post-hoc characterization, not part of the
  frozen formula.
- Deterministic rollout cannot represent the IBM's seed-level bimodality; the
  agreement metric inherits a ceiling.
- MIN_BREEDING_POP = 8 is a fitted constant; the ladder shows the boundary shifts
  with it (frac Ψ>0: 0.80 → 0.99 when removed).
- Mechanism transfers beyond the tested parameter families are unvalidated.
