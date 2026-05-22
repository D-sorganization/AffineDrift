"""Build markdown output for repository assessment reports."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from src.tools.utils.assessment_utils import CATEGORIES, GROUP_MAPPING, GROUP_WEIGHTS
from src.tools.utils.report_utils import generate_issue_document

IssueDocumentGenerator = Callable[..., Path]


def build_comprehensive_report(
    scores: dict[str, dict[str, Any]],
    final_grade: float,
    *,
    issue_generator: IssueDocumentGenerator = generate_issue_document,
) -> str:
    """Build the comprehensive assessment markdown report."""
    lines = [
        "# Comprehensive Repository Assessment",
        "",
        f"## Overall Grade: {final_grade:.2f}/10",
        f"**Weighted Average:** {final_grade:.2f}/10 (Code 25%, Testing 15%, Docs 10%, Security 15%, Perf 15%, Ops 10%, Design 10%)",
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

    lines.extend(["", "## Top Recommendations", ""])
    for i, item in enumerate(recommendations_list, 1):
        lines.append(f"{i}. **{item['name']}** (Grade: {item['grade']:.1f}): {item['text']}")

    lines.extend(["", "## Issues Created", ""])
    issues_dir = Path("docs/assessments/issues")
    issues_dir.mkdir(parents=True, exist_ok=True)

    for cat_code, info in scores.items():
        if info["grade"] < 5:
            issue_path = issue_generator(
                category_id=cat_code,
                category_name=CATEGORIES[cat_code],
                grade=info["grade"],
                details=info["details"],
            )
            lines.append(f"- Created issue: `{issue_path.name}` (Grade: {info['grade']:.1f})")

    existing_file = Path("docs/assessments/Comprehensive_Assessment.md")
    if existing_file.exists():
        content = existing_file.read_text(encoding="utf-8")
        if "## Additional Audits" in content:
            extra_content = content.split("## Additional Audits", 1)[1]
            lines.extend(["", "## Additional Audits", extra_content.strip()])

    return "\n".join(lines) + "\n"
