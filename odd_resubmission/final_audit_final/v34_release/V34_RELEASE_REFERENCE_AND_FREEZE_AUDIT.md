# v3.4 release reference and freeze audit (Stage A)

Date: 2026-11-19 (UTC). Scope: release-reference pass only. No simulation, sweep or scientific change.

## 1. Pre-flight state (verified, not inherited)

| Item | Observed |
|---|---|
| wip master before this branch | `cab9beaecfd9e2e985456e651d6ff9b1298a6b73` (merge of #830), clean tree |
| #795 | merged, merge commit `83587d5876da967f35f29d4c155eebab6758785c` |
| #801 | merged, `75a2f2d91830fac42a26e16f34e53664bd5936b6` |
| #826 | merged, `eac36d92b762f474543829e96b12de64ca8db3ed` |
| #829 | merged, `8d83812d14091c1aa12d49d59682e00c72f13091` |
| #835 | merged, `4963584aeab3720b563b2ea5f5aefe614d842963` |
| #830 | merged, `cab9beaecfd9e2e985456e651d6ff9b1298a6b73` |
| public `main` | `3e85c34bd25cdb6140201c1430d6169e525449ef` = wip-sync fast-forward of wip `cab9beaecfd9`; parent `0f6eb558`; v3.3 commit is an ancestor; vs `0f6eb558`: 11 added, 4 modified, 0 deleted; its tree equals a local re-run of the overlay (`3e0f2bfe…`) |
| main protection | `branches/main.protected = false`; `rulesets = []`; `rules/branches/main = []`; branch-protection endpoint HTTP 403 → **main protection NOT VERIFIED / UNRESOLVED** |
| `odd-2020-revision-v3.3-inline` | annotated, tag object `f35216f19c6881380361b251c5be2e6e8a4b2c68` → `84f2874036094595f4d7e515133e6c48e2d50c06`; unchanged |
| `odd-2020-revision-v3.4-inline` | **does not exist** (ls-remote of `refs/tags/odd-2020-revision-*` lists v1, v2, v3, v3.1, v3.2, v3.3 only) |

## 2. Where version references are produced

| Location | Before | After |
|---|---|---|
| `src/agentic_conservation/documents_em_odd.py` `MIRROR_TAG` | `odd-2020-revision-v3.3-inline` | `odd-2020-revision-v3.4-inline` |
| Data and code availability (manuscript clean/tracked/PDF) | `release tag …v3.3-inline (commit 84f287403609)` | `release tag odd-2020-revision-v3.4-inline.` |
| Cover letter | `release tag …v3.3-inline (commit 84f287403609)` | `release tag odd-2020-revision-v3.4-inline.` |
| Editorial response | no tag/commit reference | unchanged |
| `_mirror_commit()` (read `PUBLIC_RELEASE_COMMIT.txt`, else `[to be inserted]`) | used twice | removed; documents carry the tag name only (no self-referencing SHA) |
| `odd_resubmission/submission/final/PUBLIC_RELEASE_COMMIT.txt` | `84f287…` | kept as the historical v3.3 record; no longer read by the generator. The v3.4 commit will be recorded in `V34_TAG_PUBLICATION_AUDIT.md` (Stage B). |
| Mirror README / QC script / numeric audit | no tag reference | — |
| Older audit records (`final_audit_final/*`, `mirror_guard/*`, `operator_audit/*`) | cite v3.3 / 84f287403609 as the state at that time | left unchanged (historical records) |

Generated-document scan (text of all four DOCX): `odd-2020-revision-v3.4-inline` once in manuscript and once in cover letter; no `v3.3`, `84f287`, `to be inserted` or `TBD` in manuscript, cover letter or response.

The stable identifier is the immutable tag. A commit SHA cannot be printed in a document committed before that commit exists; the full SHA belongs in the Stage B publication audit.

## 3. Scientific / document freeze

Diff of this branch against `cab9beae`: `documents_em_odd.py` (−11/+3 lines: tag constant, two sentences, helper removed), the regenerated files in `odd_resubmission/submission/final/`, the automated QC matrix, and these release documents.

- `simulation.py`, `minimal_model.py`, `configs/`, `results/`, `tables/`, `data/`: `git diff --quiet` against master → no change.
- Regenerated DOCX vs the #835 package (paragraph text, OMML count, tables, embedded media hashes):

| File | Paragraphs | OMML | Tables | Media | Changed paragraphs |
|---|---|---|---|---|---|
| clean manuscript | 1160 = 1160 | 21 = 21 | 11 = 11 | identical | 1 (Data and code availability) |
| tracked manuscript | 333 = 333 | — | — | identical | 1 (same) |
| cover letter | 17 = 17 | — | — | — | 1 (repository sentence) |
| editorial response | 20 = 20 | — | — | — | 0 (bytes differ only by DOCX metadata/timestamps) |

- PDF: 45 pages (unchanged). `diff` of `pdftotext -layout` output differs only in the Data-availability paragraph on p. 38 and its re-flowed lines; p. 38 rendered and inspected, page breaks elsewhere unchanged.
- Figures 1–10 standalone PNGs byte-identical to the #835 package; inline images byte-identical.
- Preserved (spot-checked in the regenerated text, and unchanged because only the DAS paragraph differs): Eq. 1 `W_j` on δ and restoration with the wild-node where-clause; S5/S7 as score-based selection with the Table 4 labels described as labels from the original submission; Eq. 5 bonus/φ definitions; disease same-year recovery; Fig. 1 biobank/reserve caption; Fig. 9 without the frozen-holdout note; ablation "below 2 SE" wording; Table 11 B0 0.346 / B1 0.615 / B2 0.423 from `table9_reversal_predictors_corrected_v1.csv`; Shiga University author block; ECOMOD-26-2231 in cover letter and response; no Appendix A.

## 4. Targeted QC (actual results on this branch)

| Check | Result |
|---|---|
| `pytest -q` | 59 passed (same test set as #835) |
| `scripts/final_numeric_audit.py` | 157/157 checks match |
| `make integrated` (`qc_integrated_submission.py`) | 113/113 PASS, 0 SKIP |
| `ruff check src tests scripts` | All checks passed. (`ruff check .` reports 5 pre-existing E501 in `odd_resubmission/psi_forensics/*.py`, preserved forensic scripts, not introduced here.) |
| `SHA256SUMS.txt` | all entries OK |
| ZIP | 16 entries (5 documents, 10 figures, SHA256SUMS), each byte-identical to the files in `final/` |

Final package SHA-256 (Stage A, pending merge):

```
66be98646cb5d7b3f1ddc7d2a831990dca02a7afca897ffab07b06b8f6975fb6  EM_ODD_REVISED_MANUSCRIPT_CLEAN_FINAL.docx
d29e9e003ecd3cebde73c169f4d49255f72b2d75f97b297ceb2557cc9c193f3f  EM_ODD_REVISED_MANUSCRIPT_TRACKED_FINAL.docx
e54bc202bec3e5cccd19a99ddd3e53cc331a6210ecb7a300adc37ab58fbd8824  EM_ODD_REVISED_MANUSCRIPT_FINAL.pdf
ce138bf3265e39318ebb1e55324eb18eb533d65c12de1576ea797ea0c67f5356  EM_ODD_COVER_LETTER_FINAL.docx
0e7e897596d624a53db848d48da0e959d08b3dbe3d570abcf62d391242ed41d7  EDITOR_RESPONSE_ODD_FINAL.docx
7dce67915564c40270220bd5012060a71d6e1f9469be15c7beadaa89b5006513  EM_ODD_SUBMISSION_PACKAGE_FINAL.zip
```

## 5. What the public release will and will not contain

The sync excludes `odd_resubmission/editorial`, `odd_resubmission/submission`, `odd_resubmission/PUBLIC_MIRROR_COMMIT.txt`, `data/raw/odd_2020_sources`, `submission_zip` (editorial correspondence, journal files, publisher PDFs). The v3.4 tag will therefore contain the generator that produces the v3.4-citing manuscript and cover letter, the model, configs, results, tables, audits and tests, but **not** the submission DOCX/PDF themselves. Stage B reproduces those documents from the tagged generator and compares them with the committed package. The editorial response cannot be rebuilt from the public tree because its quotes come from the private `odd_resubmission/editorial/response_quotes.json` (QC records this as SKIP in a public clone).

## Verdict

**STAGE A READY — AWAITING AUTHOR MERGE.** Tag v3.4 does not yet exist; the release is not frozen.
