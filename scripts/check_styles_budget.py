#!/usr/bin/env python3
"""Enforce CSS quality budgets for the primary site stylesheet."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def count_important(text: str) -> int:
    return len(re.findall(r"!important\b", text))


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    config_path = repo_root / "config" / "css_quality_budget.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    styles_path = repo_root / config["styles_path"]
    css = styles_path.read_text(encoding="utf-8")

    line_count = css.count("\n") + (0 if css.endswith("\n") else 1)
    important_count = count_important(css)
    max_lines = int(config["max_lines"])
    max_important = int(config["max_important"])

    print(f"CSS budget check: {styles_path.relative_to(repo_root)}")
    print(f"- lines: {line_count} (max {max_lines})")
    print(f"- !important count: {important_count} (max {max_important})")

    failures: list[str] = []
    if line_count > max_lines:
        failures.append(
            f"Line budget exceeded: {line_count} > {max_lines}. "
            "Split page-specific blocks into scoped stylesheets."
        )
    if important_count > max_important:
        failures.append(
            f"!important budget exceeded: {important_count} > {max_important}. "
            "Prefer specificity layering and scoped selectors."
        )

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
