#!/usr/bin/env python3
"""Fail CI when UI anti-pattern counts exceed configured budget."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def is_included(path: Path, include_roots: list[str], exclude_substrings: list[str]) -> bool:
    path_str = str(path).replace("\\", "/")
    if any(excl in path_str for excl in exclude_substrings):
        return False
    return any(path_str == root or path_str.startswith(f"{root}/") for root in include_roots)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    config_path = repo_root / "config" / "ui_ux_budget.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    include_roots = config["include_roots"]
    exclude_substrings = config["exclude_substrings"]
    allowed_exts = set(config["file_extensions"])
    check_configs = config["checks"]

    compiled = {
        name: {
            "regex": re.compile(check["pattern"], re.IGNORECASE | re.MULTILINE),
            "max_count": int(check["max_count"]),
        }
        for name, check in check_configs.items()
    }
    counts = {name: 0 for name in compiled}
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

        for name, check in compiled.items():
            counts[name] += len(check["regex"].findall(text))

    print("UI/UX anti-pattern budget check")
    print(f"- files scanned: {files_scanned}")
    for name, check in compiled.items():
        print(f"- {name}: {counts[name]} (max {check['max_count']})")

    errors: list[str] = []
    for name, check in compiled.items():
        if counts[name] > check["max_count"]:
            errors.append(f"{name} budget exceeded: {counts[name]} > {check['max_count']}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
