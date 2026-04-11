from __future__ import annotations

import argparse
import logging
import sys

from .agent import run_agent
from .models import AgentReport

logger = logging.getLogger(__name__)


def log_report(report: AgentReport) -> None:
    """Log a human-readable report."""
    logger.info("=" * 60)
    logger.info("  MYPY AUTOFIX AGENT REPORT")
    logger.info("=" * 60)
    logger.info("  Total mypy errors found:  %d", report.total_errors)
    logger.info("  Errors fixed:             %d", report.errors_fixed)
    logger.info("    Real fixes:             %d", report.real_fixes)
    logger.info("    Suppressions:           %d", report.suppressions)
    logger.info("  Files modified:           %d", len(report.files_modified))

    if report.fixes_applied:
        logger.info("  Fixes applied:")
        for fix_desc in report.fixes_applied:
            logger.info("  %s", fix_desc)

    if report.skipped_reasons:
        logger.info("  Skipped (%d):", len(report.skipped_reasons))
        # Only show first 10 skipped reasons
        for reason in report.skipped_reasons[:10]:
            logger.info("    - %s", reason)
        if len(report.skipped_reasons) > 10:
            logger.info("    ... and %d more", len(report.skipped_reasons) - 10)

    logger.info("=" * 60)


def main() -> int:
    """Entry point."""
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

    # Exit code: 0 if any fixes were applied, 1 if no fixes possible
    if report.errors_fixed > 0:
        return 0
    if report.total_errors > 0:
        return 1  # Errors found but none fixable
    return 0


if __name__ == "__main__":
    sys.exit(main())
