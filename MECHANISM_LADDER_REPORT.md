# Mechanism-Addition Ladder Report

## Purpose

Stress the minimal model by toggling its mechanisms over the
deterioration × relocation-mortality grid (det ∈ {0, 0.005, …, 0.040},
reloc_mort ∈ {0, 0.0625, 0.125, 0.1875, 0.25}) and checking which mechanisms are
load-bearing for the Ψ boundary. Results: `results/reversal/mechanism_ladder_psi.csv`.

## Toggles

| toggle | what is disabled/changed | mean Ψ | frac cells Ψ>0 |
|---|---|---|---|
| base | — | 13.57 | 0.80 |
| no_engagement | engagement feedback on budget (β_engage=0) | 14.36 | 0.84 |
| no_exsitu | ex-situ breeding multiplier | 13.57 | 0.80 |
| no_latent | latent undiscovered cohort | 2.37 | 0.67 |
| no_climate | climate trend on suitability | 12.16 | 0.67 |
| high_mate_limit | stricter mate limitation (MIN_BREEDING_POP×2) | 13.96 | 0.85 |
| no_mate_limit | mate limitation removed | 13.82 | 0.99 |

## Findings

1. **The latent cohort is the largest single load-bearing mechanism.** Removing it
   collapses mean Ψ from 13.6 to 2.4 (−83%): circulation looks much less valuable
   once the hidden stock awaiting discovery cannot be relocated to safety. This is
   the mechanism whose omission took the v1 model from 88.8% to 44.8% dev accuracy.
2. **Mate limitation changes the boundary position, not its existence.**
   `no_mate_limit` raises the Ψ>0 share from 0.80 to 0.99 — small rescued populations
   become viable, so circulation dominates almost everywhere. `high_mate_limit`
   shifts it the other way slightly. The fitted constant (8) controls *where* the
   boundary sits, which is why it was frozen pre-holdout.
3. **Engagement and ex-situ are second-order.** Removing either moves mean Ψ by
   <6%; they matter near the boundary (where their absence flips marginal cells)
   but not to the gross structure.
4. **Climate velocity expands the circulation region** (frac>0 falls 0.80→0.67
   without climate drift): drift increases the suitability gap between origin and
   alternative, feeding the circulation channel.

## Implication for the derivation

Ψ's sign is driven primarily by (i) the origin-suitability trajectory (habitat
channel, always ≤ 0 for S7's reduced habitat share) and (ii) the latent + mate-limit
structure of the circulation channel. Confidence in a Ψ sign should scale with |Ψ|,
consistent with the holdout failure region (|Ψ| < 0.2 → 17% sign accuracy).
