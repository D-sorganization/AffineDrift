#!/usr/bin/env python3
"""Enforce module-level coverage thresholds for critical modules.

Each target names a dotted module, the test files that exercise it, and a
minimum per-module coverage floor. The floors ratchet against regressions: a
PR that drops a critical module's coverage below its floor fails the gate even
when the global coverage blend still passes.

Coverage is collected with ``--cov=src`` (the whole tree) rather than
``--cov=<module>``. Restricting coverage to a single submodule makes pytest-cov
import that submodule at startup, and for numpy/scipy-backed modules that
second import trips numpy's "cannot load module more than once per process"
guard during collection. Measuring the whole tree and then reading the target
module's percentage out of the JSON report avoids that import entirely.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

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


def _module_to_path(module: str) -> str:
    """Convert a dotted module name to its source file path (no extension)."""
    return module.replace(".", "/")


def _coverage_percent_for(report: dict, module: str) -> float | None:
    """Return the percent-covered for ``module`` from a coverage JSON report."""
    files = report.get("files", {})
    target = _module_to_path(module)
    for filename, data in files.items():
        normalized = filename.replace("\\", "/")
        if normalized in (f"{target}.py", f"{target}/__init__.py"):
            summary = data.get("summary", {})
            return float(summary.get("percent_covered", 0.0))
    return None


def _run_coverage(module: str, tests: list[str], threshold: int) -> int:
    """Run pytest for one target and check the module's coverage floor.

    Coverage is collected for the whole ``src`` tree to avoid importing the
    target submodule twice (which breaks numpy-backed modules); the per-module
    percentage is then read from the JSON report and compared to ``threshold``.

    Returns 0 when the module meets its floor, non-zero otherwise.
    """
    logger.info("[coverage] module=%s threshold=%d tests=%s", module, threshold, ",".join(tests))
    with tempfile.TemporaryDirectory() as tmp:
        json_path = Path(tmp) / "coverage.json"
        cmd = [
            "pytest",
            *tests,
            "--cov=src",
            "--cov=scripts",
            f"--cov-report=json:{json_path}",
            "--cov-report=term-missing",
            # The whole-tree total for a single target's tests is far below the
            # global fail_under; disable that total gate so only the per-module
            # floor (checked below from the JSON report) decides pass/fail.
            "--cov-fail-under=0",
        ]
        result = subprocess.run(cmd, check=False)
        if result.returncode not in (0, 5):
            # 5 == no tests collected; any other non-zero is a real test failure.
            logger.error("[coverage] module=%s test run failed (rc=%d)", module, result.returncode)
            return result.returncode

        if not json_path.exists():
            logger.error("[coverage] module=%s produced no coverage report", module)
            return 1

        report = json.loads(json_path.read_text(encoding="utf-8"))

    percent = _coverage_percent_for(report, module)
    if percent is None:
        logger.error("[coverage] module=%s not found in coverage report", module)
        return 1

    if percent + 1e-9 < threshold:
        logger.error(
            "[coverage] module=%s coverage %.1f%% is below floor %d%%",
            module,
            percent,
            threshold,
        )
        return 1

    logger.info("[coverage] module=%s coverage %.1f%% meets floor %d%%", module, percent, threshold)
    return 0


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
