#!/usr/bin/env python3
"""Check that _quarto.yml render rules include recursive article coverage."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    quarto_config = repo_root / "_quarto.yml"
    data = yaml.safe_load(quarto_config.read_text(encoding="utf-8"))

    render_rules = data.get("project", {}).get("render", [])
    if not isinstance(render_rules, list):
        print("ERROR: project.render is not a list")
        return 1

    required_rules = {"*.qmd", "articles/**/*.qmd"}
    missing = [rule for rule in required_rules if rule not in render_rules]
    if missing:
        print("ERROR: Missing required render rules:")
        for rule in missing:
            print(f"- {rule}")
        return 1

    print("Quarto render coverage check passed.")
    print("Render rules:")
    for rule in render_rules:
        print(f"- {rule}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
