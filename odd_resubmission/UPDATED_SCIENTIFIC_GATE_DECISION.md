# Updated scientific gate decision (after Q1–Q3 and the Ψ gates)

Date: 2026-11-10 (UTC). Branch `devin/1794264760-em-odd-resubmission-gate`.
Frozen inputs: Q1–Q3 plan `Q1_Q3_PREREGISTRATION.md` (commit a655b2b, incl. Amendment A1); Ψ confirmatory plan `PSI_CONFIRMATORY_VALIDATION_PLAN.md` (freeze commit 947d8f5 / record 244dabd, 2026-11-10T01:46:43Z). No threshold, endpoint, seed, design or prediction was changed after the runs. All outputs are kept, including unfavourable ones.

## Decision

**Gate A (conditional, scoped).** Both mandatory gates pass under their frozen rules:

| Gate | Result | Basis |
|---|---|---|
| Ecological sensitivity gate (Q1–Q3, frozen A/B/C rules) | **Pass as A, with binding conditional restatements** | No indefensible central assumption and no fundamental model–implementation contradiction (C not met). Every material dependency has a statable interpretation (B not met). |
| PSI_PROVENANCE_RECOVERY_GATE | **Pass (recovery) / original claim withdrawn** | Stored `holdout_psi.csv` reproduced exactly (56/56, max abs. diff 3.6e-15) by the launch-state model V0 with MIN_BREEDING_POP = 4. The historical holdout is **not** an evaluation of the documented frozen model (V1, "MBP = 8"), so that claim is withdrawn. |
| Ψ prospective confirmatory gate | **Pass** | 33/34 determinate cells correct (0.971; Wilson 95% 0.851–0.995); Ψ regret 0.0095 vs 0.0807 (always S6) and 0.0759 (always S7); 34 ≥ 15 determinate cells. |

Gate A here does **not** mean the original manuscript claims stand. It means the model can be defended under ODD 2020 if the manuscript is rewritten with the conditions in §5. "SUBMISSION READY" is not assigned; that requires the rewrite, QC and author approval.

## 1. Policy-contrast and ranking sensitivity (IBM, S7 − S6)

Paired contrast d = Y(S7) − Y(S6); cell sign = sign(mean d) if |mean d| > 2·SE, else indeterminate.

**Q1 – endpoints (192 paired base seeds; 56 × 12 held-out).**

| Endpoint | S6 | S7 | S7 − S6 (SE) | Base sign | Held-out S7/S6/indet. |
|---|---:|---:|---:|---|---|
| Individual persistence `survival_100` | 0.529 | 0.473 | −0.055 (0.022) | S6 | 17 / 9 / 30 |
| Reproductive proxy `viable_persistence_100` | 0.515 | 0.466 | −0.049 (0.023) | S6 | 17 / 10 / 29 |
| Wild persistence `wild_persistence_100` | 0.529 | 0.466 | −0.063 (0.023) | S6 | 6 / 10 / 40 |

- 8-policy ranking is identical on individual persistence and the reproductive proxy (Kendall τ = 1.00): S6 > S7 > S4 > S5 > S3 > S1 > S2 > S0. On wild persistence τ = 0.77 (S6 > S7 > S1 > S4 > S5 > S3 > S0 > S2); S2 and S3 drop because their surviving species persist only outside wild nodes.
- Held-out cross-tab (`q1_endpoint_sign_transitions.csv`): of the 17 S7-favoured cells on individual persistence, 6 stay S7 on wild persistence, 10 become indeterminate and 1 reverses to S6. **Most of S7's held-out advantage is persistence outside wild nodes.** The reproductive proxy changes only 1 cell (indeterminate → S6). The proxy is a co-location proxy, not a viability guarantee.

**Q2 – climate trajectory (same year-100 displacement 0.606; cumulative exposure differs).**

| Form | Cumulative exposure (disp.-yr) | × shipped | S7 − S6 (SE) | Base sign | Held-out det. sign agreement with shipped |
|---|---:|---:|---:|---|---:|
| accelerating (shipped) | 20.60 | 1.00 | −0.055 (0.022) | S6 | 1.00 |
| linear | 30.60 | 1.49 | +0.104 (0.020) | S7 | 0.69 |
| decelerating | 40.60 | 1.97 | +0.248 (0.017) | S7 | 0.62 |
| step (mid-run) | 30.91 | 1.50 | +0.389 (0.014) | S7 | 0.73 |

