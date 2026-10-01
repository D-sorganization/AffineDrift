"""Quarto dark theme adoption contract (issue #4556).

Acceptance criteria:
  - Quarto's `theme:` config declares both a `light` and a `dark` variant, so
    Quarto compiles genuine light/dark Bootstrap + syntax-highlighting bundles
    instead of the site declaring only `light` and faking dark mode entirely
    in a post-hoc CSS override.
  - Quarto auto-injects its own `.quarto-color-scheme-toggle` switch whenever
    both `light` and `dark` are configured. The site already ships a tested,
    accessible custom toggle (js/dark-mode-toggle.js, `#theme-toggle`), so the
    duplicate native switch must be hidden rather than left to confuse readers
    with two independent controls.
  - The custom toggle stays `position: fixed`, so inserting it after
    DOMContentLoaded cannot shift any other element's layout (CLS
    contribution 0): a fixed-position element is removed from normal flow and
    contributes no box to its parent regardless of when it is inserted.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
QUARTO_YML = REPO_ROOT / "_quarto.yml"
STYLES_CSS = REPO_ROOT / "styles.css"


def _html_theme() -> dict:
    data = yaml.safe_load(QUARTO_YML.read_text(encoding="utf-8"))
    return data["format"]["html"]["theme"]


def test_quarto_theme_declares_both_light_and_dark_variants() -> None:
    theme = _html_theme()
    assert "light" in theme, "theme.light must stay configured"
    assert "dark" in theme, "theme.dark must be configured to adopt Quarto dark mode support"
    assert (
        isinstance(theme["light"], list) and theme["light"]
    ), "theme.light must be a non-empty list"
    assert isinstance(theme["dark"], list) and theme["dark"], "theme.dark must be a non-empty list"


def test_quartos_native_color_scheme_toggle_is_hidden() -> None:
    # Configuring theme.dark makes Quarto auto-inject its own
    # `.quarto-color-scheme-toggle` switch into the navbar. The site already
    # has a tested custom toggle wired to its own design tokens, so the native
    # one must be suppressed to avoid two competing, out-of-sync controls.
    css = STYLES_CSS.read_text(encoding="utf-8")
    assert ".quarto-color-scheme-toggle" in css
    assert "display: none" in css.split(".quarto-color-scheme-toggle", 1)[1][:200]


def test_custom_theme_toggle_stays_fixed_position() -> None:
    # #theme-toggle is inserted by js/dark-mode-toggle.js after
    # DOMContentLoaded. `position: fixed` removes it from normal document
    # flow, so its (possibly late) insertion cannot shift any other element
    # -- the CLS contribution acceptance criterion depends on this staying true.
    css = STYLES_CSS.read_text(encoding="utf-8")
    rule_start = css.index("#theme-toggle {")
    rule_body = css[rule_start : css.index("}", rule_start)]
    assert "position: fixed" in rule_body
