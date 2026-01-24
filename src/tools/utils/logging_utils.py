"""Logging configuration utilities.

This module provides standardized logging setup for AffineDrift tools.

Example:
    from src.tools.utils import setup_logging

    logger = setup_logging(__name__)
    logger.info("Processing files...")
"""

from __future__ import annotations

import logging


def setup_logging(
    name: str | None = None,
    level: int = logging.INFO,
    format_string: str | None = None,
) -> logging.Logger:
    """Configure and return a logger with standard settings.

    Args:
        name: Logger name (typically __name__). If None, uses root logger.
        level: Logging level (default: logging.INFO).
        format_string: Custom format string. If None, uses standard format.

    Returns:
        Configured logger instance.

    Example:
        logger = setup_logging(__name__)
        logger.info("Starting process")
    """
    if format_string is None:
        format_string = "%(levelname)s: %(message)s"

    logging.basicConfig(
        level=level,
        format=format_string,
    )

    return logging.getLogger(name)


def setup_logging_with_timestamp(
    name: str | None = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """Configure and return a logger with timestamp format.

    Args:
        name: Logger name (typically __name__).
        level: Logging level (default: logging.INFO).

    Returns:
        Configured logger instance with timestamp format.

    Example:
        logger = setup_logging_with_timestamp(__name__)
        logger.info("Processing started")
    """
    return setup_logging(
        name=name,
        level=level,
        format_string="%(asctime)s - %(levelname)s - %(message)s",
    )
