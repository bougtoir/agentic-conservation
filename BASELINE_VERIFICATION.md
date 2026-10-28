# BASELINE VERIFICATION — reversal-theory phase

Date: 2026-10-27. Verifier: Devin session devin-36254e97b0fe4a95a9e92a3a5c424e15.

## Merge / baseline

- PR #733 (Ecological Modelling retarget): merged into master.
- Baseline commit used for this phase: `df40a91fd3efd2d2cd6604c60fea4d83225a759f`
  ("Merge pull request #733"). All new work branches from this commit.
- Feature branch: `devin/1793300000-reversal-theory` (sequential, single VM).

## Environment

- Python 3.10, `PYTHONPATH=src` (no installed package; pyproject lacks PEP-660 backend).
- Test suite: `python -m pytest tests/` → **35 passed** on the baseline.
- Lint: `ruff check src/` → clean on the baseline.
- Repro entrypoint: `scripts/run_pipeline.py` (pipeline registry in
  `results/checkpoints/pipeline.json`); analysis runs via
  `src/agentic_conservation/analysis.py` (`execute_specs`, RunSpec).

## Baseline artifacts (hashes)

- `results/threshold_sweeps.csv` SHA-256: `ec3e3e7ccdce20cc8fe6cba317f972a13e0adbda5ac5c99c5cc4494e94b0b2ea`
  (3000 paired-seed runs: S4/S6/S7 × 125 sweep cells × 8 reps).
- `results/threshold_cell_stability.csv` SHA-256: `ffb30df00ee7f76ed90dda525de04856231b1c80bf6fde42f2ea74fa288aede8`
  (per-cell sign estimates; 125 cells × n∈{2,4,8}).
- Registry: `results/checkpoints/pipeline.json`.

## Frozen outputs carried forward (unchanged by this phase)

- S6 survival_100 = 0.529 [0, 0.875]; S7 = 0.473 [0.125, 0.75].
- Sweep rollup: 35 robust S7-favoured, 26 robust S6-favoured, 64 indeterminate cells.
- Information (perfect-current-state) effect: −0.003 [−0.112, 0.131].
- Pareto-non-dominated policies: S0, S1, S3, S4, S6, S7.

## Commands

```
git checkout df40a91fd3efd2d2cd6604c60fea4d83225a759f
git checkout -b devin/1793300000-reversal-theory
cd agentic-conservation && PYTHONPATH=src python -m pytest tests -q
```

JCR quartile verification is explicitly deferred per the phase brief and
does not gate this work. No submission, merge, or release without
explicit user approval.
