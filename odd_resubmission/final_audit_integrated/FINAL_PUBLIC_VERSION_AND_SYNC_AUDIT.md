# FINAL PUBLIC VERSION AND SYNC AUDIT

Public repository: https://github.com/bougtoir/agentic-conservation

## Release tags

| Tag | Commit | Status |
|---|---|---|
| odd-2020-revision-v1 | dc92af7ffd35 | earlier, unchanged |
| odd-2020-revision-v2 | 21770296ff24 | appendix version; unchanged and not moved |
| odd-2020-revision-v3-inline | d92b23c01af7 | superseded intermediate: pushed before the equation and Table 11 fixes; its generator renders long equations beyond the margin in LibreOffice |
| odd-2020-revision-v3.1-inline | 10046dad043c | superseded intermediate: contains the fixes but its generator still names v3-inline as the release |
| **odd-2020-revision-v3.2-inline** | **4ccbc9c72c43** | **cited by the integrated manuscript and cover letter** |

Tags were never moved or deleted. Intermediate tags remain because the
public tags are treated as immutable.

## How the release commits were made

Each commit was created from `master`-based branch content
(agentic-conservation/ subtree) minus the excluded paths
(odd_resubmission/editorial, odd_resubmission/submission,
odd_resubmission/PUBLIC_MIRROR_COMMIT.txt, data/raw/odd_2020_sources,
submission_zip), overlaid on the current public `main` tree and committed with
the current `main` as parent, then pushed without `--force`. The diffs
against the previous `main` contained only A/M entries (no deletions).
Public `main` moved dae6c4566f32 → d92b23c01af7 → 10046dad043c →
4ccbc9c72c43 (fast-forward each time). `manuscript/`, `submission/` and
`frozen_cb_rejection_2026-10-26/` are present at 4ccbc9c72c43.

## Clean-clone verification of odd-2020-revision-v3.2-inline

| Check | Result |
|---|---|
| pytest | 43 passed |
| scripts/final_numeric_audit.py | 157/157 checks match |
| odd_resubmission/psi_forensics/reproduce_holdout_psi.py | V0 (MIN_BREEDING_POP = 4) reproduces 56/56 stored Ψ (max error 3.6e-15); MIN_BREEDING_POP = 8 reproduces 0/56 |
| scripts/build_integrated_submission.py | builds clean, tracked, cover and PDF (45 pages); response letter skipped because the private quotes are absent |
| Comparison with the submitted files | identical paragraph count, every table cell, all ten embedded image byte streams and all 20 OMML objects; the only differing paragraph is the commit hash in the Data availability statement ("[to be inserted]" in a public build, because the commit file lives in the private submission directory) |
| Private material absent | odd_resubmission/editorial and odd_resubmission/submission not present; ODD source PDFs not present |

The generated DOCX/PDF files themselves are not in the public repository
(the submission directory is excluded by the workflow); the repository holds
the generator and every input.

## Sync workflow (master, after PR #801)

- One canonical source for this mirror: `devin/agentic-conservation-public-sync`
  (fast-forwarded from master); the five former mappings are commented out.
- `FF_MAP` set for that source: overlay onto the current target tree, parent =
  current target commit, push without `--force`, no deletions.

## Remaining risk (not resolved)

The five retired source branches still exist in wip
(devin/1790233047-agentic-conservation, devin/1793050713-ecological-modelling-retarget,
devin/1793300000-reversal-theory, devin/1793300000-em-reversal-integration,
devin/1793164552-em-final-qc). Branches created before PR #801 carry the old
workflow, which maps them to this mirror and force-pushes. A push to any such
branch can reset public `main` to obsolete content, as happened on
2026-11-10. Tags are not touched by that workflow, so the cited release
remains retrievable, but `main` is not guaranteed to show the current
version. Deleting the five branches (after archiving them as tags) needs the
author's approval and has not been done.

The tag v3.2-inline contains the QC script as committed at that point; the
generator and inputs are final. Later wip commits add audit documents and
generated outputs only.