- Matching the year-100 endpoint does **not** equalise exposure: alternatives impose 1.5–2.0× the cumulative exposure. The base-case sign reverses under every alternative, mainly because S6 collapses (0.53 → 0.34 / 0.18 / 0.08) while S7 stays at 0.43–0.47.
- All agreements are < 80%, so by the pre-stated reading the location of the reversal **depends on climate timing and exposure** and must be stated as conditional on the trajectory.
- Reduced-model caveat: Ψ sums climate over t = 0..99 (total 0.594), the IBM over years 1..100 (0.606).

**Q3 – one-at-a-time ±50% literals (stage 1: 48 paired seeds; reference on the same seeds −0.055, SE 0.042, indeterminate).**
- 14/20 perturbations are material under the frozen rule. Most are flagged by criterion (i) only because the 48-seed reference is indeterminate and the perturbed contrast is determinate S6 (direction unchanged).
- **Only one perturbation reverses the direction: E1 intercept × 1.5 (0.72 → 1.08): S7 − S6 = +0.159 (SE 0.029).** By the frozen ordering (Ψ flips, then shift; cap 6) it was not selected for stage 2. It is recorded as "material, held-out not evaluated".
- Largest shift in the S6 direction: E6 eligibility threshold × 0.5 (−0.232). E1 breadth slope × 1.5 makes the contrast indeterminate.
- E1 intercept × 0.5 is a floor regime: S6 0.031, S7 0.000; 48/56 held-out cells are indeterminate.
- No perturbation needed truncation; all values are within the preregistered domains.

## 2. Ψ prediction performance (reduced model, decision rule Ψ > 0 → S7)

| Setting | Ψ version | Det. cells | Det. accuracy | All-cell accuracy | Regret (Ψ / always-S6) |
|---|---|---:|---:|---:|---|
| Historical holdout, shipped | Ψ_reg (V0, MBP 4) | 26 | 0.846 | 0.393 | 0.045 / 0.084 |
| Historical holdout, shipped | Ψ_code (V1) – exploratory | 26 | 0.962 | 0.446 | 0.010 / 0.084 |
| **Prospective confirmatory, 60 new cells** | **Ψ V1 frozen** | **34** | **0.971** | 0.550 | **0.0095 / 0.0807** |
| – in-domain (40) | V1 | 22 | 0.955 | 0.525 | 0.013 / 0.080 |
| – shifted domain (20) | V1 | 12 | 1.000 | 0.600 | 0.003 / 0.081 |
| Confirmatory, reproductive proxy (secondary) | V1 | 33 | 0.970 | 0.533 | 0.010 / 0.086 |
| Confirmatory, wild persistence (secondary) | V1 | 28 | 0.964 | 0.450 | 0.009 / 0.064 |

- The single confirmatory error (cell C21, in-domain, Ψ = +0.65) is a determinate S6 cell on all three endpoints.
- All-cell accuracy is low because 26/60 cells are indeterminate: Ψ always makes a call, but the IBM gives no determinate answer. "Accuracy" claims must therefore be restricted to determinate cells, and regret must be reported alongside them.
- **Under alternative climate forms (Q2)** the Ψ computed with shipped (accelerating) climate fails: determinate accuracy 0.72 (linear), 0.48 (decelerating), 0.43 (step). Ψ recomputed with the matching climate form gives 1.00 / 1.00 / 0.94. That recomputed result is exploratory, not confirmatory. Ψ is valid only when its climate input matches the true trajectory.
- **Under coefficient perturbations (Q3 stage 2, 6 perturbations):**
  - Ψ_code at shipped constants: determinate accuracy 0.86–1.00.
  - Ψ recomputed with the perturbed constant: 0.25 (E1 intercept × 0.5; only 8 determinate cells), 0.78 (E12 birth scale × 0.5), 0.92–1.00 otherwise.
  - Ψ sign flips: 29 / 15 / 8 / 5 / 5 / 5 of 56 cells.
  - The reduced Ψ is therefore most fragile to the E1 intercept and E12 birth scale.

## 3. Ecological-assumption sensitivity (what drives what)
- **Endpoint definition:** the S6 > S7 base result does not depend on it. S7's held-out advantage largely does.
- **Climate trajectory timing / cumulative exposure:** the dominant driver of the base-case sign. Under the shipped accelerating form, cumulative exposure is lowest.
- **Baseline suitability (E1 intercept):** the only literal that reverses the base sign under ±50%.
- **Other literals:** they change magnitude or determinacy but not direction.

## 4. Application of the frozen gate rules
- **C (not met).** No central conclusion rests on an indefensible assumption:
  - Accelerating directional climate is a defensible scenario.
  - The constants are within preregistered domains.
  - No fundamental model–implementation contradiction remains. The Ψ V0/V1 discrepancy is a provenance error, now resolved and disclosed. The climate-form mismatch between text and code is a documentation error, to be corrected in ODD.
