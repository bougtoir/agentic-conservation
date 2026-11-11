# Hostile ODD-editor review of the submitted manuscript (ECOMOD-26-2231)

Reviewer stance: an ODD-literate editor who tries to rebuild the model from the paper alone.

| # | Can the reader reconstruct it? | Manuscript section | Code | Scientific consequence | Severity | Correction |
|---|---|---|---|---|---|---|
| H1 | Annual schedule: the order yes, the update semantics no | 2.3, Algorithm 1 | run_simulation | replication ambiguity | MAJOR | ODD 3 action table |
| H2 | Agent types and state variables: no; inert variables are listed | 2.2 | _initialize_agents | the reader assumes mechanisms that do not exist (climate sensitivity, dispersal, social dependence, connectivity) | MAJOR | state-variable table; remove or label inert items |
| H3 | Observation process: yes | 2.4 | _observed_state | — | MINOR | reframe as Sensing |
| H4 | Policy decisions: mostly | 2.5, Algorithm 2 | _move_agents | literals unexplained | MAJOR | rationale + Q3 |
| H5 | Stochastic transitions: partly | 2.1 | draws | — | MINOR | stochasticity table |
| H6 | Functional-form rationale: no | 2.3, 2.7 | E1–E18 | conclusions may rest on arbitrary forms | CRITICAL | ODD 7 per-submodel rationale + Q2/Q3 |
| H7 | Excluded assumptions: no | — | — | no topology, no interspecific competition, no senescence, non-decreasing engagement | MAJOR | explicit exclusions list |
| H8 | Mechanism vs numerical convention: not distinguishable | 2.7, Table 1 | config | the editor's core concern | CRITICAL | assumption-class column (ledger) in the main text |
| H9 | Informative experiment or arbitrary toy? | Discussion | — | undecided until Q1–Q3 are answered | CRITICAL | run Q1–Q3; report outcomes either way |
| H10 | Persistence endpoint | 2.6, Results | survival_100 | a single captive individual counts as a surviving species | CRITICAL | add viability endpoint (Q1) |
| H11 | Patterns element absent | — | — | no evidence the model is fit for purpose | MAJOR | general-belief patterns P1–P4 checked on existing outputs |
| H12 | "Funding collapse" and "successful reintroductions" mislabel the mechanisms | 2.7, Results | run_simulation | overstated realism | MAJOR | rename |
