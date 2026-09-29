"""Tests for the Summary and Key Takeaways component (WEB-03.3 #4508).

Enforces:
1. One component driven by front matter (`summary-plain` and `key-takeaways`).
2. Visible without interaction (no collapse / toggle).
3. Merges with legacy lay blocks to prevent double summary boxes.
4. Styled in the print stylesheet (`css/print.css`).
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts/filters/summary-takeaways.lua"
PRINT_CSS = ROOT / "css/print.css"


def _render_html(frontmatter_extra: str, body: str = "Body paragraph.") -> str:
    """Render a synthetic page through Quarto/Pandoc with the summary-takeaways Lua filter."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the summary-takeaways integration check")
    with tempfile.TemporaryDirectory() as tmp_dir:
        qmd = Path(tmp_dir) / "test.qmd"
        content = (
            "---\n"
            "title: Test Article\n"
            "description: Test article description\n"
            f"{frontmatter_extra}\n"
            f"filters:\n  - {FILTER.resolve().as_posix()}\n"
            "format: html\n"
            "---\n\n"
            f"{body}\n"
        )
        qmd.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [quarto, "render", str(qmd), "--to", "html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0, f"quarto render failed:\n{result.stderr}\n{result.stdout}"
        html_file = qmd.with_suffix(".html")
        assert html_file.exists()
        return html_file.read_text(encoding="utf-8")


@pytest.mark.integration
def test_page_without_frontmatter_is_unchanged() -> None:
    html = _render_html("categories: [test]")
    assert "summary-takeaways-card" not in html
    assert "summary-plain-block" not in html
    assert "key-takeaways-block" not in html


@pytest.mark.integration
def test_page_with_summary_plain_renders_summary_block() -> None:
    html = _render_html(
        'summary-plain: "This is a plain-language summary of the control-affine swing model."'
    )
    assert "summary-takeaways-card" in html
    assert "summary-plain-block" in html
    assert "Plain-Language Summary" in html
    assert "This is a plain-language summary of the control-affine swing model." in html
    assert "key-takeaways-block" not in html


@pytest.mark.integration
def test_page_with_key_takeaways_renders_list() -> None:
    frontmatter = (
        "key-takeaways:\n"
        '  - "The drift field f(x) represents complete autonomous evolution."\n'
        '  - "Input forces enter linearly through control matrix G(x)."\n'
        '  - "ZTCF removes the applied control channel without biological overclaims."\n'
    )
    html = _render_html(frontmatter)
    assert "summary-takeaways-card" in html
    assert "key-takeaways-block" in html
    assert "Key Takeaways" in html
    assert "The drift field f(x) represents complete autonomous evolution." in html
    assert "Input forces enter linearly through control matrix G(x)." in html
    assert "ZTCF removes the applied control channel without biological overclaims." in html
    assert "summary-plain-block" not in html


@pytest.mark.integration
def test_page_with_both_renders_unified_card_visible_without_interaction() -> None:
    frontmatter = (
        'summary-plain: "Summary explaining the swing dynamics."\n'
        "key-takeaways:\n"
        '  - "First core finding."\n'
        '  - "Second core finding."\n'
    )
    html = _render_html(frontmatter)
    assert "summary-takeaways-card" in html
    assert "summary-plain-block" in html
    assert "key-takeaways-block" in html
    # Ensure there are no collapse buttons or hidden aria states
    assert 'aria-expanded="false"' not in html
    assert "<button" not in html


@pytest.mark.integration
def test_suppresses_legacy_laymans_terms_when_frontmatter_present() -> None:
    frontmatter = 'summary-plain: "New plain summary from front matter."'
    legacy_body = (
        "```{=html}\n"
        '<section class="laymans-terms">\n'
        '  <h2><button type="button" class="laymans-terms-header" aria-expanded="false">Legacy Lay</button></h2>\n'
        '  <div class="laymans-terms-content"><p>Old collapsed lay content.</p></div>\n'
        "</section>\n"
        "```\n\n"
        "Main article text continues here."
    )
    html = _render_html(frontmatter, body=legacy_body)
    assert "summary-takeaways-card" in html
    assert "New plain summary from front matter." in html
    # The legacy laymans-terms block should be suppressed
    assert "laymans-terms" not in html
    assert "Legacy Lay" not in html
    assert "Old collapsed lay content." not in html
    assert "Main article text continues here." in html


@pytest.mark.integration
def test_preserves_legacy_laymans_terms_when_frontmatter_absent() -> None:
    legacy_body = (
        "```{=html}\n"
        '<section class="laymans-terms">\n'
        '  <h2><button type="button" class="laymans-terms-header" aria-expanded="false">Legacy Lay</button></h2>\n'
        '  <div class="laymans-terms-content"><p>Old collapsed lay content.</p></div>\n'
        "</section>\n"
        "```\n\n"
        "Main article text continues here."
    )
    html = _render_html("categories: [test]", body=legacy_body)
    assert "summary-takeaways-card" not in html
    assert "laymans-terms" in html
    assert "Legacy Lay" in html


def test_print_stylesheet_includes_summary_takeaways_rules() -> None:
    assert PRINT_CSS.exists()
    content = PRINT_CSS.read_text(encoding="utf-8")
    assert ".summary-takeaways-card" in content
    assert "break-inside: avoid" in content
