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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast
from urllib.parse import urldefrag

from bs4 import BeautifulSoup

from src.core.contracts import require
from src.tools.utils import setup_logging
from src.tools.utils.cli_contracts import ensure_existing_dir, parse_csv_enum
from src.tools.utils.link_utils import is_external_url, is_fragment_only

logger = setup_logging(__name__)

DOCS_DIR = Path("docs")
ENTRY_POINT_NAMES = {"index.html", "404.html", "daydreams-doodles.html", "offline.html"}
ENTRY_POINT_PATHS = {"articles/ux-verification-test.html"}
IGNORED_ARTIFACT_DIRS = {"coverage", "lcov-report"}


@dataclass(frozen=True)
class BrokenLinkRecord:
    """Structured broken-link finding."""

    source: str
    target: str
    href: str
    text: str


def parse_fail_on(raw: str) -> set[str]:
    """Parse --fail-on input into a normalized set."""
    return parse_csv_enum(
        raw,
        allowed={"broken", "orphaned"},
        aliases={"all": {"broken", "orphaned"}},
        value_name="--fail-on value",
    )


def is_inside_quarto_alternate_formats(tag: Any) -> bool:
    """Return True when the tag sits inside Quarto's alternate-format nav."""
    current = tag
    while current is not None:
        classes = current.get("class", []) if hasattr(current, "get") else []
        if isinstance(classes, list) and "quarto-alternate-formats" in classes:
            return True
        current = getattr(current, "parent", None)
    return False


def _collect_html_files(*, docs_dir: Path) -> list[Path]:
    """Return all HTML files relative to docs directory."""
    html_files: list[Path] = []
    for full_path in docs_dir.rglob("*.html"):
        relative = full_path.relative_to(docs_dir)
        if any(part in IGNORED_ARTIFACT_DIRS for part in relative.parts):
            continue
        html_files.append(relative)
    return html_files


def _collect_all_files(*, docs_dir: Path) -> set[Path]:
    """Return all files relative to docs directory."""
    files: set[Path] = set()
    for full_path in docs_dir.rglob("*"):
        if not full_path.is_file():
            continue
        relative = full_path.relative_to(docs_dir)
        if any(part in IGNORED_ARTIFACT_DIRS for part in relative.parts):
            continue
        files.add(relative)
    return files


def _log_site_map(html_files: list[Path]) -> None:
    """Log a lightweight sitemap summary."""
    top_level_pages = sorted([f for f in html_files if len(f.parts) == 1])
    logger.info("Found %d top-level pages", len(top_level_pages))

    subdirs = sorted({f.parent for f in html_files if len(f.parts) > 1})
    for subdir in subdirs:
        pages: list[str] = sorted([f.name for f in html_files if f.parent == subdir])
        logger.debug("Directory %s contains %d pages", subdir, len(pages))


def _initial_orphaned_files(html_files: list[Path]) -> set[Path]:
    """Build the initial orphan candidate set."""
    orphaned_files = {
        file_path
        for file_path in html_files
        if file_path.name not in ENTRY_POINT_NAMES and str(file_path) not in ENTRY_POINT_PATHS
    }
    return {file_path for file_path in orphaned_files if "archive" not in file_path.parts}


def _resolve_internal_target(*, source_file: Path, href: str, docs_dir: Path) -> Path | None:
    """Resolve internal href to a docs-relative path when possible."""
    target_url, _anchor = urldefrag(href)
    if not target_url:
        return None

    current_dir = source_file.parent
    try:
        resolved_target = (docs_dir / current_dir / target_url).resolve()
        if not resolved_target.is_relative_to(docs_dir.resolve()):
            return None
        return resolved_target.relative_to(docs_dir.resolve())
    except (ValueError, FileNotFoundError):
        return None


