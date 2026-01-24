#!/usr/bin/env python3
"""
Orchestrate the full assessment process.

- Runs assessments A-O.
- Applies Quick Fixes for Code Style.
- Generates Comprehensive Assessment.
- Identifies Required Issues.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ASSESSMENT_SCRIPT = Path("scripts/run_assessment.py")
DOCS_DIR = Path("docs/assessments")
DOCS_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = "ABCDEFGHIJKLMNO"

# Mapping to Weighted Categories
# Code (25%), Testing (15%), Docs (10%), Security (15%), Perf (15%), Ops (10%), Design (10%)
WEIGHT_MAPPING = {
    "Code": ["A", "I", "D", "K", "O"],
    "Testing": ["C"],
    "Docs": ["B"],
    "Security": ["F"],
    "Performance": ["E", "N"],
    "Ops": ["G", "H", "L", "M"],
    "Design": ["J"],
}

WEIGHTS = {
    "Code": 0.25,
    "Testing": 0.15,
    "Docs": 0.10,
    "Security": 0.15,
    "Performance": 0.15,
    "Ops": 0.10,
    "Design": 0.10,
}


def run_single_assessment(category_id: str) -> dict[str, Any]:
    """Run a single assessment and return the JSON result."""
    output_md = DOCS_DIR / f"Assessment_{category_id}.md"
    output_json = DOCS_DIR / f"Assessment_{category_id}.json"

    cmd = [
        sys.executable,
        str(ASSESSMENT_SCRIPT),
        "--assessment",
        category_id,
        "--output",
        str(output_md),
        "--json-output",
        str(output_json),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        with open(output_json) as f:
            return json.load(f)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run assessment {category_id}: {e.stderr}")
        return {"id": category_id, "score": 0, "findings": ["Failed to execute assessment"]}
    except Exception as e:
        logger.error(f"Error reading result for {category_id}: {e}")
        return {"id": category_id, "score": 0, "findings": [f"Error: {str(e)}"]}


def apply_quick_fixes():
    """Apply quick fixes for code style."""
    logger.info("Applying Quick Fixes (Ruff & Black)...")
    try:
        subprocess.run(["ruff", "check", "--fix", "."], check=False, capture_output=True)
        subprocess.run(["black", "."], check=False, capture_output=True)
        logger.info("Quick Fixes applied.")
    except Exception as e:
        logger.error(f"Failed to apply quick fixes: {e}")


def main():
    logger.info("Starting Orchestrated Assessment...")

    results = {}

    # 1. Run all assessments initially
    for cat in CATEGORIES:
        results[cat] = run_single_assessment(cat)

    # 2. Check Code Style (I) and apply fixes if needed
    style_score = results["I"].get("score", 0)
    if style_score < 8:
        logger.info(f"Code Style score is {style_score}/10. Applying Quick Fixes...")
        apply_quick_fixes()
        # Re-run Assessment I
        results["I"] = run_single_assessment("I")
        logger.info(f"New Code Style score: {results['I'].get('score', 0)}/10")

    # 3. Rename files to match requested format Assessment_X_CATEGORY.md
    # The run_assessment.py saves as Assessment_X.md (or whatever we passed).
    # I passed Assessment_{category_id}.md.
    # The prompt asks for Assessment_X_CATEGORY.md.

    category_names = {
        "A": "Code_Structure",
        "B": "Documentation",
        "C": "Test_Coverage",
        "D": "Error_Handling",
        "E": "Performance",
        "F": "Security",
        "G": "Dependencies",
        "H": "CI_CD",
        "I": "Code_Style",
        "J": "API_Design",
        "K": "Data_Handling",
        "L": "Logging",
        "M": "Configuration",
        "N": "Scalability",
        "O": "Maintainability",
    }

    for cat, res in results.items():
        old_path = DOCS_DIR / f"Assessment_{cat}.md"
        new_name = f"Assessment_{cat}_{category_names.get(cat, 'Unknown')}.md"
        new_path = DOCS_DIR / new_name
        if old_path.exists():
            old_path.rename(new_path)
            # Update the report title in the file if needed?
            # run_assessment.py writes "Assessment {id}: {name}". That's fine.

    # 4. Calculate Comprehensive Scores
    weighted_sum = 0
    total_weight = 0

    group_scores = {}

    for group, categories in WEIGHT_MAPPING.items():
        group_total = 0
        group_count = 0
        for cat in categories:
            if cat in results:
                group_total += results[cat]["score"]
                group_count += 1

        avg = group_total / group_count if group_count > 0 else 0
        group_scores[group] = avg

        weight = WEIGHTS.get(group, 0)
        weighted_sum += avg * weight
        total_weight += weight

    final_score = weighted_sum / total_weight if total_weight > 0 else 0

    # 5. Generate Comprehensive Assessment
    comp_md = DOCS_DIR / "Comprehensive_Assessment.md"

    table_rows = []
    for cat in CATEGORIES:
        r = results[cat]
        name = category_names.get(cat, "Unknown")
        score = r["score"]
        status = "🟢" if score >= 8 else "🟡" if score >= 5 else "🔴"
        table_rows.append(f"| {cat} | {name} | {score}/10 | {status} |")

    recommendations = []
    # Collect findings from low scoring areas
    for cat in CATEGORIES:
        r = results[cat]
        if r["score"] < 10:
            for f in r["findings"]:
                if "✗" in f or "[WARN]" in f:
                    recommendations.append(f"[{cat}] {f.strip('- ')}")

    top_5_recs = recommendations[:5]
    if not top_5_recs:
        top_5_recs = ["No critical issues found. Keep up the good work!"]

    comp_content = f"""# Comprehensive Repository Assessment

