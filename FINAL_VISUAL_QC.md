# FINAL_VISUAL_QC — PASS

Rendered EM_MANUSCRIPT.docx → PDF (LibreOffice headless), 44 pages,
page-level contact sheets inspected:

- No blank pages, no orphan captions, no clipped tables, no illegible text.
- OMML Psi equation renders as native math in §2.8.
- Figures 1–10 and Tables 1–10 appear in strict first-mention order
  (programmatic scan: fig order 1..10, table order 1..10).
- Figure 1 (network) and Table 4 (GBIF coverage) were previously numbered but
  unplaced — FIXED: both placed and cited.
- Highlights: 5 bullets ≤85 chars; keywords 6; abstract 249 words.
- Fonts: TNR styles inherited from _configure_document; captions styled.
- Taxonomic authority strings ("(Cretzschmar, 1827)") in the GBIF table were
  being parsed as citations — FIXED by stripping authorities in _main_table.
