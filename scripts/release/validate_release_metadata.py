#!/usr/bin/env python3
"""Validate SPDB release metadata and bundled artefacts (local pre-flight)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = "v0.1.0-alpha"
VERSION_PATTERN = re.compile(r"0\.1\.0-alpha")


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
    if not VERSION_PATTERN.search(text):
        errors.append("CITATION.cff: version must be 0.1.0-alpha")
    if "PLACEHOLDER" in text:
        errors.append("CITATION.cff: contains PLACEHOLDER repository URL")
    for field in ("title:", "authors:", "repository-code:", "abstract:"):
        if field not in text:
            errors.append(f"CITATION.cff: missing {field}")


def check_zenodo_json(errors: list[str]) -> None:
    path = ROOT / ".zenodo.json"
    data = json.loads(_read(path))
    if data.get("version") != "0.1.0-alpha":
        errors.append(".zenodo.json: version must be 0.1.0-alpha")
    if not data.get("creators"):
        errors.append(".zenodo.json: creators required")
    if not data.get("title"):
        errors.append(".zenodo.json: title required")
    if "PLACEHOLDER" in json.dumps(data):
        errors.append(".zenodo.json: contains PLACEHOLDER values")


def check_manifest(errors: list[str]) -> None:
    manifest_path = ROOT / "releases" / RELEASE / "MANIFEST.json"
    data = json.loads(_read(manifest_path))
    if data.get("release") != RELEASE:
        errors.append("MANIFEST.json: release field mismatch")
    for key in ("schema_files", "label_inventories", "annotation_bundle", "samples"):
        if key not in data:
            errors.append(f"MANIFEST.json: missing key {key}")
    for rel in data.get("schema_files", []):
        check_file_exists(rel, errors)
    for rel in data.get("label_inventories", []):
        check_file_exists(rel, errors)
    for rel in data.get("annotation_bundle", []):
        check_file_exists(rel, errors)
    for sample in data.get("samples", []):
        rel = sample.get("path", "")
        check_file_exists(rel, errors)
        sha = sample.get("sha256")
        if sha:
            import hashlib

            digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            if digest != sha:
                errors.append(f"Checksum mismatch for {rel}")


def check_sample_counts(errors: list[str]) -> None:
    jsonl = ROOT / "releases" / RELEASE / "samples" / "parlamint_100_units.jsonl"
    lines = [ln for ln in _read(jsonl).splitlines() if ln.strip()]
    if len(lines) != 100:
        errors.append(f"parlamint_100_units.jsonl: expected 100 lines, got {len(lines)}")
    csv = ROOT / "releases" / RELEASE / "samples" / "pilot_100_units.csv"
    csv_lines = _read(csv).splitlines()
    if len(csv_lines) != 101:
        errors.append(f"pilot_100_units.csv: expected 101 lines (header + 100), got {len(csv_lines)}")


def check_readme_mentions_release(errors: list[str]) -> None:
    readme = _read(ROOT / "README.md")
    if RELEASE not in readme:
        errors.append("README.md: must mention v0.1.0-alpha")
    if "PLACEHOLDER" in readme:
        errors.append("README.md: contains PLACEHOLDER URL")


def main() -> int:
    errors: list[str] = []
    check_file_exists("README.md", errors)
    check_file_exists("CITATION.cff", errors)
    check_file_exists(".zenodo.json", errors)
    check_file_exists("docs/release_notes_v0.1.0-alpha.md", errors)
    check_file_exists("docs/github_release_checklist_v0.1.0-alpha.md", errors)
    check_file_exists("docs/pipeline.md", errors)
    check_citation_cff(errors)
    check_zenodo_json(errors)
    check_manifest(errors)
    check_sample_counts(errors)
    check_readme_mentions_release(errors)

    if errors:
        print(f"Release validation FAILED ({len(errors)} issue(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"Release validation OK: {RELEASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
