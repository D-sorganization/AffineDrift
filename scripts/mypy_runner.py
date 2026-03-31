"""Agent loop and reporting for the Mypy Autofix Agent.

Orchestrates the observe-classify-fix-report cycle and produces human-readable
summaries of all changes made (or skipped) during a run.
"""

from __future__ import annotations

import logging
from collections import defaultdict

from scripts.mypy_fixers import FIX_STRATEGIES
from scripts.mypy_io import (
    is_safe_path,
    parse_mypy_output,
    read_file_lines,
    run_mypy,
    write_file_lines,
)
from scripts.mypy_models import AgentReport, MypyError

logger = logging.getLogger(__name__)


def _group_errors_by_file(
    errors: list[MypyError],
    report: AgentReport,
) -> dict[str, list[MypyError]]:
    """Group mypy errors by file path, skipping files outside safe directories.

    Args:
        errors: All parsed mypy errors.
        report: Running report; skipped paths are recorded here.

    Returns:
        Mapping from safe file paths to their corresponding errors.
    """
    errors_by_file: dict[str, list[MypyError]] = defaultdict(list)
    for error in errors:
        if is_safe_path(error.file):
            errors_by_file[error.file].append(error)
        else:
            report.skipped_reasons.append(f"Skipped {error.file}:{error.line} - outside safe path")
    return errors_by_file


def _apply_fixes_to_file(
    lines: list[str],
    file_errors: list[MypyError],
    report: AgentReport,
    max_fixes: int,
    total_fixes: int,
    verbose: bool,
) -> tuple[bool, int]:
    """Try to fix all errors in a single file.

    Iterates errors in reverse line order (so insertions don't shift later
    line numbers) and applies the first matching strategy from FIX_STRATEGIES.

    Args:
        lines: Source lines of the file (mutated in-place).
        file_errors: Errors belonging to this file.
        report: Running report; fixes and skips are recorded here.
        max_fixes: Global upper bound on fixes for this run.
        total_fixes: Number of fixes already applied in this run.
        verbose: When True each fix is logged at INFO level.

    Returns:
        ``(file_changed, updated_total_fixes)``.
    """
    file_changed = False
    for error in sorted(file_errors, key=lambda e: e.line, reverse=True):
        if total_fixes >= max_fixes:
            break

        fix = None
        for strategy in FIX_STRATEGIES:
            fix = strategy(lines, error)
            if fix:
                break

        if fix:
            total_fixes += 1
            file_changed = True
            if fix.strategy == "real-fix":
                report.real_fixes += 1
            else:
                report.suppressions += 1
            report.fixes_applied.append(
                f"  [{fix.strategy}] {fix.file}:{fix.line} - {fix.description}"
            )
            if verbose:
                logger.info(
                    "  FIX: %s:%d [%s] %s",
                    fix.file,
                    fix.line,
                    fix.strategy,
                    fix.description,
                )
        else:
            report.skipped_reasons.append(
                f"No fix available: {error.file}:{error.line} [{error.code}] {error.message[:60]}"
            )

    return file_changed, total_fixes


def run_agent(
    max_fixes: int = 20,
    max_files: int = 15,
    dry_run: bool = False,
    verbose: bool = False,
    config_file: str | None = None,
    targets: list[str] | None = None,
) -> AgentReport:
    """Execute the main agent loop: observe, classify, fix, report.

    Args:
        max_fixes: Maximum number of individual fixes to apply in one run.
        max_files: Maximum number of files to modify in one run.
        dry_run: When True, compute fixes but do not write any files.
        verbose: When True, log each fix as it is applied.
        config_file: Optional path to a mypy configuration file.
        targets: Files/directories to check.  Defaults to src/ + tests/.

    Returns:
        An AgentReport summarising everything that happened.
    """
    report = AgentReport()

    if verbose:
        logger.info("Running mypy on targets: %s...", targets or "default")
    output = run_mypy(config_file, targets)
    errors = parse_mypy_output(output)
    report.total_errors = len(errors)

    if verbose:
        logger.info("Found %d mypy errors", len(errors))
    if not errors:
        logger.info("No mypy errors found.")
        return report

    errors_by_file = _group_errors_by_file(errors, report)

    files_modified = 0
    total_fixes = 0

    for filepath, file_errors in sorted(errors_by_file.items()):
        if files_modified >= max_files:
            report.skipped_reasons.append(f"Skipped {filepath} - max files ({max_files}) reached")
            continue
        if total_fixes >= max_fixes:
            report.skipped_reasons.append(f"Skipped {filepath} - max fixes ({max_fixes}) reached")
            continue

        lines = read_file_lines(filepath)
        if not lines:
            continue

        file_changed, total_fixes = _apply_fixes_to_file(
            lines, file_errors, report, max_fixes, total_fixes, verbose
        )

        if file_changed:
            if not dry_run:
                write_file_lines(filepath, lines)
            files_modified += 1
            report.files_modified.append(filepath)

    report.errors_fixed = total_fixes
    return report


def log_report(report: AgentReport) -> None:
    """Write a human-readable summary of *report* to the logger.

    Args:
        report: The AgentReport to summarise.
    """
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
        for reason in report.skipped_reasons[:10]:
            logger.info("    - %s", reason)
        if len(report.skipped_reasons) > 10:
            logger.info("    ... and %d more", len(report.skipped_reasons) - 10)

    logger.info("=" * 60)
