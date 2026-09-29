#!/usr/bin/env python3
"""Validate SPDB release metadata and bundled artefacts (local pre-flight)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = "v1.0.0"
VERSION = "1.0.0"
DOI = "10.5281/zenodo.20745404"
EXPECTED_CREATORS = (
    "Baena Rojas, José Jaime",
    "Pinto Pajares, Daniel",
    "Andrés, César",
)
ALPHA_RELEASE = "v0.1.0-alpha"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_file_exists(relative: str, errors: list[str]) -> None:
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"Missing required file: {relative}")


def check_citation_cff(errors: list[str]) -> None:
    path = ROOT / "CITATION.cff"
    text = _read(path)
    if "cff-version:" not in text:
        errors.append("CITATION.cff: missing cff-version")
    if f"version: {VERSION}" not in text and f'version: "{VERSION}"' not in text:
        errors.append(f"CITATION.cff: version must be {VERSION}")
    if DOI not in text:
        errors.append(f"CITATION.cff: missing doi {DOI}")
    if "PLACEHOLDER" in text:
        errors.append("CITATION.cff: contains PLACEHOLDER repository URL")
    if "0000-0000-0000-0000" in text:
        errors.append("CITATION.cff: invalid placeholder ORCID")
    # Count only top-level authors block (before preferred-citation)
    head = text.split("preferred-citation:")[0]
    author_blocks = head.split("- family-names:")[1:]
    if len(author_blocks) != 3:
        errors.append("CITATION.cff: expected 3 authors")
    for field in ("title:", "authors:", "repository-code:", "abstract:"):
        if field not in text:
            errors.append(f"CITATION.cff: missing {field}")


def check_zenodo_json(errors: list[str]) -> None:
    path = ROOT / ".zenodo.json"
    data = json.loads(_read(path))
    if data.get("version") != VERSION:
        errors.append(f".zenodo.json: version must be {VERSION}")
    if data.get("language") != "eng":
        errors.append(".zenodo.json: language must be eng")
    creators = data.get("creators", [])
    if len(creators) != 3:
        errors.append(".zenodo.json: expected 3 creators")
    creator_names = [c.get("name", "") for c in creators]
    if creator_names != list(EXPECTED_CREATORS):
        errors.append(".zenodo.json: creator order or names mismatch")
    if not data.get("title"):
        errors.append(".zenodo.json: title required")
    if "PLACEHOLDER" in json.dumps(data):
        errors.append(".zenodo.json: contains PLACEHOLDER values")
    doi_ids = [
        r.get("identifier")
        for r in data.get("related_identifiers", [])
        if r.get("scheme") == "doi"
    ]
    if DOI not in doi_ids:
        errors.append(f".zenodo.json: missing related_identifier doi {DOI}")
    for creator in creators:
        orcid = creator.get("orcid", "")
        if orcid in ("", "0000-0000-0000-0000"):
            errors.append(".zenodo.json: invalid or missing ORCID for creator")


def check_v1_manifest(errors: list[str]) -> None:
    manifest_path = ROOT / "releases" / RELEASE / "MANIFEST.json"
    check_file_exists(f"releases/{RELEASE}/MANIFEST.json", errors)
    check_file_exists(f"releases/{RELEASE}/SHA256SUMS", errors)
    check_file_exists(f"releases/{RELEASE}/samples/wave1_100_units.jsonl", errors)
    if not manifest_path.is_file():
        return
    data = json.loads(_read(manifest_path))
    if data.get("version") != VERSION:
        errors.append("v1.0.0 MANIFEST.json: version field mismatch")
    counts = data.get("key_counts", {})
    if counts.get("wave1_n") != 100:
        errors.append("v1.0.0 MANIFEST.json: wave1_n must be 100")
    if counts.get("disagreements") != 65:
        errors.append("v1.0.0 MANIFEST.json: disagreements must be 65")
    if data.get("codebooks", {}).get("revised_revalidated") is not False:
        errors.append("v1.0.0 MANIFEST.json: revised_revalidated must be false")
    # Verify SHA256SUMS entries that still exist
    for line in _read(ROOT / "releases" / RELEASE / "SHA256SUMS").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, path = line.split(None, 1)
        path = path.strip()
        fp = ROOT / path
        if not fp.is_file():
            errors.append(f"SHA256SUMS path missing: {path}")
            continue
        actual = hashlib.sha256(fp.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"Checksum mismatch for {path}")


def check_alpha_preserved(errors: list[str]) -> None:
    """Historical alpha bundle must remain intact (do not rewrite history)."""
    check_file_exists(f"releases/{ALPHA_RELEASE}/MANIFEST.json", errors)
    check_file_exists(
        f"releases/{ALPHA_RELEASE}/samples/parlamint_100_units.jsonl", errors
    )
    manifest_path = ROOT / "releases" / ALPHA_RELEASE / "MANIFEST.json"
    if not manifest_path.is_file():
        return
    data = json.loads(_read(manifest_path))
    for sample in data.get("samples", []):
        rel = sample.get("path", "")
        sha = sample.get("sha256")
        if not rel or not sha:
            continue
        fp = ROOT / rel
        if not fp.is_file():
            errors.append(f"Alpha sample missing: {rel}")
            continue
        digest = hashlib.sha256(fp.read_bytes()).hexdigest()
        if digest != sha:
            errors.append(f"Checksum mismatch for {rel}")


def check_wave1_counts(errors: list[str]) -> None:
    jsonl = ROOT / "releases" / RELEASE / "samples" / "wave1_100_units.jsonl"
    if jsonl.is_file():
        lines = [ln for ln in _read(jsonl).splitlines() if ln.strip()]
        if len(lines) != 100:
            errors.append(
                f"wave1_100_units.jsonl: expected 100 lines, got {len(lines)}"
            )
    a = ROOT / "annotation/pilot_001/pilot_100_units_annotator_a.csv"
    b = ROOT / "annotation/pilot_001/pilot_100_units_annotator_b.csv"
    for p in (a, b):
        if not p.is_file():
            errors.append(f"Missing {p.relative_to(ROOT)}")
            continue
        n = len(_read(p).splitlines()) - 1
        if n != 100:
            errors.append(f"{p.name}: expected 100 data rows, got {n}")


def check_readme_citation(errors: list[str]) -> None:
    readme = _read(ROOT / "README.md")
    if DOI not in readme:
        errors.append("README.md: must include DOI")
    for author in ("Baena Rojas", "Pinto Pajares", "Andrés"):
        if author not in readme:
            errors.append(f"README.md: missing author {author}")
    if "How to cite" not in readme and "How to Cite" not in readme:
        errors.append("README.md: missing How to cite section")
    if "PLACEHOLDER" in readme:
        errors.append("README.md: contains PLACEHOLDER URL")
    if "validated benchmark" in readme.lower():
        errors.append("README.md: must not claim validated benchmark")


def main() -> int:
    errors: list[str] = []
    check_file_exists("README.md", errors)
    check_file_exists("LICENSE", errors)
    check_file_exists("CITATION.cff", errors)
    check_file_exists(".zenodo.json", errors)
    check_file_exists("docs/release_notes_v1.0.0.md", errors)
    check_file_exists("docs/pipeline.md", errors)
    check_file_exists("annotation/codebook/SPDB_Codebook_v1.md", errors)
    check_file_exists("annotation/codebook/SPDB_Codebook_v1.1.md", errors)
    check_file_exists(
        "annotation/pilot_001/results/disagreement_taxonomy.csv", errors
    )
    check_citation_cff(errors)
    check_zenodo_json(errors)
    check_v1_manifest(errors)
    check_alpha_preserved(errors)
    check_wave1_counts(errors)
    check_readme_citation(errors)

    if errors:
        print(f"Release validation FAILED ({len(errors)} issue(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"Release validation OK: {RELEASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
