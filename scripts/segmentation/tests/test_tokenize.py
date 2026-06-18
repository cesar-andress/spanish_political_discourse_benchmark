from __future__ import annotations

from scripts.segmentation.tokenize import count_tokens_beto, estimate_token_count


def test_estimate_token_count_non_empty():
    text = "La sanidad pública requiere financiación estable."
    assert estimate_token_count(text) >= 5


def test_count_tokens_beto_fallback_without_model():
    text = "Impulsaremos la competitividad de las pymes españolas."
    assert count_tokens_beto(text, use_model=False) == estimate_token_count(text)


def test_empty_text_has_zero_tokens():
    assert count_tokens_beto("", use_model=False) == 0