**Date**: {results['A']['timestamp'][:10]}
**Overall Score**: {final_score:.2f}/10

## Score Breakdown by Category

| ID | Category | Score | Status |
|----|----------|-------|--------|
{chr(10).join(table_rows)}

## Weighted Analysis

| Group | Weight | Score |
|-------|--------|-------|
"""
    for group, score in group_scores.items():
        comp_content += f"| {group} | {WEIGHTS[group]*100}% | {score:.2f}/10 |\n"

    comp_content += f"""
## Top 5 Recommendations

{chr(10).join([f"- {r}" for r in top_5_recs])}

## Methodology

Scores are calculated based on automated analysis of code structure, linting results, test coverage, and security checks.
Weighted average is composed of: Code (25%), Testing (15%), Docs (10%), Security (15%), Perf (15%), Ops (10%), Design (10%).
"""

    with open(comp_md, "w") as f:
        f.write(comp_content)

    logger.info(f"Generated {comp_md}")

    # 6. Generate Required Issues
    issues_md = DOCS_DIR / "REQUIRED_ISSUES.md"
    low_grade_issues = []

    for cat in CATEGORIES:
        if results[cat]["score"] < 5:
            low_grade_issues.append(
                {
                    "title": f"Improve {category_names[cat]} (Assessment {cat})",
                    "body": f"The score for {category_names[cat]} is {results[cat]['score']}/10. Please review the findings in `Assessment_{cat}_{category_names[cat]}.md` and improve.",
                    "labels": ["jules:assessment", "needs-attention"],
                }
            )

    if low_grade_issues:
        issues_content = "# Required GitHub Issues\n\n"
        issues_content += "The following issues must be created (gh CLI unavailable):\n\n"

        for i, issue in enumerate(low_grade_issues, 1):
            issues_content += f"## Issue {i}: {issue['title']}\n"
            issues_content += f"**Labels**: {', '.join(issue['labels'])}\n\n"
            issues_content += f"**Body**:\n{issue['body']}\n\n"
            issues_content += "---\n\n"

        with open(issues_md, "w") as f:
            f.write(issues_content)
        logger.info(f"Generated {issues_md} with {len(low_grade_issues)} required issues.")
    else:
        logger.info("No assessments scored below 5. No issues required.")
        if issues_md.exists():
            issues_md.unlink()


if __name__ == "__main__":
    main()
