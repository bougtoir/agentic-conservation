# Public mirror audit (bougtoir/agentic-conservation) — pre-sync

Authorisation (author, 2026-11-10): sync is allowed. Deleting `manuscript/`, `submission/`, or `frozen_cb_rejection_2026-10-26/` is NOT allowed at this stage. Public history must not be rewritten without separate approval.

## State
- Mirror `main` = c1bdf813 (2026-10-26, "sync: devin/1793050713-ecological-modelling-retarget"). It predates PRs #744, #749, #750 and this branch.
- The mirror is **stale**: it lacks the reversal-theory code (`minimal_model.py`, `scripts/run_reversal_theory.py`, `results/reversal/`) that the Ecological Modelling manuscript cites. The commit d2751ec claimed in #750 is not on the remote.
- **Mechanism risk**: `.github/workflows/sync-to-repos.yml` builds an orphan commit (`git commit-tree` without a parent) and runs `git push --force` to `main`. Every scheduled or push-triggered sync therefore **rewrites public history**. This most likely explains the missing d2751ec. This branch is deliberately not added to `BRANCH_MAP`.

## Three protected directories (contents audited, not modified)
| Dir | Files / size | Content | Exposure risk | Reproducibility role |
|---|---|---|---|---|
| `manuscript/` | 16 / 6.0 MB | 2026-10-26 EM manuscript draft (names "Tatsuki Onishi (corresponding author)"); CB and EM cover letters; CB checklist; human-authoring packet; figure deck | Full unpublished manuscript text and author identity are public; journal names appear in file names. No e-mail addresses, reviewer text, or private data. EM permits preprints, but the public draft differs from the submitted version. | None for numerical reproduction. The build scripts *write* here. |
| `submission/` | 61 / 13.5 MB | Conservation Biology package, including the `anonymous_review/` set and figures | Same as above; the "anonymous" set sits next to the named manuscript, so blinding is moot | None (build output) |
| `frozen_cb_rejection_2026-10-26/` | 9 / 8.5 MB | Frozen CB package ZIP and `DECISION_LETTER_NOTE.md`, which paraphrases four CB editor criticisms | Editorial correspondence (paraphrased) is public | None |

All three fall outside the previously approved public scope (code plus numerical reproduction). Removing them later would require only a normal deletion commit, with no history rewrite. The files would stay retrievable in history unless that history is rewritten, which needs separate approval. **Recommendation, for the author to decide**: remove them from the tip in a normal commit after the EM decision, and keep history as is.

## Sync plan (non-destructive)
- One normal fast-forward commit on top of c1bdf813 (no force, no orphan), adding or updating only:
  - `src/`, `scripts/` (numerical), `config/`, `tests/`, `results/` (including `reversal/` and `odd_verification/`)
  - `figures/`, `tables/`, `data/` (excluding `data/raw/odd_2020_sources/`, the publisher PDFs)
  - `provenance/`, `requirements*.txt`, `pyproject.toml`, `Makefile`, `README.md`
  - model and theory documents
- **Not added or updated**: `manuscript/`, `submission/`, `submission_zip/`, `frozen_*`, `odd_resubmission/` (editorial), `data/raw/odd_2020_sources/`, journal-fit and editorial matrices, handoff documents. The three protected directories stay byte-identical, so nothing is deleted.
- Verification after push: a clean clone of the mirror runs `pytest` and reproduces `policy_outcomes.csv` (sampled seeds) and the reversal registry. The mirror commit SHA is recorded below.

## Data availability statement facts (for the manuscript)
- All model code, configuration, and canonical result tables are in the public mirror at a stated commit.
- GBIF context data come from the existing `data/raw` snapshots with their acquisition ledger.
- The ODD 2020 publisher files are kept privately and are not redistributed.

## Result
- 2026-11-10: one fast-forward commit `dc1c9a6473c64484b2431975464dc1cf7cf30211` pushed to `bougtoir/agentic-conservation` main on top of `c1bdf81` (no force push, no history rewrite).
- `git status` before commit: 23 modified, 24 new paths; 0 deletions; nothing under `manuscript/`, `submission/`, `frozen_cb_rejection_2026-10-26/` changed.
- Added beyond the earlier plan, for reproducibility of the Psi claims: `odd_resubmission/psi_forensics/`, `PSI_*.md`, `Q1_Q3_PREREGISTRATION.md`. Editorial files (response, cover letter, gate decisions, revised manuscript) were not published.
- Secret scan of the copied tree: no matches. `data/raw/odd_2020_sources/` not published.
- Clean clone of the mirror: `pytest` 43 passed; 36/36 sampled values of `policy_outcomes.csv` (S0/S6/S7, 3 seeds each, 4 metrics) reproduced exactly.
- Caveat: the scheduled sync workflow maps older branches to this mirror; if it re-runs on those branches it may overwrite this commit. Re-check the mirror head before submission.
