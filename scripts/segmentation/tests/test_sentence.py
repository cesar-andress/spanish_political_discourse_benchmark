from __future__ import annotations

from scripts.segmentation.sentence import split_paragraphs, split_spanish_sentences
from scripts.segmentation.tests.conftest import FIXTURES
from scripts.ingestion.common import read_jsonl


def test_split_paragraphs_preserves_offsets():
    text = "Primer párrafo.\n\nSegundo párrafo."
    spans = split_paragraphs(text)
    assert len(spans) == 2
    assert spans[0].text.startswith("Primer")
    assert spans[1].text.startswith("Segundo")
    assert spans[0].char_start == 0
    assert spans[1].char_start > spans[0].char_end


def test_split_spanish_sentences_handles_inverted_punctuation():
    paragraph_text = "¿Es serio este planteamiento? Deberíamos debatir con datos."
    spans = split_paragraphs(paragraph_text)
    sentences = split_spanish_sentences(spans[0])
    assert len(sentences) == 2
    assert sentences[0].text.startswith("¿Es serio")
    assert sentences[1].text.startswith("Deberíamos")


def test_abbreviations_do_not_over_split():
    doc = next(read_jsonl(FIXTURES / "sample_abbreviations.jsonl"))
    from scripts.segmentation.segmenter import segment_document

    units = segment_document(doc)
    assert len(units) >= 1
    assert "Sr." in units[0]["text"] or any("Sr." in unit["text"] for unit in units)
