#!/usr/bin/env python3
"""Orchestrator for the code quality check pipeline.

Ties together AST analysis, pattern checking, and report generation.
Can be invoked directly or via pre-commit hooks.
"""

from __future__ import annotations

import sys
from pathlib import Path

from src.core.contracts import require

from .ast_analyzer import check_ast_issues
from .pattern_checker import check_banned_patterns, check_magic_numbers
from .report_generator import report_issues


def check_file(filepath: Path) -> list[tuple[int, str, str]]:
    """Check a single Python file for quality issues.

    Runs all three checkers (banned patterns, magic numbers, AST issues)
    and returns the aggregated results.

    Args:
        filepath: Path to the Python file to check.

    Returns:
        List of ``(line_number, message, code_snippet)`` tuples.
    """
    require(filepath is not None, "filepath must not be None")
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.splitlines()

        issues: list[tuple[int, str, str]] = []
        issues.extend(check_banned_patterns(lines, filepath))
        issues.extend(check_magic_numbers(lines, filepath))
        issues.extend(check_ast_issues(content, filepath))
    except (OSError, UnicodeDecodeError) as e:
        return [(0, f"Error reading file: {e}", "")]
    else:
        return issues


# Directories excluded from recursive scanning
_EXCLUDE_DIRS = frozenset(
    {
        "archive",
        "Archive",
        "legacy",
        "experimental",
        ".git",
        "__pycache__",
        ".ruff_cache",
        ".mypy_cache",
        "matlab",
        "output",
        ".ipynb_checkpoints",
        ".Trash",
        "node_modules",
        "site-packages",
        "dist-packages",
        "venv",
        ".venv",
    }
)


def main() -> None:
    """Run quality checks on Python files.

    Accepts explicit file paths from ``sys.argv`` (pre-commit mode)
    or recursively scans the working directory.
    """
    # Support direct file arguments from pre-commit
    if len(sys.argv) > 1:
        python_files = [Path(arg) for arg in sys.argv[1:]]
    else:
        python_files = list(Path().rglob("*.py"))

    # Filter if scanning directory
    if len(sys.argv) <= 1:
        python_files = [
            f for f in python_files if not any(part in _EXCLUDE_DIRS for part in f.parts)
        ]

    all_issues = []
    for filepath in python_files:
        issues = check_file(filepath)
        if issues:
            all_issues.append((filepath, issues))

    # Report
    if all_issues:
        report_issues(all_issues)
        sys.exit(1)
    else:
        # Explicitly exit with success status for pre-commit hooks
        sys.exit(0)


if __name__ == "__main__":
    main()
