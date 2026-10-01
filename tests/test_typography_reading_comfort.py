"""Tests for Typography and Reading Comfort (WEB-08.6 #4557).

Enforces:
1. Prose measure of 60-75 characters (``--prose-width`` token) applies to the
   standard Quarto article/book content area (``#quarto-document-content``),
   not just the handful of hand-authored full-layout pages. Quarto wraps each
   heading's content in ``<section class="level2">`` (etc.) for ``@sec-``
   crossrefs, so a descendant selector is required: a direct-child selector
   would miss nearly all body paragraphs on long-form pages.
2. No third-party font requests: fonts are self-hosted, and no template
   references a Google Fonts (or other third-party font) host.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLES_CSS = ROOT / "styles.css"
TYPOGRAPHY_TOKENS = ROOT / "css" / "tokens" / "typography.css"
SITE_HEAD = ROOT / "_includes" / "site-head.html"
LATEX_ARTICLE_TEMPLATE = ROOT / "_templates" / "latex_article.html"
THIRD_PARTY_FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")


def test_prose_width_token_is_within_60_to_75_characters() -> None:
    """The ``--prose-width`` token must express a 60-75ch reading measure."""
    tokens = TYPOGRAPHY_TOKENS.read_text(encoding="utf-8")
    match = re.search(r"--prose-width:\s*(\d+)ch;", tokens)
    assert match, "--prose-width token not found in css/tokens/typography.css"
    assert 60 <= int(match.group(1)) <= 75


def test_prose_width_applies_to_standard_article_content() -> None:
    """Standard article/book pages (``#quarto-document-content``) must
    constrain paragraph/list measure — not only the bespoke full-layout
    pages that opt into ``.main-content-area``/``.article-body``."""
    stylesheet = STYLES_CSS.read_text(encoding="utf-8")

    assert "#quarto-content.page-layout-article #quarto-document-content p" in stylesheet
    rule = stylesheet.split(
        "#quarto-content.page-layout-article #quarto-document-content p", maxsplit=1
    )[1].split("}", maxsplit=1)[0]
    assert "max-width: var(--prose-width)" in rule


def test_site_head_has_no_third_party_font_requests() -> None:
    """The shared site head must not link a third-party font host."""
    head = SITE_HEAD.read_text(encoding="utf-8")
    for host in THIRD_PARTY_FONT_HOSTS:
        assert host not in head, f"{host} still referenced in {SITE_HEAD}"


def test_site_head_csp_has_no_third_party_font_hosts() -> None:
    """The CSP meta tag must not allow-list a third-party font host."""
    head = SITE_HEAD.read_text(encoding="utf-8")
    match = re.search(r'<meta http-equiv="Content-Security-Policy"[^>]*>', head)
    assert match, "CSP meta tag not found in site-head.html"
    csp = match.group(0)
    for host in THIRD_PARTY_FONT_HOSTS:
        assert host not in csp, f"{host} still allow-listed in CSP"


def test_legacy_article_template_has_no_third_party_font_requests() -> None:
    """The legacy LaTeX-to-HTML article template must not link a
    third-party font host either (it loads the same self-hosted font via
    the shared ``styles.css``)."""
    template = LATEX_ARTICLE_TEMPLATE.read_text(encoding="utf-8")
    for host in THIRD_PARTY_FONT_HOSTS:
        assert host not in template, f"{host} still referenced in {LATEX_ARTICLE_TEMPLATE}"


def test_playfair_display_is_self_hosted() -> None:
    """The heading font is declared locally and the referenced file exists."""
    tokens = TYPOGRAPHY_TOKENS.read_text(encoding="utf-8")
    match = re.search(
        r'@font-face\s*\{[^}]*font-family:\s*"Playfair Display"[^}]*\}', tokens, re.DOTALL
    )
    assert match, "No local @font-face declaration for Playfair Display"
    face = match.group(0)
    assert "fonts.googleapis.com" not in face
    assert "fonts.gstatic.com" not in face

    url_match = re.search(r'url\("(/fonts/[^"]+\.woff2)"\)', face)
    assert url_match, "@font-face src must reference a local /fonts/... woff2 file"
    font_path = ROOT / url_match.group(1).lstrip("/")
    assert font_path.is_file(), f"Referenced font file does not exist: {font_path}"


def test_playfair_display_font_file_has_ofl_license() -> None:
    """The self-hosted font ships with its SIL Open Font License text."""
    license_path = ROOT / "fonts" / "playfair-display" / "OFL.txt"
    assert license_path.is_file()
    assert "SIL OPEN FONT LICENSE" in license_path.read_text(encoding="utf-8")
