from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/raw/20260925T040907Z/literature_finishing_audit"
ACCESSED = "2026-09-25T04:09:07+00:00"

DOIS = {
    "przewalski_gobi": "10.22353/mjbs.2007.05.03",
    "condor_niche": "10.1016/j.biocon.2015.01.002",
    "condor_junk": "10.1017/s095927090700069x",
    "partial_observability": "10.1002/ece3.9197",
}

CITATION_METADATA = {
    DOIS["przewalski_gobi"]: {
        "reference_authors": (
            "Kaczensky P, Ganbaatar O, von Wehrden H, Enksaikhan N, "
            "Lkhagvasuren D, Walzer C"
        ),
        "citation": "Kaczensky et al. 2007",
    },
    DOIS["condor_niche"]: {
        "reference_authors": "D’Elia J, Haig SM, Johnson M, Marcot BG, Young R",
        "citation": "D’Elia et al. 2015",
    },
    DOIS["condor_junk"]: {
        "reference_authors": (
            "Mee A, Rideout BA, Hamber JA, Todd JN, Austin G, Clark M, Wallace MP"
        ),
        "citation": "Mee et al. 2007",
    },
    DOIS["partial_observability"]: {
        "reference_authors": "Williams BK, Brown ED",
        "citation": "Williams & Brown 2022",
    },
}

