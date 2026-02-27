"""Regression checks for Volume I source consolidation (#1289)."""

from __future__ import annotations

from pathlib import Path

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


def test_textbook_path_has_deprecation_notice() -> None:
    """Legacy textbook path should provide a clear canonical redirect note."""
    text = TEXTBOOK_README.read_text(encoding="utf-8")
    assert "deprecated" in text.lower()
    assert "articles/The_Geometry_of_Motion/Volume_I/main.tex" in text


def test_volume_i_main_uses_shared_geometry_bibliography() -> None:
    """Canonical Volume I main manuscript should use shared bibliography."""
    text = VOLUME_MAIN.read_text(encoding="utf-8")
    assert r"\bibliography{../geometry_of_motion}" in text


def test_volume_i_chapters_are_synchronized_from_transition_tree() -> None:
    """Transition chapter content and canonical chapter content should match."""
    for textbook_file in sorted(TEXTBOOK_CHAPTERS.glob("ch*.tex")):
        volume_file = VOLUME_CHAPTERS / textbook_file.name
        assert volume_file.exists(), f"Missing canonical chapter file: {volume_file}"
        assert textbook_file.read_text(encoding="utf-8") == volume_file.read_text(encoding="utf-8")
