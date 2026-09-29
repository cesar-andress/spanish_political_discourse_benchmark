"""Shared metadata loading for SPDB release documentation generators."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from scripts.release.dataset_card_constants import CITATION_CFF, MANIFEST


@dataclass(frozen=True)
class AuthorRecord:
    given_names: str
    family_names: str
    affiliation: str
    orcid: str


@dataclass(frozen=True)
class CitationMetadata:
    title: str
    version: str
    doi: str
    doi_url: str
    repository: str
    abstract: str
    authors_bibtex: str
    authors_apa: str
    year: str
    authors: tuple[AuthorRecord, ...]
    license_id: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _field(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}\s*:?\s*(.+)$", text, flags=re.MULTILINE)
    value = match.group(1).strip() if match else ""
    return value.strip('"')


def _block(text: str, key: str) -> str:
    match = re.search(
        rf"^{re.escape(key)}\s*:?\s*>\s*\n((?:\s+.+\n)+)",
        text,
        flags=re.MULTILINE,
    )
    if match:
        return " ".join(line.strip() for line in match.group(1).splitlines())
    return _field(text, key)


def load_citation_metadata(path: Path = CITATION_CFF) -> CitationMetadata:
    text = _read_text(path)
    # Preferred-citation duplicates author blocks; parse only the top-level authors.
    head = text.split("preferred-citation:")[0]
    title = _field(text, "title")
    version = _field(text, "version")
    doi = _field(text, "doi")
    repository = _field(text, "repository-code")
    abstract = _block(text, "abstract")
    license_id = _field(text, "license")
    year_match = re.search(r'date-released:\s*"?(\d{4})', text)
    year = year_match.group(1) if year_match else "2025"

    authors: List[AuthorRecord] = []
    author_blocks = re.split(r"\n\s*-\s+family-names:", head)[1:]
    for block in author_blocks:
        family_match = re.match(r"\s*(.+?)\n\s*given-names:\s*(.+?)\n", block)
        if not family_match:
            continue
        family = family_match.group(1).strip().strip('"')
        given = family_match.group(2).strip().strip('"')
        affiliation_match = re.search(r"affiliation:\s*(.+?)(?:\n|$)", block)
        orcid_match = re.search(r"orcid:\s*(.+?)(?:\n|$)", block)
        authors.append(
            AuthorRecord(
                given_names=given,
                family_names=family,
                affiliation=affiliation_match.group(1).strip().strip('"') if affiliation_match else "",
                orcid=orcid_match.group(1).strip().strip('"') if orcid_match else "",
            )
        )

    bibtex_names = " and ".join(f"{a.given_names} {a.family_names}" for a in authors)
    apa_parts = [f"{a.given_names[0]}. {a.family_names}" for a in authors[:-1]]
    if authors:
        last = authors[-1]
        apa_names = ", ".join(apa_parts)
        apa_names = f"{apa_names}, & {last.given_names[0]}. {last.family_names}" if len(authors) > 1 else f"{last.given_names[0]}. {last.family_names}"
    else:
        apa_names = "**TODO:** authors missing in CITATION.cff"

    return CitationMetadata(
        title=title,
        version=version,
        doi=doi,
        doi_url=f"https://doi.org/{doi}" if doi else "",
        repository=repository,
        abstract=abstract.strip(),
        authors_bibtex=bibtex_names,
        authors_apa=apa_names,
        year=year,
        authors=tuple(authors),
        license_id=license_id,
    )


def load_label_ids(path: Path) -> List[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return [row["label_id"] for row in reader if row.get("label_id")]


def release_status() -> tuple[str, str, bool]:
    if not MANIFEST.exists():
        return "development", "Schemas and tooling are public; annotated v1 splits are not yet released.", False
    manifest = json.loads(_read_text(MANIFEST))
    release = manifest.get("release", "development")
    description = manifest.get("description", "")
    published = bool(manifest.get("published", False))
    status = "released" if published else "alpha"
    return f"{release} ({status})", description, published


def count_jsonl_lines(path: Path) -> int | None:
    if not path.exists():
        return None
    count = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def todo(hint: str) -> str:
    return f"**TODO:** {hint}"


def populated(value: str | None, *, hint: str) -> str:
    if value and value.strip():
        return value.strip()
    return todo(hint)
