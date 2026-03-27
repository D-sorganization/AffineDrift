from numba import jit

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


@jit(nopython=True, fastmath=True)
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
    success_count = 0
    error_count = 0

    for entry in file_pairs:
        source = entry.get("source")
        target = entry.get("target")

        if not isinstance(source, str) or not isinstance(target, str):
            logger.error(
                "Invalid conversion entry: source and target must be strings (got %r, %r)",
                source,
                target,
            )
            error_count += 1
            continue

        if not os.path.exists(source):
            logger.warning("Source file not found: %s", source)
            error_count += 1
            continue

        if dry_run:
            logger.info("Would convert: %s -> %s", source, target)
            success_count += 1
        else:
            try:
                converter.convert_file(source, target)
                logger.info("Converted: %s -> %s", source, target)
                success_count += 1
            except (FileNotFoundError, PermissionError, OSError, ValueError) as exc:
                logger.error("Failed to convert %s: %s", source, exc)
                error_count += 1

    return error_count == 0
