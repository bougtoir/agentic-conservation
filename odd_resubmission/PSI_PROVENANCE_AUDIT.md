# Ψ provenance audit (found during the Q1–Q3 regression gate, before any Q run)

| Check | Result |
|---|---|
| IBM `policy_outcomes.csv` (24 policy × seed checks, 9 endpoints) and 12 random `holdout_runs.csv` rows | exact reproduction |
| Development Ψ (`minimal_model_dev_predictions.csv`, 125 cells) | exact reproduction (max \|ΔΨ\| 4e-16) with committed code, where `MIN_BREEDING_POP` defaults to **4** |
| Documented frozen constant | **8** (MINIMAL_MODEL_SPECIFICATION.md, THEORY_GO_NO_GO.md, HOLDOUT_PROTOCOL_AND_RESULTS.md, FINAL_HARDCODE_AUDIT.md) — contradicts the code and the dev registry |
| Held-out Ψ (`results/reversal/holdout_psi.csv`, 56 cells) | **not reproducible** from committed code with MIN_BREEDING_POP ∈ {2,4,6,8,12,20} (max \|ΔΨ\| 17–20; 0/56 exact). `stage_metrics` recomputes dev Ψ live but reads held-out Ψ from the stored CSV. Both files were committed together in f964b6641, and `minimal_model.py` was not changed afterwards, so the CSV came from an uncommitted minimal-model state. |
| Registry headline metrics (from stored Ψ) | acc_det 0.846, acc_all 0.393, regret 0.0450 |
| Same metrics with committed-code Ψ (same IBM signs) | acc_det 0.962, acc_all 0.446, regret 0.0104 |

Interpretation:
- The stored held-out Ψ is the only candidate for a prospective prediction, but no committed code produces it.
- The committed-code Ψ is reproducible but cannot be shown to be independent of the held-out results. Its better accuracy must **not** be reported as validation.
- The IBM S6/S7 results are unaffected.
- This finding concerns reproducibility and the integrity of the Ψ claim. It is not a defect in the model's ecology.

Handling (amendment A1 to the frozen plan, recorded before any Q run): every Ψ metric is reported twice:
- **Ψ_reg**: stored registry Ψ, frozen, not reproducible.
- **Ψ_code**: committed code, reproducible, independence not established.

Recomputed Ψ under the Q2 and Q3 alternatives is necessarily Ψ_code-based. The canonical registry is left unchanged.
