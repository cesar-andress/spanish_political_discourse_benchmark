"""Local command-based LLM backend adapter."""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from typing import Protocol


class AnnotationBackend(Protocol):
    def generate(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class CommandBackend:
    command: str
    timeout_seconds: int = 180

    def generate(self, prompt: str) -> str:
        parts = shlex.split(self.command)
        if not parts:
            raise ValueError("Backend command is empty")
        result = subprocess.run(
            parts,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            raise RuntimeError(
                f"Backend command failed with exit code {result.returncode}: {stderr or 'no stderr'}"
            )
        stdout = (result.stdout or "").strip()
        if not stdout:
            raise RuntimeError("Backend command returned empty stdout")
        return stdout


@dataclass(frozen=True)
class MockResponseBackend:
    responses_by_unit_id: dict[str, str]

    def generate(self, prompt: str) -> str:
        for unit_id, response in self.responses_by_unit_id.items():
            if f"unit_id: {unit_id}" in prompt or f'"unit_id": "{unit_id}"' in prompt:
                return response
        raise KeyError("No mock response configured for prompt unit_id")


def load_mock_responses(path) -> dict[str, str]:
    import json
    from pathlib import Path

    mapping: dict[str, str] = {}
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            unit_id = payload["unit_id"]
            mapping[unit_id] = json.dumps(payload, ensure_ascii=False)
    return mapping
