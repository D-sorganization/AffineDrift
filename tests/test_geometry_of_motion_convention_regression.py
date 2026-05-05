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
CH07_RECURSIVE_ALGORITHMS = (
    REPO_ROOT
    / "articles"
    / "The_Geometry_of_Motion"
    / "Volume_0"
    / "chapters"
    / "ch07_recursive_algorithms.tex"
)


def test_ch01_se3_kinematics_uses_body_twist_convention() -> None:
    """Ensure Chapter 1 states body-frame convention for SE(3) kinematics."""

    text = CH01_FOUNDATIONS.read_text(encoding="utf-8")

    assert "twist (body\nvelocity)" in text
    assert "twist (spatial velocity)" not in text

    assert r"\dot{\mat{T}} = \mat{T} \, \begin{pmatrix}" in text


def test_ch07_humanoid_parent_array_examples_match_their_descriptions() -> None:
    """Humanoid examples should describe the same topology encoded by the parent arrays."""

    text = CH07_RECURSIVE_ALGORITHMS.read_text(encoding="utf-8")

    assert r"\lambda = [-1, 0, 1, 0, 3, 0, \ldots]" in text
    assert "with link 0 as the pelvis, links 1-2 the left leg, links 3-4 the right leg," in text
    assert "link 5 the torso, etc." in text

    assert "A humanoid robot with a main body/torso (link 0), two legs (links 1–2 and 3–4)," in text
    assert "and two arms (links 5–7 and 8–10) has the parent array:" in text
    assert r"In the inward pass, when computing $\mathcal{F}_0$ (torso wrench), we sum:" in text
