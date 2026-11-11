# Final submission QC matrix

| gate | result |
|---|---|
| G1 Grimm/ODD scientific gate | PASS (scoped) |
| ODD/S1 compliance | 37 PASS / 10 PARTIAL / 0 FAIL |
| G2 editorial response integrity | PASS |
| G3 cover letter | PASS |
| numerical integrity | PASS (157/157) |
| builder QC (`scripts/qc_odd_submission.py`) | 42/42 PASS |
| pytest / ruff | 43 passed / clean |
| immutable baselines | unchanged (submitted manuscript, holdout Ψ, registries) |
| references | 42/42 DOIs resolve |
| figures/tables | PASS |
| visual QC | PASS |
| Appendix | PASS (5 tables, landscape) |
| Data Availability | PASS (tag odd-2020-revision-v2) |
| public mirror stable | **FAIL for main (regressed to dfd9ffd at 07:40Z), PASS for tag** — requires merge of https://github.com/bougtoir/wip/pull/801 |
| author metadata | **PENDING** author confirmation |

**Overall verdict: B — CONDITIONAL GO.** Remaining: merge https://github.com/bougtoir/wip/pull/795 then https://github.com/bougtoir/wip/pull/801; confirm affiliation/contact; then submission by the author (subscription route unless OA is chosen).
