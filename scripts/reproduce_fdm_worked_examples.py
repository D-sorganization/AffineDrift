#!/usr/bin/env python3
"""Reproduce Forward Dynamics Matching S1 worked examples (issue #5607).

python3 scripts/reproduce_fdm_worked_examples.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.tools.fdm_worked_examples import (
    format_scalar_report,
    format_sin_report,
    quarter_period_trapezoid_collocation,
    scalar_gradient_example,
    three_node_trapezoid_collocation,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit nonzero if canonical numbers drift from committed chapter values.",
    )
    args = parser.parse_args()

    scalar = scalar_gradient_example()
    three = three_node_trapezoid_collocation(1.0)
    quarter = quarter_period_trapezoid_collocation(1.0)

    print(format_scalar_report(scalar))
    print()
    print(format_sin_report(three, "Sin collocation — three nodes (07_collocation.qmd)"))
    print()
    print(format_sin_report(quarter, "Sin collocation — quarter-period refinement"))

    if args.check:
        expected = scalar_gradient_example()
        if abs(expected.x2 - 0.85) > 1e-9 or abs(expected.grad_a + 1.61) > 1e-9:
            return 1
        if not all(abs(value) < 1e-12 for value in three.states):
            return 1
        if abs(quarter.states[2] - 1.5707963267948966) > 1e-9:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
