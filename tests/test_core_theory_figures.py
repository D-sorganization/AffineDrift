"""Tests for Core Theory static figure generation and article embedding."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts import build_core_theory_figures

REPO_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = REPO_ROOT / "articles/figures/core_theory"

ARTICLE_FIGURE_MAP = {
    "articles/drift-control-ratio.qmd": [
        "fig_dcr_vector_decomposition.svg",
        "fig_dcr_swing_phases.svg",
        "fig_dcr_reachability_tubes.svg",
    ],
    "articles/zero-torque-counterfactual.qmd": [
        "fig_ztcf_trajectory_divergence.svg",
        "fig_ztcf_clubhead_speed_loss.svg",
        "fig_ztcf_passive_dynamics_attribution.svg",
    ],
    "articles/superposition.qmd": [
        "fig_superposition_decomposition.svg",
        "fig_superposition_modal_response.svg",
        "fig_superposition_breakdown_boundary.svg",
    ],
}


def test_all_expected_figures_exist_and_within_budget() -> None:
    """All 9 core theory figures must exist and remain well under the 500 KB budget."""
    assert FIGURES_DIR.is_dir(), f"Missing directory: {FIGURES_DIR}"

    for fig_name in build_core_theory_figures.FIGURE_NAMES:
        fig_path = FIGURES_DIR / fig_name
        assert fig_path.is_file(), f"Missing figure file: {fig_path}"
        size = fig_path.stat().st_size
        assert size > 0, f"Figure is empty: {fig_path}"
        # Assert within 500 KB budget (and specifically < 150 KB for our clean SVGs)
        assert size < 500 * 1024, f"Figure exceeds 500KB budget ({size} bytes): {fig_path}"
        assert size < 150 * 1024, f"SVG unexpectedly large ({size} bytes): {fig_path}"

        # Verify basic SVG structure
        content = fig_path.read_text(encoding="utf-8")
        assert "<svg" in content, f"Invalid SVG root tag in {fig_path}"
        assert "</svg>" in content, f"Missing closing </svg> tag in {fig_path}"


def test_build_core_theory_figures_check_passes() -> None:
    """The --check validation function must return True for the generated figures."""
    assert build_core_theory_figures.check_figures(FIGURES_DIR) is True


@pytest.mark.parametrize("article_rel_path,expected_figures", list(ARTICLE_FIGURE_MAP.items()))
def test_articles_reference_at_least_three_figures(
    article_rel_path: str,
    expected_figures: list[str],
) -> None:
    """Each core theory article must reference at least 3 distinct figures."""
    article_path = REPO_ROOT / article_rel_path
    assert article_path.is_file(), f"Article missing: {article_path}"
    content = article_path.read_text(encoding="utf-8")

    for fig_name in expected_figures:
        assert fig_name in content, f"Article {article_rel_path} does not reference {fig_name}"

    # Verify at least 3 figure references exist in total
    total_fig_refs = [fig for fig in build_core_theory_figures.FIGURE_NAMES if fig in content]
    assert (
        len(total_fig_refs) >= 3
    ), f"Expected >= 3 figures in {article_rel_path}, found {len(total_fig_refs)}"


@pytest.mark.parametrize("article_rel_path,expected_figures", list(ARTICLE_FIGURE_MAP.items()))
def test_figures_have_accessible_alt_text_and_captions(
    article_rel_path: str,
    expected_figures: list[str],
) -> None:
    """All figures must include non-empty captions and accessible fig-alt descriptions."""
    article_path = REPO_ROOT / article_rel_path
    content = article_path.read_text(encoding="utf-8")

    for fig_name in expected_figures:
        # Pattern matching: ![Caption](...fig_name...){...fig-alt="..."...}
        # or <img ... src="...fig_name..." alt="..." ...>
        escaped_name = re.escape(fig_name)
        md_pattern = re.compile(
            r"!\[([^\]]+)\]\([^\)]*" + escaped_name + r"[^\)]*\)\{[^\}]*fig-alt=\"([^\"]+)\"",
            re.DOTALL,
        )
        html_pattern = re.compile(
            r"<img[^>]*src=\"[^\"]*" + escaped_name + r"\"[^>]*alt=\"([^\"]+)\"",
            re.DOTALL,
        )

        md_match = md_pattern.search(content)
        html_match = html_pattern.search(content)

        assert (
            md_match is not None or html_match is not None
        ), f"Figure {fig_name} in {article_rel_path} lacks proper caption or fig-alt attribute."

        if md_match:
            caption, alt_text = md_match.groups()
            assert len(caption.strip()) > 10, f"Caption too short for {fig_name}"
            assert len(alt_text.strip()) > 20, f"fig-alt too short for {fig_name}"
        elif html_match:
            alt_text = html_match.group(1)
            assert len(alt_text.strip()) > 20, f"alt text too short for {fig_name}"
