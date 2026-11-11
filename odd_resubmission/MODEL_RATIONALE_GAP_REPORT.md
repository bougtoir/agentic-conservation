# Model rationale gap report

Scope: E1–E18 and Algorithms 1–2 (details in `ECOLOGICAL_ASSUMPTION_LEDGER.csv`). For each item, the question is whether the submitted manuscript explains (i) the process being approximated, (ii) why the functional form was chosen, (iii) which alternatives were set aside, (iv) the simplifying assumptions, (v) the effect on conclusions, and (vi) the evidence for or against it.

| ID | In main text? | Rationale given? | Gap | Consequence for the S6/S7 conclusions | Fixable by text alone? |
|---|---|---|---|---|---|
| E1 suitability | Eq 1 | no | literals unexplained; inert climate_sensitivity | central | **No**: literal robustness is untested (Q3) |
| E2 habitat/climate | partly (Eq 2) | no | quadratic cumulative climate not stated | central (decides the reversal) | **No**: needs an alternative-form test (Q2) |
| E3 observation | Eq 3 | partial | none material | low | yes |
| E4 discovery | prose 2.4 | partial | stage coefficients synthetic | Ψ ladder | yes (label as synthetic) |
| E5 allocation | Table 2 | yes (archetypes) | bundling | already caveated | yes |
| E6–E7 movement | Algorithm 2 | no | 0.58 trigger, 20 % take, at-least-one-move rule, no topology | central to C | partly; 0.58 is included in Q3 |
| E8–E9 movement costs | prose | partial | release counter semantics | wording | yes |
| E10 disease | repository only | no | — | low | yes |
| E11 survival | repository only | no | additive hazards, no senescence | central | yes (state + justify); robustness covered by Q3 |
| E12 reproduction | repository only | no | 5.0 scaling, species-specific density | central to the ex situ lever | partly; 5.0 is included in Q3 |
| E13 genetics | repository only | partial | not a population-genetic model | low | yes |
| E14 cap | audit doc | yes | — | none (audit) | yes |
| E15–E16 | prose | partial | biobank never restores individuals | low | yes |
| E17 welfare | prose | partial | no feedback on demography | low | yes |
| E18 engagement | prose | partial | non-decreasing engagement; "collapse" is a one-year shock | medium | yes (rename + state) |
| A1 schedule | Algorithm 1 | no | variables updated per step; synchronous vs asynchronous updating | medium | yes |
| A2 action selection | Algorithm 2 | partial | triage rationale | medium | yes |
| Endpoint | 2.6 | no | ≥ 1 individual anywhere counts as persistence | **central** | **No**: needs a viability-endpoint test (Q1) |

Summary: most of the gaps are reporting gaps that the ODD restructuring will close. Three gaps (the endpoint, the climate functional form, and the untested literals) are scientific. Better text cannot answer them, because they decide whether the main S6/S7 reversal finding belongs to the ecology of the model or to arbitrary construction choices.
