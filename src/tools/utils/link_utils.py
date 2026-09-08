"""Shared link and URL utilities for check scripts.

This module centralizes link-extraction patterns, URL classification,
and path-resolution helpers used by both ``check_links`` and
``check_site_health``.

Design by Contract:
    - All public functions validate their inputs via preconditions.
    - Return values are deterministic and well-documented.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from urllib.parse import unquote, urldefrag

from src.core.contracts import require

logger = logging.getLogger(__name__)

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
    # Treat LaTeX command targets from math expressions (e.g., [f](\x))
    # as non-links; they are not navigable website URLs.
    if stripped.startswith("\\"):
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


#: Quarto ``{{< include path >}}`` shortcode (path captured without quotes)
INCLUDE_SHORTCODE_PATTERN: re.Pattern[str] = re.compile(r'\{\{<\s*include\s+"?([^">\s]+)"?\s*>\}\}')

#: A ``## Related Articles`` (or ``###``) section heading
RELATED_HEADING_PATTERN: re.Pattern[str] = re.compile(
    r"^#{2,4}\s+Related Articles\s*$", re.MULTILINE
)

#: Any Markdown heading line
HEADING_PATTERN: re.Pattern[str] = re.compile(r"^(#{1,6})\s+(.*?)\s*$")

#: Inner heading of the canonical component (does not end the section)
SEE_ALSO_TEXT: str = "See Also"

#: Suffixes that mark a link target as a rendered site page
PAGE_SUFFIXES: tuple[str, ...] = (".html", ".qmd", ".md")


def find_links(file_path: Path) -> list[tuple[str, int]]:
    """Extract links and exact source line numbers from a file.

    Args:
        file_path: The file to scan for markdown and HTML links.

    Returns:
        A list of ``(url, line_number)`` tuples in document order.

    Raises:
        AssertionError: If ``file_path`` is None (contract).
    """
    require(file_path is not None, "file_path must not be None")
    with open(file_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    links: list[tuple[str, int]] = []
    for line_number, line in enumerate(lines, start=1):
        for pattern in ALL_LINK_PATTERNS:
            for match in pattern.findall(line):
                links.append((match.strip(), line_number))
    return links


def find_include_paths(text: str) -> list[str]:
    """Return the include targets of ``{{< include path >}}`` shortcodes.

    Args:
        text: The text of the including document.

    Returns:
        Include target paths in order of appearance (may be relative).
    """
    return [match.group(1) for match in INCLUDE_SHORTCODE_PATTERN.finditer(text)]


def extract_related_section_links(text: str) -> list[str]:
    """Extract link URLs from canonical ``Related Articles`` sections.

    The canonical component (issue #3897) is a ``## Related Articles``
    heading whose callout body carries the links; an inner ``## See Also``
    heading does not end the section. Links from every occurrence are
    concatenated in document order.

    Args:
        text: The full text of a rendered source page.

    Returns:
        Raw link URLs found inside Related Articles sections.
    """
    urls: list[str] = []
    lines = text.splitlines()
    in_section = False
    for line in lines:
        heading = HEADING_PATTERN.match(line)
        if heading:
            if in_section and heading.group(2).strip() == SEE_ALSO_TEXT:
                continue
            in_section = bool(RELATED_HEADING_PATTERN.match(line))
            continue
        if in_section:
            urls.extend(MARKDOWN_LINK_PATTERN.findall(line))
    return urls


def html_target_resolvable(*, root: Path, target: Path) -> bool:
    """Check whether an ``.html`` link target maps to renderable source.

    Args:
        root: The project root directory.
        target: The resolved target path (``.html`` suffix).

    Returns:
        True if a ``.qmd``/``.md`` source, the raw target, or an
        ``index.qmd`` under the target directory exists.
    """
    for candidate in (target.with_suffix(".qmd"), target.with_suffix(".md"), target):
        if path_exists_in_search_roots(root=root, target=candidate):
            return True
    return target.is_dir() and (target / "index.qmd").exists()


def internal_link_resolvable(*, root: Path, source_file: Path, url: str) -> bool:
    """Return True when an internal link resolves from its source context.

    Mirrors the historical ``check_links._is_broken_link`` semantics:
    ``.html`` targets may map to ``.qmd``/``.md`` sources; all other
    targets must exist under the root, ``src/``, or ``docs/`` search trees.

    Args:
        root: The project root directory.
        source_file: The file whose directory the URL is relative to.
        url: The already-normalized internal URL.

    Returns:
        True if the link target resolves.
    """
    target = resolve_relative_path(root=root, source_file=source_file, url=url)
    if target.suffix == ".html":
        return html_target_resolvable(root=root, target=target)
    return path_exists_in_search_roots(root=root, target=target)


def page_target_key(*, root: Path, source_file: Path, url: str) -> str | None:
    """Map a link to the canonical page key it renders to, if any.

    Resolution follows browser semantics: the URL is joined against the
    source directory, over-traversal above the root is clamped, and the
    target is normalized to a ``.qmd``/``.md`` source key relative to the
    root (``.html`` targets map onto their source, directory targets onto
    their ``index.qmd``).

    Args:
        root: The project root directory.
        source_file: The file containing the link.
        url: The already-normalized internal URL.

    Returns:
        The root-relative POSIX page key, or None when the target does not
        exist as a rendered page.
    """
    parts: list[str] = []
    if url.startswith("/"):
        parts = url.lstrip("/").split("/")
    else:
        for part in (*source_file.parent.parts, *url.split("/")):
            if part == "..":
                if parts:
                    parts.pop()
            elif part not in ("", "."):
                parts.append(part)
    candidate = root.joinpath(*parts)
    return page_key_for_target(root=root, target=candidate)


def page_key_for_target(*, root: Path, target: Path) -> str | None:
    """Return the canonical page key for a resolved target, if it exists.

    Args:
        root: The project root directory.
        target: A candidate target path (any suffix).

    Returns:
        Root-relative POSIX key of the existing ``.qmd``/``.md`` source,
        else None.
    """
    stem = target.with_suffix("") if target.suffix else target
    for suffix in (".qmd", ".md"):
        candidate = stem.with_suffix(suffix) if target.suffix else stem / f"index{suffix}"
        if candidate.exists() and candidate.is_relative_to(root):
            return candidate.relative_to(root).as_posix()
    return None
