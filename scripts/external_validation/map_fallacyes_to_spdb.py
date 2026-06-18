"""Map FallacyES-Political labels onto the SPDB fallacy inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List

from analysis.external_validation.fallacyes_constants import INGESTED_JSONL, MAPPED_JSONL
from analysis.external_validation.fallacyes_mapping import project_original_label


def load_jsonl(path: Path) -> List[dict]:
    records: List[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def map_record(record: dict) -> dict:
    projection = project_original_label(str(record.get("original_label", "")))
    return {
        "id": record["id"],
        "text": record["text"],
        "original_label": record.get("original_label", ""),
        "spdb_fallacy_labels": list(projection.spdb_fallacy_labels),
        "mapping_type": projection.mapping_type,
        "mapping_confidence": projection.mapping_confidence,
        "mapping_notes": projection.mapping_notes,
    }


def map_fallacyes_to_spdb(
    *,
    input_path: Path = INGESTED_JSONL,
    output_path: Path = MAPPED_JSONL,
) -> int:
    records = load_jsonl(input_path)
    mapped = [map_record(record) for record in records]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in mapped:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(mapped)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Map FallacyES-Political labels to SPDB fallacy codes.")
    parser.add_argument("--input", type=Path, default=INGESTED_JSONL)
    parser.add_argument("--output", type=Path, default=MAPPED_JSONL)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    if not args.input.exists():
        print(f"Input not found: {args.input}", file=__import__("sys").stderr)
        return 1
    count = map_fallacyes_to_spdb(input_path=args.input, output_path=args.output)
    print(f"Mapped {count} records -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
