"""Persist public empirical and bibliographic source snapshots."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests

SPECIES = [
    ("przewalski_horse", "Equus ferus przewalskii"),
    ("scimitar_horned_oryx", "Oryx dammah"),
    ("california_condor", "Gymnogyps californianus"),
]
LITERATURE_QUERIES = {
    "przewalski_horse": "Przewalski horse reintroduction conservation",
    "scimitar_horned_oryx": "scimitar horned oryx reintroduction conservation",
    "california_condor": "Gymnogyps californianus reintroduction conservation",
    "decision_theory": "conservation decision making partial observability value information",
}
LEDGER_FIELDS = [
    "source_id",
    "source",
    "url",
    "identifier_version",
    "accessed_utc",
    "retrieval_condition",
    "local_path",
    "file_size",
    "sha256",
    "license",
    "completeness",
]


def _save_response(
    response: requests.Response,
    path: Path,
    *,
    source_id: str,
    source: str,
    identifier_version: str,
    license_text: str,
    completeness: str,
) -> dict[str, str | int]:
    response.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)
    payload = path.read_bytes()
    return {
        "source_id": source_id,
        "source": source,
        "url": response.url,
        "identifier_version": identifier_version,
        "accessed_utc": datetime.now(timezone.utc).isoformat(),
        "retrieval_condition": "HTTP GET; public endpoint; no authentication",
        "local_path": str(path),
        "file_size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "license": license_text,
        "completeness": completeness,
    }


def _get_json(url: str, params: dict[str, object], path: Path, **metadata: str) -> dict:
    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": "agentic-conservation/0.1 (reproducible research)"},
        timeout=90,
    )
    ledger_row = _save_response(response, path, **metadata)
    return {"data": response.json(), "ledger": ledger_row}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_dir = root / "data" / "raw" / timestamp
    ledger_rows: list[dict[str, str | int]] = []
    taxon_matches: dict[str, dict] = {}

    for slug, scientific_name in SPECIES:
        match_params = {"name": scientific_name, "strict": "true", "verbose": "true"}
        match = _get_json(
            "https://api.gbif.org/v1/species/match",
            match_params,
            raw_dir / f"gbif_species_match_{slug}.json",
            source_id=f"gbif-match-{slug}",
            source="GBIF Species API",
            identifier_version="GBIF API v1 species/match",
            license_text="GBIF terms of use; taxonomic metadata",
            completeness="complete API response for the exact submitted name",
        )
        ledger_rows.append(match["ledger"])
        taxon_matches[slug] = match["data"]
        key = match["data"].get("usageKey")
        if key is None:
            raise RuntimeError(f"GBIF did not return a usageKey for {scientific_name}")

        occurrence_params = {
            "taxon_key": key,
            "occurrence_status": "present",
            "has_coordinate": "true",
            "limit": 0,
            "facet": "year",
            "facetLimit": 200,
        }
        occurrence = _get_json(
            "https://api.gbif.org/v1/occurrence/search",
            occurrence_params,
            raw_dir / f"gbif_occurrence_year_facet_{slug}.json",
            source_id=f"gbif-occurrence-{slug}",
            source="GBIF Occurrence API",
            identifier_version=f"taxonKey={key}; {urlencode(occurrence_params)}",
            license_text=(
                "Aggregate GBIF metadata; underlying records retain dataset-specific "
                "CC0/CC BY/CC BY-NC licenses"
            ),
            completeness=(
                "complete year-facet aggregation returned by GBIF for the recorded query; "
                "individual occurrence records were not downloaded"
            ),
        )
        ledger_rows.append(occurrence["ledger"])

    for slug, query in LITERATURE_QUERIES.items():
        crossref_params = {
            "query.bibliographic": query,
            "filter": "type:journal-article",
            "rows": 20,
            "select": (
                "DOI,title,author,published,container-title,URL,type,"
                "is-referenced-by-count,publisher,license"
            ),
        }
        crossref = _get_json(
            "https://api.crossref.org/works",
            crossref_params,
            raw_dir / f"crossref_{slug}.json",
            source_id=f"crossref-{slug}",
            source="Crossref REST API",
            identifier_version=f"query={query}; rows=20",
            license_text="Crossref metadata terms; source-article rights remain with publishers",
            completeness="first 20 relevance-ranked journal-article metadata records",
        )
        ledger_rows.append(crossref["ledger"])

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "species": dict(SPECIES),
        "taxon_matches": taxon_matches,
        "files": ledger_rows,
    }
    manifest_path = raw_dir / "retrieval_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    ledger_path = root / "provenance" / "source_ledger.csv"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, str]] = []
    if ledger_path.exists():
        with ledger_path.open(newline="", encoding="utf-8") as handle:
            existing = list(csv.DictReader(handle))
    with ledger_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=LEDGER_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(existing + ledger_rows)

    print(f"Saved {len(ledger_rows)} immutable source snapshots under {raw_dir}")


if __name__ == "__main__":
    main()
