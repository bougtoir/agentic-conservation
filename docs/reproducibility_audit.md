# Reproducibility audit

## Current build

- Pipeline mode: `full`.
- Policy replications: 192.
- Analysis sizes and replicate counts are versioned in `config/analysis.json`.
- Nested policy convergence was audited through 384 paired replications.
- Sensitivity replicates are aggregated to the design level before inference.
- All five two-factor sweeps have cell-level sign-stability outputs.
- Raw API snapshots are under `data/raw/` and are never overwritten.
- Source and run manifests retain SHA-256 checksums.
- Figures are emitted as SVG, PDF, and 320-dpi PNG.
- Tables are emitted as CSV and Markdown.
- Tests exercise budget, origin-collapse, captivity, latent-species,
  survey-cost, unlimited-budget, relocation, and movement-disease behavior.

## Reproduction sequence

```text
python3 -m pip install -r requirements-dev.txt
make empirical
make full
make audit
make figures
make package
make test
make lint
```

`make empirical` operates on the latest persisted raw snapshot and requires no
network. `make fetch` is used only to create a new immutable source version.

## Qualification

Re-running from the same raw snapshots, code commit, Python environment, and
seeds is deterministic. A fresh `make fetch` can change public-source
summaries and must be treated as a new data version.
