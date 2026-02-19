"""Logging configuration utilities.

This module provides standardized logging setup for AffineDrift tools.
All defaults are externalisable via environment variables so that the same
code can run with different verbosity in CI, production, and local dev
without any source changes (Pragmatic Programmer: Reversibility).

Environment variables
---------------------
``LOG_LEVEL``
    Default logging level.  Accepts Python level names (``DEBUG``,
    ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``).  Falls back to
    ``INFO`` when unset or invalid.

``LOG_FORMAT``
    Default ``logging.Formatter`` pattern.  Falls back to
    ``%(levelname)s: %(message)s`` when unset.

``LOG_FORMAT_TIMESTAMP``
    Timestamp-style format pattern.  Falls back to
    ``%(asctime)s - %(levelname)s - %(message)s`` when unset.

Example:
    from src.tools.utils import setup_logging

    logger = setup_logging(__name__)
    logger.info("Processing files...")
"""

from __future__ import annotations

import logging
import os

# ── Defaults (overridable via environment) ───────────────────────────────────

_DEFAULT_FORMAT = "%(levelname)s: %(message)s"
_DEFAULT_TIMESTAMP_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

_LEVEL_NAMES: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _resolve_log_level() -> int:
    """Return the logging level from ``LOG_LEVEL`` env var, or ``INFO``."""
    raw = os.environ.get("LOG_LEVEL", "").upper().strip()
    return _LEVEL_NAMES.get(raw, logging.INFO)


def _resolve_log_format() -> str:
    """Return the log format from ``LOG_FORMAT`` env var, or the default."""
    return os.environ.get("LOG_FORMAT", "").strip() or _DEFAULT_FORMAT


def _resolve_log_format_timestamp() -> str:
    """Return the timestamp format from ``LOG_FORMAT_TIMESTAMP`` env var."""
    return os.environ.get("LOG_FORMAT_TIMESTAMP", "").strip() or _DEFAULT_TIMESTAMP_FORMAT


# ── Public factory functions ─────────────────────────────────────────────────


def setup_logging(
    name: str | None = None,
    level: int | None = None,
    format_string: str | None = None,
) -> logging.Logger:
    """Configure and return a logger with standard settings.

    All parameters fall back to their corresponding environment variable
    when not explicitly supplied, making the logging behaviour reversible
    across deployment environments.

    Args:
        name: Logger name (typically ``__name__``). If ``None``, uses root logger.
        level: Logging level.  Defaults to ``LOG_LEVEL`` env var, then ``INFO``.
        format_string: Format string.  Defaults to ``LOG_FORMAT`` env var, then
            ``%(levelname)s: %(message)s``.

    Returns:
        Configured logger instance.

    Example:
        logger = setup_logging(__name__)
        logger.info("Starting process")
    """
    resolved_level = level if level is not None else _resolve_log_level()
    resolved_format = format_string if format_string is not None else _resolve_log_format()

    logging.basicConfig(
        level=resolved_level,
        format=resolved_format,
    )

    return logging.getLogger(name)


def setup_logging_with_timestamp(
    name: str | None = None,
    level: int | None = None,
) -> logging.Logger:
    """Configure and return a logger with timestamp format.

    Args:
        name: Logger name (typically ``__name__``).
        level: Logging level.  Defaults to ``LOG_LEVEL`` env var, then ``INFO``.

    Returns:
        Configured logger instance with timestamp format.

    Example:
        logger = setup_logging_with_timestamp(__name__)
        logger.info("Processing started")
    """
    return setup_logging(
        name=name,
        level=level,
        format_string=_resolve_log_format_timestamp(),
    )
