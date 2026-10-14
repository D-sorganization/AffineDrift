"""Test the drift-plus-control vector field graphic (WEB-08.2 #4554).

Verifies that the signature explanatory SVG:
- Is valid XML/SVG with required accessibility attributes
- Contains all required vector labels and state annotations
- Supports light and dark themes via CSS custom properties
- Is properly embedded in the start-here page
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from tests.helpers.entry_pages import ROOT, page_text

SVG_PATH = ROOT / "images" / "drift-plus-control-vector-field.svg"


def test_svg_file_exists() -> None:
    """SVG should exist at the canonical path."""
    assert SVG_PATH.exists(), f"SVG not found at {SVG_PATH}"


def test_svg_parses_as_valid_xml() -> None:
    """SVG must be well-formed XML."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    try:
        ET.fromstring(svg_content)  # noqa: S314 -- trusted repo SVG
    except ET.ParseError as e:
        raise AssertionError(f"SVG is not valid XML: {e}") from e


def test_svg_has_correct_namespace_and_viewbox() -> None:
    """SVG must have xmlns and viewBox attributes."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    root = ET.fromstring(svg_content)  # noqa: S314 -- trusted repo SVG
    assert (
        root.tag == "{http://www.w3.org/2000/svg}svg"
    ), "Root element must be SVG with correct namespace"
    assert "viewBox" in root.attrib, "SVG must have viewBox attribute"
    assert root.get("viewBox") == "0 0 800 420", "viewBox should match specification"


def test_svg_has_accessibility_attributes() -> None:
    """SVG must have role and aria-labelledby for accessibility."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    root = ET.fromstring(svg_content)  # noqa: S314 -- trusted repo SVG
    assert root.get("role") == "img", "SVG must have role='img'"
    aria_labelledby = root.get("aria-labelledby")
    assert aria_labelledby, "SVG must have aria-labelledby attribute"
    assert "dpc-title" in aria_labelledby, "aria-labelledby should reference title"
    assert "dpc-desc" in aria_labelledby, "aria-labelledby should reference description"


def test_svg_has_title_and_description() -> None:
    """SVG must have <title> and <desc> elements with correct ids and content."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    assert (
        '<title id="dpc-title">Drift Plus Control Vector Field Decomposition</title>' in svg_content
    ), "Missing or incorrect <title> element"
    assert '<desc id="dpc-desc">' in svg_content, "Missing <desc> element with id 'dpc-desc'"
    assert (
        "State-space diagram" in svg_content
        and "drift vector" in svg_content
        and "control push vector" in svg_content
        and "dx/dt = f(x) + G(x)u" in svg_content
    ), "Description must explain the diagram components"


def test_svg_has_drift_vector_label() -> None:
    """SVG must label the drift vector f(x) clearly."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    assert "f(x)" in svg_content, "SVG must label drift vector as f(x)"
    assert (
        'class="dpc-drift-label"' in svg_content
    ), "Drift label should have appropriate styling class"


def test_svg_has_control_vector_label() -> None:
    """SVG must label the control vector G(x)u clearly."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    assert "G(x)u" in svg_content, "SVG must label control vector as G(x)u"
    assert (
        'class="dpc-control-label"' in svg_content
    ), "Control label should have appropriate styling class"


def test_svg_has_total_velocity_vector_label() -> None:
    """SVG must label the resultant dx/dt vector."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    assert "dx/dt" in svg_content, "SVG must label total velocity as dx/dt"
    assert (
        'class="dpc-total-label"' in svg_content
    ), "Total velocity label should have appropriate styling class"


def test_svg_has_canonical_equation() -> None:
    """SVG must display the canonical control equation."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    assert "dx/dt = f(x) + G(x)u" in svg_content, "SVG must display the fundamental equation"


def test_svg_shows_state_point_annotation() -> None:
    """SVG must annotate the state point x(t₀) in the late downswing."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    assert (
        "x(t₀)" in svg_content or "x(t" in svg_content
    ), "SVG must annotate the evaluation state point"


