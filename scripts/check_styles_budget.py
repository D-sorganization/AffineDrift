#!/usr/bin/env python3
"""Enforce CSS quality budgets for the primary site stylesheet."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from src.tools.utils.budget_check_utils import load_config, report_results


def count_important(text: str) -> int:
    """Count occurrences of !important in CSS text."""
    return len(re.findall(r"!important\b", text))


def count_lines(text: str) -> int:
    """Count logical lines in CSS text (trailing newline does not add one)."""
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def evaluate_budget(
    line_count: int,
    important_count: int,
    max_lines: int,
    max_important: int,
) -> list[str]:
    """Return budget-violation messages (empty list means the budget passes).

    Pure function so the gate logic is unit-testable without filesystem or
    subprocess. A count exactly at the budget is allowed; one over fails.
    """
    errors: list[str] = []
    if line_count > max_lines:
        errors.append(
            f"Line budget exceeded: {line_count} > {max_lines}. "
            "Split page-specific blocks into scoped stylesheets."
        )
    if important_count > max_important:
        errors.append(
            f"!important budget exceeded: {important_count} > {max_important}. "
            "Prefer specificity layering and scoped selectors."
        )
    return errors


def main() -> int:
    """Check CSS stylesheet against quality budgets."""
    repo_root = Path(__file__).resolve().parent.parent
    config = load_config(repo_root, "css_quality_budget.json")

    styles_path = repo_root / config["styles_path"]
    css = styles_path.read_text(encoding="utf-8")

    line_count = count_lines(css)
    important_count = count_important(css)
    max_lines = int(config["max_lines"])
    max_important = int(config["max_important"])

    details = [
        f"lines: {line_count} (max {max_lines})",
        f"!important count: {important_count} (max {max_important})",
    ]

    errors = evaluate_budget(line_count, important_count, max_lines, max_important)

    return report_results(
        f"CSS budget check: {styles_path.relative_to(repo_root)}",
        files_scanned=1,
        details=details,
        errors=errors,
    )


if __name__ == "__main__":
    sys.exit(main())
