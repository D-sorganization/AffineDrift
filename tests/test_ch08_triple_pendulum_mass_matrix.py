"""Regression tests for the triple-pendulum mass matrix chapter text."""

from pathlib import Path


def test_triple_pendulum_mass_matrix_uses_relative_wrist_angle() -> None:
    """The club coupling terms should depend on the relative wrist angle q_3."""
    chapter = (
        Path(__file__).resolve().parents[1]
        / "articles/The_Physics_of_Golf/quarto/ch08_triple_pendulum.qmd"
    ).read_text(encoding="utf-8")

    assert "M_{13} &= I_3 + m_3" in chapter
    assert "L_{3,\\text{cm}} \\cos q_3" in chapter
    assert "M_{23} &= I_3 + m_3" in chapter
    assert "L_2 L_{3,\\text{cm}} \\cos q_3" in chapter
    assert "M_{13} &= I_3 + m_3(L_2^2 + L_1 L_2 \\cos q_2)" not in chapter
    assert "M_{23} &= I_3 + m_3(L_2^2/2)" not in chapter
