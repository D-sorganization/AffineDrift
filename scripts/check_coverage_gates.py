#!/usr/bin/env python3
"""Per-module coverage gates for AffineDrift.

Enforces minimum test-coverage thresholds for key source packages.
Designed to run in CI or locally via::

    python3 scripts/check_coverage_gates.py

Each gate runs ``pytest --cov`` for a source package against
its associated test files and fails if coverage drops below the
specified threshold.

Design-by-Contract
-------------------
Preconditions:
    - ``pytest`` and ``pytest-cov`` must be installed.
    - The working directory must be the repository root.
Postconditions:
    - Exit code 0 if ALL gates pass.
    - Exit code 1 if ANY gate fails, with a summary printed to stderr.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CoverageGate:
    """A single per-module coverage gate.

    Attributes
    ----------
    package : str
        Dotted Python import path of the package to measure
        (e.g. ``src.affine_control``).
    test_paths : tuple[str, ...]
        Filesystem paths to the test files / directories that exercise
        the package.
    threshold : int
        Minimum coverage percentage (0-100).
    """

    package: str
    test_paths: tuple[str, ...]
    threshold: int

    def __post_init__(self) -> None:
        """Validate that the coverage threshold is within 0-100 range."""
        if not 0 <= self.threshold <= 100:
            raise ValueError(f"threshold must be 0-100, got {self.threshold}")


# -----------------------------------------------------------------------
# Gate definitions
# -----------------------------------------------------------------------

COVERAGE_GATES: list[CoverageGate] = [
    CoverageGate(
        package="src.affine_control",
        test_paths=("tests/test_affine_control/",),
        threshold=80,
    ),
    CoverageGate(
        package="src.core",
        test_paths=(
            "tests/test_constants.py",
            "tests/test_protocols.py",
            "tests/test_properties.py",
            "tests/unit/test_contracts.py",
            "tests/test_dbc_application_contracts.py",
        ),
        threshold=70,
    ),
    CoverageGate(
        package="src.tangent_models",
        test_paths=(
            "tests/test_tangent_integration.py",
            "tests/test_tangent_examples.py",
        ),
        threshold=80,
    ),
    CoverageGate(
        package="src.tools.utils",
        test_paths=(
            "tests/test_analysis_utils.py",
            "tests/test_assessment_utils.py",
            "tests/test_budget_check_utils.py",
            "tests/test_file_utils.py",
            "tests/test_html_utils.py",
            "tests/test_issue_utils.py",
            "tests/test_latex_utils.py",
            "tests/test_link_utils.py",
            "tests/test_logging_utils.py",
            "tests/test_report_utils.py",
            "tests/test_shell_utils.py",
            "tests/tools/utils/test_cli_contracts.py",
            "tests/tools/utils/test_report_utils.py",
        ),
        threshold=40,
    ),
]


def _run_gate(gate: CoverageGate) -> bool:
    """Run a single coverage gate. Return True if it passes."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *gate.test_paths,
        f"--cov={gate.package}",
        "--cov-report=term-missing:skip-covered",
        f"--cov-fail-under={gate.threshold}",
        "-q",
        "--tb=short",
        "--no-header",
    ]
    logger.info(
        "Gate: %s >= %d%% (tests: %s)",
        gate.package,
        gate.threshold,
        ", ".join(gate.test_paths),
    )
    result = subprocess.run(cmd, check=False)
    passed = result.returncode == 0
    status = "PASS" if passed else "FAIL"
    logger.info("  -> %s", status)
    return passed


def main() -> int:
    """Run all coverage gates and return 0 on success, 1 on any failure."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    logger.info("Running %d coverage gates...", len(COVERAGE_GATES))
    results: list[tuple[str, bool]] = []

    for gate in COVERAGE_GATES:
        passed = _run_gate(gate)
        results.append((gate.package, passed))

    # Summary
    failures = [name for name, passed in results if not passed]
    print()
    print("=" * 60)
    print("Coverage Gate Summary")
    print("=" * 60)
    for name, passed in results:
        icon = "PASS" if passed else "FAIL"
        print(f"  [{icon}] {name}")
    print("=" * 60)

    if failures:
        logger.error(
            "%d / %d coverage gates failed: %s",
            len(failures),
            len(results),
            ", ".join(failures),
        )
        return 1

    logger.info("All %d coverage gates passed.", len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
