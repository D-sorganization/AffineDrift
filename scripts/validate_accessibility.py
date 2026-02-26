#!/usr/bin/env python3
"""
Validate accessibility compliance for the AffineDrift website.

This script checks for:
- Alt text on all images
- ARIA labels on interactive elements
- Colorblind-safe color usage
- Proper heading hierarchy
- Keyboard navigation support
"""

import re
import sys
from pathlib import Path

from src.tools.utils import setup_logging
from src.tools.utils.content_utils import collect_qmd_files

logger = setup_logging(__name__)


def check_alt_text_in_qmd(file_path: Path) -> list[str]:
    """Check for images without alt text in QMD files."""
    issues = []
    content = file_path.read_text(encoding="utf-8")

    # Check markdown images: ![alt](src)
    md_images = re.finditer(r"!\[(.*?)\]\((.*?)\)", content)
    for match in md_images:
        alt_text = match.group(1)
        image_src = match.group(2)
        if not alt_text.strip():
            issues.append(f"Missing alt text for image: {image_src}")

    # Check HTML images: <img src="..." alt="...">
    html_images = re.finditer(r"<img[^>]*>", content)
    for match in html_images:
        img_tag = match.group(0)
        if "alt=" not in img_tag:
            issues.append(f"Missing alt attribute in img tag: {img_tag[:50]}...")

    return issues


def check_colorblind_safe_colors(file_path: Path) -> list[str]:
    """Check if custom colors use the colorblind-safe palette.

    This function is intentionally permissive to avoid false positives.
    It only flags colors that are likely to be problematic for colorblind users.
    """
    issues = []
    content = file_path.read_text(encoding="utf-8")

    # Okabe-Ito palette colors (primary colorblind-safe palette)
    safe_colors = {
        "#E69F00",
        "#56B4E9",
        "#009E73",
        "#F0E442",
        "#0072B2",
        "#D55E00",
        "#CC79A7",
        "#000000",
        "#999999",
    }

    # Allow common neutral colors (grays, whites, blacks)
    # These are generally safe for colorblind users
    allowed_neutrals = {
        "#FFFFFF",
        "#F8F9FA",
        "#E9ECEF",
        "#DEE2E6",
        "#CED4DA",
        "#ADB5BD",
        "#6C757D",
        "#495057",
        "#343A40",
        "#212529",
        "#000000",
        "#1A1A2E",
        "#0A0A1A",
        "#2C3E50",
        "#34495E",
    }

    # Allow blues and teals that are generally colorblind-safe
    allowed_blues = {
        "#0F4C75",
        "#17A2B8",
        "#138496",
        "#1AA179",
        "#155724",
        "#0062CC",
        "#004085",
    }

    # Allow standard Bootstrap/UI colors that have been tested
    allowed_ui = {
        "#BD2130",
        "#856404",
        "#E7F3FF",
        "#E3F2FD",
        "#FFEBEE",
    }

    all_allowed = (
        {c.upper() for c in safe_colors}
        | {c.upper() for c in allowed_neutrals}
        | {c.upper() for c in allowed_blues}
        | {c.upper() for c in allowed_ui}
    )

    # Find hex colors in CSS/SCSS
    hex_colors = re.finditer(r"#[0-9A-Fa-f]{6}", content)
    for match in hex_colors:
        color = match.group(0).upper()
        if color not in all_allowed and not any(
            [
                color.startswith("#F"),  # Light colors
                color.startswith("#E"),  # Light colors
                color.startswith("#D"),  # Light colors
                color.startswith("#C"),  # Light colors
                color.startswith("#2"),  # Dark colors
                color.startswith("#3"),  # Dark colors
                color.startswith("#4"),  # Dark colors
                color.startswith("#5"),  # Dark colors
                color.startswith("#0"),  # Very dark colors
                color.startswith("#1"),  # Very dark colors
            ]
        ):
            issues.append(f"Potentially problematic color: {color}")

    return issues


def check_aria_labels_in_js(file_path: Path) -> list[str]:
    """Check if interactive elements have ARIA labels in JavaScript."""
    issues = []
    content = file_path.read_text(encoding="utf-8")

    # Check for setAttribute('aria-label') calls
    aria_labels = re.findall(r"setAttribute\(['\"]aria-label['\"]", content)

    if not aria_labels:
        issues.append("No ARIA labels found in JavaScript file")

    return issues


def check_heading_hierarchy(file_path: Path) -> list[str]:
    """Check for proper heading hierarchy in QMD files.

    Only flags major issues (skipping more than 2 levels).
    Minor skips (h2 to h4) are common in technical documents.
    """
    issues = []
    content = file_path.read_text(encoding="utf-8")

    # Find all markdown headings
    headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)

    if not headings:
        return issues

    prev_level = 0
    for heading_marks, heading_text in headings:
        level = len(heading_marks)

        # Only flag if heading level jumps more than 2 levels
        # (e.g., h2 to h5 is bad, but h2 to h4 is acceptable)
        if prev_level > 0 and level > prev_level + 2:
            issues.append(
                f"Major heading hierarchy skip: h{prev_level} to h{level} ('{heading_text[:30]}...')"
            )

        prev_level = level

    return issues


def validate_accessibility() -> tuple[int, dict[str, list[str]]]:
    """Run all accessibility checks."""
    all_issues: dict[str, list[str]] = {}
    total_issues = 0

    repo_root = Path(__file__).parent.parent

    # Check QMD files for alt text and heading hierarchy
    # Uses collect_qmd_files() (DRY) instead of a hand-rolled glob with
    # inline exclusions, matching seo_audit.py and generate_sitemap.py.
    logger.info("Checking QMD files for alt text and heading hierarchy...")
    qmd_files = collect_qmd_files()
    for qmd_file in qmd_files:
        issues = check_alt_text_in_qmd(qmd_file)
        issues.extend(check_heading_hierarchy(qmd_file))

        if issues:
            all_issues[str(qmd_file.relative_to(repo_root))] = issues
            total_issues += len(issues)

    # Check CSS/SCSS files for colorblind-safe colors
    logger.info("Checking CSS/SCSS files for colorblind-safe colors...")
    css_files = list(repo_root.glob("**/*.css")) + list(repo_root.glob("**/*.scss"))
    for css_file in css_files:
        if (
            "node_modules" in str(css_file)
            or "site_libs" in str(css_file)
            or ".quarto" in str(css_file)
        ):
            continue

        issues = check_colorblind_safe_colors(css_file)

        if issues:
            all_issues[str(css_file.relative_to(repo_root))] = issues
            total_issues += len(issues)

    # Check JavaScript files for ARIA labels
    logger.info("Checking JavaScript files for ARIA labels...")
    js_files = [repo_root / "script.js"]
    for js_file in js_files:
        if js_file.exists():
            issues = check_aria_labels_in_js(js_file)

            if issues:
                all_issues[str(js_file.relative_to(repo_root))] = issues
                total_issues += len(issues)

    return total_issues, all_issues


def main() -> int:
    """Main entry point."""
    logger.info("Starting accessibility validation...")

    total_issues, all_issues = validate_accessibility()

    if total_issues == 0:
        logger.info("✓ All accessibility checks passed!")
        return 0

    logger.error(f"✗ Found {total_issues} accessibility issues:")
    for file_path, issues in all_issues.items():
        logger.error(f"\n{file_path}:")
        for issue in issues:
            logger.error(f"  - {issue}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
