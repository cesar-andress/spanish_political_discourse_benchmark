"""Core discourse segmentation logic for SPDB v1."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence

from scripts.ingestion.common import normalize_text, utc_now_iso
from scripts.segmentation.common import make_unit_id
from scripts.segmentation.sentence import TextSpan, normalize_spanish_text, split_paragraphs, split_spanish_sentences
from scripts.segmentation.tokenize import count_tokens_beto

logger = logging.getLogger("spdb.segmentation.segmenter")

DOCUMENT_ID_FIELDS: Sequence[str] = ("document_id", "doc_id")
DOCUMENT_TEXT_FIELDS: Sequence[str] = ("text_raw", "text")

DEFAULTS = {
    "language": "es",
    "speaker_role": "unknown",
    "party_family": "unknown",
    "chamber_or_level": "n/a",
    "election_cycle": "n/a",
    "platform": "n/a",
    "license_ref": "unknown",
    "split": "unassigned",
    "text_redistributable": True,
    "source_type": "parliamentary",
    "source_corpus": "unknown",
    "annotation_version": "none",
}


@dataclass
class SegmentConfig:
    max_tokens_beto: int = 400
    min_chars: int = 20
    max_chars: int = 2000
    split: str = "unassigned"
    pipeline_version: str = "0.1.0"
    use_beto_model: bool = False
    language: str = "es"


def resolve_document_id(document: Mapping[str, Any]) -> str:
    for field in DOCUMENT_ID_FIELDS:
        value = document.get(field)
        if value:
            return str(value)
    raise ValueError("document record missing document_id or doc_id")


def resolve_document_text(document: Mapping[str, Any]) -> str:
    for field in DOCUMENT_TEXT_FIELDS:
        value = document.get(field)
        if value is not None:
            return str(value)
    raise ValueError("document record missing text_raw or text")


def validate_document_record(document: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    try:
        resolve_document_id(document)
    except ValueError as exc:
        errors.append(str(exc))
    try:
        resolve_document_text(document)
    except ValueError as exc:
        errors.append(str(exc))
    if not document.get("date") and not document.get("timestamp"):
        errors.append("date or timestamp: required in document metadata")
    return errors


def _count_tokens(text: str, config: SegmentConfig) -> int:
    return count_tokens_beto(text, use_model=config.use_beto_model)


def _merge_spans(spans: List[TextSpan]) -> TextSpan:
    if len(spans) == 1:
        return spans[0]
    text = " ".join(span.text for span in spans)
    return TextSpan(text=text, char_start=spans[0].char_start, char_end=spans[-1].char_end)


def _segment_paragraph(paragraph: TextSpan, config: SegmentConfig) -> List[TextSpan]:
    token_count = _count_tokens(paragraph.text, config)
    if token_count <= config.max_tokens_beto and len(paragraph.text) <= config.max_chars:
        return [paragraph]

    sentences = split_spanish_sentences(paragraph)
    if not sentences:
        return [paragraph]

    units: List[TextSpan] = []
    buffer: List[TextSpan] = []
    buffer_tokens = 0

    for sentence in sentences:
        sentence_tokens = _count_tokens(sentence.text, config)
        if buffer and (
            buffer_tokens + sentence_tokens > config.max_tokens_beto
            or len(_merge_spans(buffer + [sentence]).text) > config.max_chars
        ):
            units.append(_merge_spans(buffer))
            buffer = [sentence]
            buffer_tokens = sentence_tokens
            continue

        buffer.append(sentence)
        buffer_tokens += sentence_tokens

    if buffer:
        units.append(_merge_spans(buffer))
    return units


def segment_text(text: str, config: Optional[SegmentConfig] = None) -> List[TextSpan]:
    """
    Segment long Spanish political text into discourse spans.

    Paragraph-aware; splits long paragraphs at sentence boundaries when token
    or character caps are exceeded.
    """
    config = config or SegmentConfig()
    normalized = normalize_spanish_text(text)
    if not normalized.strip():
        return []

    source_type_hint = None
    spans: List[TextSpan] = []
    for paragraph in split_paragraphs(normalized):
        spans.extend(_segment_paragraph(paragraph, config))
    return spans


def _passes_length_filters(span: TextSpan, config: SegmentConfig) -> bool:
    length = len(span.text)
    if length < config.min_chars:
        logger.debug("Skipping span below min_chars (%d): %r", length, span.text[:40])
        return False
    if length > config.max_chars:
        logger.debug("Skipping span above max_chars (%d)", length)
        return False
    return True


def _speaker_id(document: Mapping[str, Any]) -> str:
    if document.get("speaker_id"):
        return str(document["speaker_id"])
    if document.get("author_handle"):
        return str(document["author_handle"])
    if document.get("speaker"):
        return f"speaker-{document['speaker']}"
    if document.get("party"):
        return f"party-{document['party']}"
    return "unknown"


def _metadata_value(document: Mapping[str, Any], field: str, fallback_keys: Sequence[str] = ()) -> Any:
    if field in document and document[field] not in (None, ""):
        return document[field]
    for key in fallback_keys:
        if key in document and document[key] not in (None, ""):
            return document[key]
    return DEFAULTS.get(field)


def build_discourse_unit(
    document: Mapping[str, Any],
    span: TextSpan,
    segment_index: int,
    config: SegmentConfig,
    *,
    created_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Map a text span plus source document metadata to a discourse_unit record."""
    document_id = resolve_document_id(document)
    text = normalize_text(span.text)
    token_count = _count_tokens(text, config)
    source_type = str(_metadata_value(document, "source_type"))

    unit: Dict[str, Any] = {
        "instance_id": make_unit_id(document_id, segment_index, config.split),
        "text": text,
        "text_redistributable": bool(_metadata_value(document, "text_redistributable")),
        "source_type": source_type,
        "source_corpus": str(_metadata_value(document, "source_corpus")),
        "document_id": document_id,
        "segment_index": segment_index,
        "char_start": span.char_start,
        "char_end": span.char_end,
        "language": str(_metadata_value(document, "language")),
        "date": str(_metadata_value(document, "date", ("timestamp",))),
        "speaker_id": _speaker_id(document),
        "speaker_role": str(_metadata_value(document, "speaker_role")),
        "party_family": str(_metadata_value(document, "party_family", ("party", "author_party"))),
        "chamber_or_level": str(_metadata_value(document, "chamber_or_level", ("chamber",))),
        "election_cycle": str(_metadata_value(document, "election_cycle")),
        "platform": str(_metadata_value(document, "platform")),
        "license_ref": str(_metadata_value(document, "license_ref")),
        "split": config.split,
        "annotated": bool(document.get("annotated", False)),
        "annotation_version": str(document.get("annotation_version", DEFAULTS["annotation_version"])),
        "token_count_beto": token_count,
        "character_count": len(text),
        "created_at": created_at or utc_now_iso(),
        "pipeline_version": config.pipeline_version,
    }

    if document.get("url"):
        unit["rehydration_url"] = document["url"]
    if source_type == "social_media":
        post_id = document.get("platform_post_id") or document.get("post_id")
        if post_id:
            unit["platform_post_id"] = str(post_id)
        if document.get("text_redistributable") is False:
            unit["text"] = ""
            unit["character_count"] = 0
            unit["token_count_beto"] = 0

    if unit["date"] and "T" in unit["date"]:
        unit["date"] = unit["date"][:10]

    return unit


