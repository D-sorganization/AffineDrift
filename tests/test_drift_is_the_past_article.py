"""Contract tests for 'Drift Is the Past, Control Is the Present' (#5440).

Verifies prose contracts, structural elements, Dieter's definitions,
caveats, and terminology baselines.
"""

import re
from pathlib import Path

ARTICLE_PATH = (
    Path(__file__).parent.parent / "articles" / "drift-is-the-past-control-is-the-present.qmd"
)


def test_article_exists_and_frontmatter_valid():
    """Verify article file exists and has conforming Quarto frontmatter."""
    assert ARTICLE_PATH.exists(), f"Missing article: {ARTICLE_PATH}"
    content = ARTICLE_PATH.read_text(encoding="utf-8")
    assert content.startswith("---")
    assert 'title: "Drift Is the Past, Control Is the Present' in content
    assert 'canonical: "/articles/drift-is-the-past-control-is-the-present.html"' in content
    assert "categories:" in content
    assert "theory-core" in content


def test_dieter_definitions_and_single_equation():
    """Verify Dieter's definitions (ZTCF=drift, ZVCF=control) and single equation box."""
    content = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "Zero-Torque Counterfactual (ZTCF)" in content
    assert "Zero-Velocity Counterfactual (ZVCF)" in content
    assert "M^{-1}\\tau" in content or "M(q)^{-1} \\tau" in content
    assert "ZTCF + ZVCF = Total Acceleration" in content or "ZTCF + ZVCF" in content

    # Exactly one displayed equation block ($$...$$)
    displayed_equations = re.findall(r"\$\$.*?\$\$", content, flags=re.DOTALL)
    assert (
        len(displayed_equations) == 1
    ), f"Expected at most 1 displayed equation in callout box, found {len(displayed_equations)}"
    assert "Drift (ZTCF)" in displayed_equations[0]
    assert "Control (ZVCF)" in displayed_equations[0]


def test_essential_caveats_present():
    """Verify the instantaneous snapshot vs diverging integrated trajectories caveat."""
    content = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "Snapshots Add; Movies Diverge" in content
    assert "do not add up" in content or "do not sum" in content
    assert "Passive Does Not Mean Free" in content
    assert "Not a Direct Muscle Effort Audit" in content


def test_two_lenses_and_gravity_resolution():
    """Verify Active/Passive vs Time lens and the gravity posture resolution."""
    content = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "Two Lenses on the Same Swing" in content
    assert "The Gravity Question" in content
    assert (
        "posture is a creation of the past" in content
        or "posture created by past motion" in content
    )
    assert "Table 1: Reconciling the two lenses" in content


def test_analogies_and_figures_with_alt_text():
    """Verify everyday analogies and figures with required alt text."""
    content = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "coasting car" in content.lower() or "mountain road" in content.lower()
    assert "playground swing" in content.lower()
    assert "fig-alt=" in content
    assert "fig-vector-split" in content
    assert "fig-divergence" in content
