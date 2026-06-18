#!/usr/bin/env python3
"""Mock local LLM backend for SPDB tests and dry local runs."""

from __future__ import annotations

import json
import sys

PF = ["PF_ATTACK", "PF_ADVOCACY", "PF_INFO", "PF_DEFENSE"]
FAL = ["FAL_NONE", "FAL_ADHOM", "FAL_STRAW"]


def main() -> int:
    prompt = sys.stdin.read()
    unit_id = "unknown"
    for line in prompt.splitlines():
        if line.startswith("unit_id:"):
            unit_id = line.split(":", 1)[1].strip()
            break
    index = sum(ord(ch) for ch in unit_id) % len(PF)
    payload = {
        "unit_id": unit_id,
        "model_name": "mock-local",
        "pragmatic_function": PF[index],
        "fallacy_labels": [FAL[index % len(FAL)]],
        "confidence": 0.7,
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
