#!/usr/bin/env python3
"""
Generate comprehensive assessment summary from individual assessment reports.

This script aggregates all A-O assessment results and creates:
1. A comprehensive markdown summary
2. A JSON file with structured metrics
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from src.tools.utils import setup_logging
from src.tools.utils.assessment_utils import ASSESSMENT_DEFINITIONS
from src.tools.utils.cli_contracts import ensure_existing_file

logger = setup_logging(__name__)


def extract_score_from_report(report_path: Path) -> float:
    """Extract numerical score from assessment report.

    Searches for score patterns like "Overall: 8.5" or "Score: 8.5/10" in the report.

    Args:
        report_path: Path to the assessment report file.

    Returns:
        The extracted score as a float, or 7.0 as a default if no score pattern is found
        or if an error occurs while reading the file.
    """
    try:
        with open(report_path) as f:
            content = f.read()

        # Look for score patterns like "Overall: 8.5" or "Score: 8.5/10"
        patterns = [
            r"Overall.*?(\d+\.?\d*)",
            r"Score.*?(\d+\.?\d*)",
            r"\*\*(\d+\.?\d*)\*\*.*?/10",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return float(match.group(1))

        # Default score if not found
        return 7.0

    except (OSError, UnicodeDecodeError, ValueError) as e:
        logger.warning(f"Could not extract score from {report_path}: {e}")
        return 7.0


def extract_issues_from_report(report_path: Path) -> list[dict[str, Any]]:
    """Extract issues/findings from assessment report."""
    issues = []

    try:
        with open(report_path) as f:
            content = f.read()

        # Look for severity markers
        severity_patterns = {
            "BLOCKER": r"BLOCKER:?\s*(.+)",
            "CRITICAL": r"CRITICAL:?\s*(.+)",
            "MAJOR": r"MAJOR:?\s*(.+)",
            "MINOR": r"MINOR:?\s*(.+)",
        }

        for severity, pattern in severity_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                issues.append(
                    {
                        "severity": severity,
                        "description": match.group(1).strip(),
                        "source": report_path.stem,
                    }
                )

    except (OSError, UnicodeDecodeError) as e:
        logger.warning(f"Could not extract issues from {report_path}: {e}")

    return issues


# Per-category weights for weighted scoring (names derived from ASSESSMENT_DEFINITIONS)
_CATEGORY_WEIGHTS: dict[str, float] = {
    "A": 2.0,
    "B": 2.0,
    "C": 1.5,
    "D": 1.5,
    "E": 1.5,
    "F": 1.0,
    "G": 2.0,
    "H": 1.0,
    "I": 2.0,
    "J": 1.0,
    "K": 1.0,
    "L": 1.5,
    "M": 1.0,
    "N": 1.0,
    "O": 2.0,
}

# Derive category info from the single source of truth, adding weights
SUMMARY_CATEGORIES: dict[str, dict[str, Any]] = {
    k: {"name": v["name"], "weight": _CATEGORY_WEIGHTS.get(k, 1.0)}
    for k, v in ASSESSMENT_DEFINITIONS.items()
}


def _collect_scores_and_issues(
    input_reports: list[Path],
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    """Extract scores and issues from assessment reports.

    Args:
        input_reports: List of assessment report file paths.

    Returns:
        Tuple of (scores dict keyed by assessment ID, list of all issues).
    """
    scores: dict[str, float] = {}
    all_issues: list[dict[str, Any]] = []

    for report in input_reports:
        match = re.search(r"Assessment_([A-O])_Results", report.name)
        if match:
            assessment_id = match.group(1)
            scores[assessment_id] = extract_score_from_report(report)
            all_issues.extend(extract_issues_from_report(report))

    return scores, all_issues


def _calculate_weighted_score(scores: dict[str, float]) -> float:
    """Calculate weighted average score across assessed categories.

    Args:
        scores: Dictionary mapping assessment IDs to their scores.

    Returns:
        Weighted average score, or 7.0 if no weights are available.
    """
    total_weighted_score = 0.0
    total_weight = 0.0

    for assessment_id, score in scores.items():
        if assessment_id in SUMMARY_CATEGORIES:
            weight = SUMMARY_CATEGORIES[assessment_id]["weight"]
            total_weighted_score += score * weight
            total_weight += weight

    return total_weighted_score / total_weight if total_weight > 0 else 7.0


def _build_markdown_summary(
    scores: dict[str, float],
    overall_score: float,
    critical_issues: list[dict[str, Any]],
) -> str:
    """Build the markdown content for the assessment summary.

    Args:
        scores: Dictionary mapping assessment IDs to scores.
        overall_score: Calculated weighted average score.
        critical_issues: List of BLOCKER/CRITICAL issues.

    Returns:
        Complete markdown string for the summary report.
    """
    md_lines = [
        "# Comprehensive Assessment Summary",
        "",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d')}",
        "**Generated**: Automated via Jules Assessment Auto-Fix workflow",
        f"**Overall Score**: {overall_score:.1f}/10",
        "",
        "## Executive Summary",
        "",
        f"Repository assessment completed across all {len(scores)} categories.",
        "",
        f"### Overall Health: {overall_score:.1f}/10",
        "",
        "### Category Scores",
        "",
        "| Category | Name | Score | Weight |",
        "|----------|------|-------|--------|",
    ]

    for assessment_id in sorted(scores.keys()):
        if assessment_id in SUMMARY_CATEGORIES:
            cat_info = SUMMARY_CATEGORIES[assessment_id]
            score = scores[assessment_id]
            md_lines.append(
                f"| **{assessment_id}** | {cat_info['name']} "
                f"| {score:.1f} | {cat_info['weight']}x |"
            )

    md_lines.append("")
    md_lines.append("## Critical Issues")
    md_lines.append("")
    md_lines.append(f"Found {len(critical_issues)} critical issues requiring immediate attention:")
    md_lines.append("")

    for i, issue in enumerate(critical_issues[:10], 1):
        md_lines.append(
            f"{i}. **[{issue['severity']}]** {issue['description']} (Source: {issue['source']})"
        )

    md_lines.extend(
        [
            "",
            "## Recommendations",
            "",
            "1. Address all BLOCKER issues immediately",
            "2. Create action plan for CRITICAL issues",
            "3. Schedule remediation for MAJOR issues",
            "4. Monitor trends in assessment scores",
            "",
            "## Next Assessment",
            "",
            "Recommended: 30 days from today",
            "",
            "---",
            "",
            "*Generated by Jules Assessment Auto-Fix*",
        ]
    )

    return "\n".join(md_lines) + "\n"


def _build_json_metrics(
    scores: dict[str, float],
    overall_score: float,
    all_issues: list[dict[str, Any]],
    critical_issues: list[dict[str, Any]],
    reports_analyzed: int,
) -> dict[str, Any]:
    """Build structured JSON metrics from assessment data.

    Args:
        scores: Dictionary mapping assessment IDs to scores.
        overall_score: Calculated weighted average score.
        all_issues: Complete list of all issues found.
        critical_issues: Filtered list of BLOCKER/CRITICAL issues.
        reports_analyzed: Number of input reports processed.

    Returns:
        Dictionary suitable for JSON serialization.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "overall_score": round(overall_score, 2),
        "category_scores": {
            k: {
                "score": v,
                "name": SUMMARY_CATEGORIES[k]["name"],
                "weight": SUMMARY_CATEGORIES[k]["weight"],
            }
            for k, v in scores.items()
            if k in SUMMARY_CATEGORIES
        },
        "critical_issues": critical_issues,
        "total_issues": len(all_issues),
        "reports_analyzed": reports_analyzed,
    }


