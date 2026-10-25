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

import yaml

ROOT = Path(__file__).resolve().parents[1]
STYLES_CSS = ROOT / "styles.css"
TYPOGRAPHY_TOKENS = ROOT / "css" / "tokens" / "typography.css"
PROGRAMMING_CATALOG_CSS = ROOT / "css" / "components" / "programming-catalog.css"
PROGRAMMING_META = ROOT / "models" / "programming" / "_metadata.yml"

_ARTICLE_LAYOUT_RULE = re.compile(
    r"#quarto-content\.page-layout-article[^{]*\{([^}]*)\}",
    re.DOTALL,
)


def test_article_page_grid_does_not_apply_column_or_gap() -> None:
    """Every article layout rule must not set column-gap or gap (#5164)."""
    stylesheet = STYLES_CSS.read_text(encoding="utf-8")
    blocks = _ARTICLE_LAYOUT_RULE.findall(stylesheet)
    assert blocks, "Missing #quarto-content.page-layout-article rules in styles.css"
    for index, block in enumerate(blocks):
        assert (
            "column-gap" not in block
        ), f"column-gap in article layout block {index} shrinks the body column"
        assert (
            re.search(r"\bgap\s*:", block) is None
        ), f"gap in article layout block {index} shrinks the body column"


def test_prose_width_targets_about_68ch_for_slice_1() -> None:
    """Desktop article measure should land near the epic's ~68ch target (#5164)."""
    tokens = TYPOGRAPHY_TOKENS.read_text(encoding="utf-8")
    match = re.search(r"--prose-width:\s*(\d+)ch;", tokens)
    assert match, "--prose-width token not found in css/tokens/typography.css"
    assert int(match.group(1)) == 68


def test_programming_catalog_stays_on_article_layout_with_scrollable_tables() -> None:
    """Companion catalogs must not use page-layout full (#5164 round 2)."""
    assert PROGRAMMING_CATALOG_CSS.is_file()
    catalog_css = PROGRAMMING_CATALOG_CSS.read_text(encoding="utf-8")
    assert "overflow-x" in catalog_css

    assert PROGRAMMING_META.is_file()
    meta = yaml.safe_load(PROGRAMMING_META.read_text(encoding="utf-8")) or {}
    assert meta.get("page-layout") != "full"
    assert "programming-catalog.css" in str(meta.get("format", {}).get("html", {}).get("css", ""))