def _find_broken_links_for_file(
    *,
    docs_dir: Path,
    file_path: Path,
    all_files: set[Path],
    ignore_quarto_alternate_formats: bool,
) -> tuple[list[BrokenLinkRecord], set[Path]]:
    """Parse a single HTML file and collect broken-link records."""
    full_path = docs_dir / file_path
    broken_links: list[BrokenLinkRecord] = []
    referenced_targets: set[Path] = set()
    with full_path.open(encoding="utf-8") as file_handle:
        soup = BeautifulSoup(file_handle, "html.parser")

    for anchor in soup.find_all("a", href=True):
        if ignore_quarto_alternate_formats and is_inside_quarto_alternate_formats(anchor):
            continue

        href_value = cast("Any", anchor).get("href")
        href = str(href_value) if href_value is not None else ""
        if not href:
            continue
        if is_external_url(href) or is_fragment_only(href):
            continue

        target_rel_path = _resolve_internal_target(
            source_file=file_path, href=href, docs_dir=docs_dir
        )
        if target_rel_path is None:
            continue

        if target_rel_path not in all_files:
            broken_links.append(
                BrokenLinkRecord(
                    source=str(file_path),
                    target=str(target_rel_path),
                    href=href,
                    text=anchor.get_text(strip=True)[:50],
                ),
            )
        else:
            referenced_targets.add(target_rel_path)
    return broken_links, referenced_targets


def _report_findings(
    *, broken_links: list[BrokenLinkRecord], orphaned_files: set[Path], fail_on: set[str]
) -> int:
    """Emit logs and decide exit code based on selected fail criteria."""
    has_errors = False
    if broken_links:
        logger.warning("Found %d broken links:", len(broken_links))
        for link in broken_links:
            logger.warning(
                "  %s -> %s (href: %s, text: %s)",
                link.source,
                link.target,
                link.href,
                link.text,
            )
        if "broken" in fail_on:
            has_errors = True
    else:
        logger.info("No broken links found")

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
    return 1 if has_errors else 0


def check_site_health(
    *,
    fail_on: set[str],
    ignore_quarto_alternate_formats: bool,
    docs_dir: Path | None = None,
) -> int:
    """Scans the docs directory for HTML files and verifies internal links.
    Generates a site map and reports broken links and orphaned files.
    """
    active_docs_dir = docs_dir if docs_dir is not None else DOCS_DIR
    require(active_docs_dir.exists(), "docs directory must exist")
    html_files = _collect_html_files(docs_dir=active_docs_dir)
    all_files = _collect_all_files(docs_dir=active_docs_dir)
    _log_site_map(html_files)
    broken_links: list[BrokenLinkRecord] = []
    orphaned_files = _initial_orphaned_files(html_files)

    for file_path in html_files:
        try:
            file_broken_links, referenced_targets = _find_broken_links_for_file(
                docs_dir=active_docs_dir,
                file_path=file_path,
                all_files=all_files,
                ignore_quarto_alternate_formats=ignore_quarto_alternate_formats,
            )
            broken_links.extend(file_broken_links)
            for target_path in referenced_targets:
                if target_path in orphaned_files:
                    orphaned_files.remove(target_path)
        except (ConnectionError, TimeoutError, OSError) as exc:
            logger.error("Error processing %s: %s", file_path, exc)

    return _report_findings(
        broken_links=broken_links,
        orphaned_files=orphaned_files,
        fail_on=fail_on,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for site-health checks."""
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
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Directory containing rendered HTML files to validate.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run site-health checks from CLI args."""
    args = parse_args(argv)
    try:
        fail_on = parse_fail_on(args.fail_on)
        docs_dir = ensure_existing_dir(args.docs_dir, value_name="--docs-dir")
    except ValueError as exc:
        logger.error("%s", exc)
        return 2
    return check_site_health(
        fail_on=fail_on,
        ignore_quarto_alternate_formats=not args.include_quarto_alternate_formats,
        docs_dir=docs_dir,
    )


if __name__ == "__main__":
    sys.exit(main())
