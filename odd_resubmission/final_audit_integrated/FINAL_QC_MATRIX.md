# FINAL QC MATRIX

Automated checks: FINAL_QC_MATRIX_AUTOMATED.md (scripts/qc_integrated_submission.py,
113/113 PASS on the final build).

| Gate | Result | Evidence |
|---|---|---|
| Baselines: model code, config, results, tables, data, figures (existing files), submitted manuscript, historical submission files, psi_forensics, editorial | PASS | QC: no modified/deleted file in protected paths vs branch base 35c5deb9cbf4; SHA-256 of submitted DOCX 8ff06f53…, holdout_psi.csv 57899cac… |
| Numbers unchanged | PASS | final_numeric_audit.py 157/157 (working tree and clean clone of v3.2 tag) |
| Appendix eliminated from the package | PASS | no Appendix document; no "Appendix", "Table A1–A7", "Supplementary table" in clean manuscript, response, cover letter or PDF |
| Former appendix evidence retained | PASS | Tables 9–11 and Sections 3.5/3.7; complete CSVs in tables/ and results/ (crosswalk) |
| Ten inline figures | PASS | 10 wp:inline, 0 wp:anchor; embedded bytes identical to source PNGs; aspect ratio kept; order 1–10; cited before placement; captions editable 10 pt |
| Figure content vs caption | PASS | FINAL_INLINE_FIGURE_CONTENT_REVIEW.md (Fig. 1 and 9 corrected variants; captions of Figs. 4, 7, 10 corrected) |
| Tables sequential and cited in order | PASS | Tables 1–11; each cited before it appears |
| Table values | PASS | Table 10 = all 45 × 3 canonical values; Table 9 = canonical LHS file; Table 11 baselines = per-cell record |
| OMML and format | PASS | 20 structured OMML objects (8 equations), none beyond the right margin; Times New Roman 12 pt Normal; black text; one landscape section |
| PDF | PASS | 45 pages, ten raster figures on the caption pages, no replacement glyphs, no margin overflow |
| Author metadata | PASS | identical in manuscript, response, cover letter; no "Independent researcher" |
| Editorial consistency | PASS (author review requested for one narrowed claim) | FINAL_EDITORIAL_CONSISTENCY_AUDIT.md |
| Semantic code audit | PASS | FINAL_SEMANTIC_CODE_AUDIT.md |
| Fresh-clone reproducibility of the cited release | PASS | v3.2 tag: pytest 43, numeric audit 157/157, Ψ reconstruction 56/56, rebuild identical except the commit placeholder |
| Public release | PASS (tag) / OPEN (main stability) | FINAL_PUBLIC_VERSION_AND_SYNC_AUDIT.md |
| Hostile review | CONDITIONAL | FINAL_HOSTILE_REVIEW.md items 1–2 |
| Lint and tests | PASS | ruff check src scripts tests clean; pytest 43 passed |

Verdict: **CONDITIONAL GO** (not SUBMISSION READY).
