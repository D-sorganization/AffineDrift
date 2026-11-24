"""Regression guards for NOTATION.md Wave 1.1 contract fixes (#5589)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

NOTATION = Path(__file__).resolve().parents[1] / "NOTATION.md"


def test_euler_section_states_intrinsic_zyx_prime() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "Intrinsic $Z$–$Y'$–$X''$" in text
    assert "Equivalent to intrinsic X-Y-Z on moving frame" not in text
    assert "Applied in extrinsic (fixed-frame) order" not in text
    assert "Extrinsic Z-Y-X (Yaw-Pitch-Roll)" not in text


def test_twist_wrench_block_order_is_angular_first_moment_first() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "$V=(\\omega,v)$" in text
    assert "$W=(\\boldsymbol{\\mathsf{n}},\\mathbf{f})$" in text
    assert "Linear + angular velocity" not in text
    assert "Torque + linear force" not in text


def test_cor_uses_signed_normal_relative_velocity() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "(v_out - v_contact) / (v_in - v_contact)" not in text
    assert "\\mathbf{v}_b^+" in text


def test_cross_product_right_hand_rule_prose() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "Extend thumb in direction of second vector" not in text
    assert "curl them toward the second" in text


def test_hamilton_quaternion_pins_algebra_and_active_rotation() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "$ijk=-1$" in text
    assert "$q_{WB}$" in text


def test_dgcr_is_restitution_based_not_aerodynamic() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "restitution-derived" in text or "restitution)" in text
    assert "Drag–curve ratio (aerodynamic)" not in text
    assert "aerodynamic **Drag-Curve Ratio (DgCR)**" not in text
    assert "aerodynamic drag–curve ratio" not in text


def test_cor_range_qualified_for_passive_impacts() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "passive, non-superelastic" in text
    assert "no net external energy supplied to the collision" in text
