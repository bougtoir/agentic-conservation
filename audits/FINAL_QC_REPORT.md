# FINAL_QC_REPORT (post-merge QC pass) — PASS

- Merge integrity: #744 + #749 present in master @ 354b62269; QC branch off
  master; no lost/duplicated content; sync maps verified.
- Defects found & fixed this pass: (a) Figure 1 + Table (GBIF coverage)
  numbered-but-unplaced → placed; (b) figure/table numbering did not match
  first-mention order → renumbered spec order, all 1–10 contiguous;
  (c) no in-text "Fig." citations for 6 figures → added; (d) highlight
  bullets concatenated without spaces AND exceeded 85 chars → rewritten;
  (e) 7 keywords → 6; (f) abstract 260 words → 249; (g) taxonomic authorities
  misparsed as citations → stripped at render.
- Tests: 43 pass; ruff clean; docx validation passes (literature + office).
- Visual QC: 44-page PDF render inspected, no layout defects.
- Public mirror manually synced (Actions did not post-merge-sync).
