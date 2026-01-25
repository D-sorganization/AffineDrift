#!/usr/bin/env python3
"""Consolidated HTML validation fixer.

This script fixes common HTML validation issues in generated HTML files.
It consolidates fix_html_validation.py and fix_html_validation_v2.py into
a single, DRY implementation.

Usage:
    python -m src.tools.fix_html_validation [--docs-dir DOCS_DIR] [--dry-run]

Fixes applied:
    1. crossorigin="" -> crossorigin (attribute normalization)
    2. Remove redundant role="link" on anchor elements
    3. Remove aria-labelledby on dropdown-menu (Bootstrap issue)
    4. Add aria-label to navbar brand logo links
    5. Replace dots with dashes in IDs (ID normalization)
    6. Add type="button" to buttons missing type attribute
    7. Add title to iframes missing title attribute
    8. Add aria-labels to navigation landmarks
"""

import argparse
import re
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parents[2]))

from src.tools.utils import find_html_files, process_file_content, setup_logging

logger = setup_logging(__name__)


def fix_crossorigin_attribute(content: str) -> str:
    """Fix crossorigin="" to crossorigin (boolean attribute)."""
    return re.sub(r'crossorigin=""', "crossorigin", content)


def remove_redundant_role_link(content: str) -> str:
    """Remove redundant role='link' on anchor elements."""
    return re.sub(r'\s+role="link"', "", content)


def remove_aria_labelledby_dropdown(content: str) -> str:
    """Remove aria-labelledby from dropdown-menu (Bootstrap compatibility)."""
    return re.sub(
        r'(\s+class="dropdown-menu")\s+aria-labelledby="[^"]+"',
        r"\1",
        content,
    )


def add_navbar_brand_aria_label(content: str) -> str:
    """Add aria-label to navbar brand logo links for accessibility."""
    if 'class="navbar-brand navbar-brand-logo"' not in content:
        return content

    # Add aria-label if missing
    content = re.sub(
        r'(<a [^>]*class="navbar-brand navbar-brand-logo"[^>]*)>',
        r'\1 aria-label="Home">',
        content,
    )
    # Prevent duplicate aria-label if run multiple times
    content = re.sub(
        r'aria-label="Home" aria-label="Home"',
        'aria-label="Home"',
        content,
    )
    return content


def fix_dots_in_ids(content: str) -> str:
    """Replace dots with dashes in ID attributes (invalid characters)."""

    def replace_dots(match: re.Match[str]) -> str:
        """Replace dots with dashes in the matched string."""
        return match.group(0).replace(".", "-")

    # Fix id="..." attributes
    content = re.sub(r'id="[^"]*\.[^"]*"', replace_dots, content)
    # Fix href="#..." internal links to match
    content = re.sub(r'href="#[^"]*\.[^"]*"', replace_dots, content)
    return content


def add_button_type(content: str) -> str:
    """Add type='button' to buttons missing type attribute."""

    def add_type(match: re.Match[str]) -> str:
        """Add type='button' if missing."""
        tag = match.group(0)
        if "type=" not in tag:
            return tag.replace("<button", '<button type="button"')
        return tag

    return re.sub(r"<button[^>]*>", add_type, content)


def add_iframe_title(content: str) -> str:
    """Add title attribute to iframes for accessibility."""

    def add_title(match: re.Match[str]) -> str:
        """Add title attribute if missing."""
        tag = match.group(0)
        if "title=" not in tag:
            return tag.replace("<iframe", '<iframe title="Embedded Content"')
        return tag

    return re.sub(r"<iframe[^>]*>", add_title, content)


def add_landmark_aria_labels(content: str) -> str:
    """Add aria-labels to navigation landmarks for unique identification."""
    # Table of Contents navigation
    if '<nav id="TOC"' in content and 'aria-label="Table of Contents"' not in content:
        content = content.replace(
            '<nav id="TOC"',
            '<nav id="TOC" aria-label="Table of Contents"',
        )

    # Left sidebar
    if '<aside class="left-sidebar"' in content and 'aria-label="Primary Sidebar"' not in content:
        content = content.replace(
            '<aside class="left-sidebar"',
            '<aside class="left-sidebar" aria-label="Primary Sidebar"',
        )

    # Right sidebar
    if (
        '<aside class="right-sidebar"' in content
        and 'aria-label="Secondary Sidebar"' not in content
    ):
        content = content.replace(
            '<aside class="right-sidebar"',
            '<aside class="right-sidebar" aria-label="Secondary Sidebar"',
        )

    return content


def apply_all_fixes(content: str) -> str:
    """Apply all HTML validation fixes to content.

    Args:
        content: HTML content to fix.

    Returns:
        Fixed HTML content.
    """
    # Apply fixes in order
    content = fix_crossorigin_attribute(content)
    content = remove_redundant_role_link(content)
    content = remove_aria_labelledby_dropdown(content)
    content = add_navbar_brand_aria_label(content)
    content = fix_dots_in_ids(content)
    content = add_button_type(content)
    content = add_iframe_title(content)
    content = add_landmark_aria_labels(content)
    return content


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fix HTML validation issues in generated HTML files",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="Directory containing HTML files to fix (default: docs)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )
    args = parser.parse_args()

    html_files = find_html_files(root_dir=".", docs_only=True)

    if not html_files:
        logger.warning("No HTML files found in %s", args.docs_dir)
        return 0

    fixed_count = 0
    for filepath in html_files:
        if args.dry_run:
            # Check if file would be modified
            try:
                content = filepath.read_text(encoding="utf-8")
                fixed = apply_all_fixes(content)
                if fixed != content:
                    logger.info("[DRY-RUN] Would fix: %s", filepath)
                    fixed_count += 1
            except (UnicodeDecodeError, FileNotFoundError):
                pass
        else:
            if process_file_content(filepath, apply_all_fixes):
                logger.info("Fixed: %s", filepath)
                fixed_count += 1

    logger.info("Processed %d files, fixed %d", len(html_files), fixed_count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
