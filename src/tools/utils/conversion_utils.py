"""Shared batch file conversion utility for AffineDrift converter tools.

This module provides a single, reusable conversion loop that eliminates duplication
between batch converter scripts (convert_all_latex.py, convert_all_to_quarto.py, etc.).

Example:
    from src.tools.utils.conversion_utils import batch_convert

    success = batch_convert(converter, CONVERSIONS, dry_run=False, logger=logger)
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from typing import Any


def _validate_conversion_entry(
    entry: dict[str, Any], logger: logging.Logger
) -> tuple[str, str] | None:
    """Return (source, target) for a valid entry, or None if invalid or missing."""
    source = entry.get("source")
    target = entry.get("target")

    if not isinstance(source, str) or not isinstance(target, str):
        logger.error(
            "Invalid conversion entry: source and target must be strings (got %r, %r)",
            source,
            target,
        )
        return None

    if not os.path.exists(source):
        logger.warning("Source file not found: %s", source)
        return None

    return source, target


def _perform_conversion(
    converter: Any,
    source: str,
    target: str,
    dry_run: bool,
    logger: logging.Logger,
) -> bool:
    """Run or stub a single conversion, returning True on success."""
    if dry_run:
        logger.info("Would convert: %s -> %s", source, target)
        return True
    try:
        converter.convert_file(source, target)
        logger.info("Converted: %s -> %s", source, target)
        return True
    except (FileNotFoundError, PermissionError, OSError, ValueError) as exc:
        logger.error("Failed to convert %s: %s", source, exc)
        return False


def batch_convert(
    converter: Any,
    file_pairs: Iterable[dict[str, Any]],
    dry_run: bool,
    logger: logging.Logger,
) -> bool:
    """Run a batch file conversion loop.

    Iterates over *file_pairs*, checking source existence, then either logs the
    intended conversion (dry_run) or calls ``converter.convert_file(source, target)``.

    Args:
        converter: Object that exposes a ``convert_file(source, target)`` method.
        file_pairs: Iterable of dicts, each with at minimum ``"source"`` (str) and
            ``"target"`` (str) keys.  Extra keys (e.g. ``"description"``) are ignored.
        dry_run: When *True* log what would be converted without calling convert_file.
        logger: Logger instance used for progress and error messages.

    Returns:
        ``True`` if every present source file converted without error, ``False``
        otherwise (missing source or conversion exception each count as an error).

    Raises:
        TypeError: If *file_pairs* is not iterable.
    """
    error_count = 0

    for entry in file_pairs:
        validated = _validate_conversion_entry(entry, logger)
        if validated is None:
            error_count += 1
            continue

        source, target = validated
        if not _perform_conversion(converter, source, target, dry_run, logger):
            error_count += 1

    return error_count == 0
