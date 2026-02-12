"""Verify site health by checking internal links and generating sitemap.

This tool scans the generated HTML files in the docs/ directory to verify
that all internal links resolve to existing files, helping maintain site
integrity after builds.

Usage:
    python check_site_health.py

The script will:
- Find all HTML files in docs/
- Extract and validate internal links
- Report broken or missing links
- Optionally generate a sitemap
"""

import argparse
import sys
from pathlib import Path
from typing import Any, cast
from urllib.parse import urldefrag

from bs4 import BeautifulSoup

from src.tools.utils import setup_logging

logger = setup_logging(__name__)

DOCS_DIR = Path("docs")


def parse_fail_on(raw: str) -> set[str]:
    """Parse --fail-on input into a normalized set."""
    normalized = {item.strip().lower() for item in raw.split(",") if item.strip()}
    aliases = {"all": {"broken", "orphaned"}}
    resolved: set[str] = set()
    for item in normalized:
        if item in aliases:
            resolved.update(aliases[item])
        else:
            resolved.add(item)
    return resolved


def is_inside_quarto_alternate_formats(tag: Any) -> bool:
    """Return True when the tag sits inside Quarto's alternate-format nav."""
    current = tag
    while current is not None:
        classes = current.get("class", []) if hasattr(current, "get") else []
        if isinstance(classes, list) and "quarto-alternate-formats" in classes:
            return True
        current = getattr(current, "parent", None)
    return False


def check_site_health(*, fail_on: set[str], ignore_quarto_alternate_formats: bool) -> int:
    """Scans the docs directory for HTML files and verifies internal links.
    Generates a site map and reports broken links and orphaned files.
    """
    html_files = []
    # Walk the directory
    for full_path in DOCS_DIR.rglob("*.html"):
        rel_path = full_path.relative_to(DOCS_DIR)
        html_files.append(rel_path)

    # Store all known files
    all_files = set()
    for full_path in DOCS_DIR.rglob("*"):
        if full_path.is_file():
            all_files.add(full_path.relative_to(DOCS_DIR))

    # 1. Generate Site Map (List of pages)
    top_level_pages = sorted([f for f in html_files if len(f.parts) == 1])
    logger.info("Found %d top-level pages", len(top_level_pages))

    subdirs = sorted({f.parent for f in html_files if len(f.parts) > 1})
    for d in subdirs:
        pages: list[str] = sorted([f.name for f in html_files if f.parent == d])
        logger.debug("Directory %s contains %d pages", d, len(pages))

    # 2. Check Links
    broken_links = []
    orphaned_files = set(html_files)

    # Files that are always entry points (not orphaned)
    # These include the main index, error pages, and standalone pages
    # that may be accessed directly via URL (e.g., easter eggs, standalone tools)
    entry_point_names = {"index.html", "404.html", "daydreams-doodles.html", "offline.html"}
    entry_point_paths = {"articles/ux-verification-test.html"}
    # Orphan check logic handles Path objects by comparing string representation or Path parts
    orphaned_files = {
        f
        for f in orphaned_files
        if f.name not in entry_point_names and str(f) not in entry_point_paths
    }

    # Exclude archive directories from orphan check
    # Check if "archive" is any part of the path
    orphaned_files = {f for f in orphaned_files if "archive" not in f.parts}

    for file_path in html_files:
        full_path = DOCS_DIR / file_path
        try:
            with full_path.open(encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # Find all links
            for a in soup.find_all("a", href=True):
                if ignore_quarto_alternate_formats and is_inside_quarto_alternate_formats(a):
                    continue

                href_value = cast("Any", a).get("href")
                href = str(href_value) if href_value is not None else ""

                if not href:
                    continue

                if href.startswith(("http:", "https:", "mailto:", "tel:", "ftp:", "#")):
                    continue

                # Strip anchor
                target_url, _anchor = urldefrag(href)

                if not target_url:
                    continue

                # Calculate target path
                # file_path is relative to DOCS_DIR
                # current_dir is relative to DOCS_DIR
                current_dir = file_path.parent
                # target_rel_path is relative to DOCS_DIR
                # We need to resolve ".." and "." manually or using resolve()
                # but resolve needs abs paths.
                # Easier way: (DOCS_DIR / current_dir / target_url).resolve()
                # .relative_to(DOCS_DIR.resolve())
                try:
                    resolved_target = (DOCS_DIR / current_dir / target_url).resolve()
                    # Check if it is inside DOCS_DIR
                    if not resolved_target.is_relative_to(DOCS_DIR.resolve()):
                        # Link points outside docs, maybe valid? But we only check inside docs.
                        continue
                    target_rel_path = resolved_target.relative_to(DOCS_DIR.resolve())
                except (ValueError, FileNotFoundError):
                    # If resolve fails (e.g. file doesn't exist), we construct it logically
                    # but we can't fully trust it if it doesn't exist.
                    # Actually, if it doesn't exist, resolve() might still work
                    # on Path if strictly=False (default since 3.10)
                    # But if we want to check existence, we can just check exist().
                    # Let's try logical path construction first to match `all_files` keys.
                    # However, logical resolution of ".." without file system is tricky.
                    # Let's rely on resolve() which should work if we are careful.
                    continue

                if target_rel_path not in all_files:
                    broken_links.append(
                        {
                            "source": str(file_path),
                            "target": str(target_rel_path),
                            "href": href,
                            "text": a.get_text(strip=True)[:50],
                        },
                    )
                elif target_rel_path in orphaned_files:
                    orphaned_files.remove(target_rel_path)

        except (ConnectionError, TimeoutError, OSError) as e:
            logger.error("Error processing %s: %s", file_path, e)

    # Report Broken Links
    has_errors = False
    if broken_links:
        logger.warning("Found %d broken links:", len(broken_links))
        for link in broken_links:
            logger.warning(
                "  %s -> %s (href: %s, text: %s)",
                link["source"],
                link["target"],
                link["href"],
                link["text"],
            )
        if "broken" in fail_on:
            has_errors = True
    else:
        logger.info("No broken links found")

    # Report Orphaned Files
    if orphaned_files:
        logger.warning("Found %d orphaned files:", len(orphaned_files))
        for orphaned in sorted(orphaned_files):
            logger.warning("  %s", orphaned)
        if "orphaned" in fail_on:
            has_errors = True
    else:
        logger.info("No orphaned files found")

    logger.info(
        "Site health summary: broken_links=%d orphaned_files=%d fail_on=%s",
        len(broken_links),
        len(orphaned_files),
        ",".join(sorted(fail_on)) or "none",
    )

    if has_errors:
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check generated docs site health")
    parser.add_argument(
        "--fail-on",
        default="",
        help="Comma-separated: broken,orphaned,all. Empty means warning-only.",
    )
    parser.add_argument(
        "--include-quarto-alternate-formats",
        action="store_true",
        help="Include links inside Quarto 'Other Formats' blocks in link checks.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    fail_on = parse_fail_on(args.fail_on)
    exit_code = check_site_health(
        fail_on=fail_on,
        ignore_quarto_alternate_formats=not args.include_quarto_alternate_formats,
    )
    sys.exit(exit_code)
