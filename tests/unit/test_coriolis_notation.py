"""Regression tests for Coriolis notation consistency."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAPTER_3 = REPO_ROOT / "articles/The_Geometry_of_Motion/Volume_I/chapters/ch03_superposition.tex"
CHAPTER_3_WEB = REPO_ROOT / "articles/The_Geometry_of_Motion/quarto/ch03_superposition.qmd"
CHAPTER_7 = REPO_ROOT / "articles/The_Geometry_of_Motion/Volume_I/chapters/ch07_counterfactuals.tex"
CHAPTER_8 = REPO_ROOT / "articles/The_Geometry_of_Motion/Volume_I/chapters/ch08_applications.tex"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", [CHAPTER_3, CHAPTER_3_WEB])
def test_chapter_3_distinguishes_force_vector_from_coriolis_matrix(path: Path) -> None:
    text = _read(path)
    assert r"$Cv=c$" in text
    assert r"c=\beta\sin q_2\begin{bmatrix}-2v_1v_2-v_2^2\\v_1^2\end{bmatrix}" in text
    assert r"C=\begin{bmatrix}-hv_2&-h(v_1+v_2)\\hv_1&0\end{bmatrix}" in text
    assert r"$v^Tc=\tfrac12v^T\dot Mv$" in text


def test_chapter_7_uses_matrix_notation_for_coriolis_term() -> None:
    text = _read(CHAPTER_7)
    assert r"\mat{C}(\q,\dot\q)\dot\q" in text
    assert r"C(\q,\dot\q)\dot\q" not in text


def test_chapter_8_keeps_the_same_convention() -> None:
    text = _read(CHAPTER_8)
    assert r"\mat{C}\dot\q_{\text{sys}}" in text
