#!/usr/bin/env python3
"""Enforce contract helper adoption in key CLI entrypoints."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def check_rules(repo_root: Path) -> list[str]:
    config = json.loads((repo_root / "config" / "contract_coverage_rules.json").read_text())
    violations: list[str] = []

    for rule in config["rules"]:
        rel_path = rule["path"]
        target = repo_root / rel_path
        if not target.exists():
            violations.append(f"missing required file: {rel_path}")
            continue

        content = target.read_text(encoding="utf-8")
        for token in rule["required_tokens"]:
            if token not in content:
                violations.append(f"{rel_path} missing contract token: {token}")

    return violations


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    violations = check_rules(repo_root)

    if not violations:
        print("Contract coverage check passed")
        return 0

    print("Contract coverage violations:")
    for violation in violations:
        print(f"- {violation}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
