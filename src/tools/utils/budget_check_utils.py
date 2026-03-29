"""Shared utilities for CI budget-check scripts (DRY consolidation).

This module provides the common infrastructure used by all ``check_*_budget.py``
and ``check_*_boundaries.py`` scripts:

- ``is_included``: reusable path-inclusion filter (include roots + excludes).
- ``collect_matching_files``: walk a repo tree, applying include/exclude/ext rules.
- ``report_results``: log results and return exit code.

All budget scripts had near-identical file-walking, inclusion, and reporting
boilerplate.  Pulling them here eliminates ~40 duplicate code-block detections.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.core.contracts import require

logger = logging.getLogger(__name__)


def load_config(repo_root: Path, config_name: str) -> dict[str, Any]:
    """Load a JSON config from the ``config/`` directory.

    Args:
        repo_root: Repository root path.
        config_name: Config file name (e.g. ``tech_debt_budget.json``).

    Returns:
        Parsed JSON as a dictionary.
    """
    require(repo_root is not None, "repo_root must not be None")
    require(len(config_name) > 0, "config_name must not be empty")
    config_path = repo_root / "config" / config_name
    result: dict[str, Any] = json.loads(config_path.read_text(encoding="utf-8"))
    return result


def is_included(
    path: Path | str,
    include_roots: list[str],
    exclude_substrings: list[str],
) -> bool:
    """Determine whether *path* passes inclusion/exclusion filters.

    Args:
        path: Relative path (``PurePosixPath``-style or ``Path`` object).
        include_roots: Prefixes a path must match to be included.
        exclude_substrings: Any path containing one of these is excluded.

    Returns:
        ``True`` if the path should be processed.
    """
    path_str = str(path).replace("\\", "/")
    if any(excl in path_str for excl in exclude_substrings):
        return False
    return any(path_str == root or path_str.startswith(f"{root}/") for root in include_roots)


def collect_matching_files(
    repo_root: Path,
    include_roots: list[str],
    exclude_substrings: list[str],
    allowed_extensions: set[str] | None = None,
) -> list[Path]:
    """Walk *repo_root* and return files matching inclusion rules.

    Args:
        repo_root: Repository root directory.
        include_roots: Path prefixes that must match.
        exclude_substrings: Substrings that disqualify a path.
        allowed_extensions: If provided, only files whose lowered suffix
            is in this set are returned.

    Returns:
        Sorted list of matching ``Path`` objects.
    """
    require(repo_root.is_dir(), "repo_root must be an existing directory")
    require(len(include_roots) > 0, "include_roots must not be empty")
    matched = [
        path
        for path in repo_root.rglob("*")
        if path.is_file()
        and is_included(path.relative_to(repo_root), include_roots, exclude_substrings)
        and not (
            allowed_extensions and path.suffix and path.suffix.lower() not in allowed_extensions
        )
    ]
    return sorted(matched)


def read_text_safe(path: Path) -> str | None:
    """Read text from *path*, returning ``None`` on encoding errors.

    Args:
        path: File to read.

    Returns:
        File contents or ``None`` if the file cannot be decoded.
    """
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def report_results(
    check_name: str,
    files_scanned: int,
    details: list[str],
    errors: list[str],
) -> int:
    """Log a standardized budget-check report and return an exit code.

    Args:
        check_name: Human-readable name (e.g. "Technical debt marker budget check").
        files_scanned: Number of files scanned.
        details: Lines to log under the header (counts, etc.).
        errors: Error messages.  Non-empty → exit 1.

    Returns:
        ``0`` if no errors, ``1`` otherwise.
    """
    require(len(check_name) > 0, "check_name must not be empty")
    require(files_scanned >= 0, "files_scanned must be non-negative", files_scanned)
    logger.info(check_name)
    logger.info("- files scanned: %d", files_scanned)
    for detail in details:
        logger.info("- %s", detail)

    if errors:
        for err in errors:
            logger.error("ERROR: %s", err)
        return 1
    return 0
