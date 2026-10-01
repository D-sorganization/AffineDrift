"""Independent checks for the force/work chapter's declared mechanical quantities."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "articles/proximal_distal_companion/chapters/ch10_force_work_motion.qmd"
ARCHIVE = ROOT / "reports/technical-review/force-work-provider-outcomes.json"


def test_energy_closure_declares_internal_conversion_and_potential_boundary() -> None:
    """The former boundary-power-only statement fails for an internally driven body."""
    text = CHAPTER.read_text(encoding="utf-8")
    assert (
        "Positive net work is necessary to increase a closed system's mechanical energy" not in text
    )
    assert "chemical" in text
    assert "double-count" in text


def test_general_rotation_uses_angular_velocity_and_power_conjugate_coordinates() -> None:
    """An arbitrary Euler-angle differential cannot be dotted with a spatial moment."""
    text = CHAPTER.read_text(encoding="utf-8")
    assert r"\int\boldsymbol\tau\cdot d\boldsymbol\theta" not in text
    assert "Euler" in text
    assert "generalized" in text


def test_internal_motor_increases_mechanical_energy_with_zero_external_power() -> None:
    """An ideal battery motor accelerates two free coaxial rotors oppositely."""
    inertias = np.array([2.0, 3.0])
    moments = np.array([4.0, -4.0])
    time = np.linspace(0.0, 0.75, 1001)
    speeds = time[:, None] * moments / inertias
    momentum = speeds @ inertias
    energy = 0.5 * (speeds**2) @ inertias
    motor_power = speeds @ moments
    np.testing.assert_allclose(momentum, 0.0, atol=1e-14)
    assert energy[-1] > 0.0
    assert np.trapezoid(motor_power, time) == pytest.approx(energy[-1])
    # No external wrench power; the battery supplies the positive motor work.
    assert moments.sum() == 0.0


def test_euler_rate_requires_dual_generalized_moment() -> None:
    """For R=Rz(psi)Ry(theta)Rx(phi), body omega=E*[phi_dot,theta_dot,psi_dot]."""
    phi, theta = 0.3, 0.7
    rate_map = np.array(
        [
            [1.0, 0.0, -np.sin(theta)],
            [0.0, np.cos(phi), np.sin(phi) * np.cos(theta)],
            [0.0, -np.sin(phi), np.cos(phi) * np.cos(theta)],
        ]
    )
    rates = np.array([0.2, -0.4, 1.1])
    moment = np.array([2.0, 3.0, -1.0])
    omega = rate_map @ rates
    generalized_moment = rate_map.T @ moment
    assert moment @ omega == pytest.approx(generalized_moment @ rates)
    assert abs(moment @ rates - moment @ omega) > 0.1


def test_rank_one_hand_force_preserves_power_only_with_residual() -> None:
    """A wrist-position Jacobian cannot encode an independent wrist couple."""
    angle, length = 0.6, 0.8
    jacobian = np.array([[length * np.cos(angle), 0], [length * np.sin(angle), 0]])
    generalized_drive = np.array([8.0, -6.0])
    velocity = np.array([2.0, -3.0])
    force = np.linalg.lstsq(jacobian.T, generalized_drive, rcond=None)[0]
    residual = generalized_drive - jacobian.T @ force
    force_power = force @ (jacobian @ velocity)
    assert np.linalg.matrix_rank(jacobian) == 1
    np.testing.assert_allclose(residual, [0.0, -6.0], atol=1e-12)
    assert force_power == pytest.approx(16.0)
    assert residual @ velocity == pytest.approx(18.0)
    assert generalized_drive @ velocity == pytest.approx(force_power + residual @ velocity)


def test_velocity_bias_work_is_not_an_extra_mechanical_energy_supply() -> None:
    """At q2=pi/2 with unit coupling and rates, retain the mass-matrix derivative."""
    velocity = np.ones(2)
    mass_derivative = np.array([[-2.0, -1.0], [-1.0, 0.0]])
    cross_term = np.array([-2.0, 0.0])
    squared_term = np.array([-1.0, 1.0])
    bias = cross_term + squared_term
    bias_drive_power = -bias @ velocity
    geometric_rate = 0.5 * velocity @ mass_derivative @ velocity
    assert bias_drive_power == pytest.approx(2.0)
    assert geometric_rate == pytest.approx(-2.0)
    assert bias_drive_power + geometric_rate == pytest.approx(0.0)


def test_valid_duration_fraction_does_not_bound_missing_impulse() -> None:
    """A short excluded interval can dominate an integral without an amplitude bound."""
    valid_duration, missing_duration = 0.997, 0.003
    valid_impulse = 1.0 * valid_duration
    missing_impulse = 1000.0 * missing_duration
    assert valid_duration / (valid_duration + missing_duration) > 0.996
    assert missing_impulse > valid_impulse


def test_archived_grid_selection_is_recomputed_from_all_outcomes() -> None:
    """Recompute discrete selection, without claiming a new dynamics integration."""
    archive = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    rows = archive["outcomes"]
    qualified = [r for r in rows if r["status"] == "qualified_impact"]
    assert (len(rows), len(qualified)) == (135, 91)
    candidates = {tuple(r["candidate"].values()) for r in rows}
    assert len(candidates) == 135
    impulse = max(qualified, key=lambda r: r["coriolis_absolute_tangent_impulse_n_s"])
    speed = max(qualified, key=lambda r: r["clubhead_speed_m_s"])
    assert impulse["candidate"] != speed["candidate"]
    assert impulse["candidate"]["wrist_restrain_nm"] == 10
    assert speed["candidate"]["wrist_restrain_nm"] == 5
    for name, row in [("maximum_coriolis_impulse", impulse), ("maximum_clubhead_speed", speed)]:
        summary = archive["summary"][name]
        for key, value in row["candidate"].items():
            assert summary[key] == value
        for key in ["clubhead_speed_m_s", "coriolis_absolute_tangent_impulse_n_s"]:
            assert summary[key] == row[key]
        assert row["tangent_valid_fraction"] > 0.996
    assert impulse["coriolis_work_j"] == pytest.approx(-100.69, abs=0.005)
    assert impulse["maximum_mapping_residual_nm"] == pytest.approx(54.44, abs=0.005)
    assert speed["maximum_mapping_residual_nm"] == pytest.approx(52.81, abs=0.005)
