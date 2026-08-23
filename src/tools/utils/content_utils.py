"""Shared utilities for QMD content file scanning.

Used by seo_audit.py, generate_sitemap.py, generate_feed.py,
add_meta_descriptions.py, and validate_accessibility.py to avoid
duplicating content directory iteration logic.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from src.core.contracts import require
from src.tools.utils import parse_frontmatter_dict

logger = logging.getLogger(__name__)

# Standard content directories to scan for QMD pages
DEFAULT_CONTENT_DIRS: list[str] = [".", "articles"]


def is_excluded_content_path(filepath: Path) -> bool:
    """Check if a path matches Quarto render exclusions or partial prefixes."""
    parts = filepath.parts
    if any(part.startswith("_") or part.startswith(".") for part in parts):
        return True
    posix = filepath.as_posix()
    excluded_patterns = [
        "articles/tangent-hyperplane-contraction",
        "articles/tangent-hyperplane-articles/Drafts_Original_Articles",
        "articles/tangent-hyperplane-articles/CRITICS_CORNER.qmd",
        "articles/proximal_distal_companion/chapters",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
        "critiques/INLINE_SUGGESTIONS.md",
    ]
    for pat in excluded_patterns:
        if pat in posix:
            return True
    return False


def _scan_directory_files(content_dir: str, include_critiques_md: bool) -> list[Path]:
    dir_path = Path(content_dir)
    if not dir_path.exists():
        return []
    if content_dir == ".":
        candidates = list(dir_path.glob("*.qmd"))
    else:
        candidates = list(dir_path.rglob("*.qmd"))
        if include_critiques_md and content_dir == "critiques":
            candidates.extend(dir_path.rglob("*.md"))
    return [p for p in candidates if not is_excluded_content_path(p)]


def collect_qmd_files(
    content_dirs: list[str] | None = None,
    include_critiques_md: bool = True,
) -> list[Path]:
    """Collect all non-partial, non-excluded content files from content directories.

    Args:
        content_dirs: Directories to scan. Defaults to DEFAULT_CONTENT_DIRS.
        include_critiques_md: Whether to include .md files in critiques directory.

    Returns:
        Sorted list of Path objects for content files.
    """
    dirs = content_dirs or DEFAULT_CONTENT_DIRS
    files: list[Path] = []
    for content_dir in dirs:
        files.extend(_scan_directory_files(content_dir, include_critiques_md))
    return sorted(set(files))


def read_qmd_with_frontmatter(
    filepath: Path,
) -> tuple[str, dict[str, Any]]:
    """Read a QMD file and parse its YAML frontmatter.

    Args:
        filepath: Path to the QMD file.

    Returns:
        Tuple of (full content string, parsed frontmatter dict).
        Returns empty dict on parse failure.
    """
    require(filepath is not None, "filepath must not be None")
    require(filepath.exists(), "filepath must exist")
    content = filepath.read_text(encoding="utf-8")
    try:
        frontmatter = parse_frontmatter_dict(content)
    except (ValueError, KeyError):
        frontmatter = {}
    return content, frontmatter
