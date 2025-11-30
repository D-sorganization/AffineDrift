#!/usr/bin/env python3
"""
MATLAB Quality Check Script

This script runs comprehensive quality checks on MATLAB code following the project's
.cursorrules.md requirements. It can be run from the command line and integrates
with the project's quality control system.

Usage:
    python scripts/matlab_quality_check.py [--strict] [--output-format json|text]
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Constants
MATLAB_SCRIPT_TIMEOUT_SECONDS: int = 300  # 5 minutes - allows time for large codebases

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MATLABQualityChecker:
    """Comprehensive MATLAB code quality checker with enhanced error handling and type safety."""

    def __init__(self, project_root: Path):
        """Initialize the MATLAB quality checker.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.matlab_dir = project_root / "matlab"
        self.results = {
            "timestamp": None,
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
        m_files = list(self.matlab_dir.glob("**/*.m"))
        logger.info(f"Found {len(m_files)} MATLAB files")
        return len(m_files) > 0

    def run_matlab_quality_checks(self) -> dict[str, Any]:
        """Run MATLAB quality checks using MATLAB script execution.

        Returns:
            Dictionary containing check results
        """
        logger.info("Running MATLAB quality checks...")

        # Find MATLAB quality check script
        script_path = self.matlab_dir / "run_matlab_quality_checks.m"
        if not script_path.exists():
            logger.warning(f"MATLAB script not found: {script_path}")
            return {"error": "MATLAB quality check script not found"}

        return self._run_matlab_script(script_path)

    def _run_matlab_script(self, script_path: Path) -> dict[str, Any]:
        """Execute MATLAB quality check script.

        Args:
            script_path: Path to the MATLAB script to execute

        Returns:
            Dictionary with execution results
        """
        commands = [
            ["matlab", "-batch", f"run('{script_path}')"],
            ["octave", "--no-gui", "--eval", f"run('{script_path}')"],
        ]

        for cmd in commands:
            try:
                logger.info(f"Trying command: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.matlab_dir,
                    timeout=MATLAB_SCRIPT_TIMEOUT_SECONDS,
                    check=True,
                )
                logger.info("MATLAB quality checks completed successfully")
                return {
                    "success": True,
                    "output": result.stdout,
                    "method": "matlab_script",
                }
            except subprocess.CalledProcessError as e:
                logger.warning(
                    f"Command failed with return code {e.returncode}",
                )
                logger.debug(f"stderr: {e.stderr}")
                continue
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        # If all commands fail, fall back to static analysis
        logger.info("MATLAB execution failed, falling back to static analysis")
        return self._static_matlab_analysis()

    def _static_matlab_analysis(self) -> dict[str, Any]:
        """Perform static analysis of MATLAB files without MATLAB runtime.

        Returns:
            Dictionary containing analysis results
        """
        logger.info("Performing static MATLAB analysis...")

        issues = []
        m_files = list(self.matlab_dir.glob("**/*.m"))

        for file_path in m_files:
            try:
                file_issues = self._analyze_matlab_file(file_path)
                issues.extend(file_issues)
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")

        # Update results
        self.results["timestamp"] = datetime.now().isoformat()
        self.results["total_files"] = len(m_files)
        self.results["issues"] = issues
        self.results["passed"] = len(issues) == 0
        self.results["summary"] = f"Found {len(issues)} issues in {len(m_files)} files"

        return {
            "success": True,
            "method": "static_analysis",
            "results": self.results,
        }

    def _analyze_matlab_file(self, file_path: Path) -> list[str]:
        """Analyze a single MATLAB file for quality issues.

        Args:
            file_path: Path to the MATLAB file to analyze

        Returns:
            List of issue descriptions
        """
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception as e:
            return [f"Error reading file: {e}"]

        in_function = False
        nesting_level = 0

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Skip empty lines and pure comments
            if not line_stripped or line_stripped.startswith("%"):
                continue

            # Track function definitions and nesting
            if re.search(r"^\s*function\s", line_stripped):
                in_function = True
                nesting_level = 0
                continue
            elif re.search(r"^\s*end\s*$", line_stripped):
                nesting_level -= 1
                if nesting_level <= 0:
                    in_function = False
                    nesting_level = 0
                continue
            elif re.search(r"^\s*(if|for|while|switch|try)\b", line_stripped):
                nesting_level += 1

            # Check for arguments validation block (only in functions)
            if in_function and i <= 15:  # Check only in first 15 lines of function
                if re.search(r"\barguments\b", line_stripped) and not re.search(
                    r"^\s*function\s", line_stripped
                ):
                    # Found arguments block, function is properly structured
                    break
            elif in_function and i > 15:
                # No arguments block found
                issues.append(
                    f"{file_path.name} (line {i}): Missing arguments validation block"
                )
                break

            # Check for banned patterns (in comments and code)
            if in_function:
                # Check for clear/clc/close all in functions (bad practice)
                if re.search(r"\bclear\s+(all|global)\b", line_stripped, re.IGNORECASE):
                    issues.append(
                        f"{file_path.name} (line {i}): Avoid 'clear all' or 'clear global' in functions - clears all variables, functions, and MEX links",
                    )
                elif re.search(r"\bclear\s*$", line_stripped):
                    issues.append(
                        f"{file_path.name} (line {i}): Avoid 'clear' in functions - can clear function variables",
                    )
                if re.search(r"\bclc\b", line_stripped):
                    issues.append(
                        f"{file_path.name} (line {i}): Avoid 'clc' in functions - affects user's workspace",
                    )

            # Check for load without output (loads into workspace)
            if (
                re.search(r"^\s*load\b", line_stripped)
                or re.search(r"^\s*load\s*\(", line_stripped)
            ) and not re.search(r"\w+\s*=\s*load", line_stripped):
                issues.append(
                    f"{file_path.name} (line {i}): load without output variable - use 'data = load(...)' instead",
                )

        return issues

    def run_all_checks(self) -> dict[str, Any]:
        """Run all available quality checks.

        Returns:
            Comprehensive results dictionary
        """
        logger.info("Running comprehensive MATLAB quality checks...")

        results = {
            "matlab_available": False,
            "static_analysis": {},
            "final_result": "unknown",
        }

        # Try MATLAB-based checks first
        matlab_result = self.run_matlab_quality_checks()
        if "success" in matlab_result and matlab_result["success"]:
            results["matlab_available"] = True
            results["matlab_result"] = matlab_result
            results["final_result"] = (
                "passed" if matlab_result.get("passed", True) else "failed"
            )
        else:
            # Fall back to static analysis
            static_result = self._static_matlab_analysis()
            results["static_analysis"] = static_result
            results["final_result"] = (
                "passed" if len(static_result.get("issues", [])) == 0 else "failed"
            )

        return results


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="MATLAB Code Quality Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python matlab_quality_check.py                    # Basic check
  python matlab_quality_check.py --strict         # Strict mode
  python matlab_quality_check.py --output-format json  # JSON output
        """,
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Path to project root directory (default: current directory)",
    )

    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict checking mode",
    )

    args = parser.parse_args()

    # Validate project root
    if not args.project_root.exists():
        logger.error(f"Project root does not exist: {args.project_root}")
        sys.exit(1)

    if not args.project_root.is_dir():
        logger.error(f"Project root is not a directory: {args.project_root}")
        sys.exit(1)

    # Run checks
    checker = MATLABQualityChecker(args.project_root)
    results = checker.run_all_checks()

    # Output results
    if args.output_format == "json":
        print(json.dumps(results, indent=2))
    else:
        # Text output
        print("MATLAB Quality Check Results")
        print(f"Final Result: {results['final_result']}")

        if results.get("matlab_available"):
            print("✓ MATLAB execution successful")
        else:
            print("ℹ️  Using static analysis (MATLAB not available)")

        if "static_analysis" in results and "results" in results["static_analysis"]:
            static = results["static_analysis"]["results"]
            print(f"Files analyzed: {static['total_files']}")
            print(f"Issues found: {len(static['issues'])}")

            if static["issues"]:
                print("\nIssues:")
                for issue in static["issues"][:10]:  # Show first 10 issues
                    print(f"  {issue}")
                if len(static["issues"]) > 10:
                    print(f"  ... and {len(static['issues']) - 10} more issues")

    # Exit with appropriate code
    if results["final_result"] == "passed":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
