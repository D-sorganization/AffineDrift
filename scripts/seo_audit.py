#!/usr/bin/env python3
"""SEO Audit Script - Checks all pages for proper meta descriptions and generates report.
Also suggests improvements based on content analysis.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, cast

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.tools.utils import parse_frontmatter_dict, setup_logging

logger = setup_logging(__name__)


def extract_first_paragraph(content: str) -> str:
    """Extract first meaningful paragraph for description suggestion."""
    # Remove frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]

    # Remove HTML, code blocks, headers
    content = re.sub(r"```[\s\S]*?```", "", content)
    content = re.sub(r"<[^>]+>", "", content)
    content = re.sub(r"^#+\s+.+$", "", content, flags=re.MULTILINE)
    content = re.sub(r"^\s*[-*]\s+", "", content, flags=re.MULTILINE)

    # Find first substantial paragraph
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    for p in paragraphs:
        # Skip short or link-only paragraphs
        clean_p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p)
        clean_p = re.sub(r"\s+", " ", clean_p).strip()
        if len(clean_p) > 50 and not clean_p.startswith("!"):
            return clean_p[:160]

    return ""


def check_heading_hierarchy(content: str) -> list[str]:
    """Check for proper heading hierarchy (H1 -> H2 -> H3, etc.)."""
    issues: list[str] = []

    # Remove frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]

    headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)

    if not headings:
        return issues

    prev_level = 0
    for hashes, text in headings:
        level = len(hashes)
        if prev_level > 0 and level > prev_level + 1:
            issues.append(f"Skipped heading level: H{prev_level} -> H{level} ('{text[:30]}...')")
        prev_level = level

    # Check for multiple H1s
    h1_count = sum(1 for h, _ in headings if len(h) == 1)
    if h1_count > 1:
        issues.append(f"Multiple H1 headings found ({h1_count})")

    return issues


def check_images(content: str) -> list[str]:
    """Check for images without alt text."""
    issues: list[str] = []

    # Find markdown images
    images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)
    for alt, src in images:
        if not alt.strip():
            issues.append(f"Image missing alt text: {src[:50]}")

    # Find HTML images
    html_images = re.findall(r"<img[^>]*>", content)
    for img in html_images:
        if 'alt="' not in img and "alt='" not in img:
            src_match = re.search(r'src=["\']([^"\']+)["\']', img)
            src = src_match.group(1) if src_match else "unknown"
            issues.append(f"HTML image missing alt text: {src[:50]}")

    return issues


def audit_file(filepath: Path) -> dict[str, Any]:
    """Audit a single file for SEO issues."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": str(e)}

    frontmatter = parse_frontmatter_dict(content)

    result: dict[str, Any] = {
        "title": frontmatter.get("title", ""),
        "has_description": bool(frontmatter.get("description")),
        "description": frontmatter.get("description", ""),
        "description_length": len(frontmatter.get("description", "")),
        "suggested_description": "",
        "heading_issues": [],
        "image_issues": [],
        "issues": [],
    }

    # Check description
    if not result["has_description"]:
        result["suggested_description"] = extract_first_paragraph(content)
        result["issues"].append("Missing meta description")
    elif result["description_length"] < 50:
        result["issues"].append(
            f"Description too short ({result['description_length']} chars, recommend 50-160)",
        )
    elif result["description_length"] > 160:
        result["issues"].append(
            f"Description too long ({result['description_length']} chars, recommend 50-160)",
        )

    # Check headings
    result["heading_issues"] = check_heading_hierarchy(content)
    if result["heading_issues"]:
        result["issues"].extend(result["heading_issues"])

    # Check images
    result["image_issues"] = check_images(content)
    if result["image_issues"]:
        result["issues"].extend(result["image_issues"])

    return result


def main() -> None:
    """Run SEO audit on all content files."""
    content_dirs = [".", "articles"]
    results: dict[str, Any] = {}
    total_issues = 0
    files_with_issues = 0

    for content_dir in content_dirs:
        dir_path = Path(content_dir)
        if not dir_path.exists():
            continue

        for filepath in dir_path.glob("*.qmd"):
            if filepath.name.startswith("_"):
                continue

            result = audit_file(filepath)
            results[str(filepath)] = result

            issues = result.get("issues", [])
            if issues:
                files_with_issues += 1
                total_issues += len(cast("list[str]", issues))

    # Summary
    logger.info(
        "SEO Audit Summary: %d files audited, %d with issues", len(results), files_with_issues
    )

    # Missing descriptions
    missing_desc = [(f, r) for f, r in results.items() if not r.get("has_description")]
    if missing_desc:
        logger.warning("Files missing meta descriptions: %d", len(missing_desc))
    for filepath_str, result in missing_desc:
        if result.get("suggested_description"):
            logger.info("  %s - suggested: %s", filepath_str, result["suggested_description"][:60])

    # Other issues
    other_issues = [
        (f, r) for f, r in results.items() if r.get("issues") and r.get("has_description")
    ]
    if other_issues:
        logger.warning("Files with other SEO issues: %d", len(other_issues))
    for filepath_str, result in other_issues:
        issues = [i for i in cast("list[str]", result["issues"]) if "Missing meta" not in i]
        if issues:
            for issue in issues:
                logger.info("  %s: %s", filepath_str, issue)

    # Generate JSON report
    report_path = Path("docs/data/seo_audit.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(
            {
                "summary": {
                    "files_audited": len(results),
                    "files_with_issues": files_with_issues,
                    "total_issues": total_issues,
                    "missing_descriptions": len(missing_desc),
                },
                "results": results,
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    main()
