# Policy-budget fairness audit

## Allocation accounting

All S1-S7 fixed allocations sum to one; S0 intentionally allocates zero. The
fixed vectors define policy archetypes. They are not estimates of real program
budgets and are not empirical recommendations.

## Hidden advantages

Habitat-heavy allocations can favor policies whose mechanisms operate through
quality restoration; rescue and ex-situ shares can favor movement or managed
breeding; survey shares can reduce extinction-before-discovery; and engagement
spending can compound future budgets when the hypothetical feedback coefficient
is positive. Policy identity and allocation are therefore partially confounded
in the base design.

The robustness audit compares the fixed archetype with equal shares across its
active categories, a habitat-priority reallocation, and a movement-cautious
reallocation using paired seeds. Replicate-level and summarized results are in
`results/policy_budget_robustness.csv` and
`results/policy_budget_robustness_summary.csv`.

## Within-class search

A deterministic, seeded Dirichlet search perturbs only categories active in
each policy. Candidates are selected on training seeds using a prespecified
diagnostic index combining persistence, retained species, welfare, future
option value, and EBD, then compared with the fixed allocation on held-out
paired seeds. Training selection improved held-out diagnostic utility for
4 of 7 policy classes. This search is a robustness diagnostic, not a
claim of global optimality: the utility weights are normative, the search is
small, and no policy is declared an overall winner from it.

## Interpretation rule

Base allocations remain useful as transparent archetypes only when allocation
sensitivity and reversal regions are reported alongside them. Differences that
disappear under plausible reallocations are treated as fragile. The manuscript
must not compare a tuned dynamic policy with deliberately handicapped fixed
policies or describe any allocation vector as operational advice.
