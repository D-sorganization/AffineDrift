"""Tests for Content Deprecation and Archive Policy (WEB-13.9 #4603).

Enforces:
1. CONTRIBUTING.md contains the formal Content Deprecation and Archive Policy.
2. The policy explicitly defines:
   - When a page is Deprecated (consolidation, supersession, standardization, archival).
   - How a page is bannered (frontmatter declaration, status-banner--deprecated, status-badge--deprecated).
   - When a page is removed (preservation guarantee, no broken links, removal restricted to ephemeral scratch).
   - How URLs are preserved (permanent aliases redirects and canonical pointers).
3. css/components/status-banner.css and docs/styles.css define .status-banner--deprecated and .status-pill--deprecated.
4. Deprecated family files (e.g. tangent-space drafts) have status: "deprecated", canonical links, and deprecation banners.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRIBUTING_MD = ROOT / "CONTRIBUTING.md"
STATUS_BANNER_CSS = ROOT / "css/components/status-banner.css"
DOCS_STYLES_CSS = ROOT / "docs/styles.css"

TANGENT_DRAFTS_DIR = (
    ROOT
    / "articles"
    / "tangent-hyperplane-articles"
    / "Drafts_Original_Articles"
    / "Tangent_Hyperplanes_Series_Package"
)
GOLF_APPLICATION_MD = (
    ROOT
    / "articles"
    / "tangent-hyperplane-articles"
    / "Drafts_Original_Articles"
    / "Tangent_Hyperplanes_Golf_Application.md"
)


def test_contributing_contains_content_deprecation_policy() -> None:
    assert CONTRIBUTING_MD.exists()
    content = CONTRIBUTING_MD.read_text(encoding="utf-8")

    assert "Content Deprecation and Archive Policy (WEB-13.9)" in content
    assert "When a Page Is Deprecated" in content
    assert "How Deprecated Pages Are Bannered" in content
    assert "When a Page Is Removed" in content
    assert "URL Preservation and Redirects" in content

    # Key policy guarantees
    assert ".status-banner--deprecated" in content
    assert 'status: "deprecated"' in content
    assert "aliases:" in content
    assert "canonical:" in content


def test_status_banner_css_has_deprecated_styles() -> None:
    assert STATUS_BANNER_CSS.exists()
    content = STATUS_BANNER_CSS.read_text(encoding="utf-8")

    assert ".status-banner--deprecated" in content
    assert ".status-pill--deprecated" in content
    assert "body.quarto-dark .status-pill--deprecated" in content


def test_docs_styles_css_maintains_status_banner_parity() -> None:
    assert DOCS_STYLES_CSS.exists()
    content = DOCS_STYLES_CSS.read_text(encoding="utf-8")

    assert ".status-banner--deprecated" in content
    assert ".status-pill--deprecated" in content
    assert "body.quarto-dark .status-pill--deprecated" in content


def test_tangent_drafts_family_has_deprecation_metadata_and_banners() -> None:
    draft_files = [
        TANGENT_DRAFTS_DIR / "01_Tangent_Hyperplanes_I_Geometry.qmd",
        TANGENT_DRAFTS_DIR / "02_Tangent_Hyperplanes_II_Dynamics.qmd",
        TANGENT_DRAFTS_DIR / "03_Tangent_Hyperplanes_III_Control.qmd",
        GOLF_APPLICATION_MD,
    ]

    for draft in draft_files:
        assert draft.exists(), f"Expected draft file to exist: {draft}"
        text = draft.read_text(encoding="utf-8")

        # Must declare status: "deprecated" in frontmatter
        assert re.search(
            r'status:\s*["\']?deprecated["\']?', text
        ), f"Missing status: deprecated in {draft}"

        # Must declare canonical link
        assert re.search(
            r'canonical:\s*["\']?[^"\'\n]+["\']?', text
        ), f"Missing canonical link in {draft}"

        # Must have the semantic deprecation banner
        assert "status-banner--deprecated" in text, f"Missing status-banner--deprecated in {draft}"
        assert "status-badge--deprecated" in text, f"Missing status-badge--deprecated in {draft}"