def segment_document(
    document: Mapping[str, Any],
    config: Optional[SegmentConfig] = None,
) -> List[Dict[str, Any]]:
    """Segment one document record into validated discourse_unit dicts."""
    config = config or SegmentConfig()
    errors = validate_document_record(document)
    if errors:
        raise ValueError("; ".join(errors))

    document_id = resolve_document_id(document)
    text = resolve_document_text(document)
    source_type = str(_metadata_value(document, "source_type"))

    created_at = utc_now_iso()
    if source_type == "social_media":
        span = TextSpan(text=text, char_start=0, char_end=len(text))
        units = [build_discourse_unit(document, span, 0, config, created_at=created_at)]
        logger.info("Document %s: social_media kept as single unit", document_id)
        return units

    spans = segment_text(text, config)
    spans = [span for span in spans if _passes_length_filters(span, config)]

    units = [
        build_discourse_unit(document, span, index, config, created_at=created_at)
        for index, span in enumerate(spans)
    ]
    logger.info("Document %s: produced %d discourse unit(s)", document_id, len(units))
    return units


def segment_documents(
    documents: Iterable[Mapping[str, Any]],
    config: Optional[SegmentConfig] = None,
) -> Iterator[Dict[str, Any]]:
    """Segment many documents, preserving source metadata per unit."""
    config = config or SegmentConfig()
    for index, document in enumerate(documents):
        try:
            yield from segment_document(document, config)
        except ValueError as exc:
            raise ValueError(f"document index {index}: {exc}") from exc
