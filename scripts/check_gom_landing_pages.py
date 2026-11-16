#!/usr/bin/env python3
"""Fail CI when Geometry of Motion book landing pages drift from the manuscript."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.tools.gom_landing_page_contract import collect_violations  # noqa: E402


def main() -> int:
    violations = collect_violations(REPO_ROOT)
    if violations:
        print("GoM landing page contract violations:", file=sys.stderr)
        for line in violations:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print("GoM landing pages match the manuscript chapter contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
