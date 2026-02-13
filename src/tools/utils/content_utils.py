"""Shared utilities for QMD content file scanning.

Used by seo_audit.py, generate_sitemap.py, generate_search_index.py,
add_meta_descriptions.py, and validate_accessibility.py to avoid
duplicating content directory iteration logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.tools.utils import parse_frontmatter_dict

# Standard content directories to scan for QMD pages
DEFAULT_CONTENT_DIRS: list[str] = [".", "articles"]


def collect_qmd_files(
    content_dirs: list[str] | None = None,
) -> list[Path]:
    """Collect all non-partial QMD files from content directories.

    Args:
        content_dirs: Directories to scan. Defaults to DEFAULT_CONTENT_DIRS.

    Returns:
        Sorted list of Path objects for QMD files (excluding _ prefixed).
    """
    dirs = content_dirs or DEFAULT_CONTENT_DIRS
    files: list[Path] = []
    for content_dir in dirs:
        dir_path = Path(content_dir)
        if not dir_path.exists():
            continue
        for filepath in dir_path.glob("*.qmd"):
            if not filepath.name.startswith("_"):
                files.append(filepath)
    return sorted(files)


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
    content = filepath.read_text(encoding="utf-8")
    try:
        frontmatter = parse_frontmatter_dict(content)
    except Exception:
        frontmatter = {}
    return content, frontmatter
