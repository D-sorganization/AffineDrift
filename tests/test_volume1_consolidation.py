"""Regression checks for Volume I source consolidation (#1289)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT = Path(__file__).resolve().parents[1]
BOOK_PAGE = ROOT / "books" / "tangent-space-methods.qmd"
TEXTBOOK_README = ROOT / "articles" / "textbook" / "README.md"
VOLUME_MAIN = ROOT / "articles" / "The_Geometry_of_Motion" / "Volume_I" / "main.tex"
TEXTBOOK_CHAPTERS = ROOT / "articles" / "textbook" / "chapters"
VOLUME_CHAPTERS = ROOT / "articles" / "The_Geometry_of_Motion" / "Volume_I" / "chapters"


def test_books_volume1_page_points_to_canonical_volume_i_sources() -> None:
    """Book page should reference canonical Volume I manuscript paths."""
    text = BOOK_PAGE.read_text(encoding="utf-8")
    assert "articles/textbook/" not in text
    assert "articles/The_Geometry_of_Motion/Volume_I/" in text


def test_textbook_path_is_removed() -> None:
    """Legacy textbook path should be removed now that migration is complete."""
    # The deprecated articles/textbook/ directory was fully removed in #1472.
    # Verify it is gone so we don't accidentally re-introduce it.
    assert not TEXTBOOK_README.exists(), (
        "articles/textbook/README.md should not exist; "
        "the directory was removed as part of the deprecation migration"
    )


def test_volume_i_main_uses_shared_geometry_bibliography() -> None:
    """Canonical Volume I main manuscript should use shared bibliography."""
    text = VOLUME_MAIN.read_text(encoding="utf-8")
    assert r"\bibliography{../geometry_of_motion}" in text


def test_volume_i_chapters_have_1_to_1_chapter_coverage() -> None:
    """Canonical Volume I should cover every chapter mirrored in transition tree."""
    for textbook_file in sorted(TEXTBOOK_CHAPTERS.glob("ch*.tex")):
        volume_file = VOLUME_CHAPTERS / textbook_file.name
        assert volume_file.exists(), f"Missing canonical chapter file: {volume_file}"
