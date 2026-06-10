#!/usr/bin/env python3
"""Fail CI when technical-debt markers exceed configured budget."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from src.tools.utils.budget_check_utils import (
    collect_matching_files,
    load_config,
    read_text_safe,
    report_results,
)

MARKERS = ("TRACKED" + "_TASK", "TRACKED" + "_DEFECT", "HACK", "XXX")
MARKER_RE = re.compile(
    r"\b(TRACKED_TASK|TRACKED_DEFECT|HACK|XXX)\b".replace("TRACKED_", "TRACKED" + "_"),
    re.IGNORECASE,
)


def count_markers(text: str) -> dict[str, int]:
    """Count debt markers in a single text blob, keyed by upper-case marker."""
    counts = {marker: 0 for marker in MARKERS}
    for match in MARKER_RE.finditer(text):
        marker = match.group(1).upper()
        if marker in counts:
            counts[marker] += 1
    return counts


def evaluate_tech_debt_budget(
    counts: dict[str, int], max_total: int, max_per: dict[str, int]
) -> tuple[list[str], list[str]]:
    """Evaluate marker counts against total and per-marker budgets.

    Pure function returning ``(details, errors)``; a non-empty ``errors``
    list means at least one budget was exceeded.
    """
    total = sum(counts.get(m, 0) for m in MARKERS)
    details = [f"total markers: {total} (max {max_total})"]
    details.extend(f"{m}: {counts.get(m, 0)} (max {max_per.get(m, 0)})" for m in MARKERS)

    errors: list[str] = []
    if total > max_total:
        errors.append(f"Total marker budget exceeded: {total} > {max_total}")
    for marker in MARKERS:
        limit = max_per.get(marker, 0)
        if counts.get(marker, 0) > limit:
            errors.append(f"{marker} budget exceeded: {counts[marker]} > {limit}")
    return details, errors


def main() -> int:
    """Check technical-debt marker counts against budget limits."""
    repo_root = Path(__file__).resolve().parent.parent
    config = load_config(repo_root, "tech_debt_budget.json")

    allowed_exts = set(config["file_extensions"])
    max_total = int(config["max_total_markers"])
    max_per = {k.upper(): int(v) for k, v in config["max_per_marker"].items()}

    files = collect_matching_files(
        repo_root,
        config["include_roots"],
        config["exclude_substrings"],
        allowed_exts,
    )

    counts = {marker: 0 for marker in MARKERS}
    for path in files:
        text = read_text_safe(path)
        if text is None:
            continue
        for marker, count in count_markers(text).items():
            counts[marker] += count

    details, errors = evaluate_tech_debt_budget(counts, max_total, max_per)
    return report_results("Technical debt marker budget check", len(files), details, errors)


if __name__ == "__main__":
    sys.exit(main())
