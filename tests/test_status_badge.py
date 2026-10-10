"""Tests for the Status Badge Component (WEB-04.2 #4516).

Enforces:
1. Quarto shortcode {{< status >}} correctly reads document front matter or inline args.
2. All six canonical publication states are supported: available, validated, experimental, planned, deprecated, opinion.
3. State aliases are normalized cleanly (canonical -> available, reviewed -> validated, exploratory -> experimental, etc.).
4. Both icon (accessible inline SVG) and text are rendered, ensuring meaning never depends on colour alone.
5. All badge icons include aria-hidden="true".
6. Badges link to how-to-read.html#publication-states with depth-aware relative paths.
7. Disabling links with link="false" outputs a <span> instead of an <a>.
8. CSS component exists, is imported in styles.css, and contains WCAG AA contrast rules for light and dark themes.
9. All legacy .status-pill elements in pages/tools.qmd are replaced with .status-badge.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from scripts.bundle_css import bundle

ROOT = Path(__file__).resolve().parents[1]
STATUS_LUA = ROOT / "_extensions/status/status.lua"
STATUS_CSS = ROOT / "css/components/status-badge.css"
STYLES_CSS = ROOT / "styles.css"
TOOLS_QMD = ROOT / "pages/tools.qmd"

CANONICAL_STATES = [
    "available",
    "validated",
    "experimental",
    "planned",
    "deprecated",
    "opinion",
]


def _render_html(
    frontmatter_extra: str, body: str = "Body paragraph.", rel_path: str = "test.qmd"
) -> str:
    """Render a synthetic page through Quarto/Pandoc with the status extension."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the status shortcode integration check")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        # Mirror _extensions into temporary directory
        shutil.copytree(ROOT / "_extensions", tmp_root / "_extensions")
        (tmp_root / "_quarto.yml").write_text(
            "project:\n  type: website\n  output-dir: .\n", encoding="utf-8"
        )
        qmd_file = tmp_root / rel_path
        qmd_file.parent.mkdir(parents=True, exist_ok=True)
        content = (
            "---\n"
            "title: Test Status Badge\n"
            f"{frontmatter_extra}\n"
            "format: html\n"
            "---\n\n"
            f"{body}\n"
        )
        qmd_file.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [quarto, "render", str(qmd_file), "--to", "html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(tmp_root),
        )
        assert result.returncode == 0, f"quarto render failed:\n{result.stderr}\n{result.stdout}"
        html_file = qmd_file.with_suffix(".html")
        assert html_file.exists()
        return html_file.read_text(encoding="utf-8")


# ==============================================================================
# CSS & Design System Assertions
# ==============================================================================


def test_status_badge_css_exists_and_imported_in_styles() -> None:
    assert STATUS_CSS.exists()
    content = STATUS_CSS.read_text(encoding="utf-8")
    assert ".status-badge" in content
    assert ".status-badge__icon" in content
    assert ".status-badge__text" in content

    for state in CANONICAL_STATES:
        assert f".status-badge--{state}" in content
        assert f"body.quarto-dark .status-badge--{state}" in content

    styles_content = STYLES_CSS.read_text(encoding="utf-8")
    assert "css/components/status-badge.css" in styles_content


def test_docs_styles_bundle_contains_status_badge_rules() -> None:
    content = bundle(STYLES_CSS, ROOT)
    assert ".status-badge" in content
    for state in CANONICAL_STATES:
        assert f".status-badge--{state}" in content


# ==============================================================================
# Legacy Replacement Assertions
# ==============================================================================


def test_tools_qmd_replaces_all_legacy_status_pills() -> None:
    assert TOOLS_QMD.exists()
    content = TOOLS_QMD.read_text(encoding="utf-8")
    assert "status-pill" not in content
    assert "status-badge--available" in content
    assert "status-badge--experimental" in content
    assert "how-to-read.html#publication-states" in content


# ==============================================================================
# Integration: Quarto Shortcode Rendering
# ==============================================================================


@pytest.mark.integration
def test_shortcode_reads_front_matter_status() -> None:
    html = _render_html(frontmatter_extra='status: "Available"', body="Page status: {{< status >}}")
    assert "status-badge--available" in html
    assert '<span class="status-badge__text">Available</span>' in html
    assert '<svg class="status-badge__icon"' in html
    assert 'aria-hidden="true"' in html
    assert "how-to-read.html#publication-states" in html


@pytest.mark.integration
def test_shortcode_reads_front_matter_maturity() -> None:
    html = _render_html(
        frontmatter_extra='maturity: "Validated"', body="Page status: {{< status >}}"
    )
    assert "status-badge--validated" in html
    assert '<span class="status-badge__text">Validated</span>' in html


@pytest.mark.integration
@pytest.mark.parametrize("state", CANONICAL_STATES)
def test_shortcode_all_canonical_states(state: str) -> None:
    html = _render_html(frontmatter_extra="", body=f"Inline: {{{{< status {state} >}}}}")
    assert f"status-badge--{state}" in html
    assert f'<span class="status-badge__text">{state.capitalize()}</span>' in html
    assert '<svg class="status-badge__icon"' in html
    assert 'aria-hidden="true"' in html
    assert "how-to-read.html#publication-states" in html


@pytest.mark.integration
def test_shortcode_normalizes_aliases() -> None:
    # exploratory -> experimental
    html = _render_html(frontmatter_extra="", body="Inline: {{< status exploratory >}}")
    assert "status-badge--experimental" in html
    assert '<span class="status-badge__text">Experimental</span>' in html

    # canonical -> available
    html_canon = _render_html(frontmatter_extra="", body="Inline: {{< status canonical >}}")
    assert "status-badge--available" in html_canon
    assert '<span class="status-badge__text">Available</span>' in html_canon

    # reviewed -> validated
    html_rev = _render_html(frontmatter_extra="", body="Inline: {{< status reviewed >}}")
    assert "status-badge--validated" in html_rev
    assert '<span class="status-badge__text">Validated</span>' in html_rev


@pytest.mark.integration
def test_shortcode_custom_text() -> None:
    html = _render_html(frontmatter_extra="", body='Inline: {{< status planned "In Planning" >}}')
    assert "status-badge--planned" in html
    assert '<span class="status-badge__text">In Planning</span>' in html


@pytest.mark.integration
def test_shortcode_link_false_renders_span() -> None:
    html = _render_html(frontmatter_extra="", body='Inline: {{< status validated link="false" >}}')
    assert '<span class="status-badge status-badge--validated"' in html
    assert "<a href=" not in html.split("Inline:")[1]


@pytest.mark.integration
def test_depth_aware_relative_urls() -> None:
    # Root level file
    html_root = _render_html(
        frontmatter_extra="", body="{{< status available >}}", rel_path="test_root.qmd"
    )
    assert 'href="pages/how-to-read.html#publication-states"' in html_root

    # Pages level file
    html_pages = _render_html(
        frontmatter_extra="", body="{{< status available >}}", rel_path="pages/test_pages.qmd"
    )
    assert 'href="how-to-read.html#publication-states"' in html_pages

    # Deep directory (articles/theory/...)
    html_articles = _render_html(
        frontmatter_extra="",
        body="{{< status available >}}",
        rel_path="articles/theory/test_deep.qmd",
    )
    assert 'href="../../pages/how-to-read.html#publication-states"' in html_articles
