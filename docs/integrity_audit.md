# Fabrication and integrity audit

## Passed machine-verifiable checks

- Synthetic species are labeled synthetic.
- Empirical inputs exist as immutable local raw snapshots.
- The source ledger contains retrieval URL, identifier/version, UTC time,
  condition, local path, size, SHA-256, license note, and completeness.
- GBIF summaries derive from saved API responses.
- Bibliography rows match saved exact-DOI Crossref responses.
- Figures and tables are generated from result CSV files.
- Numerical prompts in the authoring packet are read from current result files.
- No author names, affiliations, funding, conflicts, or contributions are
  invented.

## Limits requiring human verification

- {_literature_status(root)} Crossref, OpenAlex, and Semantic Scholar records
  were not treated as evidence of methods or findings beyond retained abstract
  text.
- Human authors must approve the bounded source interpretations and must not
  strengthen them without independently verified evidence.
- GBIF individual occurrence records were not downloaded; only complete
  aggregate year-facet responses for the recorded queries were saved.
- Scientific plausibility and conservation relevance cannot be established by
  tests alone.
- A human must compare the eventual manuscript against
  `results/manuscript_values.csv`.
