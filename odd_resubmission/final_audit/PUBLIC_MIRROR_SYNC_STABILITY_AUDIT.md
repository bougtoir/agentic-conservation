# Public mirror sync stability audit

Mirror: https://github.com/bougtoir/agentic-conservation

Found at start of pass: main = dfd9ffd (Oct-8 tree of `devin/1790233047-agentic-conservation`); earlier fast-forward dc1c9a6 unreachable; `frozen_cb_rejection_2026-10-26/` missing.

Root cause (`.github/workflows/sync-to-repos.yml` on master): five `BRANCH_MAP` entries target the same repo; associative-array order is arbitrary; each sync builds a parentless commit and pushes with `--force`; triggered by cron (`0 */2 * * *`) and pushes to listed branches.

Fix: https://github.com/bougtoir/wip/pull/801 (from master; only agentic-conservation mappings changed; other projects untouched; workflow not disabled): one canonical source (`devin/agentic-conservation-public-sync` ← master), exclusions for editorial correspondence / submission files / publisher PDFs, and opt-in fast-forward overlay (`FF_MAP`) that never deletes files and pushes without `--force`. Locally tested against a bare copy of the mirror (FF ancestor, 0 deletions).

Manual non-destructive sync this pass: dfd9ffd → dc92af7 (tag `odd-2020-revision-v1`) → 2177029 (tag `odd-2020-revision-v2`); both fast-forwards; 0 paths deleted relative to dfd9ffd; `manuscript/`, `submission/`, `frozen_cb_rejection_2026-10-26/` present; editorial letter, quotes, submission package and ODD source PDFs absent.

Clean-clone check of `odd-2020-revision-v2`: pytest 43 passed; final numeric audit 157/157; V0 Ψ reconstruction 56/56 exact; manuscript builder regenerates the clean manuscript (identical text except the commit string, which is a private file).

**Observed regression after the tag (check 2026-11-10T07:40:55Z, `git ls-remote`):** `main` = dfd9ffd again (the obsolete Oct-8 tree), i.e. the scheduled workflow force-pushed over 2177029 after the manual sync. Tag `odd-2020-revision-v2` (tag object c825847) still resolves to 21770296ff24c2b99ea2cc89cff48566176cd608. The force-sync problem is therefore **not resolved**; only the citable tag is protected. Re-pushing `main` before https://github.com/bougtoir/wip/pull/801 merges would be reverted again, so it was not repeated.

**Status: FAIL for `main` stability, PASS for tag stability.** Until https://github.com/bougtoir/wip/pull/801 is merged, the existing workflow may again force-push an obsolete branch to `main`. The tags are not touched by the workflow, so the cited version stays retrievable, but `main` may regress. Merge order: https://github.com/bougtoir/wip/pull/795 first, then https://github.com/bougtoir/wip/pull/801.
