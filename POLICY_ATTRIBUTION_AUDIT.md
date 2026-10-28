# Policy Attribution Audit — S7 vs S6 Factorial Decomposition

## Design (frozen in THEORY_GO_NO_GO.md)

Four arms, 125 dev cells, 8 paired seeds per cell (seed = 900000 + design_id·100 + rep):

| Arm | Budget allocation | Movement rule | Interpretation |
|-----|-------------------|---------------|----------------|
| S6  | S6 (habitat 0.68) | S6 rule (no relocation) | baseline |
| S7  | S7 (habitat 0.35 + rescue/ex-situ) | S7 rule (suitability-weighted relocation) | total package |
| S6_C | S6 | S7 rule (`decision_rule_override="S7"`) | circulation main effect under S6 budget |
| S7_NC | S7 | disabled (`movement_disabled=True`) | allocation effect of the S7 package |

New config keys added in `simulation.py` (`_move_agents`): `decision_rule_override`
(swap the rule that selects relocation candidates/targets) and `movement_disabled`
(short-circuit relocation entirely). Verified: S7 + S6-rule ≡ S7 + movement_disabled.

Decomposition per cell:
- allocation effect = S7_NC − S6
- circulation effect (under S6 budget) = S6_C − S6
- interaction = (S7 − S7_NC) − (S6_C − S6) = circulation under S7 budget − circulation under S6 budget

Note: the attribution CSV's `seed` column records the nominal policy label (script bug,
fixed in 6b-run script for future runs); per-cell means are unaffected but pairing is lost
(aggregate means over 8 reps instead of paired contrasts).

## Results (`results/reversal/attribution_cells.csv`, n = 125 cells)

Median effects by sweep:

| sweep | alloc_eff | circ_eff | total | interaction |
|-------|-----------|----------|-------|-------------|
| captivity_breeding | −0.188 | +0.203 | −0.125 | −0.156 |
| climate_assisted_risk | −0.078 | +0.078 | +0.359 | +0.375 |
| deterioration_relocation | 0.000 | +0.594 | +0.094 | −0.484 |
| engagement_habitat | −0.781 | −0.188 | −0.047 | +0.859 |
| latent_survey | −0.516 | −0.141 | −0.156 | +0.531 |
| overall median | **−0.359** | **+0.094** | — | +0.344 |

By robust dev-cell direction (final_sign at n = 8; −1 = S6, +1 = S7):

| final_sign | n cells | median alloc_eff | median circ_eff | median interaction | median total |
|---|---|---|---|---|---|
| −1 (S6) | 76 | −0.539 | +0.023 | +0.461 | −0.125 |
| 0 | 3 | −0.406 | +0.062 | +0.344 | 0.000 |
| +1 (S7) | 46 | 0.000 | +0.156 | +0.297 | +0.148 |

## Interpretation

1. **S6-favored cells are driven by the bundled allocation shift, not by circulation
   harming persistence.** Where S6 wins, the S7-budget arm without movement (S7_NC)
   already loses ≈ −0.54 on the metric; circulation under an S6 budget is roughly
   neutral (+0.02). Relocation under the S7 budget adds back ≈ +0.46 of interaction —
   i.e., circulation recovers part of the habitat-share loss but not all of it.
2. **S7-favored cells are driven by circulation.** Where S7 wins, the allocation shift
   alone is ≈ 0 and circulation contributes +0.16 (S6 budget) amplified to +0.30
   interaction under the S7 budget (rescue spend buys more moves; ex-situ spend buys
   breeding complement).
3. **Non-additivity is large** (median interaction +0.34): the circulation benefit
   depends on the budget that funds it — rescue 0.14 of budget ≈ 5–6 moves total vs
   the shared capacity cap and mate limitation. Any condition on the reversal must
   therefore model the two channels jointly, not marginally. This is what the Ψ
   decomposition (habitat channel + circulation channel + interaction absorbed into
   the circulation channel's capacity quota) encodes.

So "the S7–S6 difference" is NOT a causal effect of circulation alone: it is
circulation-under-S7-budget minus nothing-under-S6-budget, minus the S6→S7
reallocation penalty. The circulation-only comparison (S6_C − S6) is near-neutral in
median because the S6 budget funds too little rescue to move enough agents.
