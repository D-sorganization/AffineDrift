#!/usr/bin/env python3
"""Detect stale assessment references and deprecated date-stamped report paths.

Part of the docs-governance policy: ensures all assessment references point to
valid files and no deprecated naming patterns are used.
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Pattern for deprecated date-stamped assessment files at docs/assessments/ root
DEPRECATED_PATTERN = re.compile(
    r"docs/assessments/(?:comprehensive_assessment|implementation_plan|summary)"
    r"_\d{4}-\d{2}-\d{2}\.md"
)

# Pattern for assessment references in markdown/Python files
ASSESSMENT_REF_PATTERN = re.compile(r"docs/assessments/[^\s\)\"']+\.md")


def main() -> int:
    """Check for stale and deprecated assessment references."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    repo_root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    warnings: list[str] = []
    files_checked = 0

    # Scan all markdown and Python files for assessment references
    scan_dirs = [
        repo_root / "src",
        repo_root / "scripts",
        repo_root / "docs" / "development",
        repo_root / "docs" / "assessments",
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for ext in ("*.md", "*.py", "*.qmd"):
            for filepath in scan_dir.rglob(ext):
                files_checked += 1
                try:
                    content = filepath.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue

                for match in ASSESSMENT_REF_PATTERN.finditer(content):
                    ref_path = match.group(0)

                    # Check for deprecated date-stamped pattern
                    if DEPRECATED_PATTERN.match(ref_path):
                        warnings.append(
                            f"{filepath.relative_to(repo_root)}: "
                            f"deprecated date-stamped ref '{ref_path}'"
                        )

                    # Check if referenced file exists
                    full_path = repo_root / ref_path
                    if not full_path.exists():
                        errors.append(
                            f"{filepath.relative_to(repo_root)}: "
                            f"stale reference to non-existent '{ref_path}'"
                        )

    # Report results
    logger.info("=== Stale assessment reference check ===")
    logger.info("Files checked: %d", files_checked)

    if warnings:
        logger.info("Warnings (deprecated patterns): %d", len(warnings))
        for w in warnings:
            logger.info("  WARN: %s", w)

    if errors:
        logger.info("Errors (broken references): %d", len(errors))
        for e in errors:
            logger.info("  ERROR: %s", e)
        logger.info("FAIL: %d stale assessment references found", len(errors))
        return 1

    logger.info("PASS: No stale assessment references found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
