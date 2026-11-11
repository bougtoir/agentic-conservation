# Empirical evidence audit (Phase 7)

## What empirical material exists

`data/source_inventory.csv` + `provenance/source_ledger.csv` (SHA-256,
UTC, license per artifact):

- GBIF species-match + year-facet occurrence aggregates for
  Przewalski's horse (785 records queried; 700 in 2000–2025),
  scimitar-horned oryx (227; 133), California condor (33,646; 31,951).
- Crossref relevance searches (4 queries, first 20 records each).
- OpenAlex work records + DOI landing pages for 4 exemplar studies
  (local audit preservation).

## Defensible role in the manuscript

GBIF aggregates show that detection-rich, management-linked species
exist at large record volumes (esp. condor). They are used ONLY as
motivational anchors in §2.7 and Table 6. **They are not validation,
calibration, or evidence about any model parameter.**

No defensible licensed demographic parameter (survival/reintroduction
rate) was obtained for direct calibration; consequently ALL parameters
remain class C (synthetic) and the manuscript states this plainly in
§2.7 and §4 (limitations). No Japan-superiority or program-superiority
claims are made from case anecdotes; penguin/panda-style narratives were
excluded.

## Inventory

See `empirical_source_inventory.csv` (generated below).
