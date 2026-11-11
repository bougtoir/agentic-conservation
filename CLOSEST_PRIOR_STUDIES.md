# Closest prior studies audit (Phase 4)

Candidate contributions were tested against the closest verified literature
in `data/processed/bibliography.csv` (all DOIs Crossref-verified).

| Study (DOI-verified) | What it does | Distance to this paper |
|---|---|---|
| Chadès et al. 2008; Canessa et al. 2015; Chadès et al. 2021 | Decision/POMDP framing for conservation actions | They optimize policies for a single objective; we compare fixed interpretable rules across six objectives with mechanism transparency — no optimized-policy claim |
| Condé et al. 2011, 2013; Hoban et al. 2020 | ex situ–in situ integration, One Plan Approach | Descriptive/architectural; our model makes the integration dynamic and simulated, locating when it pays |
| Kaczensky et al. 2007; D'Elia et al. 2015; Mee et al. 2007 | Species-specific reintroduction modelling/monitoring | Single taxon, empirically calibrated; ours is mechanism-general and synthetic-parameterized |
| Snyder et al. 1996; Jule et al. 2008 | Reintroduction outcome meta-analysis | Empirical summary statistics; no decision rules or state-dependent policy reversals |
| Joseph et al. 2009; McCarthy & Possingham 2007 | Optimal budget allocation under scarcity | Static optimization, single outcome; ours is dynamic, multiobjective, partially observed |
| Williams & Hoffman 2009; Kennedy et al. 2008 | Decision under uncertainty, structured decision-making | Framework advice, not a mechanistic IBM comparing policy archetypes |
| Mora et al. 2011; Tedesco et al. 2014; Liu et al. 2022 | Estimating undescribed species richness | Statistical estimates of hidden diversity; we simulate the *decision consequence* — extinction before discovery under budgeted discovery |
| Bolton et al. 2022; Moss et al. 2015 | Value-of-information and monitoring design | VoI at design level; ours is a mechanistic paired comparator showing information is not the binding constraint |

## Candidate contributions and verdict

- **A. Circulation-vs-habitat threshold located inside a swept parameter
  space** — supported: 35 robust S7 cells vs 26 robust S6 cells vs 64
  indeterminate across five two-factor sweeps. GO.
- **B. Extinction-before-discovery as a structural (visibility-gated)
  failure mode** — supported: EBD persists even under the best feasible
  policy (0.174 vs 0.993 under no action); mechanism is the stage≥2
  visibility gate, not budget. GO.
- **C. Zero effect of perfect current-state information** — supported:
  paired effect −0.003 [−0.112, 0.131], stable across 6 weight
  schemes. Novel mechanistic result: action capacity, not
  observation, binds. GO.
- **D. Non-collapsible multiobjective trade-off** — supported: 6/8
  policies Pareto-non-dominated; honest, but less novel alone
  (multiobjective conservation trade-offs are known). Kept as
  supporting result, not headline.

Gate verdict: **GO** — contributions A–C are jointly distinctive relative
to the closest verified literature; no manufactured thresholds (sweep
axes are the model's own parameters, thresholds are located, not assumed).
