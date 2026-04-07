"""Tests for enhanced wrist-model kinematics helpers."""

from __future__ import annotations

import numpy as np

from src.tools.wrist_universal_joint.enhanced_model_kinematics import (
    build_info_html,
    compute_acceleration_signals,
    compute_torque_signals,
    compute_transmission_sweep,
)


def test_compute_torque_signals_preserves_input_shape() -> None:
    """Torque helper should preserve the time-series shape across outputs."""
    input_torque = np.linspace(-2.0, 2.0, 11)
    signals = compute_torque_signals(input_torque, grip_angle_deg=30, wrist_angle_deg=10)
    assert signals.torque_transmitted.shape == input_torque.shape
    assert signals.torque_alpha.shape == input_torque.shape
    assert signals.torque_gamma.shape == input_torque.shape


def test_compute_acceleration_signals_returns_zero_when_inertia_is_zero() -> None:
    """Acceleration helper should avoid division errors at zero inertia."""
    input_torque = np.ones(5)
    signals = compute_acceleration_signals(
        input_torque,
        grip_angle_deg=30,
        wrist_angle_deg=10,
        i_alpha=0.0,
        i_gamma=0.0,
    )
    assert np.allclose(signals.accel_alpha, 0.0)
    assert np.allclose(signals.accel_gamma, 0.0)


def test_compute_transmission_sweep_marks_current_domain() -> None:
    """Transmission sweep should cover the full wrist-angle domain."""
    sweep = compute_transmission_sweep(
        grip_angle_deg=45,
        wrist_angle_deg=15,
        i_alpha=1.0,
        i_gamma=0.5,
    )
    assert sweep.wrist_angle_deg[0] == -60
    assert sweep.wrist_angle_deg[-1] == 60
    assert sweep.tau_ratios.shape == sweep.wrist_angle_deg.shape
    assert sweep.omega_ratios.shape == sweep.wrist_angle_deg.shape


def test_build_info_html_includes_current_configuration() -> None:
    """Info panel helper should embed the current grip and wrist angles."""
    html = build_info_html(grip_angle_deg=25, wrist_angle_deg=-5)
    assert "Grip=25°" in html
    assert "Wrist=-5°" in html
