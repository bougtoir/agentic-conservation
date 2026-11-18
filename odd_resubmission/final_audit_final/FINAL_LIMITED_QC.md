# FINAL LIMITED QC

| Item | Result | Evidence |
|---|---|---|
| B0 determinate accuracy follows the 56-cell record and the manuscript definition | PASS | 9/26 = 0.346 (B0_HISTORICAL_METRIC_CORRECTION.md); denominator 26 determinate cells, distinct from all-cell 9/56 = 0.161 |
| Historical table preserved | PASS | tables/table9_reversal_predictors.csv SHA-256 1f975d6c… unchanged; corrected values in table9_reversal_predictors_corrected_v1.csv |
| Text, Table 11, corrected CSV and code agree | PASS | QC check "historical baselines B0–B2 rows match"; B0 0.346 / 0.161 / 0.0837, B1 0.615 / 0.286, B2 0.423 / 0.196 |
| B0 tests (toy and historical) | PASS | tests/test_b0_correction.py, 3 tests |
| Prospective Ψ unchanged | PASS | 33/34, 0.971 [0.851, 0.995], all-cell 0.550, regret 0.0095 |
| Ablation wording: sign vs robustness | PASS | 3.5: only disease beyond 2 SE; engagement feedback +0.156 (SE 0.095) and origin fidelity +0.115 (SE 0.078) positive but below 2 SE; cover letter consistent |
| Title identical in manuscript, PDF, cover letter, response | PASS | response now states the title and "substantially revised new submission referring to ECOMOD-26-2231" |
| Figures 1–10 inline, captions, order; Tables 1–11 order; no Appendix; OMML; fonts; margins; author block | PASS | scripts/qc_integrated_submission.py 113/113 on the final build |
| PDF | PASS | 45 pages; Table 11 page and changed 3.5 text inspected |
| Numbers unchanged elsewhere | PASS | final_numeric_audit.py 157/157 (clean clone of v3.3 tag) |
| pytest / ruff | PASS | 48 passed; ruff clean |
| Release tag cited = verified content | PASS | odd-2020-revision-v3.3-inline → 84f287403609; clean clone builds identical documents except the commit placeholder; QC 99/101 PASS, 2 SKIP (private response, base ref) |
| Public `main` protected against legacy pushes | CONDITIONAL | PUBLIC_MIRROR_LEGACY_TRIGGER_RESOLUTION.md (needs author action A or B) |

Verdict: **CONDITIONAL GO**.
