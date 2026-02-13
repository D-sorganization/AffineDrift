#!/usr/bin/env python3
"""Fail CI when file size budgets are exceeded."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def line_count(path: Path) -> int:
    content = path.read_text(encoding="utf-8")
    return content.count("\n") + (0 if content.endswith("\n") else 1)


def is_included(rel: str, include_roots: list[str], excludes: list[str]) -> bool:
    if any(excl in rel for excl in excludes):
        return False
    return any(rel == root or rel.startswith(f"{root}/") for root in include_roots)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    config_path = repo_root / "config" / "module_size_budget.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    include_roots = config["include_roots"]
    excludes = config["exclude_substrings"]
    max_by_ext = {k.lower(): int(v) for k, v in config["max_lines_by_extension"].items()}
    explicit_limits = {k: int(v) for k, v in config["explicit_limits"].items()}

    violations: list[str] = []
    checked = 0

    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue

        rel = path.relative_to(repo_root).as_posix()
        if not is_included(rel, include_roots, excludes):
            continue

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

    print(f"Module size budget check: files_checked={checked}")

    if not violations:
        print("Module size budget passed")
        return 0

    print("Module size violations:")
    for violation in violations:
        print(f"- {violation}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
