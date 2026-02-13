#!/usr/bin/env python3
"""Fail CI when file size budgets are exceeded."""

from __future__ import annotations

import sys
from pathlib import Path

from src.tools.utils.budget_check_utils import (
    collect_matching_files,
    load_config,
    report_results,
)


def line_count(path: Path) -> int:
    """Count lines in a text file."""
    content = path.read_text(encoding="utf-8")
    return content.count("\n") + (0 if content.endswith("\n") else 1)


def main() -> int:
    """Check file line counts against module size budget limits."""
    repo_root = Path(__file__).resolve().parent.parent
    config = load_config(repo_root, "module_size_budget.json")

    max_by_ext = {k.lower(): int(v) for k, v in config["max_lines_by_extension"].items()}
    explicit_limits = {k: int(v) for k, v in config["explicit_limits"].items()}

    files = collect_matching_files(
        repo_root,
        config["include_roots"],
        config["exclude_substrings"],
    )

    violations: list[str] = []
    checked = 0

    for path in files:
        rel = path.relative_to(repo_root).as_posix()

        if rel in explicit_limits:
            max_lines = explicit_limits[rel]
        else:
            max_lines = max_by_ext.get(path.suffix.lower())
            if max_lines is None:
                continue

        checked += 1
        lines = line_count(path)
        if lines > max_lines:
            violations.append(f"{rel}: {lines} > {max_lines}")

    return report_results(
        "Module size budget check",
        checked,
        details=[],
        errors=violations,
    )


if __name__ == "__main__":
    sys.exit(main())
