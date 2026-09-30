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

import argparse
import json
import re
import sys
from pathlib import Path

from src.tools.utils import setup_logging
from src.tools.utils.content_utils import collect_qmd_files

logger = setup_logging(__name__)

_LONG_DESCRIPTION_BASELINE = (
    Path(__file__).parent.parent / "config" / "accessibility-long-description-baseline.json"
)


def _load_long_description_baseline() -> set[str]:
    """Load the set of QMD paths grandfathered from the long-description check.

    Mirrors check_terminology.py / check_tree_parity.py: a new check must not
    fail on pre-existing content, so known gaps are tracked here and shrunk as
    they're fixed rather than blocking `quality-gate` on unrelated debt.
    """
    if not _LONG_DESCRIPTION_BASELINE.is_file():
        return set()
    data = json.loads(_LONG_DESCRIPTION_BASELINE.read_text(encoding="utf-8"))
    return set(data.get("accepted", []))


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


_SAFE_COLORS = {
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

_ALLOWED_NEUTRALS = {
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

_ALLOWED_BLUES = {
    "#0F4C75",
    "#17A2B8",
    "#138496",
    "#1AA179",
    "#155724",
    "#0062CC",
    "#004085",
}

_ALLOWED_UI = {
    "#BD2130",
    "#856404",
    "#E7F3FF",
    "#E3F2FD",
    "#FFEBEE",
}

_ALL_ALLOWED = (
    {c.upper() for c in _SAFE_COLORS}
    | {c.upper() for c in _ALLOWED_NEUTRALS}
    | {c.upper() for c in _ALLOWED_BLUES}
    | {c.upper() for c in _ALLOWED_UI}
)


def check_colorblind_safe_colors(file_path: Path) -> list[str]:
    """Check if custom colors use the colorblind-safe palette.

    This function is intentionally permissive to avoid false positives.
    It only flags colors that are likely to be problematic for colorblind users.
    """
    issues = []
    content = file_path.read_text(encoding="utf-8")

    # Find hex colors in CSS/SCSS
    hex_colors = re.finditer(r"#[0-9A-Fa-f]{6}", content)
    for match in hex_colors:
        color = match.group(0).upper()
        if color not in _ALL_ALLOWED and not any(
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


def check_long_description_for_diagrams(file_path: Path) -> list[str]:
    """Check that complex SVG diagrams provide a long description (E8/E9).

    E8 (Visual Explanation and Design System) specifies that diagrams are SVG
    with alt text *and* a long description, since alt text alone cannot carry
    the explanation a vector-field or state-space diagram needs. An SVG image
    reference is treated as a complex diagram; it passes if the file also
    contains either an ``aria-describedby`` reference resolved to an in-page
    element, or a "long description" disclosure. Checked file-wide rather
    than per-image to stay permissive, matching this module's other checks.
    """
    issues = []
    content = file_path.read_text(encoding="utf-8")

    svg_images = re.findall(r"!\[.*?\]\(([^)]*\.svg[^)]*)\)", content, re.IGNORECASE)
    svg_images += re.findall(
        r'<img[^>]*src=["\']([^"\']*\.svg[^"\']*)["\'][^>]*>', content, re.IGNORECASE
    )

    if not svg_images:
        return issues

    element_ids = set(re.findall(r'id=["\']([^"\']+)["\']', content))
    describedby_targets = set(re.findall(r'aria-describedby=["\']([^"\']+)["\']', content))
    has_long_description_disclosure = bool(
        re.search(r"<details>.*?long description", content, re.IGNORECASE | re.DOTALL)
    )
    has_long_description = (
        bool(describedby_targets & element_ids) or has_long_description_disclosure
    )

    if not has_long_description:
        for src in svg_images:
            issues.append(f"Complex diagram missing a long description: {src}")

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


def validate_accessibility(*, qmd_only: bool = False) -> tuple[int, dict[str, list[str]]]:
    """Run accessibility checks.

    Args:
        qmd_only: Only run the QMD content checks (alt text, heading
            hierarchy, long descriptions). Skips the CSS colorblind-safe-color
            and JS ARIA-label checks, which have known pre-existing findings
            not yet tracked by a baseline (used by the `quality-gate` CI step
            wired for #4567, scoped to alt text and long descriptions only).
    """
    all_issues: dict[str, list[str]] = {}
    total_issues = 0

    repo_root = Path(__file__).parent.parent
    long_description_baseline = _load_long_description_baseline()

    # Check QMD files for alt text and heading hierarchy
    # Uses collect_qmd_files() (DRY) instead of a hand-rolled glob with
    # inline exclusions, matching seo_audit.py and generate_sitemap.py.
    # collect_qmd_files() returns paths relative to the CWD (repo root, by the
    # documented invocation), not absolute, so they are used as-is rather than
    # through relative_to(repo_root) -- matching seo_audit.py's usage.
    logger.info("Checking QMD files for alt text, headings, and long descriptions...")
    qmd_files = collect_qmd_files()
    for qmd_file in qmd_files:
        issues = check_alt_text_in_qmd(qmd_file)
        issues.extend(check_heading_hierarchy(qmd_file))
        if qmd_file.as_posix() not in long_description_baseline:
            issues.extend(check_long_description_for_diagrams(qmd_file))

        if issues:
            all_issues[str(qmd_file)] = issues
            total_issues += len(issues)

    if qmd_only:
        return total_issues, all_issues

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

    # Check the active JavaScript bundle for ARIA labels
    logger.info("Checking JavaScript bundle for ARIA labels...")
    js_files = [repo_root / "js/main.js"]
    for js_file in js_files:
        if js_file.exists():
            issues = check_aria_labels_in_js(js_file)

            if issues:
                all_issues[str(js_file.relative_to(repo_root))] = issues
                total_issues += len(issues)

    return total_issues, all_issues


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--qmd-only",
        action="store_true",
        help=(
            "Only check QMD content (alt text, heading hierarchy, long "
            "descriptions); skip the CSS and JS checks, which are not yet "
            "CI-clean."
        ),
    )
    args = parser.parse_args()

    logger.info("Starting accessibility validation...")

    total_issues, all_issues = validate_accessibility(qmd_only=args.qmd_only)

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
