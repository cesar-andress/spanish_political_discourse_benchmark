"""Parse model responses into structured annotation records."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Tuple


JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def extract_json_object(raw: str) -> Dict[str, Any]:
    text = (raw or "").strip()
    if not text:
        raise ValueError("Empty model response")

    match = JSON_BLOCK_RE.search(text)
    if match:
        text = match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model response")
    payload = text[start : end + 1]
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("Model response JSON must be an object")
    return data


def parse_model_response(raw: str, *, unit_id: str, model_name: str) -> Tuple[Dict[str, Any], str | None]:
    try:
        data = extract_json_object(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        return {}, str(exc)

    data.setdefault("unit_id", unit_id)
    data.setdefault("model_name", model_name)
    return data, None