def test_svg_supports_dark_theme() -> None:
    """SVG must support dark theme via @media or [data-bs-theme] selectors."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    has_prefers_color_scheme = "@media (prefers-color-scheme: dark)" in svg_content
    has_bs_theme_selector = '[data-bs-theme="dark"]' in svg_content
    assert has_prefers_color_scheme or has_bs_theme_selector, "SVG must support dark theme via CSS"
    assert "var(--ad-" in svg_content, "SVG should use CSS custom properties for colors"


def test_svg_uses_css_custom_properties_with_fallbacks() -> None:
    """SVG colors should use CSS custom properties with high-contrast fallbacks."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    assert (
        "var(--ad-fg," in svg_content or "var(--ad-" in svg_content
    ), "SVG must use CSS custom properties for accessibility"
    # Should have fallback colors
    assert "#" in svg_content, "SVG should have hex color fallbacks"


def test_svg_is_mobile_responsive() -> None:
    """SVG must include media queries for mobile viewports."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    assert "@media (max-width:" in svg_content, "SVG should have mobile responsive design rules"


def test_svg_has_trajectory_curve() -> None:
    """SVG must show the nominal swing trajectory x(t)."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    assert "trajectory" in svg_content.lower(), "SVG should depict the swing trajectory"
    assert 'class="dpc-trajectory"' in svg_content, "Trajectory should have appropriate styling"


def test_svg_shows_ztcf_rollout() -> None:
    """SVG must show the dashed Zero-Torque Counterfactual trajectory."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    assert (
        "ZTCF" in svg_content or "rollout" in svg_content.lower()
    ), "SVG should indicate the zero-control outcome"
    assert 'class="dpc-ztcf-trajectory"' in svg_content, "ZTCF should have dashed-line styling"


def test_start_here_qmd_references_the_svg() -> None:
    """start-here.qmd must embed the drift-plus-control SVG."""
    qmd_content = page_text("pages/start-here.qmd")
    assert (
        "drift-plus-control-vector-field.svg" in qmd_content
    ), "start-here.qmd must reference the SVG"
    assert (
        "images/" in qmd_content or "../images/" in qmd_content
    ), "SVG should be referenced with correct path"


def test_start_here_contains_big_idea_section() -> None:
    """start-here.qmd must still have the required 'Big Idea' section."""
    qmd_content = page_text("pages/start-here.qmd")
    assert "## The Big Idea in One Picture" in qmd_content, "Section heading must be present"


def test_svg_has_vector_addition_concept() -> None:
    """SVG must visually explain vector addition of drift + control."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    # Should show both drift and control vectors originating from the same point
    drift_count = svg_content.count('class="dpc-drift-vector"')
    control_count = svg_content.count('class="dpc-control-vector"')
    total_count = svg_content.count('class="dpc-total-vector"')
    assert (
        drift_count >= 1 and control_count >= 1 and total_count >= 1
    ), "SVG must show drift, control, and resultant vectors"


def test_svg_axes_are_labeled() -> None:
    """SVG coordinate axes should be clearly labeled."""
    svg_content = SVG_PATH.read_text(encoding="utf-8")
    # Check for axis labels or state-space references
    assert "state" in svg_content.lower() or "x(t" in svg_content, "SVG should label the state axis"


def test_start_here_markdown_has_descriptive_alt_text() -> None:
    """SVG embedding in start-here.qmd should have descriptive alt text."""
    qmd_content = page_text("pages/start-here.qmd")
    # Look for alt text pattern in markdown image syntax
    assert "![" in qmd_content, "Markdown figure syntax should be present"
    # The alt text should describe the diagram content
    svg_section = qmd_content[
        qmd_content.find("drift-plus-control") - 500 : qmd_content.find("drift-plus-control") + 200
    ]
    assert any(
        phrase in svg_section.lower() for phrase in ["vector", "drift", "control", "trajectory"]
    ), "Alt text should describe the diagram meaningfully"
