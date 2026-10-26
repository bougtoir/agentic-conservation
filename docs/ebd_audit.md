# Extinction-before-discovery audit

EBD is recorded only when a configured latent species becomes extinct before
description (stage 2). The denominator is the number of latent species; it is
zero-safe when latent species are disabled. Discovery does not continue after
true extinction, and policy decisions do not receive latent abundance before
description.

Boundary tests cover detectability 1, near-zero detectability, near-zero survey
cost, zero survey allocation, zero latent species, and removal of directional
and anthropogenic deterioration. In the registered runs, base mean EBD was
0.278; detectability-one mean EBD was
0.021; and near-zero-detectability mean EBD was
0.993. Replicate-level variation and discovery counts are retained
in `results/ebd_boundary_outcomes.csv`.

EBD is therefore an emergent stochastic endpoint rather than a fixed label.
Its magnitude remains conditional on synthetic discovery probabilities,
survey allocation, demography, and environmental stress.
