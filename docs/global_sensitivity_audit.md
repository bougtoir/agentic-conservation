# Global sensitivity audit

The production design uses 128 stratified Latin-hypercube points and
4 stochastic replicates per point for S4, S6, and S7. Replicates
are averaged before association analysis, preventing a repeated parameter row
from being treated as an independent design.

Main effects are descriptive Spearman rank associations. Pairwise interactions
are descriptive partial rank associations between the outcome residual and
the product of two rank-standardized inputs after removing their two main
effects. They are screening statistics, not causal effects or significance
tests. Morris screening was not added because it would require a separate
trajectory design while providing less direct information about the requested
pairwise interactions.

## Registered ranges

- `habitat_deterioration`: uniform Latin-hypercube range [0, 0.025]
- `climate_velocity`: uniform Latin-hypercube range [0, 0.05]
- `relocation_mortality`: uniform Latin-hypercube range [0, 0.2]
- `relocation_stress`: uniform Latin-hypercube range [0, 0.55]
- `ex_situ_breeding_benefit`: uniform Latin-hypercube range [0, 0.55]
- `release_survival_penalty`: uniform Latin-hypercube range [0, 0.3]
- `movement_disease_risk`: uniform Latin-hypercube range [0, 0.4]
- `captivity_welfare_penalty`: uniform Latin-hypercube range [0, 0.5]
- `survey_cost`: uniform Latin-hypercube range [0.5, 60]
- `engagement_coefficient`: uniform Latin-hypercube range [-0.12, 0.24]
- `initial_budget`: uniform Latin-hypercube range [30, 220]
- `habitat_protection_efficiency`: uniform Latin-hypercube range [0.005, 0.08]

## Strongest absolute interaction screens

- S4 mean_individual_welfare: `ex_situ_breeding_benefit` × `habitat_protection_efficiency` = -0.309
- S4 mean_individual_welfare: `release_survival_penalty` × `engagement_coefficient` = -0.277
- S7 mean_individual_welfare: `release_survival_penalty` × `engagement_coefficient` = -0.270
- S7 fraction_ebd: `climate_velocity` × `initial_budget` = 0.259
- S7 mean_individual_welfare: `habitat_deterioration` × `initial_budget` = 0.254
- S7 survival_100: `survey_cost` × `habitat_protection_efficiency` = -0.254
- S6 fraction_ebd: `climate_velocity` × `initial_budget` = 0.250
- S7 future_option_value: `survey_cost` × `habitat_protection_efficiency` = -0.243
- S4 survival_100: `relocation_mortality` × `engagement_coefficient` = 0.242
- S7 fraction_ebd: `habitat_deterioration` × `survey_cost` = 0.241
- S6 fraction_ebd: `relocation_mortality` × `captivity_welfare_penalty` = -0.235
- S7 survival_100: `relocation_mortality` × `engagement_coefficient` = 0.232

Complete main-effect and interaction results are stored in
`results/sensitivity_associations.csv` and
`results/sensitivity_interactions.csv`.
