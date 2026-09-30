"""Unit and integration tests for Standard "Where Next" Footer (WEB-03.5 #4510).

Acceptance Criteria:
1. No page links to itself (strictly validated and filtered).
2. Each core page has at least one "simpler" and one "deeper" link.
3. Coordinated with #3900 (reference cluster) and #3901 (motor-control / neuro cluster).
4. Accessible markup: <nav class="where-next-card" aria-label="Where to go next">, semantic headings.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest

from src.tools.where_next import (
    CORE_PAGES,
    compute_relative_href,
    load_where_next_config,
    normalize_page_key,
    render_where_next_html,
    validate_where_next_config,
)

ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts/filters/where-next.lua"
CONFIG_PATH = ROOT / "config/where_next.yml"


def _render_html(frontmatter_extra: str, body: str = "Body paragraph.") -> str:
    """Render a synthetic page through Quarto/Pandoc with the where-next Lua filter."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the where-next integration check")
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


# --- Configuration and Validation Tests ---


def test_config_file_exists() -> None:
    assert CONFIG_PATH.exists(), f"Configuration file {CONFIG_PATH} does not exist"


def test_core_pages_count() -> None:
    # All 30 core pages specified in WEB-03.8 must be present
    assert len(CORE_PAGES) >= 30


def test_production_where_next_config_is_valid() -> None:
    cfg = load_where_next_config(CONFIG_PATH)
    errors = validate_where_next_config(cfg, ROOT)
    assert not errors, "Config validation errors found:\n" + "\n".join(errors)


def test_acceptance_criterion_1_no_self_links_rejected() -> None:
    """Validation must reject any page that links to itself."""
    mock_config: dict[str, Any] = {
        "articles/theory-part1.qmd": {
            "simpler": [{"href": "articles/theory-part1.html", "title": "Self link"}],
            "deeper": [{"href": "articles/theory-part2.html", "title": "Part 2"}],
        }
    }
    errors = validate_where_next_config(mock_config, ROOT)
    assert any("Self-link violation" in err for err in errors)


def test_acceptance_criterion_2_core_pages_require_simpler_and_deeper() -> None:
    """Each core page must have >= 1 simpler and >= 1 deeper link."""
    cfg = load_where_next_config(CONFIG_PATH)
    for core_page in CORE_PAGES:
        norm_key = normalize_page_key(core_page)
        assert norm_key in cfg, f"Core page {core_page} missing from where_next.yml"
        entry = cfg[norm_key]

        simpler = entry.get("simpler")
        assert (
            isinstance(simpler, list) and len(simpler) >= 1
        ), f"Core page {core_page} must have >= 1 'simpler' link"

        deeper = entry.get("deeper")
        assert (
            isinstance(deeper, list) and len(deeper) >= 1
        ), f"Core page {core_page} must have >= 1 'deeper' link"


def test_acceptance_criterion_3_reference_cluster_coordination() -> None:
    """Verify linking into the #3900 reference cluster from relevant core pages."""
    cfg = load_where_next_config(CONFIG_PATH)

    # Theory Part 1 must link to lagrangian-reference or notation
    t1_deeper = [item["href"] for item in cfg["articles/theory-part1.qmd"]["deeper"]]
    assert any("lagrangian-reference" in h for h in t1_deeper)
    assert any("notation" in h for h in t1_deeper)

    # Theory Part 2 must link to screw-theory-reference
    t2_deeper = [item["href"] for item in cfg["articles/theory-part2.qmd"]["deeper"]]
    assert any("screw-theory-reference" in h for h in t2_deeper)


def test_acceptance_criterion_3_motor_control_cluster_coordination() -> None:
    """Verify linking into the #3901 motor control cluster from relevant pages."""
    cfg = load_where_next_config(CONFIG_PATH)

    # Tangent series Part 7 links to nonlinear-control-insights
    p7_deeper = [
        item["href"]
        for item in cfg["articles/tangent-hyperplanes-series/part-7-residual-aware.qmd"]["deeper"]
    ]
    assert any("nonlinear-control-insights" in h for h in p7_deeper)


# --- Relative HREF Helper Tests ---


