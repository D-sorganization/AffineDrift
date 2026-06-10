#!/usr/bin/env python3
"""Fail CI when UI anti-pattern counts exceed configured budget."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from src.tools.utils.budget_check_utils import (
    collect_matching_files,
    load_config,
    read_text_safe,
    report_results,
)


def compile_checks(check_configs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Compile the configured anti-pattern regexes with their budgets."""
    return {
        name: {
            "regex": re.compile(check["pattern"], re.IGNORECASE | re.MULTILINE),
            "max_count": int(check["max_count"]),
        }
        for name, check in check_configs.items()
    }


def evaluate_ui_ux_budget(
    counts: dict[str, int], compiled: dict[str, dict[str, Any]]
) -> tuple[list[str], list[str]]:
    """Evaluate anti-pattern counts against their per-check budgets.

    Pure function returning ``(details, errors)``.
    """
    details = [
        f"{name}: {counts.get(name, 0)} (max {c['max_count']})" for name, c in compiled.items()
    ]
    errors: list[str] = []
    for name, check in compiled.items():
        if counts.get(name, 0) > check["max_count"]:
            errors.append(f"{name} budget exceeded: {counts[name]} > {check['max_count']}")
    return details, errors


def main() -> int:
    """Check UI/UX anti-pattern counts against budget limits."""
    repo_root = Path(__file__).resolve().parent.parent
    config = load_config(repo_root, "ui_ux_budget.json")

    files = collect_matching_files(
        repo_root,
        config["include_roots"],
        config["exclude_substrings"],
        set(config["file_extensions"]),
    )

    compiled = compile_checks(config["checks"])
    counts = {name: 0 for name in compiled}

    for path in files:
        text = read_text_safe(path)
        if text is None:
            continue
        for name, check in compiled.items():
            counts[name] += len(check["regex"].findall(text))

    details, errors = evaluate_ui_ux_budget(counts, compiled)
    return report_results("UI/UX anti-pattern budget check", len(files), details, errors)


if __name__ == "__main__":
    sys.exit(main())
