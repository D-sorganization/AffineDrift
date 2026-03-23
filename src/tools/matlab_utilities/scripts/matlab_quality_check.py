#!/usr/bin/env python3
"""
MATLAB Quality Check Script (Unified Version)

This script runs comprehensive quality checks on MATLAB code following the project's
.cursorrules.md requirements. It can be run from the command line and integrates
with the project's quality control system.

This is the unified version combining the best features from all repository implementations.

Usage:
    python tools/matlab_utilities/scripts/matlab_quality_check.py \
        [--strict] [--output-format json|text] [--project-root PATH]
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from src.tools.matlab_utilities.scripts.line_checks import (
    analyze_matlab_file,
    append_anti_pattern_issues,
    append_banned_pattern_issues,
    append_function_contract_issues,
    append_function_scope_issues,
    append_magic_number_issues,
    update_function_scope,
)

# Constants
MATLAB_SCRIPT_TIMEOUT_SECONDS: int = 300  # 5 minutes - allows time for large codebases

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MATLABQualityChecker:
    """Comprehensive MATLAB code quality checker.

    Line-level checks are delegated to the ``line_checks`` sub-module.
    Thin wrappers are retained on the class so that any code calling
    ``checker._update_function_scope(...)`` etc. continues to work.
    """

    # Re-export line-check helpers as static/class attrs for backward compat
    _update_function_scope = staticmethod(update_function_scope)
    _append_function_contract_issues = staticmethod(append_function_contract_issues)
    _append_banned_pattern_issues = staticmethod(append_banned_pattern_issues)
    _append_anti_pattern_issues = staticmethod(append_anti_pattern_issues)
    _append_magic_number_issues = staticmethod(append_magic_number_issues)
    _append_function_scope_issues = staticmethod(append_function_scope_issues)

    def __init__(self, project_root: Path):
        """Initialize the MATLAB quality checker.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.matlab_dir = project_root / "matlab"
        self.results: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "issues": [],
            "passed": True,
            "summary": "",
            "checks": {},
        }

    def check_matlab_files_exist(self) -> bool:
        """Check if MATLAB files exist in the project.

        Returns:
            True if MATLAB files are found, False otherwise
        """
        if not self.matlab_dir.exists():
            logger.info(
                f"MATLAB directory not found: {self.matlab_dir} (skipping MATLAB checks)",
            )
            return False

        m_files = list(self.matlab_dir.rglob("*.m"))
        self.results["total_files"] = len(m_files)

        if len(m_files) == 0:
            logger.info("No MATLAB files found (skipping MATLAB checks)")
            return False

        logger.info(f"Found {len(m_files)} MATLAB files")
        return True

    def run_matlab_quality_checks(self) -> dict[str, object]:
        """Run MATLAB quality checks using the MATLAB script.

        Returns:
            Dictionary containing quality check results
        """
        try:
            # Check if we can run MATLAB from command line
            matlab_script = self.matlab_dir / "matlab_quality_config.m"
            if not matlab_script.exists():
                # Config script not found - fall back to static analysis (primary use case)
                logger.info(
                    "MATLAB quality config script not found, using static analysis",
                )
                return self._static_matlab_analysis()

            # Try to run MATLAB quality checks
            # Note: This requires MATLAB to be installed and accessible from command line
            try:
                # First, try to run the MATLAB script directly if possible
                result = self._run_matlab_script(matlab_script)
                return result
            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.warning(f"Could not run MATLAB script directly: {e}")
                # Fall back to static analysis
                return self._static_matlab_analysis()

        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Error running MATLAB quality checks: {e}")
            return {"error": str(e)}

    def _build_matlab_commands(self, script_path: Path) -> list[list[str]]:
        """Return ordered list of MATLAB/Octave commands to attempt."""
        return [
            ["matlab", "-batch", f"run('{script_path}')"],
            ["matlab", "-nosplash", "-nodesktop", "-batch", f"run('{script_path}')"],
            ["octave", "--no-gui", "--eval", f"run('{script_path}')"],
        ]

    def _try_matlab_command(self, cmd: list[str]) -> dict[str, object] | None:
        """Try a single MATLAB command. Returns result dict on success, None on failure."""
        try:
            logger.info(f"Trying command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.matlab_dir,
                timeout=MATLAB_SCRIPT_TIMEOUT_SECONDS,
                check=False,
            )
            if result.returncode == 0:
                logger.info("MATLAB quality checks completed successfully")
                return {"success": True, "output": result.stdout, "method": "matlab_script"}
            logger.warning(f"Command failed with return code {result.returncode}")
            logger.debug(f"stderr: {result.stderr}")
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def _run_matlab_script(self, script_path: Path) -> dict[str, object]:
        """Attempt to run MATLAB script from command line.

        Args:
            script_path: Path to the MATLAB script

        Returns:
            Dictionary containing script results
        """
        try:
            for cmd in self._build_matlab_commands(script_path):
                result = self._try_matlab_command(cmd)
                if result is not None:
                    return result
            logger.info("All MATLAB commands failed, falling back to static analysis")
            return self._static_matlab_analysis()
        except (FileNotFoundError, PermissionError, OSError, UnicodeDecodeError) as e:
            logger.error(f"Error running MATLAB script: {e}")
            return {"error": str(e)}

    def _static_matlab_analysis(self) -> dict[str, object]:
        """Perform static analysis of MATLAB files without running MATLAB.

        Returns:
            Dictionary containing static analysis results
        """
        logger.info("Performing static MATLAB file analysis")

        issues: list[str] = []
        total_files = 0

        # Analyze each MATLAB file
        for m_file in self.matlab_dir.rglob("*.m"):
            total_files += 1
            file_issues = self._analyze_matlab_file(m_file)
            issues.extend(file_issues)

        self.results["total_files"] = total_files
        self.results["issues"] = issues
        self.results["passed"] = len(issues) == 0

        return {
            "success": True,
            "method": "static_analysis",
            "total_files": total_files,
            "issues": issues,
            "passed": len(issues) == 0,
        }

    def _analyze_matlab_file(self, file_path: Path) -> list[str]:
        """Analyze a single MATLAB file for quality issues.

        Delegates to the ``line_checks`` sub-module.

        Args:
            file_path: Path to the MATLAB file

        Returns:
            List of quality issues found
        """
        return analyze_matlab_file(file_path)

    def run_all_checks(self) -> dict[str, object]:
        """Run all MATLAB quality checks.

        Returns:
            Dictionary containing all quality check results
        """
        logger.info("Starting MATLAB quality checks")

        # Check if MATLAB files exist
        if not self.check_matlab_files_exist():
            self.results["passed"] = True
            self.results["summary"] = "[SKIP] No MATLAB files to check - passed"
            return self.results

        # Run MATLAB quality checks
        matlab_results = self.run_matlab_quality_checks()

        if "error" in matlab_results:
            self.results["passed"] = False
            self.results["summary"] = f"MATLAB quality checks failed: {matlab_results['error']}"
            self.results["checks"]["matlab"] = matlab_results
        else:
            self.results["checks"]["matlab"] = matlab_results
            if matlab_results.get("passed", False):
                self.results["summary"] = (
                    f"[PASS] MATLAB quality checks PASSED "
                    f"({self.results['total_files']} files checked)"
                )
            else:
                self.results["passed"] = False
                self.results["summary"] = (
                    f"[FAIL] MATLAB quality checks FAILED "
                    f"({self.results['total_files']} files checked)"
                )

        return self.results


