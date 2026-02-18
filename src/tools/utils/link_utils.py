"""Shared link and URL utilities for check scripts.

This module centralizes link-extraction patterns, URL classification,
path-resolution helpers, and broken-link detection used by both
``check_links`` and ``check_site_health``.

Design by Contract:
    - All public functions validate their inputs via preconditions.
    - Return values are deterministic and well-documented.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar
from urllib.parse import unquote, urldefrag

_T = TypeVar("_T")

# ─── Compiled regex patterns for link extraction ────────────────

#: Markdown-style links: [text](url) excluding images
MARKDOWN_LINK_PATTERN: re.Pattern[str] = re.compile(r"(?<!!)\[[^\]]*]\(([^)]+)\)")

#: Markdown-style images: ![alt](url)
MARKDOWN_IMAGE_PATTERN: re.Pattern[str] = re.compile(r"!\[[^\]]*]\(([^)]+)\)")

#: HTML href attributes: href="url" or href='url'
HTML_HREF_PATTERN: re.Pattern[str] = re.compile(r'href=["\'](.*?)["\']')

#: HTML src attributes: src="url" or src='url'
HTML_SRC_PATTERN: re.Pattern[str] = re.compile(r'src=["\'](.*?)["\']')

#: All patterns in a tuple for convenient iteration
ALL_LINK_PATTERNS: tuple[re.Pattern[str], ...] = (
    MARKDOWN_LINK_PATTERN,
    MARKDOWN_IMAGE_PATTERN,
    HTML_HREF_PATTERN,
    HTML_SRC_PATTERN,
)

#: URL prefixes that indicate external (non-local) links
EXTERNAL_PREFIXES: tuple[str, ...] = (
    "http:",
    "https:",
    "mailto:",
    "tel:",
    "ftp:",
)

#: Directory path segments that should be skipped when scanning for links
SKIP_DIRECTORIES: frozenset[str] = frozenset(
    {
        "node_modules",
        "_site",
        ".git",
        ".jules",
    }
)


# ─── Data classes ───────────────────────────────────────────────


@dataclass(frozen=True)
class BrokenLinkRecord:
    """Structured broken-link finding.

    Attributes:
        source: The file containing the broken link (relative path string).
        target: The resolved target that could not be found.
        href: The original href or URL string from the markup.
        text: Display text of the link (truncated for readability).
        line: Source line number where the link was found, or 0 if unknown.
    """

    source: str
    target: str
    href: str
    text: str
    line: int = 0


# ─── URL classification helpers ─────────────────────────────────


def is_external_url(url: str) -> bool:
    """Return True if the URL points to an external resource.

    Args:
        url: The URL string to classify.

    Returns:
        True if the URL starts with an external protocol prefix.
    """
    return url.startswith(EXTERNAL_PREFIXES)


def is_fragment_only(url: str) -> bool:
    """Return True if the URL is a same-page anchor (#fragment).

    Args:
        url: The URL string to classify.

    Returns:
        True if the URL starts with '#'.
    """
    return url.startswith("#")


def strip_fragment(url: str) -> str:
    """Remove the fragment (#section) from a URL.

    Args:
        url: The URL string to process.

    Returns:
        The URL without any fragment identifier.

    >>> strip_fragment("page.html#section-1")
    'page.html'
    >>> strip_fragment("#anchor")
    ''
    >>> strip_fragment("page.html")
    'page.html'
    """
    defragged, _ = urldefrag(url)
    return defragged


def normalize_internal_url(url: str) -> str | None:
    """Normalize a URL for internal link checking.

    Returns None for URLs that should be skipped (external, template
    variables, fragments, or trivially short).

    Args:
        url: The raw URL extracted from markup.

    Returns:
        The decoded, fragment-stripped URL, or None if it should be skipped.
    """
    stripped = strip_fragment(url)
    if not stripped:
        return None
    if is_external_url(stripped):
        return None
    if "${" in stripped or stripped == "...":
        return None
    if len(stripped) == 1:
        return None
    return unquote(stripped)


# ─── Path resolution and existence helpers ──────────────────────


def resolve_relative_path(*, root: Path, source_file: Path, url: str) -> Path:
    """Resolve a relative or absolute URL against a source file and root.

    Absolute URLs (starting with '/') resolve relative to root.
    Relative URLs resolve relative to the source file's directory.

    Args:
        root: The project root directory.
        source_file: The file containing the link.
        url: The (already normalized) URL to resolve.

    Returns:
        The resolved Path.
    """
    if url.startswith("/"):
        return root / url.lstrip("/")
    return source_file.parent / url


def path_exists_in_search_roots(*, root: Path, target: Path) -> bool:
    """Check for file existence in root, src/, and docs/ search roots.

    Args:
        root: The project root directory.
        target: The target path to check.

    Returns:
        True if the file exists in any of the search root variations.
    """
    if target.exists():
        return True
    if not target.is_relative_to(root):
        return False
    relative = target.relative_to(root)
    return (root / "src" / relative).exists() or (root / "docs" / relative).exists()


def is_html_link_resolvable(*, root: Path, target: Path) -> bool:
    """Check whether an HTML link can map to source or generated files.

    For ``.html`` targets, checks for corresponding ``.qmd`` or ``.md``
    source files, and also accepts directories containing ``index.qmd``.

    Args:
        root: The project root directory.
        target: The resolved target path (with .html suffix).

    Returns:
        True if the HTML target resolves to an existing resource.
    """
    p_qmd = target.with_suffix(".qmd")
    p_md = target.with_suffix(".md")
    if path_exists_in_search_roots(root=root, target=p_qmd):
        return True
    if path_exists_in_search_roots(root=root, target=p_md):
        return True
    if path_exists_in_search_roots(root=root, target=target):
        return True
    return target.is_dir() and (target / "index.qmd").exists()


# ─── Scanning and filtering helpers ─────────────────────────────


def should_skip_path(file_path: Path) -> bool:
    """Return True if a file path contains a directory that should be skipped.

    Checks whether any part of the path matches the common skip directories
    (node_modules, _site, .git, .jules). This is a shared subset of the
    skip logic used by both check_links and check_site_health.

    Args:
        file_path: The file path to check.

    Returns:
        True if the path should be skipped.
    """
    parts = set(file_path.parts)
    return bool(parts & SKIP_DIRECTORIES)


def extract_links_from_lines(
    lines: Sequence[str],
    patterns: tuple[re.Pattern[str], ...] = ALL_LINK_PATTERNS,
) -> list[tuple[str, int]]:
    """Extract links and line numbers from text lines using regex patterns.

    Args:
        lines: The text lines to scan (0-indexed sequence, line numbers
            are reported 1-indexed).
        patterns: Regex patterns to apply; each must have one capture group.

    Returns:
        A list of (link_url, line_number) tuples.
    """
    links: list[tuple[str, int]] = []
    for line_number, line in enumerate(lines, start=1):
        for pattern in patterns:
            for match in pattern.findall(line):
                links.append((match.strip(), line_number))
    return links


def unique_items(items: Sequence[_T]) -> list[_T]:  # noqa: UP047
    """Remove duplicates from a sequence while preserving order.

    Args:
        items: The sequence to deduplicate.

    Returns:
        A list with duplicates removed, in original order.
    """
    seen: set[_T] = set()
    unique: list[_T] = []
    for item in items:
        if item not in seen:
            unique.append(item)
            seen.add(item)
    return unique


# ─── Unified broken-link detection ─────────────────────────────


def is_broken_internal_link(*, root: Path, source_file: Path, link: str) -> bool:
    """Return True if a link is internal and cannot be resolved.

    Normalizes the URL, resolves it against the source file's directory,
    and checks for the target's existence. HTML targets get additional
    checks for corresponding .qmd/.md source files.

    Args:
        root: The project root directory.
        source_file: The file containing the link.
        link: The raw link URL from the markup.

    Returns:
        True if the link is an internal link that does not resolve.
    """
    url = normalize_internal_url(link)
    if url is None:
        return False
    target_path = resolve_relative_path(root=root, source_file=source_file, url=url)
    if target_path.suffix == ".html":
        return not is_html_link_resolvable(root=root, target=target_path)
    return not path_exists_in_search_roots(root=root, target=target_path)


def find_broken_links_in_file(
    *,
    root: Path,
    file_path: Path,
) -> list[BrokenLinkRecord]:
    """Scan a single file for broken internal links.

    Reads the file, extracts all links using regex patterns, normalizes
    and resolves each link, and returns structured records for those that
    cannot be resolved.

    Args:
        root: The project root directory.
        file_path: The file to scan (absolute path).

    Returns:
        A list of BrokenLinkRecord for each broken internal link found.
    """
    with open(file_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    links = extract_links_from_lines(lines)
    broken: list[BrokenLinkRecord] = []
    for link, line_num in links:
        if is_broken_internal_link(root=root, source_file=file_path, link=link):
            url = normalize_internal_url(link)
            target = resolve_relative_path(root=root, source_file=file_path, url=url or link)
            broken.append(
                BrokenLinkRecord(
                    source=str(file_path.relative_to(root)),
                    target=str(target),
                    href=link,
                    text="",
                    line=line_num,
                )
            )
    return broken
