# v3.4 tag release plan

Target tag: `odd-2020-revision-v3.4-inline` (new, annotated). Existing tags v1, v2, v3, v3.1, v3.2, v3.3 are never moved.

Ordering rule: the tag is created only on a public commit that already contains the v3.4-citing generator. Tagging the current `main` (3e85c34, generator still cites v3.3) is not allowed.

## Stage A (done on this PR)
Generator cites the tag name only; documents regenerated; QC evidence in `V34_RELEASE_REFERENCE_AND_FREEZE_AUDIT.md`.

## Stage B (only after the author merges the Stage A PR)

B1. Merged master: confirm `MIRROR_TAG = "odd-2020-revision-v3.4-inline"` and the committed `final/` hashes in the freeze audit.

B2. Wait for the normal `sync-to-repos` run (cron every 2 h, or the push run on master). Do not push to or reset public `main` by hand. Record the new public commit `C`:

```
git ls-remote https://github.com/bougtoir/agentic-conservation.git refs/heads/main
```

Accept `C` only if: it is a `wip-sync` fast-forward whose message names the merged wip commit; `3e85c34` and `84f2874036094595f4d7e515133e6c48e2d50c06` are ancestors; no path deleted.

B3. Pre-tag content check at `C` (exact blobs, not file names):
- `src/agentic_conservation/documents_em_odd.py` blob = merged wip `agentic-conservation/src/agentic_conservation/documents_em_odd.py` blob, contains `odd-2020-revision-v3.4-inline`.
- `simulation.py`, `minimal_model.py`, `configs/`, `results/`, `tables/` blobs = wip master (incl. `results/reversal/holdout_psi.csv`, `tables/table9_reversal_predictors.csv`, `tables/table9_reversal_predictors_corrected_v1.csv`, `scripts/correct_b0_historical_metric.py`).
- Present: `odd_resubmission/final_audit_final/operator_audit/`, `…/v34_release/`, Q1–Q3 outputs, prospective Ψ outputs, `manuscript/`, `submission/`, `frozen_cb_rejection_2026-10-26/`.
- Absent: `odd_resubmission/editorial/`, `odd_resubmission/submission/`, `data/raw/odd_2020_sources/`.
- `git ls-remote … 'refs/tags/odd-2020-revision-v3.4-inline*'` empty. If the tag already exists: stop, compare, never overwrite.

B4. Explicit author authorisation required. Then one annotated tag at `C` (no `--force`, no other ref touched):

```
git clone https://github.com/bougtoir/agentic-conservation.git ac-v34 && cd ac-v34
test "$(git rev-parse origin/main)" = "<C>"
git tag -a odd-2020-revision-v3.4-inline <C> \
  -m "ODD 2020 revision (ref. ECOMOD-26-2231): operator-level audit corrections; manuscript cites this tag"
git push origin refs/tags/odd-2020-revision-v3.4-inline
git ls-remote origin 'refs/tags/odd-2020-revision-v3.4-inline*'   # tag object + ^{} = <C>
```

If Devin's credentials cannot push the tag, the author runs the same commands; the release is not finished until `ls-remote` shows it.

B5. Fresh clone by tag (`git clone --branch odd-2020-revision-v3.4-inline --depth 1 …`): `^{}` = `C`; generator cites v3.4; `pytest -q`, `scripts/final_numeric_audit.py`, `make integrated` (response check SKIP expected; no private quotes); rebuilt clean/tracked manuscript, cover letter and PDF compared with the committed package by paragraph text, tables, OMML count, embedded media hashes and PDF page count/text.

B6. Byte differences caused only by DOCX/PDF metadata or ZIP timestamps are reported as such, separately from any substantive difference. Any substantive difference → HOLD.

B7. Write `V34_TAG_PUBLICATION_AUDIT.md` (C, tag object SHA, date, message, clean-clone results) and update `FINAL_HANDOFF.md`. Only then: RELEASE PASS — SUBMIT GO.

## Post-release checks
- v3.3 still → `84f2874036094595f4d7e515133e6c48e2d50c06`; v2 still → `21770296ff24c2b99ea2cc89cff48566176cd608`.
- Public `main` protection remains a separate owner item (ruleset: target `main`, Active, empty bypass, Block force pushes, Restrict deletions). The tag stays valid even if `main` is later overwritten.
