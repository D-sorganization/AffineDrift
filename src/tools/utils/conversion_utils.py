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
    entry: dict[str, Any],
    logger: logging.Logger,
) -> tuple[str | None, str | None]:
    """Validate a single conversion entry and return (source, target) or (None, None).

    Logs an error and returns (None, None) if the entry is invalid or the source
    file does not exist.

    Args:
        entry: Dict with ``"source"`` and ``"target"`` string keys.
        logger: Logger for error/warning messages.

    Returns:
        Tuple of (source, target) strings if valid, or (None, None) on failure.
    """
    source = entry.get("source")
    target = entry.get("target")
    if not isinstance(source, str) or not isinstance(target, str):
        logger.error(
            "Invalid conversion entry: source and target must be strings (got %r, %r)",
            source,
            target,
        )
        return None, None
    if not os.path.exists(source):
        logger.warning("Source file not found: %s", source)
        return None, None
    return source, target


def _execute_single_conversion(
    converter: Any,
    source: str,
    target: str,
    dry_run: bool,
    logger: logging.Logger,
) -> bool:
    """Execute or dry-run a single file conversion.

    Args:
        converter: Object with a ``convert_file(source, target)`` method.
        source: Path to the source file.
        target: Path to the target file.
        dry_run: If True, only log the intended conversion without converting.
        logger: Logger for progress and error messages.

    Returns:
        True on success (or dry-run), False if conversion raised an exception.
    """
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

    Args:
        converter: Object that exposes a ``convert_file(source, target)`` method.
        file_pairs: Iterable of dicts, each with ``"source"`` and ``"target"`` keys.
        dry_run: When *True* log what would be converted without calling convert_file.
        logger: Logger instance used for progress and error messages.

    Returns:
        ``True`` if every present source file converted without error, ``False`` otherwise.

    Raises:
        TypeError: If *file_pairs* is not iterable.
    """
    all_ok = True
    for entry in file_pairs:
        source, target = _validate_conversion_entry(entry, logger)
        if source is None:
            all_ok = False
            continue
        if not _execute_single_conversion(converter, source, target, dry_run, logger):
            all_ok = False
    return all_ok
