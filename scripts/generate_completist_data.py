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
from pathlib import Path
from typing import Final

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


def is_text_file(filepath: Path) -> bool:
    """Determine if a file is text-based and should be scanned."""
    ext = filepath.suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return False
    if ext in TEXT_EXTENSIONS:
        return True
    # For unknown extensions, try to detect binary content
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:  # Binary file indicator
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
        if item.is_file() and not should_exclude_path(item, repo_root):
            if is_text_file(item):
                files.append(item)
    return files


def scan_for_todo_markers(files: list[Path], repo_root: Path) -> list[str]:
    """Scan files for TODO, FIXME, XXX, HACK, TEMP markers."""
    results: list[str] = []
    pattern = re.compile(r"\b(TODO|FIXME|XXX|HACK|TEMP)\b", re.IGNORECASE)

    for filepath in files:
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, 1):
                    if pattern.search(line):
                        rel_path = filepath.relative_to(repo_root)
                        results.append(f"{rel_path}:{line_num}:{line.strip()}")
        except OSError as e:
            logger.warning("Could not read %s: %s", filepath, e)

    return results


def scan_for_not_implemented(files: list[Path], repo_root: Path) -> list[str]:
    """Scan files for NotImplementedError occurrences."""
    results: list[str] = []
    pattern = re.compile(r"NotImplementedError|raise\s+NotImplemented")

    for filepath in files:
        if filepath.suffix != ".py":
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


def scan_for_stub_functions(files: list[Path], repo_root: Path) -> list[str]:
    """Scan Python files for stub/placeholder functions."""
    results: list[str] = []
    # Patterns for stubs: pass-only functions, ellipsis, placeholder returns
    stub_patterns = [
        re.compile(r"^\s*pass\s*$"),
        re.compile(r"^\s*\.\.\.\s*$"),
        re.compile(r"return\s+None\s*#.*stub|placeholder", re.IGNORECASE),
    ]

    for filepath in files:
        if filepath.suffix != ".py":
            continue
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                current_func: str | None = None
                func_line: int = 0

                for i, line in enumerate(lines, 1):
                    # Track function definitions
                    func_match = re.match(r"^\s*def\s+(\w+)\s*\(", line)
                    if func_match:
                        current_func = func_match.group(1)
                        func_line = i

                    # Check for stub patterns
                    if current_func:
                        for pattern in stub_patterns:
                            if pattern.search(line):
                                rel_path = filepath.relative_to(repo_root)
                                results.append(f"{rel_path}:{func_line} {current_func}")
                                current_func = None
                                break

        except OSError as e:
            logger.warning("Could not read %s: %s", filepath, e)

    return results


def scan_for_incomplete_docs(files: list[Path], repo_root: Path) -> list[str]:
    """Scan Python files for functions missing docstrings."""
    results: list[str] = []

    for filepath in files:
        if filepath.suffix != ".py":
            continue
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

                for i, line in enumerate(lines):
                    func_match = re.match(r"^\s*def\s+(\w+)\s*\(", line)
                    if func_match:
                        func_name = func_match.group(1)
                        # Skip private/dunder methods
                        if func_name.startswith("_") and not func_name.startswith("__"):
                            continue

                        # Check if next non-empty line is a docstring
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

        except OSError as e:
            logger.warning("Could not read %s: %s", filepath, e)

    return results


def scan_for_abstract_methods(files: list[Path], repo_root: Path) -> list[str]:
    """Scan Python files for @abstractmethod decorators."""
    results: list[str] = []

    for filepath in files:
        if filepath.suffix != ".py":
            continue
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, 1):
                    if "@abstractmethod" in line:
                        rel_path = filepath.relative_to(repo_root)
                        results.append(f"{rel_path}:{line_num}:{line.strip()}")
        except OSError as e:
            logger.warning("Could not read %s: %s", filepath, e)

    return results


def write_output(filepath: Path, data: list[str]) -> None:
    """Write scan results to output file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(data))
    logger.info("Wrote %d entries to %s", len(data), filepath)


def main() -> int:
    """Main entry point for completist data generation."""
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

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir or (repo_root / DATA_DIR)

    logger.info("Scanning repository: %s", repo_root)
    logger.info("Output directory: %s", output_dir)

    # Collect files
    files = collect_files(repo_root)
    logger.info("Found %d text files to scan", len(files))

    # Run scans
    todo_markers = scan_for_todo_markers(files, repo_root)
    write_output(output_dir / "todo_markers.txt", todo_markers)

    not_implemented = scan_for_not_implemented(files, repo_root)
    write_output(output_dir / "not_implemented.txt", not_implemented)

    stub_functions = scan_for_stub_functions(files, repo_root)
    write_output(output_dir / "stub_functions.txt", stub_functions)

    incomplete_docs = scan_for_incomplete_docs(files, repo_root)
    write_output(output_dir / "incomplete_docs.txt", incomplete_docs)

    abstract_methods = scan_for_abstract_methods(files, repo_root)
    write_output(output_dir / "abstract_methods.txt", abstract_methods)

    # Summary
    logger.info("=== Generation Complete ===")
    logger.info("  TODO/FIXME markers: %d", len(todo_markers))
    logger.info("  NotImplementedError: %d", len(not_implemented))
    logger.info("  Stub functions: %d", len(stub_functions))
    logger.info("  Missing docstrings: %d", len(incomplete_docs))
    logger.info("  Abstract methods: %d", len(abstract_methods))

    return 0


if __name__ == "__main__":
    sys.exit(main())
