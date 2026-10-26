# Literature claim audit

The anonymous manuscript cites four case and decision-theory sources whose
complete article text was lawfully obtained and inspected, plus additional
background sources whose DOI, authors, title, year, journal, volume, and pages
were verified against persisted exact-DOI Crossref responses
(`data/raw/*/literature_expansion/`). For those background sources the claim
support is recorded separately in `provenance/literature_claim_audit.csv`:

- `ABSTRACT_LOCAL` / `ABSTRACT_DIRECT`: the bounded manuscript statement is
  directly supported by the author abstract retained in the OpenAlex or
  Semantic Scholar response;
- `METADATA_ONLY` / `TITLE_BOUNDED`: no author abstract was available; the
  manuscript statement is restricted to what the verified article title states.

Machine-generated summaries are not used as evidence. No background source is
represented as read in full, and none calibrates a model parameter or validates
a simulated policy effect. The four full-text-verified sources are:

- Kaczensky et al. (2007) directly supports a bounded account of captive-born
  Przewalski's horse release, standardized monitoring, and expansion toward
  ecosystem conservation.
- D’Elia et al. (2015) directly supports activity-specific niche modeling with
  withheld-data evaluation for condor reintroduction screening, together with
  explicit cautions about projection, ground reconnaissance, and unmodeled
  threats.
- Mee et al. (2007) directly supports a population- and period-specific claim
  about anthropogenic-material ingestion, nestling mortality, and low nest
  success in reintroduced southern California condors.
- Williams and Brown (2022) directly supports separating hidden ecological
  states from observations and using belief states in partially observable
  decisions, while documenting computational and interpretive limitations.

Five formerly selected sources remain `NOT_VERIFIED` and excluded. They are
retained in the machine-readable audit and are not cited.

Full-text snapshots with unclear redistribution rights remain in durable local
project storage and are recorded by URL, identifier, UTC retrieval time,
retrieval condition, local path, size, SHA-256, license note, and completeness
in `provenance/source_ledger.csv`. They are not included in the public archive.
