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
