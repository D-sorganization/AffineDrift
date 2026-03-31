#!/usr/bin/env python3
"""Repository Assessment Script - entry point.

Delegates all logic to focused helper modules:
  - assess_categories : the 15 individual A-O assessment functions
  - assess_runner     : orchestration and comprehensive-report generation

Generates assessments for 15 categories (A-O) and a comprehensive report.
"""

from pathlib import Path

from scripts.assess_categories import (
    assess_api_design,
    assess_cicd,
    assess_code_structure,
    assess_code_style,
    assess_configuration,
    assess_data_handling,
    assess_dependencies,
    assess_documentation,
    assess_error_handling,
    assess_logging,
    assess_maintainability,
    assess_performance,
    assess_scalability,
    assess_security,
    assess_test_coverage,
)
from scripts.assess_runner import (
    _build_comprehensive_report,
    _calculate_final_grade,
    _run_all_assessments,
)
from src.tools.utils import get_python_files, setup_logging
from src.tools.utils.assessment_utils import CATEGORIES
from src.tools.utils.report_utils import generate_markdown_report

logger = setup_logging(__name__, format_string="%(message)s")

# Re-export assessment functions so that existing test imports from
# ``scripts.assess_repo`` continue to work without modification.
__all__ = [
    "assess_api_design",
    "assess_cicd",
    "assess_code_structure",
    "assess_code_style",
    "assess_configuration",
    "assess_data_handling",
    "assess_dependencies",
    "assess_documentation",
    "assess_error_handling",
    "assess_logging",
    "assess_maintainability",
    "assess_performance",
    "assess_scalability",
    "assess_security",
    "assess_test_coverage",
    "get_python_files",
]


def main() -> None:
    """Execute the full repository assessment and generate reports."""
    root = Path.cwd()
    py_files = get_python_files(root)

    scores = _run_all_assessments(root, py_files)

    for cat_code, info in scores.items():
        generate_markdown_report(
            category_id=cat_code,
            category_name=CATEGORIES[cat_code],
            grade=info["grade"],
            details=info["details"],
            recommendations=[info["recommendation"]],
        )

    final_grade = _calculate_final_grade(scores)
    comp_content = _build_comprehensive_report(scores, final_grade)

    Path("docs/assessments/Comprehensive_Assessment.md").write_text(comp_content, encoding="utf-8")
    logger.info("Assessment complete.")


if __name__ == "__main__":
    main()
