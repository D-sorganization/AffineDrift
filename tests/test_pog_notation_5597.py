"""Regression checks for Physics of Golf notation harmonization (Refs #5597)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
POG = ROOT / "articles" / "The_Physics_of_Golf"
NOTATION = ROOT / "NOTATION.md"

CH08 = (
    POG / "quarto" / "ch08_triple_pendulum.qmd",
    POG / "chapters" / "ch08_triple_pendulum.tex",
)
CH10 = (
    POG / "quarto" / "ch10_energy_transfer.qmd",
    POG / "chapters" / "ch10_energy_transfer.tex",
)
CH25 = (
    POG / "quarto" / "ch25_motor_learning.qmd",
    POG / "chapters" / "ch25_motor_learning.tex",
)

COM_DISTANCE_IN_CH08 = re.compile(r"m_[123]c_[123]|m_[123]L_[12]c_[23]")
GRAVITY_UPPERCASE_EOM = re.compile(r"M\\ddot\s*q\+h\+G")
DELIVERY_MAP_G = re.compile(r"\\bm\{y\}=G\(\\bm\{x\}")
AFFINE_B_INPUT = re.compile(r"\\bm\{f\}\(\\bm\{x\}\)\+B\(\\bm\{x\}\)\\bm\{u\}")


@pytest.mark.parametrize("path", CH08)
def test_ch08_com_distances_use_r_not_c(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert COM_DISTANCE_IN_CH08.search(text) is None
    assert "m_3r_3" in text
    assert re.search(r"c_3=\\beta", text) is not None


@pytest.mark.parametrize("path", CH10)
def test_ch10_gravity_vector_is_lowercase_g(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert GRAVITY_UPPERCASE_EOM.search(text) is None
    assert re.search(r"M\\ddot\s*q\+h\+g=\\tau", text) is not None


@pytest.mark.parametrize("path", CH25)
def test_ch25_reserves_uppercase_g_for_input_map(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert DELIVERY_MAP_G.search(text) is None
    assert AFFINE_B_INPUT.search(text) is None
    assert "\\mathcal{D}(\\bm{x},c)" in text
    assert "\\bm{G}(\\bm{x})\\bm{u}" in text


def test_notation_documents_pog_part_i_table() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "Physics of Golf Part I Multibody Symbols" in text
    assert "| **$r_i$** | COM distance" in text
    assert "Motor Control Delay and Activation" in text
