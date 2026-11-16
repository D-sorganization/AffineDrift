"""Guard tests for Geometry of Motion pedagogy gaps (#5604)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
VOL0_CH02 = REPO_ROOT / "articles/The_Geometry_of_Motion/quarto/vol0_ch02_state_space.qmd"
VOL0_CH01 = REPO_ROOT / "articles/The_Geometry_of_Motion/quarto/vol0_ch01_linear_algebra.qmd"
ROADMAP = REPO_ROOT / "books/roadmap.qmd"

QUARTO_EQ_LABEL = re.compile(r"\$\$\s*\{#(eq-[A-Za-z0-9_:-]+)\}")
EMPTY_SPAN_EQ = re.compile(r"\[\]\{#(eq-[A-Za-z0-9_:-]+)\}")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_5604_roadmap_lists_volume0_for_volumes_i_and_ii_prerequisites() -> None:
    text = _read(ROADMAP)
    assert "Volume 0" in text or "Mathematical Primer" in text
    table_rows = [line for line in text.splitlines() if line.startswith("| I —")]
    assert table_rows, "Volume I row missing from roadmap table"
    assert "Volume 0" in table_rows[0] or "Lie" in table_rows[0] or "rigid-body" in table_rows[0]
    table_ii = [line for line in text.splitlines() if line.startswith("| II —")]
    assert table_ii
    assert "Volume 0" in table_ii[0] or "SO(3)" in table_ii[0] or "rigid-body" in table_ii[0]


def test_5604_roadmap_control_and_cross_volume_paths_mention_volume0() -> None:
    text = _read(ROADMAP)
    control_block = text.split("### Control Theory and Robotics")[1].split("###")[0]
    cross_block = text.split("### Cross-Volume Study")[1].split("##")[0]
    assert "Volume 0" in control_block or "Mathematical Primer" in control_block
    assert "Volume 0" in cross_block


def test_5604_vol0_ch02_stability_observability_use_quarto_equation_labels() -> None:
    text = _read(VOL0_CH02)
    required = {
        "eq-state-jordan-example",
        "eq-state-pbh",
        "eq-observability-matrix",
    }
    found = set(QUARTO_EQ_LABEL.findall(text))
    missing = required - found
    assert not missing, f"Missing Quarto equation labels in ch02: {missing}"
    assert "[]{#eq-state_pbh}" not in text
    assert "[]{#eq-observability_matrix}" not in text


def test_5604_vol0_ch02_stability_theorem_is_numbered_callout() -> None:
    text = _read(VOL0_CH02)
    assert "::: {#thm-stability-classification}" in text
    chapter_one = _read(VOL0_CH01)
    assert "vol0_ch02_state_space.html#thm-stability-classification" in chapter_one
    assert "@thm-stability-classification" not in chapter_one


def test_5604_vol0_ch02_references_resolved_equations_in_prose() -> None:
    text = _read(VOL0_CH02)
    assert "@eq-state-pbh" in text
    assert "@eq-observability-matrix" in text


def test_5604_vol0_ch01_prose_worked_rank_eigen_svd_examples() -> None:
    text = _read(VOL0_CH01)
    assert "Worked Examples: Rank, Spectrum, and SVD" in text
    assert r"\operatorname{rank}M=2" in text
    assert r"(\lambda+2)(\lambda+3)" in text
    assert r"(1+\sqrt5)/2" in text


@pytest.mark.parametrize(
    "rel,forbidden_span",
    [
        (VOL0_CH02, "[]{#eq-state_pbh}"),
        (VOL0_CH02, "[]{#thm-stability}"),
    ],
)
def test_5604_vol0_no_stray_empty_span_anchors(rel: Path, forbidden_span: str) -> None:
    assert forbidden_span not in _read(rel)
