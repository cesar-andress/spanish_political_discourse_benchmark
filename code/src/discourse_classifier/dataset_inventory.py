#!/usr/bin/env python3
"""Scan local data folders and build or update datasets/inventory/dataset_catalog.csv."""

import csv
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

SCAN_ROOTS = ("data", "datasets")
SCAN_EXTENSIONS = {".csv", ".json", ".jsonl", ".parquet", ".xlsx", ".txt", ".xml", ".zip"}
IGNORE_DIR_NAMES = {"build", ".git", "__pycache__", ".venv", "node_modules"}

COLUMNS = [
    "dataset_id",
    "dataset_name",
    "local_path",
    "file_type",
    "size_bytes",
    "language",
    "source_type",
    "license",
    "full_text_allowed",
    "topic",
    "start_year",
    "end_year",
    "status",
    "notes",
]

UNKNOWN = "unknown"
CATALOG_REL_PATH = Path("datasets/inventory/dataset_catalog.csv")


def benchmark_root() -> Path:
    """Resolve spanish_political_discourse_benchmark/ (dataset repo root)."""
    return Path(__file__).resolve().parents[3]


def repo_root() -> Path:
    """Resolve papers_unir/ program root."""
    return Path(__file__).resolve().parents[4]


def to_snake_case(name: str) -> str:
    """Normalize a filename stem to lowercase snake_case."""
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", name.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_").lower()
    return cleaned or "unnamed"


def should_skip_dir(dirname: str) -> bool:
    return dirname in IGNORE_DIR_NAMES


def iter_dataset_files(root: Path) -> List[Path]:
    """Return dataset-like files under configured scan roots."""
    found = []  # type: List[Path]
    for scan_root_name in SCAN_ROOTS:
        scan_root = root / scan_root_name
        if not scan_root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(scan_root):
            dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
            current_dir = Path(dirpath)
            for filename in filenames:
                path = current_dir / filename
                if path.suffix.lower() not in SCAN_EXTENSIONS:
                    continue
                if path.resolve() == (root / CATALOG_REL_PATH).resolve():
                    continue
                found.append(path)
    return sorted(found)


def relative_local_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def read_catalog(catalog_path: Path) -> Tuple[List[Dict[str, str]], Dict[str, Dict[str, str]]]:
    """Load existing catalog rows keyed by local_path."""
    if not catalog_path.is_file():
        return [], {}

    with catalog_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            raise ValueError(
                f"Unexpected catalog columns: {reader.fieldnames}. Expected {COLUMNS}."
            )
        rows = [dict(row) for row in reader]

    by_path = {row["local_path"]: row for row in rows}
    return rows, by_path


def make_new_row(root: Path, path: Path, used_ids: Set[str]) -> Dict[str, str]:
    stem = path.stem
    dataset_id = to_snake_case(stem)
    base_id = dataset_id
    suffix = 2
    while dataset_id in used_ids:
        dataset_id = f"{base_id}_{suffix}"
        suffix += 1
    used_ids.add(dataset_id)

    stat = path.stat()
    return {
        "dataset_id": dataset_id,
        "dataset_name": path.name,
        "local_path": relative_local_path(root, path),
        "file_type": path.suffix.lower().lstrip("."),
        "size_bytes": str(stat.st_size),
        "language": UNKNOWN,
        "source_type": UNKNOWN,
        "license": UNKNOWN,
        "full_text_allowed": UNKNOWN,
        "topic": UNKNOWN,
        "start_year": UNKNOWN,
        "end_year": UNKNOWN,
        "status": "available",
        "notes": UNKNOWN,
    }


def update_existing_row(row: Dict[str, str], path: Path) -> None:
    row["size_bytes"] = str(path.stat().st_size)
    row["status"] = "available"


def write_catalog(catalog_path: Path, rows: List[Dict[str, str]]) -> None:
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    with catalog_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def build_inventory(root: Optional[Path] = None) -> Tuple[Path, int, int, int]:
    """
    Scan data folders and update the dataset catalog.

    Returns:
        catalog_path, files_detected, rows_added, rows_updated
    """
    root = root or benchmark_root()
    catalog_path = root / CATALOG_REL_PATH
    files = iter_dataset_files(root)

    existing_rows, by_path = read_catalog(catalog_path)
    used_ids = {row["dataset_id"] for row in existing_rows}

    rows_added = 0
    rows_updated = 0

    for path in files:
        local_path = relative_local_path(root, path)
        if local_path in by_path:
            update_existing_row(by_path[local_path], path)
            rows_updated += 1
        else:
            new_row = make_new_row(root, path, used_ids)
            existing_rows.append(new_row)
            by_path[local_path] = new_row
            rows_added += 1

    write_catalog(catalog_path, existing_rows)
    return catalog_path, len(files), rows_added, rows_updated


def main() -> int:
    root = benchmark_root()
    catalog_path, detected, added, updated = build_inventory(root)
    print(f"Catalog written to: {catalog_path.relative_to(root).as_posix()}")
    print(f"Detected dataset files: {detected}")
    print(f"Rows added: {added}")
    print(f"Rows updated: {updated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
