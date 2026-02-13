"""Shared utilities for CI budget-check scripts (DRY consolidation).

This module provides the common infrastructure used by all ``check_*_budget.py``
and ``check_*_boundaries.py`` scripts:

- ``is_included``: reusable path-inclusion filter (include roots + excludes).
- ``collect_matching_files``: walk a repo tree, applying include/exclude/ext rules.
- ``report_results``: print results and return exit code.

All budget scripts had near-identical file-walking, inclusion, and reporting
boilerplate.  Pulling them here eliminates ~40 duplicate code-block detections.
"""

from __future__ import annotations

import json
from pathlib import Path


def load_config(repo_root: Path, config_name: str) -> dict:
    """Load a JSON config from the ``config/`` directory.

    Args:
        repo_root: Repository root path.
        config_name: Config file name (e.g. ``tech_debt_budget.json``).

    Returns:
        Parsed JSON as a dictionary.
    """
    config_path = repo_root / "config" / config_name
    return json.loads(config_path.read_text(encoding="utf-8"))


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
    matched: list[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root)
        if not is_included(rel, include_roots, exclude_substrings):
            continue
        if allowed_extensions and path.suffix and path.suffix.lower() not in allowed_extensions:
            continue
        matched.append(path)
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
    """Print a standardized budget-check report and return an exit code.

    Args:
        check_name: Human-readable name (e.g. "Technical debt marker budget check").
        files_scanned: Number of files scanned.
        details: Lines to print under the header (counts, etc.).
        errors: Error messages.  Non-empty → exit 1.

    Returns:
        ``0`` if no errors, ``1`` otherwise.
    """
    print(check_name)
    print(f"- files scanned: {files_scanned}")
    for detail in details:
        print(f"- {detail}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    return 0
