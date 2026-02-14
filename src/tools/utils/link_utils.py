"""Shared link and URL utilities for check scripts.

This module centralizes link-extraction patterns, URL classification,
and path-resolution helpers used by both ``check_links`` and
``check_site_health``.

Design by Contract:
    - All public functions validate their inputs via preconditions.
    - Return values are deterministic and well-documented.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urldefrag

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
