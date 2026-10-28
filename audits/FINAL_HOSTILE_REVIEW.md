# Final Hostile Review — EM Manuscript Integration

Questions posed, answers, and corrections applied:

1. Is Psi a derivation or a fitted restatement? — Semi-analytical: channel structure derived from E1/E2 semantics; 4 constants fitted on dev only. Manuscript explicitly calls it "not a closed-form theorem". OK.
2. Holdout untouched? — 56 cells disjoint from dev; seeds disjoint; formula frozen pre-holdout. OK.
3. Shifted/OOD/hostile reported separately? — Cell groups recorded in holdout_metrics.csv; failure concentrations named in 3.7 (captivity/all-latent). Groups tabled in Supplement-level files, text reports counts.
4. Is 0.846 conditioned on an outcome-defined subset? — Yes; stated verbatim in 3.7 with the all-cell 0.393 alongside. No conflation.
5. Does 0.393 make it unsuitable as a decision rule? — Text frames it as a criterion for sign prediction, not a deployable decision rule; regret 0.045 reported with B0 0.084 comparator; abstention labelled post-hoc.
6. Attribution vs confounding? — Manuscript states the S7–S6 contrast bundles reallocation + rule; "a positive Psi certifies the package, not circulation in isolation" (Discussion).
7. Mechanism ladder causally interpretable? — Toggles are config interventions on the reduced model only; described as "load-bearing components", not causal claims about the field.
8. Failure prominence? — Dedicated paragraph 2 in 3.7 with quantified near-boundary and hostile-cell failures.
9. Bounded, not universal? — "model-specific, bounded condition — not a general ecological law" stated in Discussion.
10. Falsifiable transferable-limited contribution? — Methods 2.8 + Results 3.7 state the pre-registration-style protocol (frozen formula, disjoint seeds, baselines) making the claim testable.

Corrections applied while drafting: near-boundary accuracy quantified (0.174);
post-hoc abstention explicitly labelled; B1 parameter named (climate_velocity) so
the dev-fitted baseline is transparent rather than oracle-like.
