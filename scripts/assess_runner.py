"""Orchestration and reporting helpers for the Repository Assessment script.

Provides:
  - _run_all_assessments  : run all 15 category assessments
  - _calculate_final_grade: compute weighted overall score
  - _build_comprehensive_report: assemble the Markdown summary document
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
from src.tools.utils.assessment_utils import CATEGORIES, GROUP_MAPPING, GROUP_WEIGHTS
from src.tools.utils.report_utils import generate_issue_document


def _run_all_assessments(root: Path, py_files: list[Path]) -> dict[str, dict[str, Any]]:
    """Run all A-O category assessments and return their results.

    Args:
        root: Repository root path.
        py_files: Python source files to include in file-level analysis.

    Returns:
        Mapping from category code (A–O) to the assessment result dict.
    """
    return {
        "A": assess_code_structure(py_files),
        "B": assess_documentation(py_files),
        "C": assess_test_coverage(root),
        "D": assess_error_handling(py_files),
        "E": assess_performance(py_files),
        "F": assess_security(root),
        "G": assess_dependencies(root),
        "H": assess_cicd(root),
        "I": assess_code_style(root),
        "J": assess_api_design(py_files),
        "K": assess_data_handling(py_files),
        "L": assess_logging(py_files),
        "M": assess_configuration(root),
        "N": assess_scalability(py_files),
        "O": assess_maintainability(py_files),
    }


def _calculate_final_grade(scores: dict[str, dict[str, Any]]) -> float:
    """Compute the weighted overall grade from all category scores.

    Each category belongs to a group defined in GROUP_MAPPING, and each group
    carries a weight defined in GROUP_WEIGHTS.

    Args:
        scores: Mapping from category code to assessment result dict.

    Returns:
        Weighted average grade in the range 0–10.
    """
    group_scores: dict[str, list[float]] = {g: [] for g in GROUP_WEIGHTS}
    for cat_code, info in scores.items():
        group = GROUP_MAPPING.get(cat_code, "Code")
        group_scores[group].append(info["grade"])

    weighted_sum = 0.0
    total_weight = 0.0
    for group, weight in GROUP_WEIGHTS.items():
        if group_scores[group]:
            avg_score = sum(group_scores[group]) / len(group_scores[group])
            weighted_sum += avg_score * weight
            total_weight += weight

    return weighted_sum / total_weight if total_weight > 0 else 0.0


def _build_comprehensive_report(scores: dict[str, dict[str, Any]], final_grade: float) -> str:
    """Assemble the comprehensive Markdown assessment report.

    Creates issue documents for any category scoring below 5, then returns
    the complete Markdown string ready to be written to disk.

    Args:
        scores: Mapping from category code to assessment result dict.
        final_grade: Weighted average grade (from _calculate_final_grade).

    Returns:
        Markdown report string (ends with a newline).
    """
    lines = [
        "# Comprehensive Repository Assessment",
        "",
        f"## Overall Grade: {final_grade:.2f}/10",
        (
            f"**Weighted Average:** {final_grade:.2f}/10 "
            "(Code 25%, Testing 15%, Docs 10%, Security 15%, Perf 15%, Ops 10%, Design 10%)"
        ),
        "",
        "## Category Breakdown",
        "",
        "| Category | Grade | Weight |",
        "|----------|-------|--------|",
    ]
    for cat_code, info in scores.items():
        weight = f"{GROUP_WEIGHTS.get(GROUP_MAPPING.get(cat_code, 'Code'), 0) * 100:.0f}%"
        lines.append(f"| {CATEGORIES[cat_code]} | {info['grade']:.1f} | {weight} |")

    recommendations_list = sorted(
        [
            {
                "name": CATEGORIES[cat_code],
                "grade": info["grade"],
                "text": info["recommendation"],
            }
            for cat_code, info in scores.items()
        ],
        key=lambda x: x["grade"],
    )[:5]

    lines += ["", "## Top Recommendations", ""]
    for i, item in enumerate(recommendations_list, 1):
        lines.append(f"{i}. **{item['name']}** (Grade: {item['grade']:.1f}): {item['text']}")

    lines += ["", "## Issues Created", ""]
    issues_dir = Path("docs/assessments/issues")
    issues_dir.mkdir(parents=True, exist_ok=True)

    for cat_code, info in scores.items():
        if info["grade"] < 5:
            issue_path = generate_issue_document(
                category_id=cat_code,
                category_name=CATEGORIES[cat_code],
                grade=info["grade"],
                details=info["details"],
            )
            lines.append(f"- Created issue: `{issue_path.name}` (Grade: {info['grade']:.1f})")

    return "\n".join(lines) + "\n"
