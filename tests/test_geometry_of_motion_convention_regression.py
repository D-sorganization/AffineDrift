"""Regression checks for Geometry of Motion conventions."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

REPO_ROOT = Path(__file__).resolve().parents[1]
CH01_FOUNDATIONS = (
    REPO_ROOT
    / "articles"
    / "The_Geometry_of_Motion"
    / "Volume_I"
    / "chapters"
    / "ch01_foundations.tex"
)


def test_ch01_se3_kinematics_uses_body_twist_convention() -> None:
    """Ensure Chapter 1 states body-frame convention for SE(3) kinematics."""

    text = CH01_FOUNDATIONS.read_text(encoding="utf-8")

    assert "twist (body\nvelocity)" in text
    assert "twist (spatial velocity)" not in text

    assert r"\dot{\mat{T}} = \mat{T} \, \begin{pmatrix}" in text


def test_ch01_time_varying_coordinate_change_reports_eigenvalue_caveat() -> None:
    """The chapter should not claim raw eigenvalue invariance under \\dot T terms."""

    text = CH01_FOUNDATIONS.read_text(encoding="utf-8")

    assert "If \\(\\dot{\\mat{T}}=0\\)" in text
    assert "When \\(\\dot{\\mat{T}}\\neq 0\\)" in text
    assert "raw eigenvalues can vary with coordinates" in text
