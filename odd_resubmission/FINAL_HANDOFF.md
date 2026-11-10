# FINAL HANDOFF — ODD 2020/S1 revision for Ecological Modelling (new submission, ref. ECOMOD-26-2231)

Status: **NOT SUBMISSION READY.** Scientific gate: Gate A (conditional, scoped) —
see `UPDATED_SCIENTIFIC_GATE_DECISION.md`. Nothing has been submitted or merged.

## Build
```
PYTHONPATH=src python -m agentic_conservation.documents_em_odd   # docx, figures
cd odd_resubmission/submission && soffice --headless --convert-to pdf EM_ODD_REVISED_MANUSCRIPT_CLEAN.docx \
  && mv EM_ODD_REVISED_MANUSCRIPT_CLEAN.pdf EM_ODD_REVISED_MANUSCRIPT.pdf
python scripts/make_odd_figures.py     # Q2 figure (figures/odd/)
python scripts/qc_odd_submission.py    # FINAL_ODD_QC_MATRIX.md, SHA256SUMS.txt, ZIP
```
Every number in the documents is read at build time from `results/` (canonical),
`results/odd_verification/` (Q1–Q3), `results/psi_confirmatory/` and
`odd_resubmission/psi_forensics/`. The submitted `manuscript/EM_MANUSCRIPT.docx` is never written
(SHA-256 8ff06f53…95b1de checked by the QC script).

## Package (`odd_resubmission/submission/`)
| file | content |
|---|---|
| EM_ODD_REVISED_MANUSCRIPT_CLEAN.docx | ODD 2020/S1-structured manuscript, OMML equations, figures separate |
| EM_ODD_REVISED_MANUSCRIPT_TRACKED.docx | comparison with submitted file: additions red, deletions blue strikethrough |
| EM_ODD_REVISED_MANUSCRIPT.pdf | PDF of clean manuscript |
| EM_ODD_APPENDIX_A.docx | supplementary tables (LHS, ablations, historical Ψ, GBIF context) |
| EDITOR_RESPONSE_ODD.docx | point-by-point response quoting the decision letter verbatim (`ECOMOD-26-2231_DECISION_LETTER.txt`) |
| EM_ODD_COVER_LETTER.docx | cover letter |
| figures/Figure_1–10.png | figures in order of first citation |
| SHA256SUMS.txt, EM_ODD_SUBMISSION_PACKAGE.zip | manifest and ZIP |

## Required before submission (author)
1. Done: verbatim decision letter supplied by the author (2026-11-10) and archived in
   `odd_resubmission/ECOMOD-26-2231_DECISION_LETTER.txt` (not mirrored publicly); every
   response point quotes it. The letter lists Associate Editor comments only; no reviewer reports.
2. Confirm affiliation and contact details.
3. Public mirror synced non-destructively (commit in `PUBLIC_MIRROR_COMMIT.txt`, cited in the
   cover letter). The scheduled sync maps an older branch to the same mirror with force-push and
   may revert it; decide how to retire that mapping, then re-check the mirror head.
4. Review `REVISED_MANUSCRIPT_CRITICAL_REVIEW.md` (items 4–8 are scientific limitations the text
   now states) and approve or request changes.
5. Upload through Editorial Manager (human-only); choose subscription unless OA is authorized.

## Claims changed relative to the submitted version
- The original held-out Ψ evaluation is withdrawn as a frozen-model test (V0, MIN_BREEDING_POP 4);
  predictive claim rests on the prospective 60-cell evaluation.
- The S6 > S7 base ordering is presented as conditional on climate timing, suitability intercept and
  several submodels.
- Climate term stated as implemented (accelerating); "release events" replaces "successful
  reintroductions"; funding shock is one year; engagement non-decreasing; inert traits listed.
