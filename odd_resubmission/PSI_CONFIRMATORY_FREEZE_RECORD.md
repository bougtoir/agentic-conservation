# Ψ confirmatory freeze record

- Freeze commit: `947d8f59cb71f59d5f95040edfb0dbda26de8245`
- Commit time (UTC): 2026-11-10T01:46:43Z
- Branch: `devin/1794264760-em-odd-resubmission-gate`
- No IBM run on the confirmatory configurations had started at this time. `results/psi_confirmatory/` contained only `designs.csv` and `psi_predictions.csv`.

| File | SHA-256 at freeze |
|---|---|
| results/psi_confirmatory/designs.csv | 53096b7a4efe1a137d158bd91cf9d6bb534ec2a0f6e1aa21d1a81ec11b47b2e1 |
| results/psi_confirmatory/psi_predictions.csv | b137f140cdf426ca2ea81526d09e672036ea7a8eab238353c0f6622c691fd85c |
| scripts/psi_confirmatory.py | 348482199545c358b6af20817630c763b4cb3cca16ef3e92feb066a304a0e06d |
| src/agentic_conservation/minimal_model.py | eee300a23f7599b5aab6ff4162fefd0016a661b53490c1dc67583a2443b5a4a2 |

Frozen predictions: 24 cells S7-favoured and 36 cells S6-favoured (Ψ range −3.20 to 2.96).

## Execution log (appended after freeze; no change to frozen content)
- 2026-11-10T03:06:48Z: confirmatory `ibm` stage was started in error while Q3 stage 2 (last perturbation, `e11_habitat_mortality@1.5`) was still running, contrary to the plan's "after Q1–Q3" ordering.
- 2026-11-10T03:08:14Z: that process was killed. `ibm_runs.csv` is written only on completion, so no confirmatory outcome was written or seen. Designs and predictions were not touched.
- 2026-11-10T03:14:09Z: Q1–Q3 chain finished.
- 2026-11-10T03:14:20Z: confirmatory `ibm` stage restarted from scratch (same frozen designs, predictions, seeds).