def generate_summary(
    input_reports: list[Path],
    output_md: Path,
    output_json: Path,
) -> int:
    """Generate comprehensive summary from assessment reports.

    Args:
        input_reports: List of assessment report files.
        output_md: Path to save markdown summary.
        output_json: Path to save JSON metrics.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    logger.info(f"Generating assessment summary from {len(input_reports)} reports...")

    scores, all_issues = _collect_scores_and_issues(input_reports)
    overall_score = _calculate_weighted_score(scores)
    critical_issues = [i for i in all_issues if i["severity"] in ("BLOCKER", "CRITICAL")]

    # Write markdown
    md_content = _build_markdown_summary(scores, overall_score, critical_issues)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    with open(output_md, "w") as f:
        f.write(md_content)
    logger.info(f"Markdown summary saved to {output_md}")

    # Write JSON
    json_data = _build_json_metrics(
        scores, overall_score, all_issues, critical_issues, len(input_reports)
    )
    with open(output_json, "w") as f:
        json.dump(json_data, f, indent=2)
    logger.info(f"JSON metrics saved to {output_json}")

    return 0


def main():
    """Parse CLI arguments and generate assessment summary."""
    parser = argparse.ArgumentParser(description="Generate assessment summary")
    parser.add_argument(
        "--input",
        nargs="+",
        type=Path,
        required=True,
        help="Input assessment report files (can use wildcards)",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output markdown summary file",
    )
    parser.add_argument(
        "--json-output",
        required=True,
        type=Path,
        help="Output JSON metrics file",
    )

    args = parser.parse_args()

    # Expand wildcards if needed
    input_reports = []
    for pattern in args.input:
        if "*" in str(pattern):
            # Expand glob pattern
            input_reports.extend(Path(".").glob(str(pattern)))
        else:
            input_reports.append(pattern)

    # Validate paths with shared CLI contracts
    validated_reports: list[Path] = []
    for report_path in input_reports:
        try:
            validated_reports.append(
                ensure_existing_file(str(report_path), value_name="--input report")
            )
        except ValueError as exc:
            logger.error(str(exc))
            return 2

    if not validated_reports:
        logger.error("No valid input reports found")
        return 1

    exit_code = generate_summary(validated_reports, args.output, args.json_output)
    return exit_code


if __name__ == "__main__":
    sys.exit(main() or 0)
