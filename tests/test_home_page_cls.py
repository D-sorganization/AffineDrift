"""Tests for Home Page CLS prevention (#5192).

Verifies that the primary visual asset on the homepage (.big-idea-graphic)
declares explicit intrinsic dimensions and CSS aspect-ratio to prevent
Cumulative Layout Shift (CLS) on desktop and mobile viewports.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_QMD = REPO_ROOT / "index.qmd"
HOME_HERO_CSS = REPO_ROOT / "css" / "components" / "home-hero.css"
DPC_SVG = REPO_ROOT / "pics" / "drift-plus-control-vector-field.svg"


class TestHomePageGraphicDimensions:
    """Ensure homepage hero graphic has explicit dimensions and aspect ratio."""

    def test_svg_viewbox_matches_expected_dimensions(self) -> None:
        """The source SVG must define a known viewBox from which aspect ratio derives."""
        assert DPC_SVG.is_file(), f"Missing graphic at {DPC_SVG}"
        content = DPC_SVG.read_text(encoding="utf-8")
        match = re.search(r'viewBox="([^"]+)"', content)
        assert match is not None, "viewBox attribute not found in SVG"
        viewbox = match.group(1)
        assert viewbox == "0 0 800 420", f"Unexpected viewBox: {viewbox}"

    def test_index_qmd_declares_width_and_height_attributes(self) -> None:
        """The <img> element in index.qmd must have explicit width and height attributes."""
        content = INDEX_QMD.read_text(encoding="utf-8")
        match = re.search(r'<img[^>]*class="[^"]*big-idea-graphic[^"]*"[^>]*>', content)
        assert match is not None, "Could not find <img> with class big-idea-graphic in index.qmd"
        img_tag = match.group(0)

        assert (
            'width="800"' in img_tag
        ), f'Missing width="800" attribute on big-idea-graphic: {img_tag}'
        assert (
            'height="420"' in img_tag
        ), f'Missing height="420" attribute on big-idea-graphic: {img_tag}'

    def test_home_hero_css_declares_aspect_ratio(self) -> None:
        """css/components/home-hero.css must declare aspect-ratio: 800 / 420 on .big-idea-graphic."""
        content = HOME_HERO_CSS.read_text(encoding="utf-8")
        assert ".big-idea-graphic" in content, "Missing .big-idea-graphic rule in home-hero.css"

        match = re.search(r"\.big-idea-graphic\s*\{([^}]+)\}", content)
        assert match is not None, "Could not parse .big-idea-graphic block in home-hero.css"
        block = match.group(1)

        assert (
            "aspect-ratio" in block
        ), "Missing aspect-ratio declaration in .big-idea-graphic block"
        aspect_match = re.search(r"aspect-ratio:\s*([^;]+);", block)
        assert aspect_match is not None
        val = aspect_match.group(1).replace(" ", "")
        assert val in (
            "800/420",
            "40/21",
            "1.90476",
            "1.9047619",
        ), f"Unexpected aspect-ratio value: {val}"
