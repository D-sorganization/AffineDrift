"""Verify companion chapter links in upstreamdrift-physics-models resolve to rendered pages."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTICLE = REPO_ROOT / "articles" / "upstreamdrift-physics-models.qmd"
COMPANION_PAGE = REPO_ROOT / "articles" / "proximal-distal-a-journey-through-the-swing.qmd"
CH12_CHAPTER = (
    REPO_ROOT
    / "articles"
    / "proximal_distal_companion"
    / "chapters"
    / "ch12_two_hands_one_wrench.qmd"
)


def test_upstreamdrift_physics_models_ch12_companion_link_uses_rendered_anchor() -> None:
    """Article must link to the rendered companion page anchor, not excluded chapter HTML."""
    article_text = ARTICLE.read_text(encoding="utf-8")

    assert not re.search(
        r"proximal_distal_companion/chapters/[^)\s]+\.html",
        article_text,
    ), "upstreamdrift-physics-models.qmd must not link to excluded chapter HTML"

    expected_href = "proximal-distal-a-journey-through-the-swing.html#sec-lay-ch12"
    assert (
        expected_href in article_text
    ), f"upstreamdrift-physics-models.qmd must link to {expected_href}"

    companion_text = COMPANION_PAGE.read_text(encoding="utf-8")
    assert (
        "{{< include proximal_distal_companion/chapters/ch12_two_hands_one_wrench.qmd >}}"
        in companion_text
    ), "Companion page must include ch12_two_hands_one_wrench.qmd"

    ch12_text = CH12_CHAPTER.read_text(encoding="utf-8")
    assert (
        "{#sec-lay-ch12}" in ch12_text
    ), "ch12_two_hands_one_wrench.qmd must define the #sec-lay-ch12 section anchor"
