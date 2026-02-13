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

MARKERS = ("TODO", "FIXME", "HACK", "XXX")
MARKER_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)


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
        for match in MARKER_RE.finditer(text):
            marker = match.group(1).upper()
            if marker in counts:
                counts[marker] += 1

    total = sum(counts.values())
    details = [f"total markers: {total} (max {max_total})"]
    details.extend(f"{m}: {counts[m]} (max {max_per.get(m, 0)})" for m in MARKERS)

    errors: list[str] = []
    if total > max_total:
        errors.append(f"Total marker budget exceeded: {total} > {max_total}")
    for marker in MARKERS:
        limit = max_per.get(marker, 0)
        if counts[marker] > limit:
            errors.append(f"{marker} budget exceeded: {counts[marker]} > {limit}")

    return report_results("Technical debt marker budget check", len(files), details, errors)


if __name__ == "__main__":
    sys.exit(main())
