"""Abstract ingestion pipeline for SPDB v1."""

from __future__ import annotations

import argparse
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence

from scripts.ingestion.common import (
    read_jsonl,
    setup_logging,
    validate_discourse_unit,
    write_jsonl,
)


@dataclass
class IngestConfig:
    input_path: Path
    intermediate_path: Path
    processed_path: Path
    pipeline_version: str = "0.1.0"
    split: str = "unassigned"
    dry_run: bool = False
    validate_only: bool = False


class BaseIngestor(ABC):
    """Three-stage ingestion: raw → intermediate JSONL → discourse_unit JSONL."""

    source_name: str
    source_type: str
    source_corpus: str

    def __init__(self, config: IngestConfig, logger: Optional[logging.Logger] = None) -> None:
        self.config = config
        self.logger = logger or logging.getLogger(f"spdb.ingestion.{self.source_name}")

    @classmethod
    def add_source_cli_args(cls, parser: argparse.ArgumentParser) -> None:
        """Optional hook for source-specific CLI flags."""

    @abstractmethod
    def parse_raw(self, input_path: Path) -> Iterator[Dict[str, Any]]:
        """Parse vendor-specific raw files into intermediate-ready records."""

    @abstractmethod
    def to_discourse_units(self, intermediate_records: Iterable[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """Map intermediate records to discourse_unit objects."""

    def validate_units(self, units: Iterable[Dict[str, Any]]) -> List[str]:
        errors: List[str] = []
        for index, unit in enumerate(units):
            field_errors = validate_discourse_unit(unit)
            for message in field_errors:
                errors.append(f"record {index}: {message}")
        return errors

    def run(self) -> tuple[int, int]:
        """
        Execute the ingestion pipeline.

        Returns:
            (intermediate_count, processed_count)
        """
        self.logger.info(
            "Starting %s ingestion: input=%s",
            self.source_name,
            self.config.input_path,
        )

        if not self.config.input_path.exists():
            raise FileNotFoundError(f"Input path not found: {self.config.input_path}")

        intermediate_records = list(self.parse_raw(self.config.input_path))
        self.logger.info("Parsed %d intermediate record(s)", len(intermediate_records))

        if self.config.dry_run:
            self.logger.info("Dry run: skipping writes")
            units = list(self.to_discourse_units(intermediate_records))
            validation_errors = self.validate_units(units)
            if validation_errors:
                for message in validation_errors[:10]:
                    self.logger.error(message)
                raise ValueError(
                    f"Validation failed with {len(validation_errors)} error(s) during dry run"
                )
            return len(intermediate_records), len(units)

        if not self.config.validate_only:
            intermediate_written = write_jsonl(self.config.intermediate_path, intermediate_records)
            self.logger.info(
                "Wrote intermediate JSONL: %s (%d records)",
                self.config.intermediate_path,
                intermediate_written,
            )
        else:
            intermediate_written = len(intermediate_records)
            self.logger.info("Validate-only: skipping intermediate write")

        source_records = (
            intermediate_records
            if self.config.validate_only
            else read_jsonl(self.config.intermediate_path)
        )
        units = list(self.to_discourse_units(source_records))
        validation_errors = self.validate_units(units)
        if validation_errors:
            for message in validation_errors[:10]:
                self.logger.error(message)
            raise ValueError(f"Validation failed with {len(validation_errors)} error(s)")

        if not self.config.validate_only:
            processed_written = write_jsonl(self.config.processed_path, units)
            self.logger.info(
                "Wrote processed JSONL: %s (%d records)",
                self.config.processed_path,
                processed_written,
            )
        else:
            processed_written = len(units)
            self.logger.info("Validate-only: skipping processed write")

        return intermediate_written, processed_written


def add_common_cli_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to raw input file or directory manifest (local only; no downloads).",
    )
    parser.add_argument(
        "--intermediate-out",
        type=Path,
        help="Output path for intermediate JSONL (default: data/intermediate/<source>/documents.jsonl).",
    )
    parser.add_argument(
        "--processed-out",
        type=Path,
        help="Output path for discourse_unit JSONL (default: data/processed/<source>/discourse_units.jsonl).",
    )
    parser.add_argument(
        "--pipeline-version",
        default="0.1.0",
        help="Pipeline version string stored in provenance fields.",
    )
    parser.add_argument(
        "--split",
        default="unassigned",
        choices=["train", "dev", "test", "unassigned"],
        help="Split label embedded in instance_id (final split assignment happens downstream).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without writing output files.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Parse and validate discourse units without writing any output files.",
    )


def run_ingest_cli(
    ingestor_cls: type[BaseIngestor],
    argv: Optional[Sequence[str]] = None,
    default_intermediate: Optional[Path] = None,
    default_processed: Optional[Path] = None,
) -> int:
    parser = argparse.ArgumentParser(description=f"SPDB v1 ingestion — {ingestor_cls.source_name}")
    add_common_cli_args(parser)
    ingestor_cls.add_source_cli_args(parser)
    args = parser.parse_args(argv)

    setup_logging(args.log_level)
    config = IngestConfig(
        input_path=args.input,
        intermediate_path=args.intermediate_out or default_intermediate,
        processed_path=args.processed_out or default_processed,
        pipeline_version=args.pipeline_version,
        split=args.split,
        dry_run=args.dry_run,
        validate_only=args.validate_only,
    )
    if config.intermediate_path is None or config.processed_path is None:
        raise SystemExit("Missing default output paths; pass --intermediate-out and --processed-out.")

    ingestor = ingestor_cls(config)
    intermediate_count, processed_count = ingestor.run()
    logging.getLogger("spdb.ingestion").info(
        "Done: intermediate=%d processed=%d",
        intermediate_count,
        processed_count,
    )
    return 0
