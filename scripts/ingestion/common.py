"""Shared helpers for SPDB ingestion scripts."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$"
)
SCHEMA_REL_PATH = Path("schemas/discourse_unit.schema.json")
PARLIAMENT_DOCUMENT_SCHEMA_REL_PATH = Path("schemas/parliament_document.schema.json")
PIPELINE_DISCOURSE_UNIT_SCHEMA_REL_PATH = Path("schemas/pipeline_discourse_unit.schema.json")


def benchmark_root() -> Path:
    """Resolve spanish_political_discourse_benchmark/ repository root."""
    return Path(__file__).resolve().parents[2]


def default_raw_path(source: str, *parts: str) -> Path:
    return benchmark_root() / "data" / "raw" / source / Path(*parts)


def default_intermediate_path(source: str, *parts: str) -> Path:
    return benchmark_root() / "data" / "intermediate" / source / Path(*parts)


def default_processed_path(source: str, filename: str = "discourse_units.jsonl") -> Path:
    return benchmark_root() / "data" / "processed" / source / filename


def default_parliament_documents_path() -> Path:
    """Default intermediate JSONL for parliamentary ingestion."""
    return benchmark_root() / "data" / "intermediate" / "parliament_documents.jsonl"


def default_pipeline_discourse_units_path() -> Path:
    """Default processed JSONL for the first SPDB pipeline stage."""
    return benchmark_root() / "data" / "processed" / "discourse_units.jsonl"


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure root logger for CLI scripts."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    return logging.getLogger("spdb.ingestion")


def read_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    """Yield JSON objects from a UTF-8 JSONL file."""
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            yield record


def write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> int:
    """Write records to JSONL; return number of lines written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(dict(record), ensure_ascii=False))
            handle.write("\n")
            count += 1
    return count


def load_schema(schema_path: Optional[Path] = None) -> Dict[str, Any]:
    path = schema_path or (benchmark_root() / SCHEMA_REL_PATH)
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _type_matches(value: Any, schema_type: str) -> bool:
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "boolean":
        return isinstance(value, bool)
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "array":
        return isinstance(value, list)
    return True


def _validate_property(name: str, value: Any, spec: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    expected_type = spec.get("type")
    if expected_type and not _type_matches(value, expected_type):
        errors.append(f"{name}: expected {expected_type}, got {type(value).__name__}")
        return errors

    if expected_type == "string":
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{name}: value {value!r} not in {spec['enum']}")
        if "minLength" in spec and len(value) < spec["minLength"]:
            errors.append(f"{name}: shorter than minLength {spec['minLength']}")
        if "pattern" in spec and not re.match(spec["pattern"], value):
            errors.append(f"{name}: does not match pattern {spec['pattern']!r}")
        if spec.get("format") == "date" and not ISO_DATE_RE.match(value):
            errors.append(f"{name}: invalid ISO date {value!r}")
        if spec.get("format") == "date-time" and not ISO_DATETIME_RE.match(value):
            errors.append(f"{name}: invalid ISO date-time {value!r}")

    if expected_type == "integer":
        if "minimum" in spec and value < spec["minimum"]:
            errors.append(f"{name}: value {value} below minimum {spec['minimum']}")

    return errors


def validate_against_schema(
    record: Mapping[str, Any],
    schema: Mapping[str, Any],
    *,
    record_label: str = "record",
) -> List[str]:
    """Validate a JSON object against a JSON Schema subset used by SPDB."""
    errors: List[str] = []
    if not isinstance(record, dict):
        return [f"{record_label}: must be a JSON object"]

    allowed = set(schema.get("properties", {}))
    if schema.get("additionalProperties") is False:
        for key in record:
            if key not in allowed:
                errors.append(f"{record_label}.{key}: unexpected field")

    properties = schema.get("properties", {})
    for field in schema.get("required", []):
        if field not in record:
            errors.append(f"{record_label}.{field}: required field missing")

    for name, value in record.items():
        if name not in properties:
            continue
        errors.extend(
            _validate_property(f"{record_label}.{name}", value, properties[name])
        )

    return errors


def validate_discourse_unit(
    record: Mapping[str, Any],
    schema: Optional[Mapping[str, Any]] = None,
) -> List[str]:
    """
    Validate a discourse_unit record against discourse_unit.schema.json.

    Returns a list of human-readable error strings (empty if valid).
    """
    schema = schema or load_schema()
    errors = validate_against_schema(record, schema)
    properties = schema.get("properties", {})

    for rule in schema.get("allOf", []):
        condition = rule.get("if", {})
        then_clause = rule.get("then", {})
        props = condition.get("properties", {})
        if not props:
            continue
        matches = all(record.get(key) == spec.get("const") for key, spec in props.items())
        if matches:
            for field in then_clause.get("required", []):
                if field not in record or record[field] in (None, ""):
                    errors.append(f"{field}: required when {props}")

    if (
        record.get("char_end") is not None
        and record.get("char_start") is not None
        and record["char_end"] < record["char_start"]
    ):
        errors.append("char_end: must be >= char_start")

    return errors


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_instance_id(document_id: str, segment_index: int, split: str = "unassigned") -> str:
    """Stable instance_id prefix per SPDB v1 convention."""
    digest = hashlib.sha256(f"{document_id}:{segment_index}".encode("utf-8")).hexdigest()[:12]
    return f"spdb-v1-{split}-{digest}"


def make_unit_id(document_id: str, segment_index: int, split: str = "unassigned") -> str:
    """Stable discourse-unit identifier for the first pipeline stage."""
    return make_instance_id(document_id, segment_index, split)


def load_parliament_document_schema(schema_path: Optional[Path] = None) -> Dict[str, Any]:
    path = schema_path or (benchmark_root() / PARLIAMENT_DOCUMENT_SCHEMA_REL_PATH)
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_pipeline_discourse_unit_schema(schema_path: Optional[Path] = None) -> Dict[str, Any]:
    path = schema_path or (benchmark_root() / PIPELINE_DISCOURSE_UNIT_SCHEMA_REL_PATH)
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_parliament_document(
    record: Mapping[str, Any],
    schema: Optional[Mapping[str, Any]] = None,
) -> List[str]:
    schema = schema or load_parliament_document_schema()
    return validate_against_schema(record, schema, record_label="document")


def validate_pipeline_discourse_unit(
    record: Mapping[str, Any],
    schema: Optional[Mapping[str, Any]] = None,
) -> List[str]:
    schema = schema or load_pipeline_discourse_unit_schema()
    errors = validate_against_schema(record, schema, record_label="unit")
    metadata = record.get("metadata")
    if isinstance(metadata, dict):
        metadata_schema = schema.get("properties", {}).get("metadata", {})
        errors.extend(
            validate_against_schema(metadata, metadata_schema, record_label="unit.metadata")
        )
        if (
            metadata.get("char_end") is not None
            and metadata.get("char_start") is not None
            and metadata["char_end"] < metadata["char_start"]
        ):
            errors.append("unit.metadata.char_end: must be >= char_start")
    if (
        record.get("character_count") is not None
        and record.get("text") is not None
        and record["character_count"] != len(record["text"])
    ):
        errors.append("unit.character_count: must match len(text)")
    return errors


def normalize_text(text: str) -> str:
    """Lightweight normalization stub (NFC + whitespace collapse)."""
    import unicodedata

    normalized = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", normalized).strip()
