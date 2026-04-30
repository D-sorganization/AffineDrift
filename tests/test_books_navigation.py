"""Regression tests for the Books section website information architecture."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

REPO_ROOT = Path(__file__).resolve().parents[1]
QUARTO_CONFIG = REPO_ROOT / "_quarto.yml"
BOOKS_DIR = REPO_ROOT / "books"

EXPECTED_BOOK_PAGES = (
    "index.qmd",
    "tangent-space-methods.qmd",
    "control-is-motion.qmd",
    "biomechanics-biology-to-systems.qmd",
    "human-motor-control.qmd",
)


def test_quarto_render_includes_books_folder() -> None:
    """Quarto project render list should include the Books folder."""
    quarto = QUARTO_CONFIG.read_text(encoding="utf-8")
    assert "books/**/*.qmd" in quarto


def test_navbar_includes_books_tab() -> None:
    """Book-related pages are linked from the navbar.

    Issue #2343: Add books section to top-level navigation now that the four
    book pages are rendered and expected to be navigable.
    """
    quarto = QUARTO_CONFIG.read_text(encoding="utf-8")
    assert "books/index.html" in quarto


def test_navbar_includes_tools_and_repositories() -> None:
    """Program/tools and repository hubs should be present in navbar links.

    Issue #2343 identified these rendered sections as missing from navigation.
    """
    quarto = QUARTO_CONFIG.read_text(encoding="utf-8")
    assert "pages/tools.html" in quarto
    assert "repositories/repositories.html" in quarto


def test_books_pages_exist_and_use_shared_sidebar() -> None:
    """Books hub and the 4 book pages should exist and bind to shared sidebar."""
    for relative_name in EXPECTED_BOOK_PAGES:
        page_path = BOOKS_DIR / relative_name
        assert page_path.exists(), f"Missing Books page: {relative_name}"
        page_text = page_path.read_text(encoding="utf-8")
        assert "sidebar: books-nav" in page_text


def test_books_series_page_links_to_each_book() -> None:
    """Books series landing page should link to all four main books."""
    series_page = (BOOKS_DIR / "index.qmd").read_text(encoding="utf-8")
    assert "tangent-space-methods.html" in series_page
    assert "control-is-motion.html" in series_page
    assert "biomechanics-biology-to-systems.html" in series_page
    assert "human-motor-control.html" in series_page
