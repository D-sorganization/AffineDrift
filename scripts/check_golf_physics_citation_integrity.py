#!/usr/bin/env python3
"""CI gate for Physics of Golf citation defects (AffineDrift issue #5600).

Runs offline checks on ``golf_physics.bib`` and the paired Quarto chapters
that were corrected in the 2026-11-10 technical review (F7--F10). Exits 0
when clean, 1 with a human-readable violation list.

    python3 scripts/check_golf_physics_citation_integrity.py
"""

from __future__ import annotations

import sys

from src.tools.golf_physics_citation_integrity import find_violations


def main() -> int:
    violations = find_violations()
    if not violations:
        print("Physics of Golf citation-integrity check passed.")
        return 0

    print("Physics of Golf citation-integrity violations:")
    for item in violations:
        print(f"  - {item}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
