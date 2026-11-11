# G1 — Grimm/ODD scientific gate

**Verdict: PASS (scoped).** No material scientific contradiction found. Conditions below are interpretive, already reflected in the text.

## Independent recomputation
`scripts/final_numeric_audit.py` recomputes every headline number from run-level CSVs (not from summary tables): 157/157 checks match (`results/final_audit/numeric_recompute.csv`).
- Two first-run mismatches were audit-script errors, not registry errors: (1) the step trajectory applies the full displacement in year 50 (`first_year + years//2 - 1`), so cumulative exposure is 0.606×51 = 30.906 (my first audit placed it after year 50); (2) the confirmatory code uses z = 1.96 in the Wilson interval; with z = 1.959964 the lower bound differs by ≤7×10⁻⁶. The prespecified z = 1.96 is used. No registry was changed.

## Q1 (endpoints)
Base S7−S6: individual −0.055 (SE 0.022), reproductive proxy −0.049 (0.023), wild −0.063 (0.023): ordering S6 > S7 under all three. Held-out (V0 cells): 17 S7-favoured cells → 6 remain for wild persistence, 10 indeterminate, 1 reversed. The reproductive criterion is called a proxy throughout; no viability guarantee is claimed.

## Q2 (climate trajectory)
Same year-100 displacement 0.606; cumulative exposure 20.604 / 30.603 / 40.602 / 30.906 (×1.00/1.49/1.97/1.50). S7−S6 = +0.104 / +0.248 / +0.389 for linear / decelerating / step. Interpretation corrected this pass: in these forms earlier exposure also means larger cumulative dose, so timing and dose are not separated (Section 3.4, Discussion).

## Q3 (coefficients)
Ten literals × {0.5, 1.5} within domains; 14/20 material; one directional reversal (E1 intercept ×1.5, +0.159, SE 0.029), not held-out tested under the frozen cap of six reruns — stated in Abstract, 2.7.2 and 3.5. Ψ sensitivity is reported separately (3.6: intercept ×0.5 29/56 flips; breadth slope ×1.5 15; birth scale ×0.5 8).

## Ψ provenance and prospective validation
V0 reproduces all 56 stored values (max |Δ| 3.6×10⁻¹⁵, re-run from a clean clone of tag odd-2020-revision-v2); MBP=8 and committed V1 do not. Historical V0: 0.846 determinate / 0.393 all-cell / 0.045 regret. V1 same-cell: exploratory. Prospective: freeze commit 947d8f5 (2026-11-10T01:46:43Z) precedes first IBM outcome commit 005061d (03:25:40Z); 60 cells (40 in-domain, 20 shifted), 34 determinate, 33 correct = 0.9706, Wilson 0.851–0.995, all-cell 0.550, regret 0.0095 vs 0.0807 (always-S6) and 0.0759 (always-S7). Independence rests on the freeze record and unused parameter/seed ranges, not on seeds alone; the same investigator and the same model produced both, so this is internal prospective validation, not external validation (stated).

## Interpretation checks
No universal superiority (Conclusions: "neither generally superior nor useless"); no calibration or external-validation claim; bundled S7–S6 contrast stated (2.10.1, Limitations); Ψ limited to the shipped structure (3.6); release events not equated with establishment (2.7.6); perfect-current-state null no longer read as "information has no value" (3.7, fixed this pass).
