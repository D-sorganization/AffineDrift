"""File discovery and path utilities.

This module provides common file finding patterns used across AffineDrift tools.

Example:
    from src.tools.utils import find_qmd_files, find_files_by_extension

    qmd_files = find_qmd_files()
    tex_files = find_files_by_extension([".tex"], search_dirs=["articles"])
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from pathlib import Path

from src.core.contracts import require

from .constants import EXCLUDE_DIRS_CONTENT, EXCLUDE_DIRS_PYTHON

logger = logging.getLogger(__name__)


def find_qmd_files(
    root_dir: str | Path = ".",
    exclude_dirs: list[str] | None = None,
    include_root: bool = True,
) -> list[Path]:
    """Find all .qmd files in relevant directories.

    Args:
        root_dir: Root directory to search from.
        exclude_dirs: Directory names to exclude (default: _site, .quarto, docs, archive).
        include_root: Whether to include root directory files.

    Returns:
        List of Path objects for found .qmd files.

    Example:
        files = find_qmd_files(exclude_dirs=["_site", "docs"])
    """
    if exclude_dirs is None:
        exclude_dirs = list(EXCLUDE_DIRS_CONTENT)

    root = Path(root_dir)
    files = []

    # Root files
    if include_root:
        for f in root.iterdir():
            if f.is_file() and f.suffix == ".qmd":
                files.append(f)

    # Recursive search excluding certain directories
    for f in root.rglob("*.qmd"):
        if not any(excluded in f.parts for excluded in exclude_dirs) and (
            not include_root or f.parent != root
        ):
            files.append(f)

    return files


def find_markdown_files(
    root_dir: str | Path = ".",
    include_qmd: bool = True,
    exclude_readme: bool = True,
    search_dirs: list[str] | None = None,
) -> list[Path]:
    """Find all Markdown-like files (.md, .qmd) in directories.

    Args:
        root_dir: Root directory to search from.
        include_qmd: Whether to include .qmd files.
        exclude_readme: Whether to exclude README files.
        search_dirs: Specific subdirectories to search (default: articles, critiques).

    Returns:
        List of Path objects for found files.

    Example:
        files = find_markdown_files(search_dirs=["articles", "posts"])
    """
    if search_dirs is None:
        search_dirs = ["articles", "critiques"]

    suffixes = {".md"}
    if include_qmd:
        suffixes.add(".qmd")

    root = Path(root_dir)
    files = []

    # Root files
    for f in root.iterdir():
        if (
            f.is_file()
            and f.suffix in suffixes
            and not (exclude_readme and f.name.startswith("README"))
        ):
            files.append(f)

    # Search specified directories
    for d in search_dirs:
        path = root / d
        if path.exists():
            for f in path.rglob("*"):
                if f.is_file() and f.suffix in suffixes and "archive" not in f.parts:
                    files.append(f)

    return files


def find_files_by_extension(
    extensions: list[str],
    paths: Sequence[str | Path] | None = None,
    root_dir: str | Path = ".",
    recursive: bool = False,
) -> list[Path]:
    """Find files by extension in given paths or root directory.

    Args:
        extensions: List of file extensions to find (e.g., [".tex", ".py"]).
        paths: Specific paths (files or directories) to search. If None, uses root_dir.
        root_dir: Root directory when paths is None.
        recursive: Whether to search recursively in directories.

    Returns:
        List of Path objects for found files.

    Example:
        tex_files = find_files_by_extension([".tex"], paths=["articles", "papers"])
        py_files = find_files_by_extension([".py"], recursive=True)
    """
    require(len(extensions) > 0, "extensions list must not be empty")
    # Normalize extensions
    extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]

    found_files: list[Path] = []

    if paths is None:
        # Search root directory
        root = Path(root_dir)
        if recursive:
            for ext in extensions:
                found_files.extend(root.rglob(f"*{ext}"))
        else:
            for ext in extensions:
                found_files.extend(root.glob(f"*{ext}"))
    else:
        # Search specified paths
        for path_str in paths:
            path = Path(path_str)
            if not path.exists():
                continue

            if path.is_file() and path.suffix in extensions:
                found_files.append(path)
            elif path.is_dir():
                for ext in extensions:
                    if recursive:
                        found_files.extend(path.rglob(f"*{ext}"))
                    else:
                        found_files.extend(path.glob(f"*{ext}"))

    return found_files


def process_file_content(
    filepath: Path,
    transform_fn: Callable[[str], str],
    encoding: str = "utf-8",
) -> bool:
    """Read a file, apply a transformation, and write back if changed.

    This is a common pattern for file processing scripts that modify content.
    It handles encoding errors gracefully and only writes if content changed.

    Args:
        filepath: Path to the file to process.
        transform_fn: Function that takes content string and returns transformed content.
        encoding: File encoding (default: utf-8).

    Returns:
        True if file was modified, False otherwise.

    Example:
        def fix_whitespace(content: str) -> str:
            return content.rstrip() + "\\n"

        modified = process_file_content(Path("file.txt"), fix_whitespace)
    """
    require(filepath is not None, "filepath must not be None")
    try:
        content = filepath.read_text(encoding=encoding)
    except UnicodeDecodeError:
        return False
    except FileNotFoundError:
        return False

    original_content = content
    new_content = transform_fn(content)

    if new_content != original_content:
        filepath.write_text(new_content, encoding=encoding)
        return True

    return False


def find_html_files(
    root_dir: str | Path = ".",
    docs_only: bool = True,
    limit: int | None = None,
) -> list[Path]:
    """Find HTML files, typically in docs directory.

    Args:
        root_dir: Root directory to search from.
        docs_only: Whether to only search in docs/ directory.
        limit: Maximum number of files to return.

    Returns:
        List of Path objects for found HTML files.

    Example:
        html_files = find_html_files(limit=10)
    """
    root = Path(root_dir)

    if docs_only:
        search_path = root / "docs"
        if not search_path.exists():
            return []
    else:
        search_path = root

    files = list(search_path.rglob("*.html"))

    if limit is not None:
        files = files[:limit]

    return files


def get_python_files(
    root_dir: str | Path = ".",
    exclude_dirs: list[str] | None = None,
) -> list[Path]:
    """Find all .py files excluding common non-source directories.

    Args:
        root_dir: Root directory to search from.
        exclude_dirs: Directory names to exclude (default: .git, .venv, etc.).

    Returns:
        List of Path objects for found .py files.
    """
    if exclude_dirs is None:
        exclude_dirs = list(EXCLUDE_DIRS_PYTHON)

    root = Path(root_dir)
    return [
        p for p in root.rglob("*.py") if not any(excluded in p.parts for excluded in exclude_dirs)
    ]
