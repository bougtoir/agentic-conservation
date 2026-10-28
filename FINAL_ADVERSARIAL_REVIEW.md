# Final adversarial review (Phase 10) — reenacting the editor's objections

Each objection from the Conservation Biology desk rejection is replayed
against the rebuilt material, plus the eight standing Chisholm questions.

## Editor's four criticisms — resolution status

1. **Essential model mechanics absent.** Resolved. MODEL_SPECIFICATION.md
   reverse-engineers all equations (E1–E18) from code;
   EQUATION_ALGORITHM_CODE_MATRIX.csv maps every mechanism to source
   function, config parameter, test, and output metric; Algorithms 1–2
   now appear in main-text Methods (§2.3, §2.5).
2. **Opaque jargon.** Resolved. "oracle" → "perfect-current-state-
   information comparator" throughout code and prose; no POMDP/EVPI
   claims; MCMC/POMDP distinction stated in §2.1; misleading engine
   labels corrected (S5 `greedy_suitability_heuristic`, S7
   `weighted_suitability_heuristic`); glossary in MODEL_SPECIFICATION.
3. **Empirical connection too weak.** Partially resolved by design:
   GBIF aggregates and case literature are demoted to clearly-labelled
   motivational anchors; parameters honestly declared synthetic; no
   validation claim. A real calibrated parameter set was not obtainable
   — framed as honest synthetic limitation, not hidden.
4. **No transferable message.** Resolved. Discussion reframes to a
   mechanistic, falsifiable claim: the circulation-vs-habitat reversal
   is *located* in a swept parameter plane; information is not the
   bottleneck; EBD is structural. CLOSEST_PRIOR_STUDIES.md gates the
   novelty claim vs 8 verified nearest works.

## Chisholm questions

1. What exactly is the model? — Answered §2.1–2.3 (IBM, annual, stochastic).
2. What is a policy? — §2.5 + Algorithm 2 + Table 2; rules, not solutions.
3. What is the observation process? — §2.4 (noise, delay, visibility gate).
4. What does the comparator measure? — §2.6; information effect, not EVPI.
5. Are budget comparisons fair? — one budget line, Σa≤1 enforced, S0=0;
   S6's unused rescue share documented in Algorithm 2 and §2.7.
6. Do numbers reproduce? — registry-sourced; 35 tests; manifest+SHA256.
7. What is new? — Phase-4 gate: A–C pass; D supporting.
8. What are the limits? — §2.7, §4, explicit synthetic framing.

## Residual risks

- JCR quartile for Ecological Modelling unverifiable (SJR Q1 yes) —
  flagged in JOURNAL_FIT_AND_APC_AUDIT.md; if Q1 is required by rule,
  a fallback Q1 hybrid modelling journal should be reconsidered.
- Manuscript prose is a generator draft in the house style; human
  author must finalize scientific voice before submission.
