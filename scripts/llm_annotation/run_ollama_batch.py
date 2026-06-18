#!/usr/bin/env python3
"""Run SPDB pilot annotation across configured Ollama models."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Sequence

from analysis.llm_annotation.backend import CommandBackend
from analysis.llm_annotation.constants import DEFAULT_OUTPUT_DIR, DEFAULT_PILOT_INPUT, DEFAULT_REPORT_DIR
from analysis.llm_annotation.pipeline import run_local_annotation
from analysis.llm_annotation.registry import (
    DEFAULT_REGISTRY,
    OllamaModelSpec,
    load_ollama_registry,
    ollama_cli_available,
    resolve_model_availability,
)


@dataclass
class BatchFailure:
    model_name: str
    reason: str


@dataclass
class BatchRunResult:
    successes: List[str] = field(default_factory=list)
    failures: List[BatchFailure] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def write_batch_failures_report(
    *,
    path: Path,
    failures: Sequence[BatchFailure],
    skipped: Sequence[str],
    successes: Sequence[str],
    registry_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Ollama batch annotation failures",
        "",
        f"Registry: `{registry_path}`",
        f"Generated: {timestamp}",
        "",
    ]
    if successes:
        lines.extend(["## Successful models", ""])
        for model in successes:
            lines.append(f"- `{model}`")
        lines.append("")

    if skipped:
        lines.extend(["## Skipped models", ""])
        for note in skipped:
            lines.append(f"- {note}")
        lines.append("")

    if failures:
        lines.extend(["## Runtime failures", ""])
        for failure in failures:
            lines.append(f"- `{failure.model_name}`: {failure.reason}")
        lines.append("")
    elif not skipped:
        lines.append("_No failures recorded._")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def probe_backend(command: str, *, timeout_seconds: int = 45) -> tuple[bool, str]:
    try:
        backend = CommandBackend(command, timeout_seconds=timeout_seconds)
        backend.generate("Reply with the single word OK.")
        return True, ""
    except Exception as exc:  # noqa: BLE001 - batch runner records all startup failures
        return False, str(exc)


def run_ollama_batch(
    *,
    registry_path: Path = DEFAULT_REGISTRY,
    pilot_path: Path = DEFAULT_PILOT_INPUT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    failures_report: Path = DEFAULT_REPORT_DIR / "ollama_batch_failures.md",
    skip_availability_check: bool = False,
    skip_probe: bool = False,
    models: Sequence[OllamaModelSpec] | None = None,
) -> BatchRunResult:
    specs = list(models) if models is not None else load_ollama_registry(registry_path)
    result = BatchRunResult()

    ready_specs = specs
    if not skip_availability_check:
        ready_specs, skipped = resolve_model_availability(specs)
        result.skipped.extend(skipped)
        if not ollama_cli_available() and specs:
            write_batch_failures_report(
                path=failures_report,
                failures=result.failures,
                skipped=result.skipped,
                successes=result.successes,
                registry_path=registry_path,
            )
            return result

    for spec in ready_specs:
        if not skip_probe:
            ok, reason = probe_backend(spec.command)
            if not ok:
                result.failures.append(BatchFailure(model_name=spec.name, reason=f"startup probe failed: {reason}"))
                continue

        try:
            run_result = run_local_annotation(
                pilot_path=pilot_path,
                model_name=spec.name,
                backend_command=spec.command,
                output_dir=output_dir,
            )
        except Exception as exc:  # noqa: BLE001 - continue with remaining models
            result.failures.append(BatchFailure(model_name=spec.name, reason=str(exc)))
            continue

        if run_result.output_path and run_result.output_path.exists():
            result.successes.append(spec.name)
        else:
            result.failures.append(
                BatchFailure(model_name=spec.name, reason="annotation run completed without output JSONL")
            )

    write_batch_failures_report(
        path=failures_report,
        failures=result.failures,
        skipped=result.skipped,
        successes=result.successes,
        registry_path=registry_path,
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SPDB pilot annotation across Ollama models.")
    parser.add_argument("--config", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--pilot-input", type=Path, default=DEFAULT_PILOT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--failures-report", type=Path, default=DEFAULT_REPORT_DIR / "ollama_batch_failures.md")
    parser.add_argument(
        "--skip-availability-check",
        action="store_true",
        help="Do not check `ollama list` before running (useful for mock/test commands).",
    )
    parser.add_argument(
        "--skip-probe",
        action="store_true",
        help="Skip the startup probe and run annotation directly.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    result = run_ollama_batch(
        registry_path=args.config,
        pilot_path=args.pilot_input,
        output_dir=args.output_dir,
        failures_report=args.failures_report,
        skip_availability_check=args.skip_availability_check,
        skip_probe=args.skip_probe,
    )
    print(f"Successful models: {len(result.successes)}")
    for model in result.successes:
        print(f"- {model}")
    if result.skipped:
        print(f"Skipped models: {len(result.skipped)}")
    if result.failures:
        print(f"Failed models: {len(result.failures)} (see {args.failures_report})")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
