"""Shared helpers for batch conversion scripts."""

from __future__ import annotations

import logging
import os
from collections.abc import Mapping, Sequence
from typing import Protocol


class FileConverter(Protocol):
    """Minimal protocol for file-based converters."""

    def convert_file(self, source: str, target: str) -> None: ...


def run_batch_conversion(
    *,
    conversions: Sequence[Mapping[str, object]],
    converter: FileConverter,
    logger: logging.Logger,
    dry_run: bool,
    description_key: str | None = None,
) -> tuple[int, int]:
    """Run a shared conversion loop across a list of source/target mappings."""
    success_count = 0
    error_count = 0

    for conversion in conversions:
        source = conversion.get("source")
        target = conversion.get("target")
        description = conversion.get(description_key, "") if description_key else ""

        if not isinstance(source, str) or not isinstance(target, str):
            logger.error("Invalid conversion entry: source and target must be strings")
            error_count += 1
            continue

        if not os.path.exists(source):
            if description:
                logger.warning("Source file not found: %s (%s)", source, description)
            else:
                logger.warning("Source file not found: %s", source)
            error_count += 1
            continue

        if dry_run:
            logger.info("Would convert: %s -> %s", source, target)
            success_count += 1
            continue

        try:
            converter.convert_file(source, target)
            logger.info("Converted: %s -> %s", source, target)
            success_count += 1
        except (FileNotFoundError, PermissionError, OSError, ValueError) as error:
            logger.error("Failed to convert %s: %s", source, error)
            error_count += 1

    return success_count, error_count
