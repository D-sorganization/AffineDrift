from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
THEORY_PART1 = REPO_ROOT / "articles" / "theory-part1.qmd"
THEORY_PART2 = REPO_ROOT / "articles" / "theory-part2.qmd"


def test_theory_part1_uses_distinct_symbol_for_shaft_deformation() -> None:
    """The shaft deformation field must not reuse the control-input symbol u."""
    text = THEORY_PART1.read_text(encoding="utf-8")
    assert "$w(s, t) = \\sum_{i=1}^m \\phi_i(s) \\eta_i(t)$" in text
    assert "$u(s, t) = \\sum_{i=1}^m \\phi_i(s) \\eta_i(t)$" not in text
    assert "| $w(s, t)$ | Local shaft deformation field relative to the hand frame |" in text


def test_theory_part2_uses_explicit_rigid_torque_row_block() -> None:
    """The drift-torque derivation should keep rigid-flexible coupling explicit."""
    text = THEORY_PART2.read_text(encoding="utf-8")
    assert "M_{q}(q,\\eta)" not in text
    assert "M_{qq}(q,\\eta) & M_{q\\eta}(q,\\eta)" in text
    assert "full drift acceleration vector, including both rigid and flexible components" in text
