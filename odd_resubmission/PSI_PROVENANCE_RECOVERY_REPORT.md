# PSI_PROVENANCE_RECOVERY_GATE — recovery report

Status: **PROVENANCE RECOVERED; ORIGINAL CLAIM NOT SUPPORTED AS STATED.**
The stored Ψ values are reproduced exactly. They do **not** come from the documented frozen model.

## 1. Question
`results/reversal/holdout_psi.csv` (commit f964b66) was not reproducible from any committed code (0/56 cells, any MIN_BREEDING_POP). The documents also said `MIN_BREEDING_POP = 8` while the code defaults to 4.

## 2. Evidence used
- Git history: f964b66 (03:30:53Z), b5538ee, ba665ea (05:09:07Z); PR #744 and #749 descriptions; branch `origin/devin/1793300000-reversal-theory`.
- The generating session's event log, `36254e97b0fe4a95a9e92a3a5c424e15`: exact shell commands, heredoc patch text, file-edit records with line counts, and process outputs.
- No other branch, stash, or archived script contains another version of `minimal_model.py`; `git log --all` on the file lists only f964b66 and this branch.
- The session's `/tmp/reversal.log` is not recoverable (the VM's temp directory). Its tails, as quoted in the session log, contain progress lines only.

## 3. Recovered generating implementation
The holdout run started at 2026-10-28T03:06:31Z. Two Ψ-relevant edits were applied to `minimal_model.py` after it started (03:08:29Z, 03:08:58Z). Both patches are recorded verbatim in the session log. Reversing exactly these two patches on the f964b66 file gives **V0**:

| Element | V0 (generated holdout_psi.csv) | V1 (committed f964b66 / current default) |
|---|---|---|
| Latent discovery | per-individual: `discovered = ell * p_detect` each year | whole cohort at `t >= ceil(1/(p_detect·detectability))` |
| Ψ log-ratio floor `eps` | 1e-9 | 0.02 |
| `MIN_BREEDING_POP` | 4.0 (default; no override) | 4.0 (default) |
| Everything else | identical (other post-launch edits only add the `moved` output; then `ruff format`) | — |

Reproduction (`psi_forensics/reproduce_holdout_psi.py`, output `holdout_psi_reproduction_check.csv`):

| Candidate | Max abs diff (Ψ) | Exact cells | Sign agreement |
|---|---|---|---|
| committed f964b66 | 19.47 | 0/56 | 37/56 |
| **V0, MBP = 4** | **3.6e-15** | **56/56** | **56/56** |
| V0, MBP = 8 | 1.00 | 0/56 | 39/56 |

The V0/MBP = 4 result was identified by mechanism, not by accuracy. It is the only configuration consistent with the recorded launch state, and it reproduces Ψ and both channels to floating-point precision. MBP = 8 is excluded by the data. Accuracy played no part in the identification.

## 4. MIN_BREEDING_POP = 8 vs 4: resolved
- At 03:02:42Z MBP became a config key with **default 4.0**. A development sweep then passed MBP only as an override: dev accuracy 0.608 at 4 and 0.896 at 8.
- `THEORY_GO_NO_GO.md` (03:05:42Z) and PR #744 then documented "MBP = 8 frozen; dev 0.896". **The code default was never changed to 8**, and no run used 8 except the sweep.
- **Correct record**: MBP = 8 was *selected* on development data but *never implemented*. Both the holdout run (V0) and the committed model (V1) use 4. The "MBP = 8" statement in THEORY_GO_NO_GO.md, MINIMAL_MODEL_SPECIFICATION.md, HOLDOUT_PROTOCOL_AND_RESULTS.md, FINAL_HARDCODE_AUDIT.md, FINAL_QC_REPORT.md, FINAL_HOSTILE_REVIEW.md, PR #744, and the derived manuscript text is **incorrect**.

## 5. Metrics by recovered version
Script: `psi_forensics/dev_and_holdout_by_version.py`. Holdout signs come from the unchanged `holdout_metrics.csv`; regret uses the registry definition.

| Version | Dev all | Dev det | Holdout all | Holdout det | Regret Ψ |
|---|---|---|---|---|---|
| **V0, MBP = 4 (generated the registry)** | **0.608** | 0.623 | **0.393** | **0.846** | **0.0450** |
| V1, MBP = 4 (committed; produced the dev registry 0.888) | 0.888 | 0.910 | 0.446 | 0.962 | 0.0104 |
| V0, MBP = 8 (counterfactual; never run) | 0.896 | 0.918 | 0.429 | 0.923 | 0.0164 |
| V1, MBP = 8 (counterfactual) | 0.848 | 0.869 | 0.446 | 0.962 | 0.0113 |

The two counterfactual rows are shown for completeness only. **None of them is put forward as the "original" or as a validation result.**

## 6. Consequences (binding for the revision)
1. The registry holdout values (0.846 / 0.393 / 0.045) **are reproducible** from V0. They evaluate V0, a model with development accuracy 0.608, that was never documented, never committed, and is not the model described in the manuscript.
2. The manuscript pairs V1 development accuracy (0.888 / 0.910) with V0 holdout accuracy, and describes the model as "frozen at MBP = 8". **This is a model–implementation contradiction in the reported validation.**
3. **Withdrawn claim**: that the original holdout is an independently reproducible evaluation of the frozen model described in the manuscript. V0 is now reproducible, but it was not the described or frozen model.
4. V1 holdout values (0.962 / 0.446 / 0.0104) remain **exploratory**. V1 was finalised (03:10Z) before any holdout outcome was read (03:26Z), and the edits were driven by a unit test. However, V1 was never pre-specified for the holdout, its post-launch changes were not disclosed, and its evaluation was first run only after the original holdout had been inspected. Per the author's instruction, it is not used as validation.
5. No registry, CSV, or historical document was modified. Forensic files are in `odd_resubmission/psi_forensics/`, with checksums in `SHA256SUMS.txt`.

## 7. Gate verdict
PSI_PROVENANCE_RECOVERY_GATE: **PASS for provenance** (the generating implementation is identified exactly). **FAIL for the original validation claim**, which is withdrawn. Ψ validation now depends on the new prospective confirmatory evaluation (PSI_CONFIRMATORY_VALIDATION_PLAN.md).
