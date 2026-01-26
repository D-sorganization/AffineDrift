#!/usr/bin/env python3
"""
Run a specific assessment (A-O) on the repository.

This script executes an individual assessment and generates a detailed report
based on actual code analysis.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.tools.utils import (
    get_python_files,
    setup_logging,
)
from src.tools.utils.assessment_utils import ASSESSMENT_DEFINITIONS as ASSESSMENTS
from src.tools.utils.shell_utils import run_black_check, run_ruff_check

logger = setup_logging(__name__)


def count_test_files() -> int:
    """Count test files in the repository."""
    test_patterns = ["**/test_*.py", "**/*_test.py", "**/tests/*.py"]
    test_files = set()
    for pattern in test_patterns:
        test_files.update(Path(".").glob(pattern))
    return len(test_files)


def check_documentation() -> dict:
    """Check documentation status."""
    has_readme = Path("README.md").exists()
    has_docs = Path("docs").exists()
    has_changelog = Path("CHANGELOG.md").exists()
    return {
        "has_readme": has_readme,
        "has_docs_dir": has_docs,
        "has_changelog": has_changelog,
    }


def run_assessment(assessment_id: str, output_path: Path) -> int:
    """
    Run a specific assessment and generate report.

    Args:
        assessment_id: Assessment ID (A-O)
        output_path: Path to save the assessment report

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    assessment = ASSESSMENTS.get(assessment_id)
    if not assessment:
        logger.error(f"Unknown assessment: {assessment_id}")
        return 1

    logger.info(f"Running Assessment {assessment_id}: {assessment['name']}...")

    # Gather metrics based on assessment type
    findings = []
    score = 10  # Start with perfect score

    python_files = get_python_files()
    file_count = len(python_files)

    if assessment_id == "A":  # Architecture
        # Check directory structure
        has_src = Path("src").exists() or Path("python").exists()
        has_tests = Path("tests").exists()
        findings.append(f"- Python files found: {file_count}")
        findings.append(f"- Source directory structure: {'✓' if has_src else '✗'}")
        findings.append(f"- Tests directory: {'✓' if has_tests else '✗'}")
        if not has_src:
            score -= 2
        if not has_tests:
            score -= 1

    elif assessment_id == "B":  # Hygiene & Quality
        ruff_result = run_ruff_check()
        black_result = run_black_check()
        findings.append(
            f"- Ruff check: {'✓ passed' if ruff_result['exit_code'] == 0 else '✗ issues found'}"
        )
        findings.append(
            f"- Black formatting: {'✓ formatted' if black_result['exit_code'] == 0 else '✗ needs formatting'}"
        )
        if ruff_result["exit_code"] != 0:
            score -= 2
        if black_result["exit_code"] != 0:
            score -= 1

    elif assessment_id == "C":  # Documentation
        docs = check_documentation()
        findings.append(f"- README.md: {'✓' if docs['has_readme'] else '✗'}")
        findings.append(f"- docs/ directory: {'✓' if docs['has_docs_dir'] else '✗'}")
        findings.append(f"- CHANGELOG.md: {'✓' if docs['has_changelog'] else '✗'}")
        if not docs["has_readme"]:
            score -= 3
        if not docs["has_docs_dir"]:
            score -= 1

    elif assessment_id == "G":  # Testing
        test_count = count_test_files()
        findings.append(f"- Test files found: {test_count}")
        findings.append("- Test coverage: Run pytest --cov for details")
        if test_count == 0:
            score -= 5
        elif test_count < 5:
            score -= 2

    else:
        # No automated checks available for this category
        # DO NOT fabricate a score - require real bot/manual review
        score = None  # Explicitly unscored - requires real review
        findings.append(f"- Python files analyzed: {file_count}")
        findings.append("- **REQUIRES REVIEW**: No automated checks available for this category")
        findings.append("- Score must be assigned by Jules bot or manual code review")
        findings.append("- Do NOT use a default score - real analysis is required")

    # Format score display
    if score is not None:
        score = max(0, min(10, score))
        score_display = f"{score}/10"
    else:
        score_display = "PENDING REVIEW"

    # Generate report
    report_content = f"""# Assessment {assessment_id}: {assessment["name"]}

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Assessment**: {assessment_id} - {assessment["name"]}
**Description**: {assessment["description"]}
**Generated**: Automated via Jules Assessment Auto-Fix workflow

## Score: {score_display}

## Findings

{chr(10).join(findings)}

## Recommendations

- Review findings above
- Address any ✗ items
- Re-run assessment after fixes

## Automation Notes

This assessment was generated automatically. For detailed analysis:
1. Run specific tools (ruff, black, pytest, etc.)
2. Review code manually for context-specific issues
3. Create GitHub issues for actionable items
"""

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write report
    with open(output_path, "w") as f:
        f.write(report_content)

    logger.info(f"✓ Assessment {assessment_id} report saved to {output_path}")
    logger.info(f"  Score: {score_display}")
    return 0


def main():
    """Parse command-line arguments and run the specified assessment."""
    parser = argparse.ArgumentParser(description="Run repository assessment")
    parser.add_argument(
        "--assessment",
        required=True,
        choices=list("ABCDEFGHIJKLMNO"),
        help="Assessment ID (A-O)",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output file path for assessment report",
    )

    args = parser.parse_args()

    exit_code = run_assessment(args.assessment, args.output)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
