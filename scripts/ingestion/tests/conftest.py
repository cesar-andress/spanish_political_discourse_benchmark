"""Pytest configuration for ingestion tests."""

from __future__ import annotations

import sys
from pathlib import Path

BENCHMARK_ROOT = Path(__file__).resolve().parents[3]
if str(BENCHMARK_ROOT) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_ROOT))

FIXTURES = BENCHMARK_ROOT / "tests" / "fixtures" / "pipeline"
