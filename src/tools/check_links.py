"""Extract and validate links from HTML and Markdown files.

This tool scans files for both Markdown-style [text](url) links and
HTML href="url" links, then validates that internal links resolve to
existing files and external links are properly formatted.

Usage:
    python check_links.py <file_path>

Example:
    python check_links.py docs/articles/my-article.html
"""

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

from src.core.contracts import require
from src.tools.utils import setup_logging
from src.tools.utils.link_utils import (
    ALL_LINK_PATTERNS,
    normalize_internal_url,
    path_exists_in_search_roots,
    resolve_relative_path,
)

logger = logging.getLogger(__name__)

logger = setup_logging(__name__, format_string="%(message)s")
SCANNED_EXTENSIONS = {".qmd", ".html"}
SKIP_FILES = {
    "WEBSITE_ENHANCEMENT_RECOMMENDATIONS.md",
    "WEBSITE_MANAGEMENT.md",
    "CONTENT_SHARING_GUIDE.md",
    "QUICK_WINS_IMPLEMENTATION.md",
    "HOUSE_STYLE.md",
    "CONVERSION_GUIDE.md",
    "EMBEDDING_GUIDE.md",
    "CONTRIBUTING.md",
}


@dataclass(frozen=True)
class LinkResolutionContext:
    """Facade for resolving links relative to a project root and source file."""

    root_path: Path
    source_file: Path

    def resolve_target_path(self, url: str) -> Path:
        """Resolve a normalized internal URL to its candidate target path."""
        return _resolve_target_path(root_path=self.root_path, file_path=self.source_file, url=url)

    def path_exists(self, target_path: Path) -> bool:
        """Return whether the target exists in one of the supported search roots."""
        return _path_exists_in_search_roots(root_path=self.root_path, target_path=target_path)

    def _html_candidate_paths(self, target_path: Path) -> tuple[Path, Path, Path]:
        """Return candidate source/generated paths for an HTML target."""
        return (
            target_path.with_suffix(".qmd"),
            target_path.with_suffix(".md"),
            target_path,
        )

    def is_html_target_resolvable(self, target_path: Path) -> bool:
        """Return whether an HTML link maps to a supported source or output artifact."""
        if any(
            self.path_exists(candidate)
            for candidate in self._html_candidate_paths(target_path)
        ):
            return True
        return target_path.is_dir() and self.path_exists(target_path / "index.qmd")

    def is_broken(self, link: str) -> bool:
        """Return True when the link is internal and cannot be resolved."""
        url = _normalize_internal_url(link)
        if url is None:
            return False
        target_path = self.resolve_target_path(url)
        if target_path.suffix == ".html":
            return not self.is_html_target_resolvable(target_path)
        return not self.path_exists(target_path)


def find_links(file_path: Path) -> list[tuple[str, int]]:
    """Extract links and exact source line numbers from a file."""
    require(file_path is not None, "file_path must not be None")
    with open(file_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    links: list[tuple[str, int]] = []
    for line_number, line in enumerate(lines, start=1):
        for pattern in ALL_LINK_PATTERNS:
            links.extend([(match.strip(), line_number) for match in pattern.findall(line)])
    return links


def unique_broken(links: list[tuple[str, int, str]]) -> list[tuple[str, int, str]]:
    """Remove duplicate broken links."""
    seen: set[tuple[str, int, str]] = set()
    unique: list[tuple[str, int, str]] = []
    for link in links:
        if link not in seen:
            unique.append(link)
            seen.add(link)
    return unique


def _should_scan_file(file_path: Path) -> bool:
    """Return whether a file should be scanned for internal links."""
    return not (
        file_path.suffix not in SCANNED_EXTENSIONS
        or "node_modules" in str(file_path)
        or "_site" in str(file_path)
        or ".git" in str(file_path)
        or "archive" in str(file_path)
        or "docs" in str(file_path)
        or "content" in str(file_path)
        or "_templates" in str(file_path)
        or ".jules" in str(file_path)
        or file_path.name in SKIP_FILES
    )


def _normalize_internal_url(link: str) -> str | None:
    """Normalize link and return internal URL or None for skipped links."""
    return normalize_internal_url(link)


def _resolve_target_path(*, root_path: Path, file_path: Path, url: str) -> Path:
    """Resolve a link URL against a source file and root path."""
    return resolve_relative_path(root=root_path, source_file=file_path, url=url)


def _path_exists_in_search_roots(*, root_path: Path, target_path: Path) -> bool:
    """Check for target existence in root, src, and docs prefixes."""
    return path_exists_in_search_roots(root=root_path, target=target_path)


def _is_html_link_resolvable(*, root_path: Path, target_path: Path) -> bool:
    """Check whether an HTML link can map to source or generated files."""
    context = LinkResolutionContext(root_path=root_path, source_file=root_path)
    return context.is_html_target_resolvable(target_path)


def _is_broken_link(*, root_path: Path, file_path: Path, link: str) -> bool:
    """Return True if a link is internal and unresolved."""
    return LinkResolutionContext(root_path=root_path, source_file=file_path).is_broken(link)


def check_links(root_dir: str) -> list[tuple[str, int, str]]:
    """Check for broken internal links in the project."""
    require(len(root_dir) > 0, "root_dir must not be empty")
    root_path = Path(root_dir)
    broken_links: list[tuple[str, int, str]] = []

    logger.info(f"Scanning {root_path}...")

    for file_path in root_path.rglob("*"):
        if not _should_scan_file(file_path):
            continue

        try:
            links = find_links(file_path)
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.exception(f"Error reading {file_path}: {e}")
            continue

        broken_links.extend(
            (str(file_path.relative_to(root_path)), line_num, link)
            for link, line_num in links
            if _is_broken_link(root_path=root_path, file_path=file_path, link=link)
        )

    return unique_broken(broken_links)


if __name__ == "__main__":
    broken = check_links(".")
    if broken:
        logger.info("\nBroken Links Found:")
        for file, line, link in broken:
            logger.info(f"{file}:{line} -> {link}")
        sys.exit(1)
    else:
        logger.info("\nNo broken internal links found.")
