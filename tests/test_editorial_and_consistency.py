"""Unit tests validating roadmap status, chapter mapping consistency, and editorial cleanliness (Issues #3922, #3921, #3920)."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_development_roadmap_consistency():
    """Verify the roadmap uses live authorities instead of stale progress claims."""
    roadmap = (REPO_ROOT / "pages" / "development-roadmap.qmd").read_text(encoding="utf-8")
    prose = " ".join(roadmap.split())

    assert "This page is an evergreen map, not a schedule or progress meter" in prose
    assert "Protected merge history is the authority for delivered changes" in prose
    assert "Dates, percentages, and promises are intentionally omitted" in prose
    assert "## State Contract" in roadmap
    assert "#4021" in roadmap
    assert "#4063" in roadmap
    assert "8cc236c6879e7535bb6bd15aecbe3396fb6dbb36" in roadmap

    # Stale schedule and hand-maintained completion claims stay out of the page.
    assert re.search(r"\bQ[1-4]\s+20\d{2}\b", roadmap) is None
    assert re.search(r"\b\d{1,3}%\s+complete\b", roadmap, re.IGNORECASE) is None
    assert "chapters complete" not in roadmap

    # Clean formatting / no undefined icons or raw check ticks
    assert "🟠" not in roadmap
    assert "✓ [x]" not in roadmap
    assert "research-reviews.qmd" not in roadmap


def test_volume1_chapter_mapping():
    """Verify Volume I chapter mapping in books/tangent-space-methods.qmd (Issue #3921)."""
    book1 = (REPO_ROOT / "books" / "tangent-space-methods.qmd").read_text(encoding="utf-8")

    # Check all 8 chapter sources
    for i in range(1, 9):
        assert f"## Chapter {i}:" in book1

    assert "ch01_foundations.tex" in book1
    assert "ch02_variational.tex" in book1
    assert "ch03_superposition.tex" in book1
    assert "ch04_contraction.tex" in book1
    assert "ch05_optimal_control.tex" in book1
    assert "ch06_duality.tex" in book1
    assert "ch07_counterfactuals.tex" in book1
    assert "ch08_applications.tex" in book1

    # Check chapter titles
    assert "Foundations: Tangent Spaces and Exactness" in book1
    assert "Variational Dynamics and the Moving Frame" in book1
    assert "Superposition: From Linear to Affine" in book1
    assert "Contraction Theory and Metric Certificates" in book1
    assert "Local Optimal Control: LQR, DDP, and Riccati" in book1
    assert "The Stability–Optimality Duality" in book1
    assert "Forward Dynamics, Counterfactuals, and Drift" in book1
    assert "Applications: Biomechanics, Robotics, and Beyond" in book1

    # Check only single View LaTeX Source link (no duplicate View Source Manuscript)
    assert book1.count("Volume_I/main.tex") == 1


def test_phantom_section_references_resolved():
    """Verify phantom section references have been replaced with descriptive titles/anchors (Issue #3921)."""
    inv_dyn = (REPO_ROOT / "articles" / "inverse-dynamics.qmd").read_text(encoding="utf-8")
    assert "Section 4 - often significant" not in inv_dyn
    assert "Section 2):" not in inv_dyn
    assert "Section 3):" not in inv_dyn
    assert "Section 4):" not in inv_dyn
    assert "(§2)" not in inv_dyn
    assert "(§3)" not in inv_dyn
    assert "(§4)" not in inv_dyn

    affine = (REPO_ROOT / "articles" / "affine-nature-golf-swing.qmd").read_text(encoding="utf-8")
    assert "made in Section 2" not in affine
    assert "@sec-assumptions" in affine

    manifesto = (REPO_ROOT / "articles" / "drifter-manifesto.qmd").read_text(encoding="utf-8")
    assert "**Section 1** defines" not in manifesto
    assert "**Section 2** derives" not in manifesto
    assert "**Section 3** formalizes" not in manifesto
    assert "**Part 1** defines" in manifesto


def test_empty_cross_reference_targets_resolved():
    """Verify empty cross-reference targets and adjacent headings are resolved (Issue #3921)."""
    proximal = (REPO_ROOT / "articles" / "proximal-distal-energy-transfer.qmd").read_text(
        encoding="utf-8"
    )
    # sec-methods should have body prose directly following it
    match = re.search(r"# Computational Methods \{#sec-methods\}\s*\n+([^\n#]+)", proximal)
    assert match is not None, "sec-methods heading must have direct body prose"
    assert "numerical analyses use an open-source" in match.group(1)

    affine = (REPO_ROOT / "articles" / "affine-nature-golf-swing.qmd").read_text(encoding="utf-8")
    assert "### Modeling Assumptions {#sec-assumptions}\n\n## Modeling Assumptions" not in affine
    assert "## Modeling Assumptions for the Theoretical Framework {#sec-assumptions}" in affine
    assert "## Appendices {.appendix}\n\n## Mathematical Derivations" not in affine


def test_editorial_residue_resolved():
    """Verify duplicate notices, maintainer notes, and tracker numbers are eliminated (Issue #3920)."""
    affine = (REPO_ROOT / "articles" / "affine-nature-golf-swing.qmd").read_text(encoding="utf-8")
    assert "## Duplicate Content Notice" not in affine
    assert "Foundational Monograph" in affine

    manifesto = (REPO_ROOT / "articles" / "drifter-manifesto.qmd").read_text(encoding="utf-8")
    assert (
        "substantive edits should be made there and mirrored here."
        not in manifesto.replace("<!--", "").replace("-->", "")
        or "<!--" in manifesto
    )
    assert "experimental application..." not in manifesto

    theory3 = (REPO_ROOT / "articles" / "theory-part3.qmd").read_text(encoding="utf-8")
    assert "experimental application..." not in theory3

    # Revision History callouts removed from reader prose
    dcr = (REPO_ROOT / "articles" / "controllability-drift-ratio.qmd").read_text(encoding="utf-8")
    assert "## Revision History" not in dcr

    sec_axis = (REPO_ROOT / "articles" / "secondary-axis-stability.qmd").read_text(encoding="utf-8")
    assert "## Revision History" not in sec_axis

    # Sprint issue numbers in research prose
    proximal = (REPO_ROOT / "articles" / "proximal-distal-energy-transfer.qmd").read_text(
        encoding="utf-8"
    )
    for epic in ["#8684", "#8751", "#8505", "#8507", "#8497", "#8499"]:
        assert epic not in proximal, f"Epic {epic} found in proximal-distal-energy-transfer.qmd"

    ud_integration = (
        REPO_ROOT / "articles" / "upstreamdrift-educational-integration.qmd"
    ).read_text(encoding="utf-8")
    assert "#7431" not in ud_integration

    green = (REPO_ROOT / "articles" / "green-simulation.qmd").read_text(encoding="utf-8")
    assert "#3777" not in green
    assert "#4125" not in green

    # Author voice
    about = (REPO_ROOT / "pages" / "about.qmd").read_text(encoding="utf-8")
    assert "Human in the loop: Dieter Olson." not in about

    # Developer task comment
    overview = (REPO_ROOT / "pages" / "overview.qmd").read_text(encoding="utf-8")
    assert "#3338" not in overview

    # Unifying geometry phrasing
    tech = (REPO_ROOT / "pages" / "technology.qmd").read_text(encoding="utf-8")
    assert "These three instruments measure dual halves" not in tech
