#!/usr/bin/env python3
"""Enforce module-level coverage thresholds for critical tooling paths."""

from __future__ import annotations

import logging
import subprocess
import sys

logger = logging.getLogger(__name__)

CRITICAL_COVERAGE_TARGETS: list[tuple[str, list[str], int]] = [
    ("src.tools.check_site_health", ["tests/test_check_site_health.py"], 85),
    (
        "src.tools.check_links",
        ["tests/test_check_links.py", "tests/test_check_links_additional.py"],
        70,
    ),
    ("src.tools.update_navigation", ["tests/test_update_navigation.py"], 80),
    ("scripts.generate_sitemap", ["tests/test_generate_sitemap.py"], 50),
    # Physics / control modules. Thresholds are set a few points below current
    # measured coverage so the gate ratchets against regressions rather than
    # immediately blocking PRs.
    (
        "src.golf_simulation.ball_flight",
        ["tests/test_golf_simulation/test_ball_flight.py"],
        85,
    ),
    (
        "src.golf_simulation.round_simulator",
        ["tests/test_golf_simulation/test_round_simulator.py"],
        85,
    ),
    (
        "src.golf_simulation.putting",
        ["tests/test_golf_simulation/test_putting.py"],
        75,
    ),
    (
        "src.golf_simulation.clubs",
        ["tests/test_golf_simulation/test_clubs.py"],
        85,
    ),
    (
        "src.core.optimizers.ilqr_solver",
        [
            "tests/test_ilqr_solver.py",
            "tests/test_ilqr_solver_invariants.py",
            "tests/test_ilqr_solver_preconditions.py",
            "tests/test_ilqr_central_diff.py",
        ],
        70,
    ),
    (
        "src.affine_control.swing_optimizer",
        [
            "tests/test_affine_control/test_swing_optimizer.py",
            "tests/test_affine_control/test_property_based.py",
        ],
        70,
    ),
]


def _run_coverage(module: str, tests: list[str], threshold: int) -> int:
    """Run pytest coverage for one module target."""
    cmd = [
        "pytest",
        *tests,
        f"--cov={module}",
        "--cov-report=term",
        f"--cov-fail-under={threshold}",
    ]
    logger.info("[coverage] module=%s threshold=%d tests=%s", module, threshold, ",".join(tests))
    result = subprocess.run(cmd, check=False)
    return result.returncode


def main() -> int:
    """Run module-level coverage checks and fail if any threshold is missed."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    failures = 0
    for module, tests, threshold in CRITICAL_COVERAGE_TARGETS:
        failures += 1 if _run_coverage(module, tests, threshold) != 0 else 0
    if failures:
        logger.error("%d critical module coverage checks failed.", failures)
        return 1
    logger.info("All critical module coverage checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
