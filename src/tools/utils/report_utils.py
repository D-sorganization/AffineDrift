"""Utilities for generating assessment reports and issues.

This module provides common functions for writing Markdown reports
and GitHub-style issue documents from assessment findings.
"""

from __future__ import annotations

from pathlib import Path

from src.core.contracts import check_range, require


def generate_markdown_report(
    category_id: str,
    category_name: str,
    grade: float,
    details: str,
    recommendations: list[str] | None = None,
    output_dir: str | Path = "docs/assessments",
) -> Path:
    """Generate a markdown report for a specific assessment category.

    Args:
        category_id: Assessment ID (e.g., 'A').
        category_name: Human-readable name (e.g., 'Architecture').
        grade: Score from 0 to 10.
        details: Detailed findings string.
        recommendations: Optional list of recommendations.
        output_dir: Directory to save the report.

    Returns:
        Path to the generated report file.
    """
    require(len(category_id) > 0, "category_id must not be empty")
    require(len(category_name) > 0, "category_name must not be empty")
    check_range(grade, 0, 10, "grade")
    if recommendations is None:
        recommendations = ["See detailed findings"]

    safe_name = category_name.replace(" ", "_").replace("/", "_")
    filename = f"Assessment_{category_id}_{safe_name}.md"
    output_path = Path(output_dir) / filename

    content = [
        f"# Assessment: {category_name}",
        "",
        f"## Grade: {grade:.1f}/10",
        "",
        "## Details",
        details,
        "",
        "## Recommendations",
    ]

    for rec in recommendations:
        content.append(f"- {rec}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return output_path


def generate_issue_document(
    category_id: str,
    category_name: str,
    grade: float,
    details: str,
    output_dir: str | Path = "docs/assessments/issues",
) -> Path:
    """Generate a GitHub issue document for a low-scoring assessment.

    Args:
        category_id: Assessment ID.
        category_name: Human-readable name.
        grade: Score from 0 to 10.
        details: Detailed findings.
        output_dir: Directory to save the issue.

    Returns:
        Path to the generated issue file.
    """
    require(len(category_id) > 0, "category_id must not be empty")
    require(len(category_name) > 0, "category_name must not be empty")
    check_range(grade, 0, 10, "grade")
    safe_name = category_name.replace(" ", "_").replace("/", "_")
    filename = f"ISSUE_Assessment_{category_id}_{safe_name}.md"
    output_path = Path(output_dir) / filename

    report_filename = f"Assessment_{category_id}_{safe_name}.md"

    content = f"""---
title: "Assessment Finding: Low Score in {category_name}"
labels: jules:assessment, needs-attention
---

# Issue: Low Score in {category_name}

**Grade**: {grade:.1f}/10
**Details**: {details}

## Recommended Actions
- Review the detailed assessment in `docs/assessments/{report_filename}`
- Create a remediation plan.
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
