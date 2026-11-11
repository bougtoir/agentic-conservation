# Final numerical consistency audit

Independent recomputation from run-level CSVs: **157/157 PASS** (`results/final_audit/numeric_recompute.csv`, script `scripts/final_numeric_audit.py`, also passing from a clean clone of tag `odd-2020-revision-v2`).

Manuscript text check: all headline values (0.529, 0.473, −0.055/0.022, 0.606, +0.104/+0.248/+0.389, +0.159/0.029, 0.971, 0.851–0.995, 0.0095, 0.0807, 0.0759, 0.550, 0.846, 0.393, 0.045, 0.970, 0.964, 34 of 60, ×1.49–1.97) appear in the clean manuscript; cumulative exposures appear rounded to 0.1 in Table 7 (20.6/30.6/40.6/30.9).

First-run discrepancies (resolved as audit-script errors, see G1): step exposure placement; Wilson z constant (≤7×10⁻⁶). Canonical registries unchanged: `manuscript/EM_MANUSCRIPT.docx` sha256 8ff06f53…91de, `results/reversal/holdout_psi.csv` sha256 57899cac…332c.