def _print_text_results(results: dict[str, object]) -> None:
    """Print MATLAB quality check results in human-readable text format.

    Logs a formatted summary including timestamp, file count, pass/fail status,
    summary message, and an enumerated list of any issues found.

    Args:
        results: Results dictionary as returned by ``MATLABQualityChecker.run_all_checks``.
    """
    logger.info("\n" + "=" * 60)
    logger.info("MATLAB QUALITY CHECK RESULTS")
    logger.info("=" * 60)
    logger.info(f"Timestamp: {results.get('timestamp', 'N/A')}")
    logger.info(f"Total Files: {results.get('total_files', 0)}")
    logger.info(f"Status: {'PASSED' if results.get('passed', False) else 'FAILED'}")
    logger.info(f"Summary: {results.get('summary', 'N/A')}")

    issues_raw = results.get("issues", [])
    issues: list[str] = issues_raw if isinstance(issues_raw, list) else []
    if issues:
        logger.info(f"\nIssues Found ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            logger.info(f"  {i}. {issue}")

    logger.info("\n" + "=" * 60)


def main() -> None:
    """Main entry point for the MATLAB quality check script."""
    parser = argparse.ArgumentParser(description="MATLAB Code Quality Checker")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode")
    parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        logger.error(f"Project root does not exist: {project_root}")
        sys.exit(1)

    checker = MATLABQualityChecker(project_root)
    results = checker.run_all_checks()

    if args.output_format == "json":
        logger.info(json.dumps(results, indent=2, default=str))
    else:
        _print_text_results(results)

    passed = results.get("passed", False)
    has_issues = bool(results.get("issues"))
    exit_code = (0 if (passed and not has_issues) else 1) if args.strict else (0 if passed else 1)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
