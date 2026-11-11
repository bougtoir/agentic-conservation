# FINAL_PUBLIC_REPRODUCTION — PASS

- Merge integrity: master @ 354b62269 contains merges of #744 (2cc0a6e22) and
  #749 (ba665ea88). Branch devin/1793164552-em-final-qc = master + QC fixes.
- Tests: pytest → 43 passed (12.4s); ruff → clean.
- Clean-clone reproduction (/tmp/em_repro, same VM): build_outputs.py +
  build_em_documents regenerated; SHA256 of
  results/manuscript_values.csv, results/reversal/manuscript_reversal_values.csv,
  tables/table9_reversal_predictors.csv identical; EM_MANUSCRIPT.docx
  document.xml byte-identical.
- Registry lookups only: no hand-typed derived values in builder text.
- GBIF raw pulls persisted under data/raw with provenance ledger; used as
  motivation only, never as calibration/validation.
- Public mirror bougtoir/agentic-conservation: sync-to-repos Actions did NOT
  update it post-merge (stale at dfd9ffd, pre-retarget). Documented cause:
  workflow pushes map branches, not merges; cron run status unverifiable
  here. Manual authorized sync performed 2026-10-28 → main @ d2751ec now
  mirrors merged subdir (sync commit labelled
  "sync: devin/1793164552-em-final-qc ... merged #744+#749").
  Note: QC-fixed manuscript (this branch) will be mirrored after merge or by
  a follow-up sync; current mirror content = master pre-QC-fix.
