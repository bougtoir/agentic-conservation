# Agentic Conservation under the Anthropocene

Reproducible synthetic simulation and empirical source audit for a potential
*Conservation Biology* Contributed Paper. The project asks when dynamic
conservation networks spanning wild and managed environments differ from fixed
strategies under environmental change, partial observability, heterogeneous
individuals, latent biodiversity, finite budgets, and conflicting objectives.

The model is a transparent research instrument, not a recommendation engine.
It is designed to expose trade-offs and reversal conditions. Synthetic
outcomes are never presented as empirical estimates.

The simulation represents 9 node types, individual animals, 5 initially known
species, 3 latent species, S0–S7 policies, noisy observations, staged discovery,
disease, genetics, welfare, biobanking, engagement feedback, and explicit
annual budgets. Synthetic outcomes and empirical data-availability evidence are
kept separate.

## Reproduce

```bash
python3 -m pip install -r requirements-dev.txt
make fetch       # persist immutable GBIF and Crossref snapshots
make empirical   # analyze only the persisted snapshots
make quick       # smoke-scale analysis
make full        # production Monte Carlo and robustness analysis
make figures     # figures, tables, and values registry
make package     # inline DOCX, figure deck, audits, and submission ZIP
make test
make lint
```

`make full` uses two local worker processes on one VM. It does not use child
sessions, remote workers, distributed computing, or external analysis
services.

## Main structure

- `config/`: base model, species, nodes, and empirical source selection.
- `src/agentic_conservation/`: simulation and analysis implementation.
- `scripts/`: retrieval, analysis, output, and packaging entry points.
- `data/raw/`: immutable timestamped public-source snapshots.
- `data/processed/`: reproducible empirical summaries.
- `results/`: Monte Carlo, sensitivity, threshold, ablation, and registry data.
- `figures/`: separate PNG (320 dpi), PDF, and SVG figure files.
- `tables/`: CSV and Markdown tables.
- `manuscript/`: human-authoring and submission-support materials.
- `provenance/`: source ledger, environment, run manifest, and checksums.
- `docs/`: journal requirements, model specification, and audits.

## Scientific boundaries

- The eight modeled species are synthetic. Five are initially observed and
  three are latent to decision makers.
- GBIF records are used only to compare open observation coverage. They are
  not interpreted as abundance, trend, occupancy, or intervention effects.
- Crossref records verify bibliographic metadata only. Article-level claims
  require human reading and appraisal.
- Results depend on explicit toy-model assumptions and prespecified policy
  allocations. They do not establish that circulation, captivity, habitat
  protection, assisted colonization, or return to origin is generally best.
- The final manuscript must be written and scientifically interpreted by
  accountable human authors. The generated inline DOCX is explicitly labeled
  as a human-review draft and is not a submission-ready final manuscript.
- `FIGURE_DECK.pptx` has editable title and caption text, but its artwork is
  image-based. Edit figure code or result sources and run `make figures` to
  regenerate axes, series, labels, and separate PNG/PDF/SVG files.

## Key reproducibility records

- `results/manuscript_values.csv` traces proposed numbers to result files and
  code.
- `provenance/source_ledger.csv` records URL, access time, local snapshot,
  size, SHA-256, license note, and completeness.
- `provenance/run_manifest.json` records the production configuration and
  output hashes.
- `FINAL_REPORT.md` gives the project-level completion and limitation audit.
