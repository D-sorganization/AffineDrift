#!/usr/bin/env python3
"""
Create GitHub issues from assessment findings.

This script reads the assessment summary JSON and creates GitHub issues
for untracked critical findings.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.tools.utils import setup_logging
from src.tools.utils.assessment_utils import classify_assessment_category
from src.tools.utils.issue_utils import format_issue_body, get_repo_short_name

logger = setup_logging(__name__)


def get_existing_issues() -> list[dict[str, Any]]:
    """Fetch existing GitHub issues."""
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--limit", "200", "--json", "number,title,state,labels"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except Exception as e:
        logger.warning(f"Could not fetch existing issues: {e}")
        return []


def issue_exists(title: str, existing_issues: list[dict[str, Any]]) -> bool:
    """Check if an issue with similar title already exists."""
    title_lower = title.lower()
    for issue in existing_issues:
        if issue["state"] == "OPEN":
            existing_title = issue["title"].lower()
            if title_lower in existing_title or existing_title in title_lower:
                return True
    return False


def create_github_issue(
    title: str,
    body: str,
    labels: list[str],
    dry_run: bool = False,
) -> bool:
    """Create a GitHub issue using gh CLI."""
    if dry_run:
        logger.info(f"[DRY RUN] Would create issue: {title}")
        return True

    try:
        cmd = ["gh", "issue", "create", "--title", title, "--body", body]
        if labels:
            cmd.extend(["--label", ",".join(labels)])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issue_url = result.stdout.strip()
        logger.info(f"✓ Created issue: {issue_url}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Failed to create issue '{title}': {e.stderr}")
        return False


def prepare_issue_data(
    issue: dict[str, Any], summary: dict[str, Any], repo_short: str
) -> dict[str, Any]:
    """Prepare issue title, body, and labels from a finding."""
    severity = issue.get("severity", "UNKNOWN")
    description = issue.get("description", "No description")
    source = issue.get("source", "Unknown")

    category = classify_assessment_category(source, description)

    # Clean description for title (remove markdown, truncate)
    clean_desc = description.replace("**", "").replace("*", "").replace("`", "")
    clean_desc = clean_desc.split("\n")[0]  # First line only
    if len(clean_desc) > 60:
        clean_desc = clean_desc[:57] + "..."

    title = f"[{repo_short}] {severity} {category}: {clean_desc}"
    body = format_issue_body(
        severity=severity,
        category=category,
        source=source,
        description=description,
        timestamp=summary.get("timestamp", "Unknown"),
    )

    labels = ["auto-generated", "quality-control"]
    if severity in ("BLOCKER", "CRITICAL"):
        labels.append("bug")
    else:
        labels.append("enhancement")

    return {"title": title, "body": body, "labels": labels}


def process_assessment_findings(
    summary_file: Path,
    severities: list[str],
    check_existing: bool = True,
    dry_run: bool = False,
) -> int:
    """Process assessment findings and create issues."""
    try:
        with open(summary_file) as f:
            summary = json.load(f)
    except Exception as e:
        logger.error(f"Could not load summary file: {e}")
        return 1

    findings = summary.get("critical_issues", [])
    if not findings:
        logger.info("No critical issues found in assessment")
        return 0

    logger.info(f"Found {len(findings)} issues. Filtering by severities: {', '.join(severities)}")
    filtered_issues = [i for i in findings if i.get("severity") in severities]

    existing_issues = get_existing_issues() if check_existing else []
    repo_short = get_repo_short_name()

    created_count = 0
    skipped_count = 0

    for issue in filtered_issues[:20]:
        data = prepare_issue_data(issue, summary, repo_short)

        if check_existing and issue_exists(data["title"], existing_issues):
            logger.info(f"⊘ Skipping (already exists): {data['title']}")
            skipped_count += 1
            continue

        if create_github_issue(data["title"], data["body"], data["labels"], dry_run):
            created_count += 1

    logger.info(f"\n✓ Summary: Created {created_count} issues, skipped {skipped_count}")
    return 0


def main():
    """Parse command-line arguments and create GitHub issues from assessment."""
    parser = argparse.ArgumentParser(description="Create GitHub issues from assessment")
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Assessment summary JSON file",
    )
    parser.add_argument(
        "--severity",
        default="BLOCKER,CRITICAL",
        help="Comma-separated list of severities to create issues for",
    )
    parser.add_argument(
        "--check-existing",
        action="store_true",
        help="Check for existing issues before creating",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print issues instead of creating them",
    )

    args = parser.parse_args()

    severities = [s.strip().upper() for s in args.severity.split(",")]

    exit_code = process_assessment_findings(
        args.input,
        severities,
        args.check_existing,
        args.dry_run,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
