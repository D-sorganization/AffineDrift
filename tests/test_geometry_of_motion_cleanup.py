"""Regression checks for Geometry of Motion Quarto source cleanup (#2319)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT = Path(__file__).resolve().parents[1]
QUARTO_DIR = ROOT / "articles" / "The_Geometry_of_Motion" / "quarto"

EXPECTED_VOLUME0_FILES = {
    "vol0_ch01_linear_algebra.qmd",
    "vol0_ch02_state_space.qmd",
    "vol0_ch03_configuration.qmd",
    "vol0_ch04_rotations_se3.qmd",
    "vol0_ch05_screw_axes.qmd",
    "vol0_ch06_exponential_coordinates.qmd",
    "vol0_ch07_recursive_algorithms.qmd",
    "vol0_ch08_spatial_algebra.qmd",
    "vol0_ch09_product_of_exponentials.qmd",
    "vol0_ch10_articulated_body_algorithm.qmd",
    "vol0_ch11_lagrangian_mechanics.qmd",
    "vol0_ch12_machine_learning.qmd",
}


def test_volume0_chapter_files_match_the_canonical_include_set() -> None:
    """Volume 0 should only keep the chapter files that the index includes."""
    actual = {path.name for path in QUARTO_DIR.glob("vol0_ch*.qmd")}
    assert actual == EXPECTED_VOLUME0_FILES
    text = (QUARTO_DIR / "volume0.qmd").read_text(encoding="utf-8")
    for filename in EXPECTED_VOLUME0_FILES:
        assert f"{{{{< include {filename} >}}}}" in text


def test_volume2_is_monolithic_and_has_no_split_qmd_duplicates() -> None:
    """Volume II should render from the monolithic content file only."""
    text = (QUARTO_DIR / "volume2.qmd").read_text(encoding="utf-8")
    assert "{{< include volume2_content.qmd >}}" in text
    assert not any((QUARTO_DIR / "vol2").glob("*.qmd"))