- **B (not met, with stated judgement calls).**
  - E1 intercept × 0.5 has 86% indeterminate held-out cells. We judge its interpretation statable (both policies fail; floor effect), so it is not a B trigger.
  - E1 intercept × 1.5 (base reversal) lacks a held-out run because of the frozen cap. Its base result is determinate and interpretable, so it is reported as "held-out not evaluated", not as unresolved.
  - The constants have no empirical calibration. The ±50% range is a sensitivity range, not an evidence-based range. This is reported as a limitation.
  - If the author regards any of these as unresolved, the decision would be B.
- **A.** Every dependency is reported as a bounded conditional result, and its rationale goes into the ODD Submodels.

## 4a. Outcome against the earlier Gate 1 decision criteria (GATE1_DECISION.md)
GATE1_DECISION.md listed provisional criteria per question before Q1_Q3_PREREGISTRATION.md replaced the gate rules (author instruction 4). They are reported here for transparency, unchanged:
- **Q1** ("base sign and determinate-cell accuracy ≥ 0.75 hold under the viable endpoint"): **met**. The base sign is S6 on all endpoints. Ψ_reg determinate accuracy on the viable endpoint is 0.852.
- **Q2** ("base sign unchanged and ≥ 80 % holdout agreement"): **not met**. The sign reversed under all three forms, and agreement was 0.62–0.73. The stated consequence was "the claim becomes conditional", which is what §5 item 3 requires.
- **Q3** ("sign of S7−S6 unchanged in ≥ 18 of 20"): result depends on the reading.
  - Read as direction (no determinate reversal): **met**, 19/20.
  - Read as strict sign-category equality with the 48-seed reference, which is itself indeterminate (−0.055, SE 0.042): **not met**, 6/20. Most changes are indeterminate → determinate S6.
  - The only direction reversal is E1 intercept × 1.5, which is treated as a load-bearing assumption (§5 item 3).

## 5. Binding conditions on the revised manuscript
1. Withdraw the claim that the original holdout (0.846 / 0.393 / 0.045) was an independent evaluation of a frozen model. Report it as a V0 historical result, with the V0/V1 and MBP 4-vs-8 chronology (PSI_PROVENANCE_RECOVERY_REPORT.md, PSI_CHRONOLOGY_AND_FREEZE_AUDIT.md). State MIN_BREEDING_POP = 4.
2. The confirmatory evidence for Ψ is the prospective 60-cell evaluation (§2), stated for shipped structural assumptions and accelerating climate only. The current-code historical holdout values (0.962 / 0.010) may appear only as exploratory.
3. State the S6/S7 ordering as conditional on climate trajectory and cumulative exposure (Q2) and on baseline suitability (E1 intercept), not as a general ranking.
4. Report all three endpoints. State that S7's held-out advantage is mainly persistence outside wild nodes.
5. ODD Submodels must give the accelerating climate equation as implemented (v·t/T per year), the full literal table with the Q3 ranges, and the reduced-model 0.594 vs 0.606 caveat.
6. Ψ accuracy must be reported on determinate cells, together with indeterminate counts and regret.

## 6. Deviations and limitations
- The confirmatory IBM stage was false-started at 03:06:48Z while the last Q3 perturbation was still running. It was killed at 03:08:14Z before any output was written, then restarted at 03:14:20Z after Q1–Q3 completed (logged in PSI_CONFIRMATORY_FREEZE_RECORD.md). Hashes of the designs, predictions, script and model at evaluation match the freeze record.
- Q2/Q3 report E-ind and E-rep only (as preregistered); wild persistence was evaluated in Q1 and in the confirmatory set.
- Q3 compares only S6/S7, not all 8 policies.
- The 12 replicates per cell give many indeterminate cells. No replicate count was changed post hoc.
- The verbatim ECOMOD-26-2231 decision letter is not on the VM, so no editor text is quoted yet.

## 7. Files
- `results/odd_verification/`: Q1 (`q1_*`, `psi_reg_vs_code.csv`), Q2 (`q2_*`), Q3 (`q3_*`), run-level CSVs and summaries.
- `results/psi_confirmatory/`: `designs.csv`, `psi_predictions.csv`, `ibm_runs.csv`, `cell_results.csv`, `metrics.csv`.
- `odd_resubmission/`: PSI_PROVENANCE_RECOVERY_REPORT.md, PSI_CHRONOLOGY_AND_FREEZE_AUDIT.md, PSI_CONFIRMATORY_VALIDATION_PLAN.md, PSI_CONFIRMATORY_FREEZE_RECORD.md, Q1_Q3_PREREGISTRATION.md, GATE1_DECISION.md, PUBLIC_MIRROR_AND_DATA_AVAILABILITY_AUDIT.md, psi_forensics/.
