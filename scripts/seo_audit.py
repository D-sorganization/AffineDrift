#!/usr/bin/env python3
"""
SEO Audit Script - Checks all pages for proper meta descriptions and generates report.
Also suggests improvements based on content analysis.
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            current_key = None
            for line in yaml_content.split("\n"):
                if line.startswith("  ") and current_key:
                    continue  # Skip nested content
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    frontmatter[key] = value
                    current_key = key
    return frontmatter


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


def check_heading_hierarchy(content: str) -> list:
    """Check for proper heading hierarchy (H1 -> H2 -> H3, etc.)."""
    issues = []

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


def check_images(content: str) -> list:
    """Check for images without alt text."""
    issues = []

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


def audit_file(filepath: Path) -> dict:
    """Audit a single file for SEO issues."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": str(e)}

    frontmatter = extract_frontmatter(content)

    result = {
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
        result["issues"].append(f"Description too short ({result['description_length']} chars, recommend 50-160)")
    elif result["description_length"] > 160:
        result["issues"].append(f"Description too long ({result['description_length']} chars, recommend 50-160)")

    # Check headings
    result["heading_issues"] = check_heading_hierarchy(content)
    if result["heading_issues"]:
        result["issues"].extend(result["heading_issues"])

    # Check images
    result["image_issues"] = check_images(content)
    if result["image_issues"]:
        result["issues"].extend(result["image_issues"])

    return result


def main():
    """Run SEO audit on all content files."""
    print("=" * 70)
    print("AffineDrift SEO Audit Report")
    print("=" * 70)

    content_dirs = [".", "articles"]
    results = {}
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

            if result.get("issues"):
                files_with_issues += 1
                total_issues += len(result["issues"])

    # Summary
    print(f"\nFiles audited: {len(results)}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issues found: {total_issues}")

    # Missing descriptions
    missing_desc = [(f, r) for f, r in results.items() if not r.get("has_description")]
    if missing_desc:
        print(f"\n{'=' * 70}")
        print(f"MISSING META DESCRIPTIONS ({len(missing_desc)} files)")
        print("=" * 70)
        for filepath, result in missing_desc:
            print(f"\n{filepath}")
            print(f"  Title: {result.get('title', 'N/A')}")
            if result.get("suggested_description"):
                print(f"  Suggested: {result['suggested_description'][:100]}...")

    # Other issues
    other_issues = [(f, r) for f, r in results.items() if r.get("issues") and r.get("has_description")]
    if other_issues:
        print(f"\n{'=' * 70}")
        print(f"OTHER SEO ISSUES ({len(other_issues)} files)")
        print("=" * 70)
        for filepath, result in other_issues:
            issues = [i for i in result["issues"] if "Missing meta" not in i]
            if issues:
                print(f"\n{filepath}")
                for issue in issues:
                    print(f"  - {issue}")

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
    print(f"\nDetailed report saved to: {report_path}")


if __name__ == "__main__":
    main()
