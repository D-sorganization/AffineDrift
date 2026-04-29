"""Regression tests for Coriolis notation consistency."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAPTER_3 = REPO_ROOT / "articles/The_Geometry_of_Motion/Volume_I/chapters/ch03_superposition.tex"
CHAPTER_7 = REPO_ROOT / "articles/The_Geometry_of_Motion/Volume_I/chapters/ch07_counterfactuals.tex"
CHAPTER_8 = REPO_ROOT / "articles/The_Geometry_of_Motion/Volume_I/chapters/ch08_applications.tex"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_chapter_3_uses_matrix_notation_for_coriolis_term() -> None:
    text = _read(CHAPTER_3)
    assert r"\mat{C}(\q,\dot\q)\dot\q" in text
    assert r"C(\q,\dot\q)\dot\q" not in text


def test_chapter_7_uses_matrix_notation_for_coriolis_term() -> None:
    text = _read(CHAPTER_7)
    assert r"\mat{C}(\q,\dot\q)\dot\q" in text
    assert r"C(\q,\dot\q)\dot\q" not in text


def test_chapter_8_keeps_the_same_convention() -> None:
    text = _read(CHAPTER_8)
    assert r"\mat{C}\dot\q_{\text{sys}}" in text
