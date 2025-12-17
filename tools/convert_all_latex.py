#!/usr/bin/env python3
"""
Batch LaTeX to HTML Converter for AffineDrift
Converts all LaTeX article files to HTML and updates root-level HTML files
"""

import os
import sys

from latex_to_html import LaTeXToHTMLConverter

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
    """Convert all LaTeX files to HTML"""
    converter = LaTeXToHTMLConverter()

    print("=" * 70)
    print("AffineDrift LaTeX to HTML Batch Converter")
    print("=" * 70)
    print()

    if dry_run:
        print("DRY RUN MODE - No files will be modified")
        print()

    success_count = 0
    error_count = 0

    for conversion in CONVERSIONS:
        source = conversion["source"]
        target = conversion["target"]
        if not isinstance(source, str) or not isinstance(target, str):
            print(f"  ✗ Invalid conversion entry: {conversion}")
            error_count += 1
            continue

        print(f"Processing: {source}")
        print(f"  -> Target: {target}")

        if not os.path.exists(source):
            print(f"  ✗ Source file not found: {source}")
            error_count += 1
            continue

        if dry_run:
            print("  ✓ Would convert (dry run)")
            success_count += 1
        else:
            try:
                converter.convert_file(source, target)
                success_count += 1
            except Exception as e:
                print(f"  ✗ Error converting: {e}")
                error_count += 1

        print()

    print("=" * 70)
    print("Conversion Summary:")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    print("=" * 70)

    return error_count == 0


def main() -> None:
    """Main entry point"""
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python3 convert_all_latex.py [--dry-run|-n] [--help|-h]")
        print()
        print("Options:")
        print("  --dry-run, -n  : Preview what would be converted without making changes")
        print("  --help, -h     : Show this help message")
        sys.exit(0)

    success = convert_all(dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
