# Monte Carlo convergence audit

The audit uses nested paired prefixes at N=24, 48, 96, 192, and 384.
It reports Monte Carlo standard errors, replicate percentile intervals,
changes from the N=384 estimate, and sign stability. Percentile intervals
describe simulated outcome distributions, not empirical confidence intervals.

At N=384, the paired S7-S6 survival contrast was
-0.0573 with Monte Carlo SE 0.0158. Full endpoint
results are in `results/convergence_audit.csv`; paired current-state information
effects are in `results/information_convergence.csv`.

For every registered S6, S7, and paired S7-S6 endpoint, the N=192 estimate was
within two N=192 Monte Carlo standard errors of the N=384 estimate and
the qualitative sign was stable. The N=192 current-state-information effects
also met that criterion; their intervals span zero, so the supported
conclusion is negligible or uncertain effect rather than a directional
benefit. The production count of 192 is therefore sufficient for the reported
point estimates and qualitative conclusions. N=384 is retained as a
convergence audit and does not replace the production analysis.
