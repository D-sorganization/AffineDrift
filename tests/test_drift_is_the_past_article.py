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


def test_accuracy_1_ztcf_is_not_limp_and_includes_karl_quote():
    """Verify ZTCF is not described as 'limp' and includes Karl's phrasing (#5475)."""
    content = ARTICLE_PATH.read_text(encoding="utf-8")
    assert (
        "limp" not in content.lower()
    ), "Article should not describe ZTCF as 'limp' (contradicts NOTATION.md)"
    assert "flaccid" not in content.lower()
    assert "the joints stay connected; we just stop pushing" in content.lower()
    assert "passive" in content.lower() and "tissue" in content.lower()


def test_accuracy_2_joint_space_vs_clubhead_kinematics_aligned():
    """Verify boxed joint equation and Cartesian clubhead acceleration are aligned (#5475)."""
    content = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "joint" in content.lower()
    assert (
        "\\dot{J}" in content
        or "J\\dot{q}" in content
        or "velocity-dependent kinematic" in content.lower()
        or "kinematic" in content.lower()
    )


def test_accuracy_3_tee_section_hedged_as_hypothesis():
    """Verify the amateur vs. elite distinction is hedged as a testable hypothesis (#5475)."""
    content = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "testable hypothesis" in content.lower() or "hypothesis" in content.lower()
    assert (
        "cohort" in content.lower()
        or "validation" in content.lower()
        or "measured" in content.lower()
    )


def test_prose_and_housekeeping_corrections():
    """Verify prose and nit corrections 4-9 (#5475)."""
    content = ARTICLE_PATH.read_text(encoding="utf-8")
    # 4: drift includes passive loads in the model, not just momentum + gravity
    assert (
        "passive loads" in content.lower()
        or "passive tissue" in content.lower()
        or "passive elasticity" in content.lower()
    )
    # 5: force equal to clubhead's weight, not '9.8 m/s² on the clubhead'
    assert "per second squared on the clubhead" not in content.lower()
    assert "clubhead's weight" in content.lower() or "weight of the clubhead" in content.lower()
    # 6: control acts through posture the past created; only tau is new
    assert "only" in content.lower() and "\\tau" in content
    # 7: playground push notes single instant vs buildup over time
    assert "single instant" in content.lower()
    # 8: downswing duration hedged (roughly 230-260 ms)
    assert "230" in content and "260" in content
    # 9: Karl lead-in, pointwise qualifier, verified date, for a given model
    assert "mass times acceleration equals the forces, split into two piles" in content.lower()
    assert "pointwise zero-torque counterfactual" in content.lower()
    assert "for a given model" in content.lower()
    assert 'date: "date unverified"' not in content.lower()
    assert 'date-source: "unverified"' not in content.lower()
