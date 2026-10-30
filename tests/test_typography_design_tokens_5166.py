"""Contract tests for UX slice 3: typography and design tokens (#5166).

Static analysis of the CSS sources only: no browser, no Quarto render. These
tests pin the token contract (one heading face, a strictly decreasing h1-h4
scale at phone and desktop widths, readable text floors, no mid-word break
policy on text, no link-coloured headings, ``custom.scss`` mirroring the
tokens). They do not replace the Lighthouse/axe/screenshot protocol that the
issue requires on a built site.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STYLES_CSS = ROOT / "styles.css"
TYPOGRAPHY_CSS = ROOT / "css" / "tokens" / "typography.css"
COLORS_CSS = ROOT / "css" / "tokens" / "colors.css"
SUMMARY_CSS = ROOT / "css" / "components" / "summary-takeaways.css"
CUSTOM_SCSS = ROOT / "custom.scss"
PHYSICS_BOOK_CONFIG = ROOT / "articles" / "The_Physics_of_Golf" / "quarto" / "_quarto.yml"
PHYSICS_BOOK_TYPOGRAPHY = ROOT / "articles" / "The_Physics_of_Golf" / "quarto" / "typography.css"

ROOT_FONT_PX = 16.0
VIEWPORTS_PX = (375, 768, 1440)
BODY_MIN_PX = 16.0
CODE_MIN_PX = 14.0
WCAG_AA_TEXT = 4.5
HEADING_TAG = r"h[1-6]"
TEXT_TAG = r"(?:h[1-6]|p|li|body)"
BAD_WORD_BREAKS = {"break-all", "break-word"}


def strip_comments(css: str) -> str:
    """Remove CSS comments so brace/selector parsing is not confused by prose."""
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def parse_rules(css: str) -> list[tuple[list[str], dict[str, str]]]:
    """Return ``(selectors, declarations)`` for every innermost rule block.

    ``@media`` wrappers are flattened: only blocks without nested braces match.
    """
    rules: list[tuple[list[str], dict[str, str]]] = []
    for head, body in re.findall(r"([^{}]+)\{([^{}]*)\}", strip_comments(css)):
        head = head.strip()
        if head.startswith("@"):
            continue
        selectors = [s.strip() for s in head.split(",") if s.strip()]
        decls: dict[str, str] = {}
        for decl in body.split(";"):
            if ":" in decl:
                name, value = decl.split(":", maxsplit=1)
                decls[name.strip()] = " ".join(value.split())
        rules.append((selectors, decls))
    return rules


def token(css: str, name: str) -> str:
    """Return the first declared value of custom property ``name``."""
    match = re.search(rf"{re.escape(name)}\s*:\s*([^;]+);", strip_comments(css))
    assert match, f"{name} is not declared"
    return " ".join(match.group(1).split())


def _term_px(term: str, viewport_px: float) -> float:
    match = re.fullmatch(r"(-?[\d.]+)(vw|rem|px)?", term)
    assert match, f"unsupported length term: {term!r}"
    number, unit = float(match.group(1)), match.group(2)
    if unit == "vw":
        return number * viewport_px / 100.0
    if unit == "px":
        return number
    return number * ROOT_FONT_PX


def clamp_px(value: str, viewport_px: float) -> float:
    """Evaluate ``clamp(min, a*vw + b*rem, max)`` (or a plain length) to px."""
    match = re.fullmatch(r"clamp\((.+)\)", value.strip())
    if not match:
        return _term_px(value.strip(), viewport_px)
    low, preferred, high = (part.strip() for part in match.group(1).split(","))
    expression = preferred.replace(" - ", " + -")
    pref_px = sum(_term_px(t.strip(), viewport_px) for t in expression.split(" + "))
    return max(_term_px(low, viewport_px), min(pref_px, _term_px(high, viewport_px)))


def heading_px(css: str, level: int, viewport_px: float) -> float:
    return clamp_px(token(css, f"--font-size-h{level}"), viewport_px)


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(hex_color: str) -> float:
        channels = [int(hex_color.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def stylesheet_paths() -> list[Path]:
    return [STYLES_CSS, *sorted((ROOT / "css").rglob("*.css"))]


@pytest.fixture(scope="module")
def typography() -> str:
    return TYPOGRAPHY_CSS.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def styles() -> str:
    return STYLES_CSS.read_text(encoding="utf-8")


def test_heading_family_token_names_the_hosted_face(typography: str) -> None:
    """The token must name Playfair Display, the face that actually renders."""
    assert token(typography, "--font-family-heading").startswith('"Playfair Display"')


def test_no_stylesheet_hard_codes_the_heading_face_or_display_alias() -> None:
    """The face is spelled once (the token); everything else consumes the token."""
    offenders = []
    for path in stylesheet_paths():
        if path == TYPOGRAPHY_CSS:
            continue
        text = strip_comments(path.read_text(encoding="utf-8"))
        if re.search(r"font-family:[^;]*Playfair", text) or "--font-display" in text:
            offenders.append(path.relative_to(ROOT).as_posix())
    assert not offenders, f"hard-coded heading face in: {offenders}"


def test_global_heading_rule_uses_the_family_token(styles: str) -> None:
    for selectors, decls in parse_rules(styles):
        if "h1" in selectors and "h6" in selectors:
            assert decls["font-family"].startswith("var(--font-family-heading)")
            return
    pytest.fail("global h1..h6 rule not found in styles.css")


def test_custom_scss_serif_stack_mirrors_the_token(typography: str) -> None:
    scss = CUSTOM_SCSS.read_text(encoding="utf-8")
    match = re.search(r"\$font-family-serif:\s*([^;]+);", scss)
    assert match, "$font-family-serif missing from custom.scss"
    assert " ".join(match.group(1).split()) == token(typography, "--font-family-heading")


def test_custom_scss_text_and_link_colours_mirror_tokens() -> None:
    colors = COLORS_CSS.read_text(encoding="utf-8")
    scss = CUSTOM_SCSS.read_text(encoding="utf-8")
    body = re.search(r"\$body-color:\s*(#[0-9a-fA-F]{6});", scss)
    link = re.search(r"\$link-color:\s*(#[0-9a-fA-F]{6});", scss)
    assert body and link, "$body-color/$link-color must be literal hex mirrors of the tokens"
    assert body.group(1).lower() == token(colors, "--text-primary").lower()
    assert link.group(1).lower() == token(colors, "--color-link").lower()


@pytest.mark.parametrize("viewport", VIEWPORTS_PX)
def test_heading_scale_strictly_decreases_h1_to_h4(typography: str, viewport: int) -> None:
    sizes = [heading_px(typography, level, viewport) for level in range(1, 7)]
    assert sizes[0] > sizes[1] > sizes[2] > sizes[3], f"{viewport}px: {sizes}"
    assert sizes[3] >= sizes[4] >= sizes[5], f"{viewport}px: {sizes}"


def test_base_heading_rules_consume_the_scale_tokens_at_every_width(styles: str) -> None:
    """h1-h4 take their size only from ``--font-size-hN``: no raw sizes, no overrides."""
    seen: dict[str, int] = {}
    for selectors, decls in parse_rules(styles):
        for tag in ("h1", "h2", "h3", "h4"):
            if selectors == [tag] and "font-size" in decls:
                assert decls["font-size"] == f"var(--font-size-{tag})", (tag, decls)
                seen[tag] = seen.get(tag, 0) + 1
    assert seen == {"h1": 1, "h2": 1, "h3": 1, "h4": 1}, seen


def test_quarto_page_title_uses_the_h1_scale_token(styles: str) -> None:
    for selectors, decls in parse_rules(styles):
        if selectors == ["#title-block-header .title"]:
            assert decls.get("font-size") == "var(--font-size-h1)", decls
            return
    pytest.fail("Quarto page title rule not found in styles.css")


def test_physics_book_uses_the_shared_heading_tokens() -> None:
    config = PHYSICS_BOOK_CONFIG.read_text(encoding="utf-8")
    assert "typography.css" in config, "the book must load its typography overrides"

    css = PHYSICS_BOOK_TYPOGRAPHY.read_text(encoding="utf-8")
    assert '@import url("../../../css/tokens/typography.css")' in css
    rules = parse_rules(css)
    shared_family = next(
        (
            decls
            for selectors, decls in rules
            if all(f"h{level}" in selectors for level in range(1, 7))
        ),
        {},
    )
    assert shared_family.get("font-family") == "var(--font-family-heading)"
    for level in range(1, 7):
        heading_rule = next(
            (
                decls
                for selectors, decls in rules
                if f"h{level}" in selectors and f".h{level}" in selectors and "font-size" in decls
            ),
            {},
        )
        assert heading_rule.get("font-size") == f"var(--font-size-h{level})"
    prose_rule = next(
        (decls for selectors, decls in rules if selectors == ["#quarto-document-content p"]),
        {},
    )
    assert prose_rule.get("max-width") == "var(--prose-width)"


def test_summary_box_titles_sit_below_h4_on_the_scale(typography: str) -> None:
    css = SUMMARY_CSS.read_text(encoding="utf-8")
    sizes = [
        decls["font-size"]
        for selectors, decls in parse_rules(css)
        if any(s.endswith("-title") for s in selectors) and "font-size" in decls
    ]
    assert sizes, "summary box title rule not found"
    for size in sizes:
        assert re.fullmatch(r"var\(--font-size-h[1-6]\)", size), size
        level = int(size[-2])
        assert level >= 5, "box titles must not outrank an h4"
        for viewport in VIEWPORTS_PX:
            assert heading_px(typography, level, viewport) <= heading_px(typography, 4, viewport)


def test_no_heading_selector_uses_a_link_colour() -> None:
    offenders = []
    heading_selector = re.compile(rf"(?:^|[\s>+~]){HEADING_TAG}(?:[.:#\[].*)?$")
    for path in stylesheet_paths():
        for selectors, decls in parse_rules(path.read_text(encoding="utf-8")):
            colour = decls.get("color", "")
            if "color-link" in colour and any(heading_selector.search(s) for s in selectors):
                offenders.append(f"{path.relative_to(ROOT).as_posix()}: {selectors}")
    assert not offenders, offenders


@pytest.mark.parametrize("name", ["--font-size-body", "--font-size-prose"])
@pytest.mark.parametrize("viewport", VIEWPORTS_PX)
def test_body_and_prose_tokens_are_at_least_one_rem(
    typography: str, name: str, viewport: int
) -> None:
    assert clamp_px(token(typography, name), viewport) >= BODY_MIN_PX


@pytest.mark.parametrize("viewport", VIEWPORTS_PX)
def test_code_token_is_at_least_14px(typography: str, viewport: int) -> None:
    assert clamp_px(token(typography, "--font-size-code"), viewport) >= CODE_MIN_PX


def test_body_rule_font_size_is_at_least_one_rem(styles: str) -> None:
    for selectors, decls in parse_rules(styles):
        if selectors == ["body"] and "font-size" in decls:
            for viewport in VIEWPORTS_PX:
                assert clamp_px(decls["font-size"], viewport) >= BODY_MIN_PX
            return
    pytest.fail("body font-size rule not found in styles.css")


def test_text_selectors_have_no_midword_break_policy() -> None:
    """Headings and body text never use break-all/break-word or auto hyphenation.

    Long tokens (URLs, inline code) may use ``overflow-wrap: anywhere`` on their
    own selectors; normal words must not split.
    """
    text_selector = re.compile(rf"(?:^|[\s>+~]){TEXT_TAG}$")
    offenders = []
    for path in stylesheet_paths():
        for selectors, decls in parse_rules(path.read_text(encoding="utf-8")):
            bad = decls.get("word-break") in BAD_WORD_BREAKS or decls.get("hyphens") == "auto"
            if bad and any(text_selector.search(s) for s in selectors):
                offenders.append(f"{path.relative_to(ROOT).as_posix()}: {selectors}")
    assert not offenders, offenders


def test_prose_width_is_defined_once_at_the_reading_measure(typography: str, styles: str) -> None:
    """61-62ch lands near 68 real characters per line at 1440px (issue follow-up)."""
    assert int(re.fullmatch(r"(\d+)ch", token(typography, "--prose-width")).group(1)) == 61
    assert "--prose-width:" not in strip_comments(styles)


def test_text_safe_status_colour_tokens_pass_aa() -> None:
    colors = COLORS_CSS.read_text(encoding="utf-8")
    for name in ("--color-warning-text", "--color-info-text"):
        values = re.findall(rf"{name}:\s*(#[0-9a-fA-F]{{6}});", colors)
        assert len(values) == 3, f"{name}: expected light + two dark declarations"
        assert contrast_ratio(values[0], "#ffffff") >= WCAG_AA_TEXT
        for dark_value in values[1:]:
            assert contrast_ratio(dark_value, "#0d0d1a") >= WCAG_AA_TEXT


def test_physics_book_toc_numbers_and_captions_use_text_color() -> None:
    rules = parse_rules(PHYSICS_BOOK_TYPOGRAPHY.read_text(encoding="utf-8"))
    text_safe_rule = next(
        (
            decls
            for selectors, decls in rules
            if ".header-section-number" in selectors
            and "figcaption" in selectors
            and ".figure-caption" in selectors
        ),
        {},
    )
    assert text_safe_rule.get("color") == "var(--text-primary)"
