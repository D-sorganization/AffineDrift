#!/usr/bin/env python3
"""Utility CLI for synchronizing the top navigation across legacy HTML files."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from src.tools.utils import setup_logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

NEW_NAV = dedent(
    """
    <ul class="nav-links">
        <li><a href="index.html">Affine Drift</a></li>
        <li><a href="articles.html">Articles</a></li>
        <li><a href="research-reviews.html">Reviews</a></li>
        <li><a href="resources.html">Resources</a></li>
        <li><a href="book-reviews.html">Book Reviews</a></li>
        <li><a href="daydreams-doodles.html">Daydreams & Doodles</a></li>
        <li><a href="contact.html">Contact</a></li>
        <li><a href="about.html">About</a></li>
    </ul>
    """,
).strip()

PAGES_TO_UPDATE: tuple[str, ...] = (
    "book-reviews.html",
    "contact.html",
    "daydreams-doodles.html",
    "modelling.html",
    "research-reviews.html",
    "theory-part1.html",
    "theory-part2.html",
    "theory-part3.html",
    "theory-part4.html",
    "theory-part5.html",
    "theory.html",
    "wscg-research.html",
)

LOGO_LEGACY = "logo/AffineDriftLogo.png"
LOGO_UPDATED = "logo/Logo Transparent/1.png"
NAV_LIST_PATTERN = re.compile(
    r'(?P<indent>[ \t]*)<ul class="nav-links">.*?</ul>',
    re.DOTALL,
)
RAW_NAV_PATTERN = re.compile(r"<nav(?![^>]*class=)", re.IGNORECASE)
LOGGER = setup_logging(__name__, format_string="%(message)s")


def _ensure_top_nav(html: str) -> str:
    """Attach the `top-nav` class to bare <nav> tags for styling consistency."""

    def _inject_class(_: re.Match[str]) -> str:
        """Inject the top-nav class."""
        return '<nav class="top-nav">'

    return RAW_NAV_PATTERN.sub(_inject_class, html)


def _replace_logo_path(html: str) -> str:
    """Point legacy logo references at the optimized transparent logo asset."""
    return html.replace(LOGO_LEGACY, LOGO_UPDATED)


def _resolve_targets(pages: Iterable[str | Path]) -> list[Path]:
    """Normalize CLI arguments into concrete paths."""
    return [Path(page).resolve() for page in pages]


def _render_nav(match: re.Match[str], nav_markup: str = NEW_NAV) -> str:
    """Apply the supplied navigation markup while preserving indentation."""
    indent = match.group("indent")
    return "\n".join(f"{indent}{line}" for line in nav_markup.splitlines())


def update_navigation(file_path: Path, nav_markup: str = NEW_NAV) -> bool:
    """Update the navigation list, nav class, and logo references for a file.

    :param file_path: HTML file whose navigation needs to be patched.
    :param nav_markup: Replacement markup for the navigation <ul>.
    :returns: True if the file was updated, False if no changes were required.
    :raises ValueError: If the navigation <ul> block cannot be located.
    """
    original = file_path.read_text(encoding="utf-8")
    if NAV_LIST_PATTERN.search(original) is None:
        message = f'No <ul class="nav-links"> block found in "{file_path}".'
        raise ValueError(message)

    updated = NAV_LIST_PATTERN.sub(
        lambda match: _render_nav(match, nav_markup),
        original,
        count=1,
    )

    updated = _ensure_top_nav(updated)
    updated = _replace_logo_path(updated)

    if updated == original:
        return False

    file_path.write_text(updated, encoding="utf-8")
    return True


def main(pages: Sequence[str] | None = None) -> int:
    """CLI entry point for batch-updating navigation markup."""
    targets = _resolve_targets(pages or PAGES_TO_UPDATE)
    exit_code = 0
    for target in targets:
        if not target.exists():
            LOGGER.error("✗ Not found: %s", target)
            exit_code = 1
            continue

        try:
            changed = update_navigation(target)
        except ValueError:
            LOGGER.exception("✗ Failed to update %s", target)
            exit_code = 1
            continue

        status = "✓ Updated" if changed else "• Already up to date"
        LOGGER.info("%s %s", status, target)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
