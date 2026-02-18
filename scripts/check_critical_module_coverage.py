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
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    failures = 0
    for module, tests, threshold in CRITICAL_COVERAGE_TARGETS:
        failures += 1 if _run_coverage(module, tests, threshold) != 0 else 0
    if failures:
        logger.error("ERROR: %d critical module coverage checks failed.", failures)
        return 1
    logger.info("All critical module coverage checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
