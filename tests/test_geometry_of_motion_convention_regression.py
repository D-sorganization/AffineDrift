"""Regression checks for Geometry of Motion conventions."""

from __future__ import annotations

import re
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


def test_ch07_parent_array_matches_the_described_branch_in_both_editions() -> None:
    """The illustrated siblings and descendant must match the encoded tree."""
    web = CH07_RECURSIVE_ALGORITHMS.parents[2] / "quarto/vol0_ch07_recursive_algorithms.qmd"
    for source in (CH07_RECURSIVE_ALGORITHMS, web):
        text = source.read_text(encoding="utf-8")
        match = re.search(r"\\lambda=\((\d+(?:,\d+)+)\).*?four moving bodies", text)
        assert match is not None
        parents = [int(value) for value in match[1].split(",")]
        children = {
            parent: [child for child, value in enumerate(parents, 1) if value == parent]
            for parent in range(len(parents) + 1)
        }
        assert all(parent < child for child, parent in enumerate(parents, 1))
        assert children == {0: [1], 1: [2, 3], 2: [], 3: [4], 4: []}
        assert "bodies 2 and 3 branch from body 1" in text
        assert "body 4 attaches to body 3" in text
