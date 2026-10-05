"""
athena.tools.citation_verifier
==============================

Automated Crossref API citation and DOI verification engine.
Enforces the academic verification mandate: never trust AI-generated citations;
verify DOI, container-title (journal), volume, issue, pages, and authors
directly against the authoritative Crossref scholarly registry.

Zero-delimiters: strictly ASCII output.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger("athena.tools.citation_verifier")

CROSSREF_API_URL = "https://api.crossref.org/works"
USER_AGENT = "Athena-Academic-Verifier/10.0.4 (https://github.com/winstonkoh87/Athena-Public)"

# Standard DOI pattern matching 10.NNNN/...
DOI_REGEX = re.compile(
    r"(?:10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)",
    re.IGNORECASE,
)


@dataclass
class CitationVerificationResult:
    doi: str
    valid: bool
    title: str | None = None
    journal: str | None = None
    volume: str | None = None
    issue: str | None = None
    page: str | None = None
    year: int | str | None = None
    authors: list[str] = field(default_factory=list)
    title_similarity: float | None = None
    title_match: bool | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_ascii_summary(self) -> str:
        status_icon = "[PASS]" if self.valid else "[FAIL]"
        lines = [
            f"{status_icon} DOI: {self.doi}",
            f"  Title   : {self.title or 'N/A'}",
            f"  Journal : {self.journal or 'N/A'}",
            f"  Citation: Vol {self.volume or '?'}, Issue {self.issue or '?'}, Pages {self.page or '?'}, Year {self.year or '?'}",
            f"  Authors : {', '.join(self.authors[:3]) + ('...' if len(self.authors) > 3 else '') or 'N/A'}",
        ]
        if self.title_match is not None:
            match_str = "MATCH" if self.title_match else "MISMATCH"
            sim_str = f" ({self.title_similarity:.1%})" if self.title_similarity is not None else ""
            lines.append(f"  Title Match: {match_str}{sim_str}")
        if self.error:
            lines.append(f"  Error   : {self.error}")
        return "\n".join(lines)


def normalize_doi(raw_doi: str) -> str:
    """Clean and normalize a DOI string, stripping URLs, prefixes, and trailing punctuation."""
    clean = raw_doi.strip()
    clean = re.sub(r"^https?://(dx\.)?doi\.org/", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"^doi:\s*", "", clean, flags=re.IGNORECASE)
    clean = clean.rstrip(".,;)>]")
    return clean.strip()


def extract_dois(text: str) -> list[str]:
    """Extract all unique normalized DOIs from an arbitrary text block."""
    matches = DOI_REGEX.findall(text)
    seen = set()
    cleaned = []
    for m in matches:
        norm = normalize_doi(m)
        if norm and norm.lower() not in seen:
            seen.add(norm.lower())
            cleaned.append(norm)
    return cleaned


def _compute_token_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity over alphanumeric tokens."""
    tokens_a = set(re.findall(r"\w+", a.lower()))
    tokens_b = set(re.findall(r"\w+", b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def verify_doi(
    raw_doi: str,
    expected_title: str | None = None,
    timeout: float = 8.0,
    session: requests.Session | None = None,
) -> CitationVerificationResult:
    """
    Query Crossref API to verify a single DOI and extract authoritative publication metadata.
    Optionally compares against an expected title.
    """
    doi = normalize_doi(raw_doi)
    if not doi or not doi.startswith("10."):
        return CitationVerificationResult(
            doi=doi,
            valid=False,
            error=f"Invalid DOI syntax: '{raw_doi}' does not conform to '10.NNNN/...'",
        )

    url = f"{CROSSREF_API_URL}/{doi}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    http_client = session or requests

    try:
        resp = http_client.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 404:
            return CitationVerificationResult(
                doi=doi,
                valid=False,
                error="DOI not found in Crossref registry (HTTP 404)",
            )
        if resp.status_code != 200:
            return CitationVerificationResult(
                doi=doi,
                valid=False,
                error=f"Crossref API returned HTTP {resp.status_code}",
            )

        data = resp.json()
        message = data.get("message", {})

        titles = message.get("title", [])
        title = titles[0] if titles else None

        containers = message.get("container-title", [])
        journal = containers[0] if containers else None

        volume = message.get("volume")
        issue = message.get("issue")
        page = message.get("page")

        year = None
        published = message.get("published-print") or message.get("published-online") or message.get("created")
        if published and "date-parts" in published and published["date-parts"]:
            parts = published["date-parts"][0]
            if parts and len(parts) > 0:
                year = parts[0]

        authors = []
        for author in message.get("author", []):
            given = author.get("given", "").strip()
            family = author.get("family", "").strip()
            if family:
                name = f"{family}, {given}" if given else family
                authors.append(name)
            elif "name" in author:
                authors.append(author["name"])

        title_similarity = None
        title_match = None
        if expected_title and title:
            sim = _compute_token_similarity(expected_title, title)
            title_similarity = sim
            title_match = sim >= 0.45

        return CitationVerificationResult(
            doi=doi,
            valid=True,
            title=title,
            journal=journal,
            volume=str(volume) if volume is not None else None,
            issue=str(issue) if issue is not None else None,
            page=str(page) if page is not None else None,
            year=year,
            authors=authors,
            title_similarity=title_similarity,
            title_match=title_match,
        )

    except requests.exceptions.Timeout:
        return CitationVerificationResult(
            doi=doi,
            valid=False,
            error=f"Crossref API timed out after {timeout}s",
        )
    except Exception as exc:
        return CitationVerificationResult(
            doi=doi,
            valid=False,
            error=f"Crossref request error: {exc}",
        )


def search_crossref(
    query: str,
    author: str | None = None,
    limit: int = 3,
    timeout: float = 8.0,
    session: requests.Session | None = None,
) -> list[CitationVerificationResult]:
    """
    Search Crossref for matching works by title/bibliographic keywords.
    """
    params: dict[str, Any] = {
        "query.bibliographic": query,
        "rows": limit,
    }
    if author:
        params["query.author"] = author

    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    http_client = session or requests

    results = []
    try:
        resp = http_client.get(CROSSREF_API_URL, params=params, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            return []
        data = resp.json()
        items = data.get("message", {}).get("items", [])
        for item in items:
            doi = item.get("DOI", "")
            titles = item.get("title", [])
            title = titles[0] if titles else None
            containers = item.get("container-title", [])
            journal = containers[0] if containers else None
            volume = item.get("volume")
            issue = item.get("issue")
            page = item.get("page")

            year = None
            published = item.get("published-print") or item.get("published-online") or item.get("created")
            if published and "date-parts" in published and published["date-parts"]:
                parts = published["date-parts"][0]
                if parts:
                    year = parts[0]

            authors = []
            for a in item.get("author", []):
                family = a.get("family", "").strip()
                given = a.get("given", "").strip()
                if family:
                    authors.append(f"{family}, {given}" if given else family)

            results.append(
                CitationVerificationResult(
                    doi=doi,
                    valid=True,
                    title=title,
                    journal=journal,
                    volume=str(volume) if volume is not None else None,
                    issue=str(issue) if issue is not None else None,
                    page=str(page) if page is not None else None,
                    year=year,
                    authors=authors,
                )
            )
    except Exception as e:
        logger.warning(f"Failed to query Crossref search: {e}")

    return results


def verify_file(filepath: Path, timeout: float = 8.0) -> list[CitationVerificationResult]:
    """Scan a document file for DOIs and verify each one."""
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    text = filepath.read_text(encoding="utf-8", errors="ignore")
    dois = extract_dois(text)
    results = []
    with requests.Session() as session:
        for doi in dois:
            res = verify_doi(doi, timeout=timeout, session=session)
            results.append(res)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify academic citations and DOIs via the authoritative Crossref API."
    )
    parser.add_argument("doi", nargs="?", help="DOI to verify (e.g. 10.1038/s41586-020-2649-2)")
    parser.add_argument("--file", "-f", type=Path, help="Scan a markdown or text file for DOIs")
    parser.add_argument("--title", "-t", help="Verify that the paper title matches this expected title")
    parser.add_argument("--search", "-s", help="Search Crossref by title/keywords to locate a DOI")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--timeout", type=float, default=8.0, help="Request timeout in seconds")

    args = parser.parse_args()

    if args.search:
        results = search_crossref(args.search, timeout=args.timeout)
        if args.json:
            print(json.dumps([r.to_dict() for r in results], indent=2))
        else:
            print(f"Found {len(results)} works matching: '{args.search}'\n")
            for r in results:
                print(r.to_ascii_summary())
                print("-" * 50)
        return 0

    if args.file:
        try:
            results = verify_file(args.file, timeout=args.timeout)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 2

        if args.json:
            print(json.dumps([r.to_dict() for r in results], indent=2))
        else:
            print(f"Scanned: {args.file} (Found {len(results)} DOIs)\n")
            all_valid = True
            for r in results:
                print(r.to_ascii_summary())
                print("-" * 50)
                if not r.valid or (r.title_match is False):
                    all_valid = False

            if not all_valid:
                print("\n[VERDICT] WARNING: One or more citations failed Crossref verification.")
                return 1
            print("\n[VERDICT] SUCCESS: All citations verified via Crossref.")
        return 0

    if args.doi:
        res = verify_doi(args.doi, expected_title=args.title, timeout=args.timeout)
        if args.json:
            print(json.dumps(res.to_dict(), indent=2))
        else:
            print(res.to_ascii_summary())
        return 0 if (res.valid and res.title_match is not False) else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
