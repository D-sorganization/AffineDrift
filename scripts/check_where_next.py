#!/usr/bin/env python3
"""CLI check for the Standard "Where Next" Footer (WEB-03.5 #4510).

Validates:
1. No page links to itself (Acceptance Criterion 1).
2. Each core page has at least one "simpler" and one "deeper" link (Acceptance Criterion 2).
3. All configured link targets exist and are valid.
"""

from __future__ import annotations

import sys
from pathlib import Path

from src.tools.where_next import load_where_next_config, validate_where_next_config


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "config" / "where_next.yml"
    if not config_path.exists():
        print(f"ERROR: {config_path} does not exist.", file=sys.stderr)
        return 1

    try:
        config = load_where_next_config(config_path)
    except Exception as exc:
        print(f"ERROR loading {config_path}: {exc}", file=sys.stderr)
        return 1

    errors = validate_where_next_config(config, repo_root)
    if errors:
        print(f"FAILED: Found {len(errors)} where_next error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"SUCCESS: Validated {len(config)} where_next entries. All criteria passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
