#!/usr/bin/env python3
"""Generate completist data files by scanning the repository.

This script scans the repository for various completion gaps and generates
intermediate data files that are consumed by analyze_completist_data.py.

Stage 1 of the Completist Pipeline: Data Generation

Output files:
- .jules/completist_data/todo_markers.txt
- .jules/completist_data/not_implemented.txt
- .jules/completist_data/stub_functions.txt
- .jules/completist_data/incomplete_docs.txt
- .jules/completist_data/abstract_methods.txt
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Final

from src.tools.utils.cli_contracts import ensure_existing_dir, ensure_writable_output_file

# Configuration
DATA_DIR: Final[str] = ".jules/completist_data"

# File extensions to scan
TEXT_EXTENSIONS: Final[set[str]] = {
    ".py",
    ".js",
    ".ts",
    ".m",
    ".qmd",
    ".md",
    ".yml",
    ".yaml",
    ".json",
    ".html",
    ".css",
    ".scss",
}

# Binary extensions to skip (helps avoid corrupted output)
BINARY_EXTENSIONS: Final[set[str]] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".svg",
    ".mp4",
    ".webm",
    ".webp",
    ".zip",
    ".tar",
    ".gz",
}

# Directories to exclude
EXCLUDED_DIRS: Final[set[str]] = {
    ".git",
    ".github",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".vscode",
    ".jules",
    "docs",
    "archive",
    "legacy",
    ".quarto",
    "_site",
    "dist",
    "build",
}

logger = logging.getLogger(__name__)


# ─── File Collection ─────────────────────────────────────────────


def is_text_file(filepath: Path) -> bool:
    """Determine if a file is text-based and should be scanned."""
    ext = filepath.suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return False
    if ext in TEXT_EXTENSIONS:
        return True
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return False
    except OSError:
        return False
    return True


def should_exclude_path(path: Path, repo_root: Path) -> bool:
    """Check if path should be excluded from scanning."""
    rel_path = path.relative_to(repo_root)
    parts = rel_path.parts
    return any(part in EXCLUDED_DIRS for part in parts)


def collect_files(repo_root: Path) -> list[Path]:
    """Collect all text files in the repository."""
    files: list[Path] = []
    for item in repo_root.rglob("*"):
        if item.is_file() and not should_exclude_path(item, repo_root) and is_text_file(item):
            files.append(item)
    return files


# ─── Generic Line Scanner (DRY) ─────────────────────────────────


def _scan_files_by_line(
    files: list[Path],
    repo_root: Path,
    pattern: re.Pattern[str],
    *,
    py_only: bool = False,
) -> list[str]:
    """Scan files line-by-line for regex matches.

    This is the consolidated scanner that eliminates the repeated
    open-read-match-append boilerplate in every ``scan_for_*`` function.

    Args:
        files: Files to scan.
        repo_root: Root to compute relative paths.
        pattern: Compiled regex to match against each line.
        py_only: If True, only scan ``.py`` files.

    Returns:
        List of ``rel_path:line_num:stripped_line`` strings.
    """
    results: list[str] = []
    for filepath in files:
        if py_only and filepath.suffix != ".py":
            continue
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, 1):
                    if pattern.search(line):
                        rel_path = filepath.relative_to(repo_root)
                        results.append(f"{rel_path}:{line_num}:{line.strip()}")
        except OSError as e:
            logger.warning("Could not read %s: %s", filepath, e)
    return results


def _scan_files_multi_pattern(
    files: list[Path],
    repo_root: Path,
    patterns: list[re.Pattern[str]],
) -> list[str]:
    """Scan files line-by-line for any of multiple patterns.

    Args:
        files: Files to scan.
        repo_root: Root to compute relative paths.
        patterns: Compiled regex patterns (any match → record).

    Returns:
        List of ``rel_path:line_num:stripped_line`` strings.
    """
    results: list[str] = []
    for filepath in files:
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, 1):
                    for pattern in patterns:
                        if pattern.search(line):
                            rel_path = filepath.relative_to(repo_root)
                            results.append(f"{rel_path}:{line_num}:{line.strip()}")
                            break  # one match per line
        except OSError as e:
            logger.warning("Could not read %s: %s", filepath, e)
    return results


# ─── Specific Scanners (delegates to generic) ───────────────────


def scan_for_todo_markers(files: list[Path], repo_root: Path) -> list[str]:
    """Scan files for completion markers (TODO, FIXME, etc)."""
    markers = ["TOD" + "O", "FIX" + "ME", "XXX", "HACK", "TEMP"]
    pattern = re.compile(r"\b(" + "|".join(markers) + r")\b", re.IGNORECASE)
    return _scan_files_by_line(files, repo_root, pattern)


def scan_for_placeholders(files: list[Path], repo_root: Path) -> list[str]:
    """Scan files for placeholder content."""
    patterns = [
        re.compile(r"\bplaceholder\b", re.IGNORECASE),
        re.compile(r"\bcoming\s+soon\b", re.IGNORECASE),
        re.compile(r"\bunder\s+construction\b", re.IGNORECASE),
        re.compile(r"\blorem\s+ipsum\b", re.IGNORECASE),
        re.compile(r"placehold\.co", re.IGNORECASE),
    ]
    return _scan_files_multi_pattern(files, repo_root, patterns)


def scan_for_not_implemented(files: list[Path], repo_root: Path) -> list[str]:
    """Scan files for NotImplementedError occurrences."""
    nie = "Not" + "ImplementedError"
    pattern = re.compile(nie + r"|raise\s+Not" + r"Implemented")
    return _scan_files_by_line(files, repo_root, pattern, py_only=True)


def scan_for_abstract_methods(files: list[Path], repo_root: Path) -> list[str]:
    """Scan Python files for @abstractmethod decorators."""
    pattern = re.compile(r"@abstractmethod")
    return _scan_files_by_line(files, repo_root, pattern, py_only=True)


def _iter_python_file_lines(
    files: list[Path],
) -> Iterator[tuple[Path, list[str]]]:
    """Yield (filepath, lines) for each Python file that can be read.

    Centralises the filter-by-ext / open / readlines / error-handling
    boilerplate shared by stub and docstring scanners.
    """
    for filepath in files:
        if filepath.suffix != ".py":
            continue
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                yield filepath, f.readlines()
        except OSError as e:
            logger.warning("Could not read %s: %s", filepath, e)


def scan_for_stub_functions(files: list[Path], repo_root: Path) -> list[str]:
    """Scan Python files for stub/placeholder functions."""
    results: list[str] = []
    stub_patterns = [
        re.compile(r"^\s*pass\s*$"),
        re.compile(r"^\s*\.\.\.\s*$"),
        re.compile(r"return\s+None\s*#.*stub|placeholder", re.IGNORECASE),
    ]

    for filepath, lines in _iter_python_file_lines(files):
        current_func: str | None = None
        func_line: int = 0

        for i, line in enumerate(lines, 1):
            func_match = re.match(r"^\s*def\s+(\w+)\s*\(", line)
            if func_match:
                current_func = func_match.group(1)
                func_line = i

            if current_func:
                for pattern in stub_patterns:
                    if pattern.search(line):
                        rel_path = filepath.relative_to(repo_root)
                        results.append(f"{rel_path}:{func_line} {current_func}")
                        current_func = None
                        break

    return results


def scan_for_incomplete_docs(files: list[Path], repo_root: Path) -> list[str]:
    """Scan Python files for functions missing docstrings."""
    results: list[str] = []

    for filepath, lines in _iter_python_file_lines(files):
        for i, line in enumerate(lines):
            func_match = re.match(r"^\s*def\s+(\w+)\s*\(", line)
            if not func_match:
                continue
            func_name = func_match.group(1)
            if func_name.startswith("_") and not func_name.startswith("__"):
                continue

            has_docstring = False
            for j in range(i + 1, min(i + 5, len(lines))):
                next_line = lines[j].strip()
                if not next_line:
                    continue
                if next_line.startswith('"""') or next_line.startswith("'''"):
                    has_docstring = True
                break

            if not has_docstring:
                rel_path = filepath.relative_to(repo_root)
                results.append(f"{rel_path}:{i + 1} {func_name}")

    return results


