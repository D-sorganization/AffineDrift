from __future__ import annotations

import logging
from collections import defaultdict

from .file_utils import is_safe_path, read_file_lines, write_file_lines
from .models import AgentReport, MypyError
from .parser import parse_mypy_output, run_mypy
from .strategies import FIX_STRATEGIES

logger = logging.getLogger(__name__)


def _group_errors_by_file(
    errors: list[MypyError], report: AgentReport
) -> dict[str, list[MypyError]]:
    """Group mypy errors by file, filtering unsafe paths.

    Args:
        errors: Parsed mypy errors.
        report: Agent report to record skipped reasons.

    Returns:
        Dictionary mapping safe file paths to their errors.
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
    """Apply fix strategies to errors in a single file.

    Args:
        lines: File lines (modified in-place).
        file_errors: Errors in this file.
        report: Agent report to record fixes and skips.
        max_fixes: Global fix limit.
        total_fixes: Current global fix count.
        verbose: Whether to log individual fixes.

    Returns:
        Tuple of (file_changed, updated total_fixes).
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
    """Main agent loop: observe, classify, fix, report."""
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
