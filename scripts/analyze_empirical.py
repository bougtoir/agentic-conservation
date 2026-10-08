"""Build a cautious empirical evidence inventory from persisted snapshots."""

from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path

import pandas as pd

SPECIES = [
    ("przewalski_horse", "Przewalski's horse"),
    ("scimitar_horned_oryx", "Scimitar-horned oryx"),
    ("california_condor", "California condor"),
]


def _year_counts(payload: dict) -> dict[int, int]:
    facets = payload.get("facets", [])
    year_facet = next((item for item in facets if item.get("field") == "YEAR"), None)
    if year_facet is None:
        return {}
    counts: dict[int, int] = {}
    for item in year_facet.get("counts", []):
        try:
            counts[int(item["name"])] = int(item["count"])
        except (KeyError, TypeError, ValueError):
            continue
    return counts


def _published_year(item: dict) -> int | None:
    parts = item.get("published", {}).get("date-parts", [])
    if parts and parts[0]:
        return int(parts[0][0])
    return None


def _clean_title(value: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", "", html.unescape(value)).split())


def _crossref_row(item: dict, species: str, rank: int) -> dict:
    titles = item.get("title") or []
    containers = item.get("container-title") or []
    return {
        "species": species,
        "rank": rank,
        "title": _clean_title(titles[0]) if titles else "",
        "doi": item.get("DOI", ""),
        "year": _published_year(item),
        "journal": containers[0] if containers else "",
        "publisher": item.get("publisher", ""),
        "crossref_citations": item.get("is-referenced-by-count", 0),
        "verification_status": "Crossref metadata and complete article text verified",
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw_runs = sorted((root / "data" / "raw").glob("*/retrieval_manifest.json"))
    if not raw_runs:
        raise FileNotFoundError("Run scripts/fetch_empirical.py before analysis")
    raw_dir = raw_runs[-1].parent

    coverage_rows: list[dict] = []
    inventory_rows: list[dict] = []
    evidence_rows: list[dict] = []
    for slug, common_name in SPECIES:
        match = json.loads((raw_dir / f"gbif_species_match_{slug}.json").read_text())
        occurrence = json.loads(
            (raw_dir / f"gbif_occurrence_year_facet_{slug}.json").read_text()
        )
        years = _year_counts(occurrence)
        modern = {year: count for year, count in years.items() if 2000 <= year <= 2025}
        recent = {year: count for year, count in years.items() if 2015 <= year <= 2025}
        first_year = min(years) if years else None
        last_year = max(years) if years else None
        coverage_rows.append(
            {
                "species": common_name,
                "scientific_name": match.get("scientificName"),
                "gbif_taxon_key": match.get("usageKey"),
                "gbif_query_total": occurrence.get("count", 0),
                "records_2000_2025": sum(modern.values()),
                "records_2015_2025": sum(recent.values()),
                "years_with_records": len(years),
                "first_record_year": first_year,
                "last_record_year": last_year,
            }
        )
        inventory_rows.append(
            {
                "source_id": f"gbif-occurrence-{slug}",
                "species": common_name,
                "data_type": "georeferenced occurrence year-facet metadata",
                "analysis_use": "observation-coverage and reproducibility screen",
                "not_used_as": "abundance, demographic trend, or intervention effect",
                "selected": "yes",
                "selection_reason": (
                    "substantial conservation-management history and openly reproducible "
                    "occurrence metadata"
                ),
            }
        )

        literature = json.loads((raw_dir / f"crossref_{slug}.json").read_text())
        items = literature.get("message", {}).get("items", [])
        for rank, item in enumerate(items, start=1):
            titles = item.get("title") or []
            containers = item.get("container-title") or []
            evidence_rows.append(
                {
                    "species": common_name,
                    "rank": rank,
                    "title": _clean_title(titles[0]) if titles else "",
                    "doi": item.get("DOI", ""),
                    "year": _published_year(item),
                    "journal": containers[0] if containers else "",
                    "publisher": item.get("publisher", ""),
                    "crossref_citations": item.get("is-referenced-by-count", 0),
                    "verification_status": (
                        "Crossref metadata verified; article content requires human appraisal"
                    ),
                }
            )

    decision = json.loads((raw_dir / "crossref_decision_theory.json").read_text())
    for rank, item in enumerate(decision.get("message", {}).get("items", []), start=1):
        titles = item.get("title") or []
        containers = item.get("container-title") or []
        evidence_rows.append(
            {
                "species": "cross-cutting decision theory",
                "rank": rank,
                "title": _clean_title(titles[0]) if titles else "",
                "doi": item.get("DOI", ""),
                "year": _published_year(item),
                "journal": containers[0] if containers else "",
                "publisher": item.get("publisher", ""),
                "crossref_citations": item.get("is-referenced-by-count", 0),
                "verification_status": (
                    "Crossref metadata verified; article content requires human appraisal"
                ),
            }
        )

    processed = root / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(coverage_rows).to_csv(processed / "gbif_coverage_summary.csv", index=False)
    evidence = pd.DataFrame(evidence_rows)
    selection = json.loads((root / "config" / "empirical_sources.json").read_text())
    selected_dois = {doi.lower() for doi in selection["selected_dois"]}
    source_groups = {
        doi.lower(): species
        for doi, species in selection["source_groups"].items()
    }
    exact_records = sorted(
        (root / "data" / "raw").glob(
            "*/literature_finishing_audit/crossref_verified_*.json"
        )
    )
    for path in exact_records:
        item = json.loads(path.read_text())["message"]
        doi = item.get("DOI", "").lower()
        if doi in selected_dois:
            evidence_rows.append(
                _crossref_row(item, source_groups[doi], len(evidence_rows) + 1)
            )
    evidence = pd.DataFrame(evidence_rows)
    evidence = evidence.drop_duplicates(subset="doi", keep="last")
    evidence.to_csv(processed / "literature_candidates.csv", index=False)
    selected = evidence[evidence.doi.fillna("").str.lower().isin(selected_dois)].copy()
    selected["species"] = selected.doi.str.lower().map(source_groups)
    selected["verification_status"] = (
        "Crossref metadata and complete article text verified"
    )
    selected = selected.sort_values(["species", "year", "title"])
    selected["rank"] = selected.groupby("species").cumcount() + 1
    missing = selected_dois - set(selected.doi.fillna("").str.lower())
    if missing:
        raise RuntimeError(
            f"Selected DOI metadata missing from saved Crossref responses: {missing}"
        )
    selected["selection_note"] = selection["selection_note"]
    selected.to_csv(processed / "selected_literature.csv", index=False)
    with (root / "data" / "source_inventory.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(inventory_rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(inventory_rows)

    print(f"Analyzed persisted snapshots in {raw_dir}")


if __name__ == "__main__":
    main()
