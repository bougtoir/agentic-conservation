# Consequential modeling choices

- The tractable model uses vectorized individual agents and annual time steps.
  It is not an exact POMDP. Non-oracle policies use noisy abundance and delayed
  habitat observations; S7 uses a forward-rollout proxy and is compared with a
  current-state-information S7 alternative using the same action class. The
  comparison supplies true current abundance and quality, but not future
  environmental draws or realized outcomes, so the paired effect can be
  positive or negative and is not theoretical EVPI.
- Eight synthetic species (five initially known and three latent) and nine node
  types provide a transparent toy system. Synthetic labels are deliberately not
  mapped to real taxa.
- The fixed S0–S7 budget shares were specified before outcome generation and
  are not optimized to favor S7.
- Common seed sets pair policies. Policy-dependent state changes cause random
  streams to diverge after interventions, so the design is paired but not a
  mathematically perfect common-random-number coupling.
- The production replication count is fixed at 192 after a nested audit through
  384 paired replications; simulation error remains reported.
- Latin-hypercube sensitivity is used instead of Sobol because it is tractable
  without a large higher-order sampling design on the single VM.
- GBIF occurrence metadata are used only to assess empirical observation
  coverage and case-study reproducibility. They are not treated as abundance,
  demographic trend, or intervention-effect data.
