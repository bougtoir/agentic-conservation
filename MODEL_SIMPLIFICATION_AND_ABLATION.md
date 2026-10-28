# Model simplification and ablation audit (Phase 5)

## Minimal explanatory core

The nine feature ablations (`results/ablations.csv`) and six adverse
conditions (`results/adverse_conditions.csv`) identify the mechanisms
that are load-bearing for each headline result:

| Result | Load-bearing mechanism (ablation evidence) | Non-essential |
|---|---|---|
| S7 vs S6 reversal | relocation mortality; habitat deterioration; visibility-gated movement; captivity breeding benefit | engagement feedback (quantitative only), biobank (outcome carrier, not a driver of survival ordering) |
| EBD persistence | discovery stage gating + visibility requirement for rescue | genetics module, welfare scoring |
| Zero information effect | movement capacity + movement cost + visibility gate dominate observation noise | comparator utility weights (result stable across 6 schemes) |

## Decision on splitting analyses

**Kept a single study.** The policy comparison, sweeps, EBD, and
information comparator all share one engine and one production design;
splitting would duplicate Methods and weaken the central claim (the
trade-offs exist *within* one system). The full design table was moved
to Methods; auxiliary audits (convergence, budget fairness, S3 failure
decomposition, population-cap audit) remain as repository audits
summarized in one Results paragraph — equivalent to supplementary
material, which is consistent with the minimal-SI house rule.

## What was removed from the front matter of the manuscript

- Optimized/strategic language ("forward rollout", "oracle", "EVPI",
  "POMDP" as capability claims) — corrected in code labels
  (`greedy_suitability_heuristic`, `weighted_suitability_heuristic`)
  and throughout prose.
- All results text now derives from `results/manuscript_values.csv` —
  no prose numbers are hard-coded outside the registry.
