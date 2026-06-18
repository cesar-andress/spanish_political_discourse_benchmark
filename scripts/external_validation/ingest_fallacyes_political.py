"""Ingest FallacyES-Political from Zenodo into SPDB JSONL format."""

from __future__ import annotations

import argparse
import csv
import json
import urllib.request
from pathlib import Path
from typing import Iterable, List

from analysis.external_validation.fallacyes_constants import (
    INGESTED_JSONL,
    RAW_CSV,
    RAW_DIR,
    SOURCE_DATASET,
    ZENODO_CSV_FILENAME,
    ZENODO_CSV_URL,
)


def download_raw_csv(dest: Path = RAW_CSV) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    request = urllib.request.Request(ZENODO_CSV_URL, headers={"User-Agent": "spdb-external-validation/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        dest.write_bytes(response.read())
    return dest


def _make_row_id(document: str, index: int) -> str:
    safe_doc = document.replace("/", "-")
    return f"fep_{safe_doc}_{index:04d}"


def ingest_csv(csv_path: Path) -> List[dict]:
    records: List[dict] = []
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=1):
            text = (row.get("text") or "").strip()
            if not text:
                continue
            document = (row.get("document") or "").strip()
            record = {
                "id": _make_row_id(document, index),
                "text": text,
                "original_label": (row.get("category") or "").strip(),
                "source_dataset": SOURCE_DATASET,
                "metadata": {
                    "document": document,
                    "prev_context": (row.get("prev_context") or "").strip(),
                    "foll_context": (row.get("foll_context") or "").strip(),
                    "speaker_id": (row.get("speaker_id") or "").strip(),
                    "speaker_name": (row.get("speaker_name") or "").strip(),
                    "speaker_party": (row.get("speaker_party") or "").strip(),
                },
            }
            records.append(record)
    return records


def write_jsonl(path: Path, records: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def ingest_fallacyes_political(
    *,
    csv_path: Path | None = None,
    output_path: Path = INGESTED_JSONL,
    download: bool = True,
) -> int:
    source = csv_path
    if source is None:
        source = download_raw_csv() if download else RAW_CSV
    if not source.exists():
        raise FileNotFoundError(
            f"FallacyES-Political CSV not found at {source}. "
            f"Download from {ZENODO_CSV_URL} or pass --csv-path."
        )
    records = ingest_csv(source)
    write_jsonl(output_path, records)
    return len(records)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest FallacyES-Political into SPDB JSONL.")
    parser.add_argument("--csv-path", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=INGESTED_JSONL)
    parser.add_argument("--no-download", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    count = ingest_fallacyes_political(
        csv_path=args.csv_path,
        output_path=args.output,
        download=not args.no_download,
    )
    print(f"Ingested {count} records -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
