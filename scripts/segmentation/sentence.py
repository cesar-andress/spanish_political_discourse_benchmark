"""Spanish sentence and paragraph boundary detection."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import List

# Common Spanish abbreviations that should not trigger a sentence break.
SPANISH_ABBREVS = {
    "a",
    "a.c",
    "a.j",
    "av",
    "c",
    "cf",
    "dr",
    "dra",
    "etc",
    "excmo",
    "exma",
    "ff",
    "fig",
    "gob",
    "gr",
    "hr",
    "hrs",
    "ing",
    "lic",
    "min",
    "mr",
    "mrs",
    "n",
    "núm",
    "num",
    "p",
    "págs",
    "pags",
    "pp",
    "prof",
    "profa",
    "sr",
    "sra",
    "sres",
    "sras",
    "ud",
    "uds",
    "vol",
    "vv",
    "aa",
}

SENTENCE_BOUNDARY_RE = re.compile(
    r"""
    (?<=[.!?…])          # sentence-ending punctuation
    [\"'\)\]\»]*         # optional closing quotes/brackets
    \s+                  # whitespace
    (?=
        [¿¡\"'\(\«A-ZÁÉÍÓÚÜÑ]
    )
    """,
    re.VERBOSE,
)

PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")


@dataclass(frozen=True)
class TextSpan:
    text: str
    char_start: int
    char_end: int


def normalize_spanish_text(text: str) -> str:
    """Unicode NFC normalization with collapsed whitespace (non-destructive casing)."""
    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    return normalized


def split_paragraphs(text: str) -> List[TextSpan]:
    """Split text on blank lines while preserving character offsets."""
    normalized = normalize_spanish_text(text)
    if not normalized.strip():
        return []

    spans: List[TextSpan] = []
    cursor = 0
    for match in PARAGRAPH_SPLIT_RE.finditer(normalized):
        chunk = normalized[cursor : match.start()]
        if chunk.strip():
            start = cursor
            end = match.start()
            spans.append(TextSpan(text=chunk.strip(), char_start=start, char_end=end))
        cursor = match.end()

    tail = normalized[cursor:]
    if tail.strip():
        spans.append(
            TextSpan(
                text=tail.strip(),
                char_start=cursor,
                char_end=cursor + len(tail.rstrip()),
            )
        )
    return spans


def _ends_with_abbreviation(sentence: str) -> bool:
    stripped = sentence.rstrip().rstrip("\"'»)]")
    if not stripped:
        return False
    token = stripped.split()[-1].lower().rstrip(".")
    return token in SPANISH_ABBREVS


def split_spanish_sentences(paragraph: TextSpan) -> List[TextSpan]:
    """
    Split a paragraph into sentence spans using Spanish punctuation rules.

    Handles inverted question/exclamation marks and filters common abbreviations.
    """
    text = paragraph.text
    if not text.strip():
        return []

    boundaries = [0]
    for match in SENTENCE_BOUNDARY_RE.finditer(text):
        candidate_end = match.start() + 1
        chunk = text[boundaries[-1] : candidate_end]
        if _ends_with_abbreviation(chunk):
            continue
        boundaries.append(match.end())

    if boundaries[-1] != len(text):
        boundaries.append(len(text))

    sentences: List[TextSpan] = []
    for index in range(len(boundaries) - 1):
        start = boundaries[index]
        end = boundaries[index + 1]
        sentence = text[start:end].strip()
        if not sentence:
            continue
        abs_start = paragraph.char_start + start
        abs_end = paragraph.char_start + end
        sentences.append(TextSpan(text=sentence, char_start=abs_start, char_end=abs_end))

    if not sentences and text.strip():
        sentences.append(paragraph)
    return sentences
