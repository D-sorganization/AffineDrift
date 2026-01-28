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

import sys
from pathlib import Path
from typing import Any, cast
from urllib.parse import urldefrag

from bs4 import BeautifulSoup

# Add project root to sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.tools.utils import setup_logging

logger = setup_logging(__name__)

DOCS_DIR = Path("docs")


def check_site_health() -> None:
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

        except Exception as e:
            logger.error("Error processing %s: %s", file_path, e)

    # Report Broken Links
    has_errors = False
    if broken_links:
        logger.error("Found %d broken links:", len(broken_links))
        for link in broken_links:
            logger.error(
                "  %s -> %s (href: %s, text: %s)",
                link["source"],
                link["target"],
                link["href"],
                link["text"],
            )
        has_errors = True
    else:
        logger.info("No broken links found")

    # Report Orphaned Files
    if orphaned_files:
        logger.warning("Found %d orphaned files:", len(orphaned_files))
        for orphaned in sorted(orphaned_files):
            logger.warning("  %s", orphaned)
        # Don't fail on orphaned files - they're just warnings
    else:
        logger.info("No orphaned files found")

    if has_errors:
        sys.exit(1)


if __name__ == "__main__":
    check_site_health()
