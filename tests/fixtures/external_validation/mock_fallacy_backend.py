#!/usr/bin/env python3
"""Mock local LLM backend for SPDB external fallacy batch tests."""

from __future__ import annotations

import json
import sys

FAL_CYCLE = [
    [],
    ["FAL_ADHOM"],
    ["FAL_STRAW"],
    ["FAL_WHATABOUT", "FAL_EMOTION"],
]


def main() -> int:
    prompt = sys.stdin.read()
    row_id = "unknown"
    for line in prompt.splitlines():
        if line.startswith("row_id:"):
            row_id = line.split(":", 1)[1].strip()
            break

    index = sum(ord(ch) for ch in row_id) % len(FAL_CYCLE)
    labels = FAL_CYCLE[index]
    payload = {
        "fallacy_labels": labels,
        "fallacy_none_explicit": not labels,
        "confidence": 0.72,
        "explanation": "Etiquetado simulado para prueba del pipeline SPDB.",
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
