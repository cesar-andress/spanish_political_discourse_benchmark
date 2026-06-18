"""BETO token counting for SPDB segmentation caps."""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import Optional

logger = logging.getLogger("spdb.segmentation.tokenize")

BETO_MODEL_ID = "dccuchile/bert-base-spanish-wwm-cased"
_TOKENIZER: Optional[object] = None


@lru_cache(maxsize=1)
def _load_beto_tokenizer():
    try:
        from transformers import AutoTokenizer
    except ImportError:
        logger.debug("transformers not installed; using token estimate fallback")
        return None

    try:
        return AutoTokenizer.from_pretrained(BETO_MODEL_ID)
    except Exception as exc:  # pragma: no cover - network/model unavailable in CI
        logger.warning("Could not load BETO tokenizer (%s); using estimate fallback", exc)
        return None


def estimate_token_count(text: str) -> int:
    """
    Heuristic Spanish token estimate when BETO tokenizer is unavailable.

    Uses whitespace tokens plus punctuation splits, scaled to approximate BPE length.
    """
    if not text:
        return 0
    pieces = re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)
    return max(1, int(len(pieces) * 1.15))


def count_tokens_beto(text: str, *, use_model: bool = False) -> int:
    """
    Count tokens with the BETO tokenizer when available.

    Parameters
    ----------
    text:
        Input string (Spanish).
    use_model:
        When True, attempt to load the Hugging Face BETO tokenizer.
        Default False keeps tests/offline runs on the estimate fallback.
    """
    if not text:
        return 0

    tokenizer = _load_beto_tokenizer() if use_model else None
    if tokenizer is None:
        return estimate_token_count(text)

    token_ids = tokenizer.encode(text, add_special_tokens=False)
    return len(token_ids)
