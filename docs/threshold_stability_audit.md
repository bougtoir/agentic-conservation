# Two-factor threshold stability audit

All five prespecified sweeps use paired process-keyed seeds for S6 and S7.
Cell means and Monte Carlo standard errors are evaluated at nested replicate
prefixes 2, 4, 8. A direction is called
robust only when its sign is unchanged from N=4 to
N=8 and its absolute paired mean exceeds 1.96 Monte Carlo standard
errors. Other cells are classified as indeterminate rather than used to count
policy reversals.

- `captivity_breeding`: robust S7-higher cells 0/25, robust S6-higher cells 5/25, indeterminate cells 20/25; 20/25 raw signs stable from N=4 to N=8.
- `climate_assisted_risk`: robust S7-higher cells 15/25, robust S6-higher cells 3/25, indeterminate cells 7/25; 23/25 raw signs stable from N=4 to N=8.
- `deterioration_relocation`: robust S7-higher cells 15/25, robust S6-higher cells 2/25, indeterminate cells 8/25; 21/25 raw signs stable from N=4 to N=8.
- `engagement_habitat`: robust S7-higher cells 5/25, robust S6-higher cells 7/25, indeterminate cells 13/25; 17/25 raw signs stable from N=4 to N=8.
- `latent_survey`: robust S7-higher cells 0/25, robust S6-higher cells 9/25, indeterminate cells 16/25; 20/25 raw signs stable from N=4 to N=8.

Cell-level estimates and sign checks are stored in
`results/threshold_cell_stability.csv`; sweep summaries are stored in
`results/threshold_sweep_audit.csv`.
