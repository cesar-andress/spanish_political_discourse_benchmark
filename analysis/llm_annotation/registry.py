"""Ollama model registry helpers for SPDB LLM annotation."""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence


DEFAULT_REGISTRY = Path("configs/ollama_models.yaml")


@dataclass(frozen=True)
class OllamaModelSpec:
    name: str
    command: str


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_ollama_registry(path: Path = DEFAULT_REGISTRY) -> List[OllamaModelSpec]:
    if not path.exists():
        raise FileNotFoundError(f"Ollama registry not found: {path}")

    models: List[OllamaModelSpec] = []
    current_name: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- name:"):
            current_name = _strip_quotes(line.split(":", 1)[1])
            continue
        if line.startswith("name:") and current_name is None:
            current_name = _strip_quotes(line.split(":", 1)[1])
            continue
        if line.startswith("command:") and current_name:
            command = _strip_quotes(line.split(":", 1)[1])
            models.append(OllamaModelSpec(name=current_name, command=command))
            current_name = None

    if not models:
        raise ValueError(f"No models found in registry: {path}")
    return models


def ollama_cli_available() -> bool:
    return shutil.which("ollama") is not None


def list_installed_ollama_models() -> set[str]:
    if not ollama_cli_available():
        return set()
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return set()
    if result.returncode != 0:
        return set()

    installed: set[str] = set()
    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        name = line.split()[0]
        installed.add(name)
        installed.add(name.split(":", 1)[0])
    return installed


def model_is_installed(model_name: str, installed: Sequence[str] | None = None) -> bool:
    available = set(installed) if installed is not None else list_installed_ollama_models()
    if model_name in available:
        return True
    prefix = f"{model_name}:"
    return any(name == model_name or name.startswith(prefix) for name in available)


def resolve_model_availability(specs: Sequence[OllamaModelSpec]) -> tuple[List[OllamaModelSpec], List[str]]:
    if not ollama_cli_available():
        return [], [f"Ollama CLI not found in PATH; skipped {len(specs)} configured model(s)."]

    installed = list_installed_ollama_models()
    if not installed:
        return [], ["`ollama list` returned no installed models. Pull models before running the batch."]

    ready: List[OllamaModelSpec] = []
    notes: List[str] = []
    for spec in specs:
        if model_is_installed(spec.name, installed):
            ready.append(spec)
        else:
            notes.append(f"Model `{spec.name}` is not installed locally (not found in `ollama list`).")
    return ready, notes


def extract_ollama_model_name(command: str) -> str | None:
    parts = command.strip().split()
    if len(parts) >= 3 and parts[0] == "ollama" and parts[1] == "run":
        return parts[2]
    match = re.search(r"ollama\s+run\s+(\S+)", command)
    return match.group(1) if match else None
