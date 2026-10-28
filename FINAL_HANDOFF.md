# FINAL HANDOFF — Ecological Modelling retarget

## Verdict: CONDITIONAL GO (human finalization + Q1 caveat)

Not SUBMIT: the instruction prompt prohibits submission without user
approval, JCR Q1 status of Ecological Modelling could not be verified
(see JOURNAL_FIT_AND_APC_AUDIT.md), and the manuscript prose is a
generator draft requiring the author's scientific voice.

## What changed vs the rejected CB submission

| Editorial criticism | Resolution | Evidence |
|---|---|---|
| C1 mechanics absent | Full spec + algorithms in main text | MODEL_SPECIFICATION.md, ALGORITHM_1/2, EQUATION_ALGORITHM_CODE_MATRIX.csv, Methods §2.2–2.6 |
| C2 jargon | oracle→comparator; no POMDP/EVPI claims; engine labels fixed | §2.1, simulation.py rename, FINAL_ADVERSARIAL_REVIEW.md |
| C3 weak empiricism | honest synthetic framing; GBIF demoted to anchors | EMPIRICAL_EVIDENCE_AUDIT.md, §2.7, §4 |
| C4 no transferable message | mechanism-located reversals + EBD + null info effect | CLOSEST_PRIOR_STUDIES.md gate (GO), §4 |

## Deliverables

- `manuscript/EM_MANUSCRIPT.docx` — non-anonymous EM draft, 3,230
  words (Abstract→Acknowledgments), Algorithms 1–2 + Eqs. 1–3 in main
  text, Tables 1–8, Figures 1–9, 40 author–date references.
- `manuscript/EM_COVER_LETTER.docx` — first-person ("I") new-
  submission cover letter.
- Phase documents: EDITORIAL_RESPONSE_MATRIX, JOURNAL_FIT_AND_APC_AUDIT,
  MODEL_SPECIFICATION, ALGORITHM_1/2, EQUATION_ALGORITHM_CODE_MATRIX,
  CLOSEST_PRIOR_STUDIES, MODEL_SIMPLIFICATION_AND_ABLATION,
  EMPIRICAL_EVIDENCE_AUDIT, FINAL_ADVERSARIAL_REVIEW,
  REPRODUCTION_AND_INTEGRITY.
- `frozen_cb_rejection_2026-10-26/` — frozen rejected submission +
  decision note + SHA256SUMS.
- Code: `src/agentic_conservation/documents_em.py` (EM builder),
  honest engine labels in `simulation.py`.
- Sync: `devin/1793050713-ecological-modelling-retarget` registered
  in sync-to-repos BRANCH_MAP/SUBDIR_MAP → public mirror
  `bougtoir/agentic-conservation`.

## Human checklist before submission

1. Verify journal choice: Ecological Modelling is provisional pending
   JCR Q1 confirmation (SJR Q1 verified; JCR unverifiable).
2. Revise prose in your own voice; approve all claims (declared in the
   Acknowledgments AI-assistance note).
3. Regenerate `EM_MANUSCRIPT.docx` via
   `PYTHONPATH=src python3 -c "from agentic_conservation.documents_em
   import build_em_documents; build_em_documents(Path('.'))"`.
4. Prepare separate figure/table files for Editorial Manager (EM
   uploads figures as separate files; PNG/SVG/PDF already in
   `figures/` and `tables/`).
5. Submission ZIP intentionally not built — decide file set at
   submission time per Editorial Manager requirements.
