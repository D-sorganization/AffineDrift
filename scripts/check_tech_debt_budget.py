#!/usr/bin/env python3
"""Fail CI when technical-debt markers exceed configured budget."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MARKERS = ("TODO", "FIXME", "HACK", "XXX")
MARKER_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)


def is_included(path: Path, include_roots: list[str], exclude_substrings: list[str]) -> bool:
    path_str = str(path).replace("\\", "/")
    if any(excl in path_str for excl in exclude_substrings):
        return False
    return any(path_str == root or path_str.startswith(f"{root}/") for root in include_roots)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    config_path = repo_root / "config" / "tech_debt_budget.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    include_roots = config["include_roots"]
    exclude_substrings = config["exclude_substrings"]
    allowed_exts = set(config["file_extensions"])
    max_total = int(config["max_total_markers"])
    max_per = {k.upper(): int(v) for k, v in config["max_per_marker"].items()}

    counts = {marker: 0 for marker in MARKERS}
    files_scanned = 0

    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root)
        if not is_included(rel, include_roots, exclude_substrings):
            continue
        if path.suffix and path.suffix.lower() not in allowed_exts:
            continue

        files_scanned += 1
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for match in MARKER_RE.finditer(text):
            marker = match.group(1).upper()
            if marker in counts:
                counts[marker] += 1

    total = sum(counts.values())
    print("Technical debt marker budget check")
    print(f"- files scanned: {files_scanned}")
    print(f"- total markers: {total} (max {max_total})")
    for marker in MARKERS:
        print(f"- {marker}: {counts[marker]} (max {max_per.get(marker, 0)})")

    errors: list[str] = []
    if total > max_total:
        errors.append(f"Total marker budget exceeded: {total} > {max_total}")
    for marker in MARKERS:
        limit = max_per.get(marker, 0)
        if counts[marker] > limit:
            errors.append(f"{marker} budget exceeded: {counts[marker]} > {limit}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
