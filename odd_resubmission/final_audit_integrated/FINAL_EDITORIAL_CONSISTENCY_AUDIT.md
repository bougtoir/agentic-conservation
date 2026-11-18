# FINAL EDITORIAL CONSISTENCY AUDIT

Documents: EM_ODD_MAIN_TEXT_INTEGRATED_CLEAN.docx (C), _TRACKED.docx (T),
_INTEGRATED.pdf (P), EM_ODD_EDITOR_RESPONSE_INTEGRATED.docx (R),
EM_ODD_COVER_LETTER_INTEGRATED.docx (L). The decision letter is held
privately (odd_resubmission/editorial/); this audit does not reproduce it.

| Check | Result | Evidence |
|---|---|---|
| Five quoted passages in R are verbatim from the decision letter | PASS | whitespace-normalised substring match of each quote against ECOMOD-26-2231_DECISION_LETTER.txt; original spelling "submisison" and the missing full stop before "Without" kept |
| No invented reviewer comments | PASS | R and L state that the letter contained no separate reviewer reports |
| R/L do not say the editors asked for appendix removal or inline figures | PASS | R point 2 and L describe where results are reported; no attribution to the editors |
| Section references 2.1–2.10, 3.1–3.7, 4 in R exist in C | PASS | headings present in C |
| Table/figure numbers in R and L match C | PASS | R: Tables 1, 2, 6, 7, 8, 9, 10, 11; Fig. 8. L: Tables 9 and 10. All generated from the same numbering object as C |
| File names cited in R and L exist in the package | PASS | EM_ODD_EDITOR_RESPONSE_INTEGRATED, EM_ODD_COVER_LETTER_INTEGRATED |
| Author block identical in C, R, L | PASS | Onishi Tatsuki; Data Science and AI Innovation Research Promotion Center, Shiga University; 1-1-1, Bamba, Hikone, Shiga, 522-8522, Japan; bougtoir@gmail.com; ORCID 0000-0001-7261-9062 (QC) |
| "Independent researcher" absent from C, R, L | PASS | QC |
| First person singular in R and L | PASS | QC |
| Claims in L match C | PASS | 0.971 of 34 determinate cells; withdrawal of frozen-model claim; reversal under earlier exposure and higher suitability intercept (not re-tested on held-out cells); disease ablation the only ablation beyond 2 SE (C 3.5, Table 10); biobank holds genetic material, animals move among wild and managed-care nodes (C 2.2, Fig. 1) |
| Q2 wording | PASS | C 3.4: equal year-100 displacement, cumulative exposure 1.49–1.97 × ; timing and cumulative exposure not separated |
| Reproductive criterion described as a proxy | PASS | C 2.1, 3.3 |
| Null information effect not read as zero value | PASS | C 3.7 (two paragraphs) |
| Historical V0 not called confirmatory; V1 same cells exploratory | PASS | C 2.10.2, 3.6, Table 11 status column and note |
| Data availability cites the release that contains the generator | PASS | C and L: tag odd-2020-revision-v3.2-inline, commit 4ccbc9c72c43 (verified by clean clone) |
| Tracked version compares against the submitted ECOMOD-26-2231 file | PASS | T header; submitted file SHA-256 unchanged (8ff06f53…) |
| P is a rendering of C | PASS | same page count on rebuild; captions and figures located on the pages listed in FINAL_INLINE_FIGURE_QC.md |
| Change in a signed claim of L | NOTE | L previously listed "disease and engagement feedbacks" as reversal conditions. With paired SE from the per-seed records only the disease ablation exceeds 2 SE; L and C were narrowed accordingly. Author review requested |