# ─── Output ──────────────────────────────────────────────────────


def write_output(filepath: Path, data: list[str]) -> None:
    """Write scan results to output file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(data))
    logger.info("Wrote %d entries to %s", len(data), filepath)


# ─── Scanner Registry (DRY dispatch) ────────────────────────────

ScanFunc = Callable[[list[Path], Path], list[str]]

SCAN_REGISTRY: list[tuple[str, ScanFunc]] = [
    ("todo_markers.txt", scan_for_todo_markers),
    ("not_implemented.txt", scan_for_not_implemented),
    ("stub_functions.txt", scan_for_stub_functions),
    ("incomplete_docs.txt", scan_for_incomplete_docs),
    ("abstract_methods.txt", scan_for_abstract_methods),
    ("placeholder_content.txt", scan_for_placeholders),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for completist data generation."""
    parser = argparse.ArgumentParser(
        description="Generate completist data files by scanning the repository."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=f"Output directory for data files (default: {DATA_DIR})",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Main entry point for completist data generation."""
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        repo_root = ensure_existing_dir(str(args.repo_root), value_name="--repo-root").resolve()
        output_dir = (
            ensure_writable_output_file(str(args.output_dir), value_name="--output-dir").resolve()
            if args.output_dir
            else (repo_root / DATA_DIR)
        )
    except ValueError as exc:
        logger.error("%s", exc)
        return 2

    logger.info("Scanning repository: %s", repo_root)
    logger.info("Output directory: %s", output_dir)

    files = collect_files(repo_root)
    logger.info("Found %d text files to scan", len(files))

    # Run all scanners via registry
    for filename, scanner in SCAN_REGISTRY:
        results = scanner(files, repo_root)
        write_output(output_dir / filename, results)
        label = filename.replace(".txt", "").replace("_", " ").title()
        logger.info("  %s: %d", label, len(results))

    logger.info("=== Generation Complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
