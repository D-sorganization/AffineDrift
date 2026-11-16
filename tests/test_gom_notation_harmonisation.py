"""Regression tests for Geometry of Motion notation harmonisation (#5602)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def test_control_is_motion_transverse_uses_et_not_projector_as_coordinates() -> None:
    text = _read("books/control-is-motion.qmd")
    assert "z = E(t)^T" in text
    assert "z = P(t)" not in text


def test_ch03b_uses_hm_not_p_for_constrained_acceleration_operator() -> None:
    text = _read(
        "articles/The_Geometry_of_Motion/quarto/ch03b_induced_acceleration_biomechanics.qmd"
    )
    assert r"\mathcal{H}_M" in text
    assert r"P&=M^{-1}-M^{-1}A^{\mathsf T}W^{-1}AM^{-1}" not in text
    assert r"\mathcal{H}_M Q_0" in text


def test_ch03b_singular_operational_inertia_uses_kc_not_w() -> None:
    text = _read(
        "articles/The_Geometry_of_Motion/quarto/ch03b_induced_acceleration_biomechanics.qmd"
    )
    assert "inverting singular $K_c$" in text
    assert "inverting singular $W$" not in text


def test_ch03b_gamma_sign_matches_notation_registry() -> None:
    text = _read(
        "articles/The_Geometry_of_Motion/quarto/ch03b_induced_acceleration_biomechanics.qmd"
    )
    assert r"J_c\dot v=-\gamma" in text
    assert r"\gamma=\dot J_c v" in text
    assert r"\gamma=-\dot J_c v" not in text
    assert r"J_c\ddot q=\gamma" not in text
    assert r"a_c&=-M^{-1}J_c^{\mathsf T}K_c^{-1}\gamma" in text


def test_ch07_constrained_symbols_match_ch09_registry() -> None:
    text = _read("articles/The_Geometry_of_Motion/quarto/ch07_counterfactuals.qmd")
    assert r"J_c\dot v=-\gamma" in text
    assert r"P_v=I-M^{-1}J_c^T" in text
    assert r"A\dot v=-b" not in text


def test_notation_md_documents_gom_constrained_projector_split() -> None:
    text = _read("NOTATION.md")
    assert "Geometry of Motion Notation" in text
    assert r"\mathcal{H}_M" in text
    assert r"\Pi_M" in text


@pytest.mark.parametrize(
    "rel",
    [
        "articles/The_Geometry_of_Motion/quarto/vol0_ch04_rotations_se3.qmd",
        "articles/The_Geometry_of_Motion/quarto/vol0_ch05_screw_axes.qmd",
        "articles/The_Geometry_of_Motion/quarto/vol0_ch06_exponential_coordinates.qmd",
    ],
)
def test_volume0_rotation_chapters_include_notation_note(rel: str) -> None:
    assert "gom_rotation_notation_note.qmd" in _read(rel)
