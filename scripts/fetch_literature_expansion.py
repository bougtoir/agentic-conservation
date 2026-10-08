from __future__ import annotations

import csv
import hashlib
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data/manual/literature_expansion_candidates.tsv"
USER_AGENT = "agentic-conservation-literature-audit/1.0 (mailto:research@example.org)"
FIELDS = [
    "key",
    "doi",
    "source",
    "url",
    "accessed_utc",
    "http_status",
    "local_path",
    "file_size",
    "sha256",
    "license",
    "completeness",
]


def _get(url: str) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def main(stamp: str, candidates_path: Path) -> None:
    snapshot = ROOT / "data/raw" / stamp / "literature_expansion"
    snapshot.mkdir(parents=True, exist_ok=False)
    rows = []
    with candidates_path.open(encoding="utf-8") as handle:
        candidates = [line.rstrip("\n").split("\t") for line in handle if line.strip()]
    for key, doi, _topic in candidates:
        quoted = urllib.parse.quote(doi, safe="")
        for source, url, license_note in [
            (
                "Crossref REST API",
                f"https://api.crossref.org/works/{quoted}",
                "Crossref metadata terms; article rights remain with publisher",
            ),
            (
                "OpenAlex API",
                f"https://api.openalex.org/works/doi:{doi}",
                "OpenAlex CC0 metadata; abstract text rights remain with publisher",
            ),
            (
                "Semantic Scholar Graph API",
                f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
                "?fields=title,year,venue,authors,abstract,tldr",
                "Semantic Scholar API terms; abstract text rights remain with publisher",
            ),
        ]:
            accessed = datetime.now(timezone.utc).isoformat(timespec="seconds")
            status, body = _get(url)
            suffix = source.split()[0].lower()
            path = snapshot / f"{key}_{suffix}.json"
            path.write_bytes(body)
            rows.append(
                {
                    "key": key,
                    "doi": doi,
                    "source": source,
                    "url": url,
                    "accessed_utc": accessed,
                    "http_status": status,
                    "local_path": str(path.relative_to(ROOT)),
                    "file_size": path.stat().st_size,
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "license": license_note,
                    "completeness": "complete exact-DOI API response"
                    if status == 200
                    else "request failed; response body retained",
                }
            )
            time.sleep(1.2)
    with (snapshot / "retrieval_manifest.csv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(snapshot)


if __name__ == "__main__":
    main(
        sys.argv[1]
        if len(sys.argv) > 1
        else datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        Path(sys.argv[2]) if len(sys.argv) > 2 else CANDIDATES,
    )
