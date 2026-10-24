"""Regression guards for article page grid width (UX slice 1, #5164).

Quarto's ``page-columns`` grid exposes several zero-width tracks on article
pages. Applying ``column-gap`` on ``#quarto-content.page-layout-article``
inserts gaps between every track and squeezes ``#quarto-document-content`` on
phones (~254px at 375px viewport). Spacing belongs on sidebar elements or on
``.standard-page-layout`` grids that use ``gap`` intentionally.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLES_CSS = ROOT / "styles.css"

_ARTICLE_LAYOUT_RULE = re.compile(
    r"#quarto-content\.page-layout-article\s*\{([^}]*)\}",
    re.DOTALL,
)


def _article_layout_rule_block(stylesheet: str) -> str:
    match = _ARTICLE_LAYOUT_RULE.search(stylesheet)
    assert match, "Missing #quarto-content.page-layout-article rule in styles.css"
    return match.group(1)


def test_article_page_grid_does_not_apply_column_gap() -> None:
    """The Quarto article page grid must not set column-gap (#5164)."""
    block = _article_layout_rule_block(STYLES_CSS.read_text(encoding="utf-8"))
    assert "column-gap" not in block, (
        "column-gap on #quarto-content.page-layout-article shrinks the article "
        "column between Quarto's zero-width page-columns tracks"
    )
