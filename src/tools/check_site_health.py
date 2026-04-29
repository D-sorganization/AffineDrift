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
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag

from bs4 import BeautifulSoup, Tag

from src.core.contracts import require
from src.tools.utils import setup_logging
from src.tools.utils.cli_contracts import ensure_existing_dir, parse_csv_enum
from src.tools.utils.link_utils import is_external_url, is_fragment_only

logger = logging.getLogger(__name__)

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


@dataclass(frozen=True)
class SiteHealthLinkCandidate:
    """Narrow view of an internal anchor link during site-health scans."""

    href: str
    target: Path
    text: str

    @classmethod
    def from_anchor(
        cls,
        *,
        anchor: Tag,
        source_file: Path,
        docs_dir: Path,
        ignore_quarto_alternate_formats: bool,
    ) -> "SiteHealthLinkCandidate | None":
        """Build a candidate from a BeautifulSoup anchor when it is actionable."""
        if ignore_quarto_alternate_formats and is_inside_quarto_alternate_formats(anchor):
            return None

        href = _anchor_href(anchor)
        if not href or is_external_url(href) or is_fragment_only(href):
            return None

        target_rel_path = _resolve_internal_target(
            source_file=source_file,
            href=href,
            docs_dir=docs_dir,
        )
        if target_rel_path is None:
            return None

        return cls(
            href=href,
            target=target_rel_path,
            text=_anchor_text(anchor),
        )

    def to_broken_link_record(self, *, source_file: Path) -> BrokenLinkRecord:
        """Convert the candidate to the public broken-link record."""
        return BrokenLinkRecord(
            source=str(source_file),
            target=str(self.target),
            href=self.href,
            text=self.text,
        )


def parse_fail_on(raw: str) -> set[str]:
    """Parse --fail-on input into a normalized set."""
    return parse_csv_enum(
        raw,
        allowed={"broken", "orphaned"},
        aliases={"all": {"broken", "orphaned"}},
        value_name="--fail-on value",
    )


def _tag_classes(tag: Tag | None) -> list[str]:
    """Return the class list for a tag-like node."""
    if tag is None:
        return []
    classes = tag.get("class", [])
    return classes if isinstance(classes, list) else []


def _anchor_href(anchor: Tag) -> str:
    """Return the normalized href string for an anchor."""
    href_value = anchor.get("href")
    return str(href_value) if href_value is not None else ""


def _anchor_text(anchor: Tag) -> str:
    """Return a short, stable text summary for an anchor."""
    return anchor.get_text(strip=True)[:50]


def is_inside_quarto_alternate_formats(tag: Any) -> bool:
    """Return True when the tag sits inside Quarto's alternate-format nav."""
    current = tag if isinstance(tag, Tag) else None
    while current is not None:
        if "quarto-alternate-formats" in _tag_classes(current):
            return True
        parent = getattr(current, "parent", None)
        current = parent if isinstance(parent, Tag) else None
    return False


def _collect_html_files(*, docs_dir: Path) -> list[Path]:
    """Return all HTML files relative to docs directory."""
    return [
        full_path.relative_to(docs_dir)
        for full_path in docs_dir.rglob("*.html")
        if not any(part in IGNORED_ARTIFACT_DIRS for part in full_path.relative_to(docs_dir).parts)
    ]


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
        if not isinstance(anchor, Tag):
            continue
        candidate = SiteHealthLinkCandidate.from_anchor(
            anchor=anchor,
            source_file=file_path,
            docs_dir=docs_dir,
            ignore_quarto_alternate_formats=ignore_quarto_alternate_formats,
        )
        if candidate is None:
            continue
        if candidate.target not in all_files:
            broken_links.append(candidate.to_broken_link_record(source_file=file_path))
        else:
            referenced_targets.add(candidate.target)
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
