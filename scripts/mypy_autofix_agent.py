"""Mypy Autofix Agent - entry point.

Delegates all logic to focused helper modules:
  - mypy_models   : data models and constants
  - mypy_io       : subprocess I/O, file reading/writing, path safety
  - mypy_fixers   : individual fix strategies
  - mypy_runner   : agent loop and report formatting

Usage:
    python scripts/mypy_autofix_agent.py [--max-fixes N] [--max-files N] [--dry-run] [--verbose]
"""

from __future__ import annotations

import argparse
import logging
import sys

from scripts.mypy_runner import log_report, run_agent

logger = logging.getLogger(__name__)


def main() -> int:
    """Parse CLI arguments and run the agent."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(
        description="Mypy Autofix Agent - Intelligently fix mypy errors"
    )
    parser.add_argument(
        "--max-fixes",
        type=int,
        default=20,
        help="Maximum number of fixes per run (default: 20)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=15,
        help="Maximum files to modify per run (default: 15)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without modifying files",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default=None,
        help="Path to mypy config file (default: uses pyproject.toml)",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="Files or directories to check (default: src)",
    )
    args = parser.parse_args()

    report = run_agent(
        max_fixes=args.max_fixes,
        max_files=args.max_files,
        dry_run=args.dry_run,
        verbose=args.verbose,
        config_file=args.config_file,
        targets=args.targets,
    )

    log_report(report)

    if report.errors_fixed > 0:
        return 0
    if report.total_errors > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
