# Final Data Availability audit

Statement (manuscript Declarations and cover letter use the same version): repository https://github.com/bougtoir/agentic-conservation, release tag `odd-2020-revision-v2`, commit 21770296ff24.

| item | in tagged mirror | path |
|---|---|---|
| model code, configuration | yes | src/, config/ |
| synthetic outputs, canonical registries | yes | results/, tables/ |
| Q1–Q3 outputs | yes | results/odd_verification/ |
| prospective Ψ (plan, freeze record, predictions, runs, metrics) | yes | odd_resubmission/PSI_*, results/psi_confirmatory/ |
| historical Ψ reconstruction | yes | odd_resubmission/psi_forensics/ |
| seeds | yes (seed column in every run CSV) | results/** |
| GBIF | aggregates only; no individual records | tables/table5_empirical_coverage.csv |
| literature | metadata only; no full texts | tables/table6_empirical_evidence.csv |
| DOI for software | none claimed | — |

Tag/commit consistency (2026-11-10T07:40Z): `git ls-remote` gives `refs/tags/odd-2020-revision-v2` → tag object c825847 → `^{}` 21770296ff24c2b99ea2cc89cff48566176cd608 = the commit printed in the manuscript (first 12 characters 21770296ff24). A fresh clone of the tag checks out that commit; in it pytest 43 passed, `scripts/final_numeric_audit.py` 157/157, V0 Ψ reconstruction 56/56 exact, and the builder regenerates clean/tracked/cover/appendix. `manuscript/` (16 files), `submission/` (61), `frozen_cb_rejection_2026-10-26/` (9) present; `odd_resubmission/editorial/` and `data/raw/odd_2020_sources/` absent (0 files) as intended. `main` currently does not contain this commit (regressed to dfd9ffd), which is why the statement cites the tag and not `main`.

Wording corrected this pass: "run manifests" replaced by what exists (seed per run record; preregistration and freeze records). PASS for content; stability of `main` depends on https://github.com/bougtoir/wip/pull/801 (tag is stable).
