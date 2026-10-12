"""Single-source contract for the Okabe-Ito palette tokens (issue #4553).

The colourblind-safe ``--color-*`` palette used to be declared in
``custom.scss`` (``:root``) while every other colour token lived in
``css/tokens/colors.css``.  The CSS custom properties now live only in the
token file; ``custom.scss`` keeps just the SCSS variables Bootstrap needs for
compile-time maths, and this test keeps the two in lock-step.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PALETTE = ("orange", "sky-blue", "green", "yellow", "blue", "vermillion", "purple")


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def _scss_palette() -> dict[str, str]:
    scss = _read("custom.scss")
    return {
        name: value.lower()
        for name, value in re.findall(r"^\$color-([a-z-]+):\s*(#[0-9A-Fa-f]{6});", scss, re.M)
    }


def _token_palette() -> dict[str, str]:
    css = _read("css/tokens/colors.css")
    return {
        name: value.lower()
        for name, value in re.findall(r"^\s*--color-([a-z-]+):\s*(#[0-9A-Fa-f]{3,6});", css, re.M)
        if name in PALETTE
    }


def test_token_file_declares_every_palette_colour() -> None:
    """Every Okabe-Ito colour is a CSS custom property in the token file."""
    assert set(_token_palette()) == set(PALETTE)


def test_scss_and_token_palettes_agree() -> None:
    """The SCSS variables Bootstrap compiles with equal the CSS tokens."""
    scss = _scss_palette()
    tokens = _token_palette()
    for name in PALETTE:
        assert scss[name] == tokens[name], f"palette drift for {name}"


def test_custom_scss_does_not_redeclare_palette_custom_properties() -> None:
    """``custom.scss`` must not carry a second copy of the CSS palette tokens."""
    scss = _read("custom.scss")
    names = "|".join(PALETTE)
    assert not re.search(rf"^\s*--color-(?:{names}|gray)\s*:", scss, re.M)


def test_gray_token_is_declared_once() -> None:
    """``--color-gray`` has exactly one declaration across the token files."""
    css = _read("css/tokens/colors.css")
    assert len(re.findall(r"^\s*--color-gray\s*:", css, re.M)) == 1
