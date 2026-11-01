"""Static contracts for UX slice 4 (#5167): phone header and nav landmarks."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STYLES_CSS = REPO_ROOT / "styles.css"
HEADER_CSS = REPO_ROOT / "css" / "components" / "header-nav.css"
HEADER_LUA = REPO_ROOT / "scripts" / "filters" / "page-header-card.lua"
PHONE_MEDIA = r"@media \(max-width: 991\.98px\) \{(.*?)\n\}\n"


def _rule_body(css: str, selector: str) -> str:
    start = css.index(selector + " {")
    return css[start : css.index("}", start)]


def test_header_stylesheet_is_imported_by_styles() -> None:
    assert "css/components/header-nav.css" in STYLES_CSS.read_text(encoding="utf-8")


def test_theme_toggle_is_in_flow_with_a_44px_target() -> None:
    rule = _rule_body(HEADER_CSS.read_text(encoding="utf-8"), "#theme-toggle")
    assert "position: fixed" not in rule
    assert "min-width: 44px" in rule
    assert "min-height: 44px" in rule


def test_no_fixed_position_theme_toggle_remains_in_styles() -> None:
    assert "#theme-toggle {" not in STYLES_CSS.read_text(encoding="utf-8")


def test_native_quarto_color_scheme_toggle_stays_hidden() -> None:
    css = STYLES_CSS.read_text(encoding="utf-8")
    assert "display: none" in css.split(".quarto-color-scheme-toggle", 1)[1][:200]


def test_phone_header_drops_vertical_padding_and_keeps_one_row() -> None:
    header_css = HEADER_CSS.read_text(encoding="utf-8")
    phone = re.search(PHONE_MEDIA, header_css, re.S)
    assert phone, "phone media block missing in header-nav.css"
    block = phone.group(1)
    assert re.search(r"\.navbar-brand-container \{[^}]*min-width:\s*0", block)
    # Outer header padding clears in styles.css (after the fixed #quarto-header rule) so the
    # bundled CSS keeps position: fixed in the first header block (see test_css_bundle).
    styles_css = STYLES_CSS.read_text(encoding="utf-8")
    assert re.search(
        r"@media \(max-width: 991\.98px\) \{\s*#quarto-header \{[^}]*padding:\s*0",
        styles_css,
        re.S,
    )


def test_phone_search_button_fits_in_the_primary_header_row() -> None:
    header_css = HEADER_CSS.read_text(encoding="utf-8")
    phone = re.search(PHONE_MEDIA, header_css, re.S)
    assert phone, "phone media block missing in header-nav.css"
    block = phone.group(1)
    search = re.search(r"#quarto-header \.navbar-container #quarto-search \{([^}]+)\}", block, re.S)
    assert search, "search container must get a compact phone rule"
    assert re.search(r"flex:\s*0 0 44px", search.group(1))
    assert re.search(r"min-width:\s*44px", search.group(1))
    button = re.search(
        r"#quarto-header #quarto-search \.aa-DetachedSearchButton \{([^}]+)\}",
        block,
        re.S,
    )
    assert button, "search button must have a compact phone rule"
    assert re.search(r"width:\s*44px", button.group(1))
    assert re.search(r"min-width:\s*44px", button.group(1))


def test_page_header_card_is_not_a_landmark_region() -> None:
    lua = HEADER_LUA.read_text(encoding="utf-8")
    assert '<header class="page-header-card"' in lua
    assert 'role="region"' not in lua
