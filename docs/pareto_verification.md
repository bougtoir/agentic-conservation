# Six-objective Pareto verification

The production policy means are compared without a weighted overall score.
Objective directions are:

- `survival`: maximize
- `welfare`: maximize
- `genetics`: maximize
- `ebd`: minimize
- `cost`: minimize
- `future_option`: maximize

Dominance requires another policy to be no worse on all six objectives within
an absolute numerical tolerance of 1e-12, and better by more
than that tolerance on at least one objective. This tolerance handles floating
point equality; it is not a claim that Monte Carlo uncertainty is zero.

The nondominated policies are S0, S1, S3, S4, S6, S7. Pairwise dominance records are:

- S2 is dominated by S1.
- S2 is dominated by S3.
- S2 is dominated by S4.
- S2 is dominated by S5.
- S2 is dominated by S6.
- S2 is dominated by S7.
- S5 is dominated by S7.

`results/pareto_front.csv` stores the objective means, Pareto flag, dominators,
and tolerance. `results/pareto_dominance.csv` stores the nonnegative
direction-adjusted objective advantages for every dominance pair. The
manuscript policy-outcome table reports the same production means and
intervals; `results/manuscript_values.csv` stores each policy's Pareto
indicator and the nondominated count.
