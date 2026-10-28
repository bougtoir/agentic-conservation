# Final QC Report — Reversal Theory Package

## Checks performed

1. **Tests**: `PYTHONPATH=src python3 -m pytest tests/ -q` — all pass (35 baseline
   + 8 new minimal-model tests, incl. limiting cases: no circulation ⇒ no channel,
   deadly relocation shrinks channel, latent-blocks-circulation).
2. **Lint**: `ruff check src/ scripts/ tests/` — clean.
3. **Number traceability**: every statistic in the theory documents is computed
   from `results/reversal/*.csv` or `results/threshold_*.csv`; see
   FINAL_HARDCODE_AUDIT.md for the mapping.
4. **Reproduction commands**:
   - minimal-model dev predictions:
     `PYTHONPATH=src python3 -c "from agentic_conservation.minimal_model import load_config, psi_index; ..."` (see results/minimal_model_dev_predictions.csv)
   - full pipeline: `nohup python3 scripts/run_reversal_theory.py all` (~18 min,
     writes results/reversal/*.csv)
   - IBM baseline: `pytest tests/test_simulation.py`
5. **Hostile review**: FINAL_HOSTILE_REVIEW.md — six attacks documented, residual
   weaknesses disclosed.
6. **Fabrication audit**: FINAL_HARDCODE_AUDIT.md — no hand-entered IBM outputs;
   one stale-artifact note (factorial_variants seed column) disclosed and fixed
   in the script.

## Known limitations (carried into handoff)

- Ψ cannot abstain; near-boundary |Ψ| < 0.2 predictions are unreliable (17%).
- MIN_BREEDING_POP=8 fitted on dev; boundary position sensitive to it.
- Attribution pairing lost via seed-column bug (means unaffected; SEs wider).
- Verdict B means manuscript integration is allowed but only as a bounded,
  conditional claim — see THEORY_GO_NO_GO.md.