def test_compute_relative_href() -> None:
    # Same directory
    assert (
        compute_relative_href("articles/theory-part1.qmd", "articles/theory-part2.html")
        == "theory-part2.html"
    )
    # Target in another directory
    assert (
        compute_relative_href("articles/theory-part1.qmd", "pages/notation.html")
        == "../pages/notation.html"
    )
    # From deep nested folder
    assert (
        compute_relative_href(
            "articles/tangent-hyperplanes-series/part-1-geometry.qmd",
            "articles/theory-part1.html",
        )
        == "../theory-part1.html"
    )
    # External URLs or anchors preserved
    assert (
        compute_relative_href("articles/theory-part1.qmd", "https://example.com")
        == "https://example.com"
    )
    assert compute_relative_href("articles/theory-part1.qmd", "#section") == "#section"


# --- HTML Rendering and Pandoc Filter Integration Tests ---


def test_render_where_next_html_accessible_structure() -> None:
    entry: dict[str, Any] = {
        "series-prev": {"href": "articles/theory-part1.html", "title": "Part 1"},
        "series-next": {"href": "articles/theory-part3.html", "title": "Part 3"},
        "simpler": [
            {
                "href": "articles/affine-nature-golf-swing.html",
                "title": "Affine Nature",
                "blurb": "Overview",
            }
        ],
        "deeper": [
            {
                "href": "articles/screw-theory-reference.html",
                "title": "Screw Theory",
                "blurb": "Deep dive",
            }
        ],
        "evidence": {
            "href": "reports/scientific-claim-audit.html",
            "title": "Audit",
            "blurb": "Proof",
        },
        "try-it": {
            "href": "articles/rotation-converter.html",
            "title": "Converter",
            "blurb": "Tool",
        },
    }
    html = render_where_next_html(entry, "articles/theory-part2.qmd")

    # Accessibility assertions
    assert '<nav class="where-next-card" aria-label="Where to go next">' in html
    assert '<h2 class="where-next-title unlisted unnumbered">Where Next</h2>' in html
    assert 'role="group" aria-label="Series progression"' in html
    assert "Previous in Series" in html
    assert "Next in Series" in html
    assert "Go Simpler" in html
    assert "Go Deeper" in html
    assert "See the Evidence" in html
    assert "Try It" in html
    # Self-contained links
    assert 'href="theory-part1.html"' in html
    assert 'href="theory-part3.html"' in html
    assert 'href="affine-nature-golf-swing.html"' in html
    assert 'href="screw-theory-reference.html"' in html
    assert 'href="../reports/scientific-claim-audit.html"' in html
    assert 'href="rotation-converter.html"' in html


@pytest.mark.integration
def test_filter_renders_from_frontmatter() -> None:
    frontmatter = (
        "where-next:\n"
        "  simpler:\n"
        "    - href: simpler-page.html\n"
        "      title: Simpler Version\n"
        "      blurb: An easier read\n"
        "  deeper:\n"
        "    - href: deeper-page.html\n"
        "      title: Deeper Derivation\n"
        "      blurb: Full math\n"
    )
    html = _render_html(frontmatter)
    assert '<nav class="where-next-card"' in html
    assert "Where Next" in html
    assert "Simpler Version" in html
    assert "Deeper Derivation" in html
    assert "An easier read" in html


@pytest.mark.integration
def test_filter_discards_self_link_if_provided() -> None:
    """Filter must never output a link pointing back to the current page."""
    frontmatter = (
        "where-next:\n"
        "  simpler:\n"
        "    - href: test.html\n"
        "      title: Self Page\n"
        "    - href: other-page.html\n"
        "      title: Other Page\n"
        "  deeper:\n"
        "    - href: deeper-page.html\n"
        "      title: Deeper Page\n"
    )
    html = _render_html(frontmatter)
    assert '<nav class="where-next-card"' in html
    assert "Other Page" in html
    assert "Deeper Page" in html
    # Self Page should have been filtered out
    assert "Self Page" not in html


@pytest.mark.integration
def test_filter_supersedes_legacy_related_articles() -> None:
    frontmatter = (
        "where-next:\n"
        "  simpler:\n"
        "    - href: simpler.html\n"
        "      title: Simpler Article\n"
        "  deeper:\n"
        "    - href: deeper.html\n"
        "      title: Deeper Article\n"
    )
    body = (
        "Main article body text.\n\n"
        "## Related Articles\n\n"
        "- Legacy bullet link 1\n"
        "- Legacy bullet link 2\n"
    )
    html = _render_html(frontmatter, body)
    assert '<nav class="where-next-card"' in html
    assert "Where Next" in html
    # Legacy Related Articles header was superseded
    assert "Legacy bullet link 1" not in html
