"""Regression checks that GoM book landing pages track the manuscript (#5606)."""

from __future__ import annotations

from pathlib import Path

from src.tools.gom_landing_page_contract import collect_violations

ROOT = Path(__file__).resolve().parents[1]


def test_gom_landing_pages_match_manuscript_contract() -> None:
    """Books/quarto landing pages must align with chapter lists, titles, and section IDs."""
    violations = collect_violations(ROOT)
    assert not violations, "GoM landing drift:\n" + "\n".join(violations)


def test_volume_ii_web_chapter_links_use_manuscript_section_ids() -> None:
    """Volume II per-chapter links must target explicit ids in volume2_content.qmd."""
    landing = (ROOT / "books" / "control-is-motion.qmd").read_text(encoding="utf-8")
    assert "volume2.html#sec-throwing-away-the-target" in landing
    assert "volume2.html#sec-ch-underactuation" in landing
    assert "volume2.html#throwing-away-the-target" not in landing


def test_gom_readme_concordance_matches_books_index() -> None:
    """Manuscript README titles must track the books hub concordance (#5606 F10)."""
    readme = (ROOT / "articles" / "The_Geometry_of_Motion" / "README.md").read_text(
        encoding="utf-8"
    )
    index = (ROOT / "books" / "index.qmd").read_text(encoding="utf-8")
    assert "Volume II: Control Is Motion" in readme
    assert "Volume II: Control Is Motion" in index
    assert "Trajectory and Motor Control" not in readme


def test_volume_v_title_page_uses_series_not_volume_i_heading() -> None:
    """Volume V LaTeX title page must not reuse the Volume I canonical title."""
    tex = (ROOT / "articles" / "The_Geometry_of_Motion" / "Volume_V" / "main.tex").read_text(
        encoding="utf-8"
    )
    assert "Tangent-Space Methods for Nonlinear Control and Biomechanics" not in tex
    assert "The Geometry of Motion" in tex
