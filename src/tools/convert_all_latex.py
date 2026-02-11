#!/usr/bin/env python3
"""Batch LaTeX to HTML Converter for AffineDrift
Converts all LaTeX article files to HTML and updates root-level HTML files.
"""

import os
import sys
from pathlib import Path

from latex_to_html import LaTeXToHTMLConverter


from src.tools.utils import setup_logging

logger = setup_logging(__name__)

# Mapping of LaTeX files to their target HTML locations
CONVERSIONS = [
    {
        "source": "content/Wrist as Universal Joint/Wrist_Universal_Claude.tex",
        "target": "content/Wrist as Universal Joint/Wrist_Universal_Claude.html",
        "root_page": None,  # This is a content page, not a root-level page
    },
    {
        "source": (
            "content/Inverse Dynamics Analysis/Drafts/Inverse Dynamics Claude Current/"
            "inverse_dynamics_final.tex"
        ),
        "target": (
            "content/Inverse Dynamics Analysis/Drafts/Inverse Dynamics Claude Current/"
            "inverse_dynamics_article.html"
        ),
        "root_page": None,  # This is a content page
    },
]


def convert_all(dry_run: bool = False) -> bool:
    """Convert all LaTeX files to HTML."""
    converter = LaTeXToHTMLConverter()

    if dry_run:
        logger.info("Dry run mode - no files will be converted")

    success_count = 0
    error_count = 0

    for conversion in CONVERSIONS:
        source = conversion["source"]
        target = conversion["target"]
        if not isinstance(source, str) or not isinstance(target, str):
            logger.error("Invalid conversion entry: source and target must be strings")
            error_count += 1
            continue

        if not os.path.exists(source):
            logger.warning("Source file not found: %s", source)
            error_count += 1
            continue

        if dry_run:
            logger.info("Would convert: %s -> %s", source, target)
            success_count += 1
        else:
            try:
                converter.convert_file(source, target)
                logger.info("Converted: %s -> %s", source, target)
                success_count += 1
            except (FileNotFoundError, PermissionError, OSError, ValueError) as e:
                logger.error("Failed to convert %s: %s", source, e)
                error_count += 1

    return error_count == 0


def main() -> None:
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        sys.exit(0)

    success = convert_all(dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
