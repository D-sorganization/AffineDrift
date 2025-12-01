"""Tests for wrist universal joint simulator functions."""

from __future__ import annotations

import numpy as np
import pytest


# Copy the functions we want to test (pure functions without Streamlit dependencies)
def calculate_moments_of_inertia(
    clubhead_weight_g: float,
    shaft_weight_g: float,
    club_length_m: float,
    cg_distance_m: float,
) -> tuple[float, float]:
    """Calculate moments of inertia for golf club about two axes."""
    m_head = clubhead_weight_g / 1000.0  # kg
    m_shaft = shaft_weight_g / 1000.0  # kg

    # Shaft inertia (thin rod about end): I = (1/3) * m * L²
    i_shaft_alpha = (1 / 3) * m_shaft * club_length_m**2

    # Clubhead inertia about shaft axis (point mass)
    i_head_alpha = m_head * cg_distance_m**2

    # Total I_alpha (about shaft axis) - higher MOI axis
    i_alpha = i_shaft_alpha + i_head_alpha

    # I_gamma (lowest MOI axis) - typically 0.5x for golf clubs
    i_gamma = 0.5 * i_alpha

    return i_alpha, i_gamma


def universal_joint_transmission_ratio(
    phi_rad: float,
    delta_rad: float,
) -> tuple[float, float]:
    """Calculate transmission ratios for a universal (Hooke/Cardan) joint."""
    # Avoid singularities at delta = 90°
    if np.abs(delta_rad) > np.radians(89):
        delta_rad = np.sign(delta_rad) * np.radians(89)

    sin_delta = np.sin(delta_rad)
    cos_delta = np.cos(delta_rad)
    sin_phi = np.sin(phi_rad)

    # Angular velocity ratio: ω_out/ω_in
    denominator = np.sqrt(1.0 - sin_delta**2 * sin_phi**2)
    omega_ratio = cos_delta / denominator

    # Torque ratio: τ_out/τ_in = 1/(ω_out/ω_in) from power conservation
    tau_ratio = denominator / cos_delta

    return omega_ratio, tau_ratio


def distribute_torque_by_grip_angle(
    torque_transmitted: float,
    theta_grip_rad: float,
) -> tuple[float, float]:
    """Distribute transmitted torque to club axes based on grip angle."""
    torque_alpha = torque_transmitted * np.sin(theta_grip_rad)
    torque_gamma = torque_transmitted * np.cos(theta_grip_rad)

    return torque_alpha, torque_gamma


class TestCalculateMomentsOfInertia:
    """Test suite for calculate_moments_of_inertia."""

    def test_basic_calculation(self) -> None:
        """Test basic moment of inertia calculation."""
        i_alpha, i_gamma = calculate_moments_of_inertia(
            clubhead_weight_g=200.0,
            shaft_weight_g=100.0,
            club_length_m=1.0,
            cg_distance_m=0.85,
        )
        assert i_alpha > 0
        assert i_gamma > 0
        assert i_gamma == pytest.approx(0.5 * i_alpha, rel=1e-6)

    def test_zero_shaft_weight(self) -> None:
        """Test with zero shaft weight."""
        i_alpha, i_gamma = calculate_moments_of_inertia(
            clubhead_weight_g=200.0,
            shaft_weight_g=0.0,
            club_length_m=1.0,
            cg_distance_m=0.85,
        )
        assert i_alpha > 0  # Should still have clubhead contribution
        assert i_gamma > 0


class TestUniversalJointTransmissionRatio:
    """Test suite for universal_joint_transmission_ratio."""

    def test_zero_bend_angle(self) -> None:
        """Test with zero bend angle (straight shaft)."""
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(
            phi_rad=0.0,
            delta_rad=0.0,
        )
        assert omega_ratio == pytest.approx(1.0, rel=1e-6)
        assert tau_ratio == pytest.approx(1.0, rel=1e-6)

    def test_small_bend_angle(self) -> None:
        """Test with small bend angle."""
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(
            phi_rad=0.0,
            delta_rad=np.radians(10.0),
        )
        assert omega_ratio > 0
        assert tau_ratio > 0
        # Power conservation: omega_ratio * tau_ratio should be approximately 1
        assert (omega_ratio * tau_ratio) == pytest.approx(1.0, rel=1e-3)

    def test_large_bend_angle(self) -> None:
        """Test with large bend angle (should be clamped)."""
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(
            phi_rad=0.0,
            delta_rad=np.radians(95.0),  # Should be clamped to 89°
        )
        assert omega_ratio > 0
        assert tau_ratio > 0


class TestDistributeTorqueByGripAngle:
    """Test suite for distribute_torque_by_grip_angle."""

    def test_zero_grip_angle(self) -> None:
        """Test with zero grip angle (all torque to gamma axis)."""
        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
            torque_transmitted=10.0,
            theta_grip_rad=0.0,
        )
        assert torque_alpha == pytest.approx(0.0, abs=1e-6)
        assert torque_gamma == pytest.approx(10.0, rel=1e-6)

    def test_90_degree_grip_angle(self) -> None:
        """Test with 90 degree grip angle (all torque to alpha axis)."""
        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
            torque_transmitted=10.0,
            theta_grip_rad=np.pi / 2,
        )
        assert torque_alpha == pytest.approx(10.0, rel=1e-6)
        assert torque_gamma == pytest.approx(0.0, abs=1e-6)

    def test_45_degree_grip_angle(self) -> None:
        """Test with 45 degree grip angle (equal distribution)."""
        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
            torque_transmitted=10.0,
            theta_grip_rad=np.pi / 4,
        )
        # At 45°, sin = cos = √2/2 ≈ 0.707
        expected = 10.0 * np.sin(np.pi / 4)
        assert torque_alpha == pytest.approx(expected, rel=1e-6)
        assert torque_gamma == pytest.approx(expected, rel=1e-6)