FIELDS = [
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _record(
    filename: str,
    *,
    source_id: str,
    source: str,
    url: str,
    identifier: str,
    condition: str,
    license_note: str,
    completeness: str,
) -> dict[str, str | int]:
    path = SNAPSHOT / filename
    if not path.exists():
        raise FileNotFoundError(path)
    return {
        "source_id": source_id,
        "source": source,
        "url": url,
        "identifier_version": identifier,
        "accessed_utc": ACCESSED,
        "retrieval_condition": condition,
        "local_path": str(path),
        "file_size": path.stat().st_size,
        "sha256": _sha256(path),
        "license": license_note,
        "completeness": completeness,
    }


def build_records() -> list[dict[str, str | int]]:
    return [
        _record(
            "crossref_verified_przewalski_gobi.json",
            source_id="literature-finishing-crossref-przewalski-gobi",
            source="Crossref REST API",
            url="https://api.crossref.org/works/10.22353/mjbs.2007.05.03",
            identifier="DOI 10.22353/mjbs.2007.05.03; exact work record",
            condition="HTTP GET; public API; no authentication",
            license_note="Crossref metadata terms; article rights remain with publisher",
            completeness="complete exact-DOI Crossref API response",
        ),
        _record(
            "crossref_verified_partial_observability.json",
            source_id="literature-finishing-crossref-partial-observability",
            source="Crossref REST API",
            url="https://api.crossref.org/works/10.1002/ece3.9197",
            identifier="DOI 10.1002/ece3.9197; exact work record",
            condition="HTTP GET; public API; no authentication",
            license_note="Crossref metadata terms; article rights remain with publisher",
            completeness="complete exact-DOI Crossref API response",
        ),
        _record(
            "przewalski_gobi_fulltext.html",
            source_id="literature-finishing-fulltext-przewalski-gobi",
            source="PubMed Central",
            url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3207201/",
            identifier="PMCID PMC3207201; DOI 10.22353/mjbs.2007.05.03",
            condition="HTTP GET; public full-text page; no authentication",
            license_note="PMC copyright notice; local audit preservation only",
            completeness="complete article HTML including references",
        ),
        _record(
            "partial_observability_fulltext.html",
            source_id="literature-finishing-fulltext-partial-observability",
            source="PubMed Central",
            url="https://pmc.ncbi.nlm.nih.gov/articles/PMC9468910/",
            identifier="PMCID PMC9468910; DOI 10.1002/ece3.9197",
            condition="HTTP GET; public full-text page; no authentication",
            license_note="Creative Commons Attribution 4.0",
            completeness="complete article HTML including references",
        ),
        _record(
            "condor_niche_author_manuscript.pdf",
            source_id="literature-finishing-fulltext-condor-niche",
            source="ScholarsArchive@OSU",
            url="https://ir.library.oregonstate.edu/downloads/8w32r719m",
            identifier="DOI 10.1016/j.biocon.2015.01.002; repository copy",
            condition="HTTP GET; public institutional repository; no authentication",
            license_note=(
                "Oregon State University repository terms; local audit preservation "
                "only; redistribution not established"
            ),
            completeness="complete 11-page version-of-record PDF",
        ),
    ]


AUDIT_FIELDS = [
    "claim_id",
    "citation_status",
    "manuscript_section",
    "claim_summary",
    "reference",
    "doi",
    "full_text_access",
    "relevant_section",
    "support_level",
    "notes",
    "required_action",
]


def write_evidence_audit(expansion_rows: list[dict[str, str]]) -> None:
    rows = [
        {
            "claim_id": "LIT-01",
            "citation_status": "CITED",
            "manuscript_section": "Introduction",
            "claim_summary": (
                "A Przewalski's horse reintroduction developed from captive-born "
                "release toward standardized monitoring and broader ecosystem work."
            ),
            "reference": "Kaczensky et al. (2007)",
            "doi": DOIS["przewalski_gobi"],
            "full_text_access": "FULL_TEXT_LOCAL",
            "relevant_section": "Abstract; Introduction; Monitoring; Conclusion",
            "support_level": "DIRECT",
            "notes": (
                "The complete PMC article reports transport of captive-born horses "
                "in 1992, release in 1997, wild-born foals in 1999, standardized "
                "monitoring from 2002, and expansion toward ecosystem conservation."
            ),
            "required_action": "Keep the claim bounded to this documented project.",
        },
        {
            "claim_id": "LIT-02",
            "citation_status": "CITED",
            "manuscript_section": "Introduction",
            "claim_summary": (
                "Activity-specific niche models evaluated with withheld data can "
                "inform condor reintroduction screening, but site selection still "
                "requires ground reconnaissance and unmodeled-threat assessment."
            ),
            "reference": "D’Elia et al. (2015)",
            "doi": DOIS["condor_niche"],
            "full_text_access": "FULL_TEXT_LOCAL",
            "relevant_section": "Abstract; Methods; Results; Discussion",
            "support_level": "DIRECT",
            "notes": (
                "The complete repository PDF describes nesting, roosting, and "
                "feeding models, evaluation with withheld occurrence data, candidate "
                "areas, projection uncertainty, and the need for reconnaissance and "
                "threat information outside the models."
            ),
            "required_action": "Do not treat modeled suitability as site validation.",
        },
        {
            "claim_id": "LIT-03",
            "citation_status": "CITED",
            "manuscript_section": "Introduction",
            "claim_summary": (
                "Anthropogenic material ingestion contributed to nestling mortality "
                "and low nest success in a reintroduced southern California condor "
                "population."
            ),
            "reference": "Mee et al. (2007)",
            "doi": DOIS["condor_junk"],
            "full_text_access": "FULL_TEXT_LOCAL",
            "relevant_section": "Summary; Methods; Results; Discussion",
            "support_level": "DIRECT",
            "notes": (
                "The complete publisher PDF reports nine wild-hatched nestlings, six "
                "deaths near nests, two removals for health reasons, and two deaths "
                "attributed to junk ingestion; historical comparisons are qualified."
            ),
            "required_action": "Keep the claim population- and period-specific.",
        },
        {
            "claim_id": "LIT-04",
            "citation_status": "CITED",
            "manuscript_section": "Introduction and Methods",
            "claim_summary": (
                "Ecological decisions under partial observability distinguish hidden "
                "states from observations and track belief states, with substantial "
                "computational and interpretive costs."
            ),
            "reference": "Williams & Brown (2022)",
            "doi": DOIS["partial_observability"],
            "full_text_access": "FULL_TEXT_LOCAL",
            "relevant_section": "Introduction; Process specification; Discussion",
            "support_level": "DIRECT",
            "notes": (
                "The complete CC BY article defines states, observations, actions, "
                "returns, and belief-state updating and discusses scaling, solution, "
                "and interpretation challenges in ecological POMDPs."
            ),
            "required_action": (
                "Do not imply that the present heuristic simulation solves a POMDP."
            ),
        },
        {
            "claim_id": "EXC-01",
            "citation_status": "EXCLUDED",
            "manuscript_section": "Not cited",
            "claim_summary": "Former reintroduction-planning background citation.",
            "reference": "Van Dierendonck & Wallis de Vries (1996)",
            "doi": "10.1046/j.1523-1739.1996.10030728.x",
            "full_text_access": "ABSTRACT_ONLY",
            "relevant_section": "OpenAlex-indexed abstract",
            "support_level": "NOT_VERIFIED",
            "notes": "Complete article text was not obtained.",
            "required_action": "Excluded from the final citation set and substantive claims.",
        },
        {
            "claim_id": "EXC-02",
            "citation_status": "EXCLUDED",
            "manuscript_section": "Not cited",
            "claim_summary": "Former Przewalski's horse case citation.",
            "reference": "Xia et al. (2014)",
            "doi": "10.1016/j.biocon.2014.06.021",
            "full_text_access": "METADATA_ONLY",
            "relevant_section": "Title and bibliographic metadata",
            "support_level": "NOT_VERIFIED",
            "notes": "Complete article text was not obtained.",
            "required_action": "Excluded from the final citation set and substantive claims.",
        },
        {
            "claim_id": "EXC-03",
            "citation_status": "EXCLUDED",
            "manuscript_section": "Not cited",
            "claim_summary": "Former scimitar-horned oryx genetics citation.",
            "reference": "Ogden et al. (2020)",
            "doi": "10.1016/j.biocon.2019.108244",
            "full_text_access": "METADATA_ONLY",
            "relevant_section": "Title and bibliographic metadata",
            "support_level": "NOT_VERIFIED",
            "notes": (
                "The indexed repository file was blocked by an access-control "
                "challenge; no article text was obtained."
            ),
            "required_action": "Excluded from the final citation set and substantive claims.",
        },
        {
            "claim_id": "EXC-04",
            "citation_status": "EXCLUDED",
            "manuscript_section": "Not cited",
            "claim_summary": "Former value-of-information background citation.",
            "reference": "Moore & Runge (2012)",
            "doi": "10.1111/j.1523-1739.2012.01907.x",
            "full_text_access": "ABSTRACT_ONLY",
            "relevant_section": "OpenAlex-indexed abstract",
            "support_level": "NOT_VERIFIED",
            "notes": "Complete article text was not obtained.",
            "required_action": "Excluded from the final citation set and substantive claims.",
        },
        {
            "claim_id": "EXC-05",
            "citation_status": "EXCLUDED",
            "manuscript_section": "Not cited",
            "claim_summary": "Former partial-observability background citation.",
            "reference": "Memarzadeh & Boettiger (2018)",
            "doi": "10.1016/j.biocon.2018.05.009",
            "full_text_access": "METADATA_ONLY",
            "relevant_section": "Title and bibliographic metadata",
            "support_level": "NOT_VERIFIED",
            "notes": "Complete article text was not obtained.",
            "required_action": "Excluded from the final citation set and substantive claims.",
        },
    ]
    audit_path = ROOT / "provenance/literature_claim_audit.csv"
    with audit_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(
            [row for row in rows if row["citation_status"] == "CITED"]
            + expansion_rows
            + [row for row in rows if row["citation_status"] != "CITED"]
        )

    docs = ROOT / "docs/literature_claim_audit.md"
    docs.write_text(
        """# Literature claim audit

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
""",
        encoding="utf-8",
    )


EXPANSION_CANDIDATES = ROOT / "data/manual/literature_expansion_candidates.tsv"
EXPANSION_CLAIMS = ROOT / "data/manual/literature_expansion_claims.csv"
CORE_KEYS = ROOT / "data/manual/literature_core_metadata.tsv"
METADATA_CORRECTIONS = {
    # Crossref splits "L. Michael Romero" into given "L." and family "Michael Romero".
    "10.1016/j.biocon.2010.02.032": {"authors": ("Michael Romero L", "Romero LM")},
    # Crossref article-number repeats the DOI suffix; the e-location is 20210007.
    "10.1098/rsbl.2021.0007": {"pages": "20210007"},
    # Crossref has no pages; the retained PMC full text cites 5(1-2):13-18.
    "10.22353/mjbs.2007.05.03": {"pages": "13-18"},
}
BIBLIOGRAPHY_FIELDS = [
    "key",
    "doi",
    "reference_authors",
    "citation",
    "year",
    "title",
    "journal",
    "volume",
    "issue",
    "pages",
    "evidence_level",
    "crossref_path",
    "abstract_path",
]


def _read_tsv(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8") as handle:
        return {
            line.split("\t")[0]: line.split("\t")[1]
            for line in handle.read().splitlines()
            if line.strip()
        }


def _expansion_manifests() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = "*/literature_expansion/retrieval_manifest.csv"
    for manifest in sorted((ROOT / "data/raw").glob(pattern)):
        with manifest.open(newline="", encoding="utf-8") as handle:
            rows.extend(csv.DictReader(handle))
    return rows


def _latest(manifests: list[dict[str, str]], key: str, source: str) -> list[Path]:
    paths = [
        ROOT / row["local_path"]
        for row in manifests
        if row["key"] == key and row["source"].startswith(source) and row["http_status"] == "200"
    ]
    return sorted(paths, key=lambda path: path.parts[-3], reverse=True)


def _family(name: str) -> str:
    if not re.search(r"[A-Z]{3}", name):
        return name
    if name.startswith("Mc"):
        return "Mc" + name[2:].capitalize()
    return "-".join(part.capitalize() for part in name.split("-"))


def _initials(given: str) -> str:
    parts = re.split(r"[\s.]+", given.strip())
    return "".join(
        "-".join(piece[0] for piece in part.split("-") if piece) for part in parts if part
    )


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", html.unescape(text)).replace("\u2010", "-")
    return re.sub(r"\s+", " ", text).strip()


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _clean(text).lower())


def _abstract(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    inverted = payload.get("abstract_inverted_index") or {}
    if inverted:
        positions = {pos: word for word, places in inverted.items() for pos in places}
        return " ".join(positions[index] for index in sorted(positions))
    return payload.get("abstract") or ""


def build_bibliography() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    manifests = _expansion_manifests()
    candidates = _read_tsv(EXPANSION_CANDIDATES)
    core = _read_tsv(CORE_KEYS)
    with EXPANSION_CLAIMS.open(newline="", encoding="utf-8") as handle:
        claims = list(csv.DictReader(handle))
    core_citations = {doi: CITATION_METADATA[doi] for doi in core.values()}
    bibliography = []
    audit_rows = []
    for key, doi in [*core.items(), *[(row["key"], candidates[row["key"]]) for row in claims]]:
        crossref_path = _latest(manifests, key, "Crossref")[0]
        message = json.loads(crossref_path.read_text(encoding="utf-8"))["message"]
        if message["DOI"].lower() != doi.lower():
            raise RuntimeError(f"Crossref DOI mismatch for {key}")
        dated = message.get("published-print") or message["issued"]
        year = str(dated["date-parts"][0][0])
        if doi in core_citations:
            authors = core_citations[doi]["reference_authors"]
            citation = core_citations[doi]["citation"]
            families = []
        else:
            people = [person for person in message["author"] if "family" in person]
            families = [_family(person["family"]) for person in people]
            authors = ", ".join(
                f"{_family(person['family'])} {_initials(person.get('given', ''))}".strip()
                for person in people
            )
            lead = families[0]
            if len(families) == 1:
                citation = f"{lead} {year}"
            elif len(families) == 2:
                citation = f"{lead} & {families[1]} {year}"
            else:
                citation = f"{lead} et al. {year}"
        authors = _clean(authors)
        pages = message.get("page") or message.get("article-number", "")
        correction = METADATA_CORRECTIONS.get(doi, {})
        if "authors" in correction:
            authors = authors.replace(*correction["authors"])
        pages = correction.get("pages", pages)
        abstract_path = ""
        evidence = "FULL_TEXT_LOCAL" if doi in core_citations else "METADATA_ONLY"
        for source in ["OpenAlex", "Semantic"]:
            for path in _latest(manifests, key, source):
                if doi not in core_citations and evidence == "METADATA_ONLY" and _abstract(path):
                    abstract_path = str(path.relative_to(ROOT))
                    evidence = "ABSTRACT_LOCAL"
        bibliography.append(
            {
                "key": key,
                "doi": doi,
                "reference_authors": authors,
                "citation": citation,
                "year": year,
                "title": _clean(message["title"][0]),
                "journal": _clean(message["container-title"][0]),
                "volume": message.get("volume", ""),
                "issue": message.get("issue", ""),
                "pages": pages,
                "evidence_level": evidence,
                "crossref_path": str(crossref_path.relative_to(ROOT)),
                "abstract_path": abstract_path,
            }
        )
    by_key = {row["key"]: row for row in bibliography}
    for index, claim in enumerate(claims, start=5):
        entry = by_key[claim["key"]]
        abstract_based = claim["evidence_basis"] == "ABSTRACT"
        if abstract_based and entry["evidence_level"] != "ABSTRACT_LOCAL":
            raise RuntimeError(f"No retained author abstract for {claim['key']}")
        haystack = entry["title"]
        if abstract_based:
            haystack += " " + _abstract(ROOT / entry["abstract_path"])
        fragments = [part.strip() for part in claim["evidence_excerpt"].split(";")]
        missing = [part for part in fragments if _normalize(part) not in _normalize(haystack)]
        if missing:
            raise RuntimeError(f"Evidence excerpt not found for {claim['key']}: {missing}")
        audit_rows.append(
            {
                "claim_id": f"LIT-{index:02d}",
                "citation_status": "CITED",
                "manuscript_section": claim["manuscript_section"],
                "claim_summary": claim["claim_summary"],
                "reference": entry["citation"].rsplit(" ", 1)[0] + f" ({entry['year']})",
                "doi": entry["doi"],
                "full_text_access": entry["evidence_level"],
                "relevant_section": "Author abstract" if abstract_based else "Verified title",
                "support_level": "ABSTRACT_DIRECT" if abstract_based else "TITLE_BOUNDED",
                "notes": (
                    "Exact-DOI Crossref metadata verified; supporting text: "
                    f"{claim['evidence_excerpt']}"
                ),
                "required_action": (
                    "Background citation only; do not strengthen beyond the "
                    + ("abstract." if abstract_based else "article title.")
                ),
            }
        )
    path = ROOT / "data/processed/bibliography.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=BIBLIOGRAPHY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(bibliography)
    ledger = [
        {
            "source_id": (
                f"literature-expansion-{row['key']}-{row['source'].split()[0].lower()}-"
                f"{Path(row['local_path']).parts[-3]}"
            ),
            "source": row["source"],
            "url": row["url"],
            "identifier_version": f"DOI {row['doi']}; exact-DOI API response",
            "accessed_utc": row["accessed_utc"],
            "retrieval_condition": f"HTTP GET; public endpoint; status {row['http_status']}",
            "local_path": str(ROOT / row["local_path"]),
            "file_size": row["file_size"],
            "sha256": row["sha256"],
            "license": row["license"],
            "completeness": row["completeness"],
        }
        for row in manifests
    ]
    return audit_rows, ledger


def add_condor_junk_record(existing: list[dict[str, str]]) -> None:
    old_snapshot = ROOT / "data/raw/20260925T004616Z/literature_fulltext_audit"
    path = old_snapshot / "condor_junk_fulltext.pdf"
    if not path.exists():
        raise FileNotFoundError(path)
    source_id = "literature-audit-fulltext-condor-junk"
    if any(row["source_id"] == source_id for row in existing):
        return
    existing.append(
        {
            "source_id": source_id,
            "source": "Cambridge Core",
            "url": (
                "https://www.cambridge.org/core/services/aop-cambridge-core/"
                "content/view/363E14BD4E4068AD8D9E5E2467905E65/"
                "S095927090700069Xa.pdf"
            ),
            "identifier_version": (
                "DOI 10.1017/s095927090700069x; publisher PDF"
            ),
            "accessed_utc": "2026-09-25T00:46:16+00:00",
            "retrieval_condition": (
                "HTTP GET; public publisher PDF; no authentication"
            ),
            "local_path": str(path),
            "file_size": path.stat().st_size,
            "sha256": _sha256(path),
            "license": "publisher terms; local audit preservation only",
            "completeness": (
                "complete 12-page publisher PDF; redistribution not established"
            ),
        }
    )


def main() -> None:
    records = build_records()
    manifest = SNAPSHOT / "retrieval_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

    ledger_path = ROOT / "provenance/source_ledger.csv"
    with ledger_path.open(newline="", encoding="utf-8") as handle:
        existing = list(csv.DictReader(handle))
    expansion_rows, expansion_ledger = build_bibliography()
    current_ids = {row["source_id"] for row in records + expansion_ledger}
    existing = [row for row in existing if row["source_id"] not in current_ids]
    add_condor_junk_record(existing)
    with ledger_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(existing + records + expansion_ledger)

    write_evidence_audit(expansion_rows)

    citation_path = ROOT / "data/processed/literature_citation_metadata.csv"
    with citation_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["doi", "reference_authors", "citation", "metadata_source"],
            lineterminator="\n",
        )
        writer.writeheader()
        for doi, metadata in CITATION_METADATA.items():
            writer.writerow(
                {
                    "doi": doi,
                    **metadata,
                    "metadata_source": (
                        "complete article plus retained Crossref or PMC metadata"
                    ),
                }
            )


if __name__ == "__main__":
    main()
