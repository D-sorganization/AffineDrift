"""Tests for wrist universal joint simulator functions.

Includes both unit tests and property-based tests (Hypothesis) for:
- Moment of inertia calculations
- Universal joint transmission ratios
- Grip-angle torque distribution
- Signal generation
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.core.contracts import ContractViolationError
from src.tools.wrist_universal_joint.torque_calculator import (
    calculate_moments_of_inertia,
    distribute_torque_by_grip_angle,
    generate_sample_torque,
    universal_joint_transmission_ratio,
)

# ─── Strategies ───────────────────────────────────────────────

# Grip angle in degrees: [0, 90]
grip_angles_deg = st.floats(min_value=0.0, max_value=90.0, allow_nan=False, allow_infinity=False)

# Wrist angle in degrees: [-60, 60]
wrist_angles_deg = st.floats(min_value=-60.0, max_value=60.0, allow_nan=False, allow_infinity=False)

# Positive physical quantities
positive_floats = st.floats(min_value=1e-6, max_value=1e6, allow_nan=False, allow_infinity=False)


# ─── Unit Tests ───────────────────────────────────────────────


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

    def test_rejects_non_positive_weight(self) -> None:
        """Test that non-positive weights are rejected by DbC."""
        with pytest.raises(ContractViolationError):
            calculate_moments_of_inertia(
                clubhead_weight_g=-1.0,
                shaft_weight_g=100.0,
                club_length_m=1.0,
                cg_distance_m=0.85,
            )

    def test_rejects_zero_length(self) -> None:
        """Test that zero club length is rejected by DbC."""
        with pytest.raises(ContractViolationError):
            calculate_moments_of_inertia(
                clubhead_weight_g=200.0,
                shaft_weight_g=100.0,
                club_length_m=0.0,
                cg_distance_m=0.85,
            )


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
            delta_rad=np.radians(95.0),  # Should be clamped to 89 degrees
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
        expected = 10.0 * np.sin(np.pi / 4)
        assert torque_alpha == pytest.approx(expected, rel=1e-6)
        assert torque_gamma == pytest.approx(expected, rel=1e-6)


class TestGenerateSampleTorque:
    """Test suite for generate_sample_torque."""

    def test_sinusoidal_signal(self) -> None:
        """Test sinusoidal signal generation."""
        t = np.linspace(0, 1, 500)
        torque, error = generate_sample_torque("Sinusoidal", t)
        assert error is None
        assert torque.shape == t.shape
        assert np.all(np.isfinite(torque))

    def test_step_signal(self) -> None:
        """Test step signal generation."""
        t = np.linspace(0, 1, 500)
        torque, error = generate_sample_torque("Step", t)
        assert error is None
        assert torque.shape == t.shape
        assert np.all(torque[:250] == 0.0)
        assert np.all(torque[250:] == 3.0)

    def test_polynomial_valid(self) -> None:
        """Test valid polynomial expression returns array of correct shape."""
        t = np.linspace(0, 1, 500)
        # Use sin() which is explicitly supported in the evaluator
        torque, error = generate_sample_torque("Polynomial", t, "sin(t)")
        assert error is None
        assert torque.shape == t.shape
        np.testing.assert_allclose(torque, np.sin(t), rtol=1e-10)

    def test_polynomial_invalid_syntax(self) -> None:
        """Test invalid polynomial returns fallback with error."""
        t = np.linspace(0, 1, 500)
        torque, error = generate_sample_torque("Polynomial", t, "t *** t")
        assert error is not None
        assert torque.shape == t.shape


# ─── Property-Based Tests ────────────────────────────────────


class TestMomentOfInertiaProperties:
    """Hypothesis-based property tests for calculate_moments_of_inertia."""

    @given(
        head_g=st.floats(min_value=1.0, max_value=1000.0),
        shaft_g=st.floats(min_value=1.0, max_value=500.0),
        length_m=st.floats(min_value=0.1, max_value=2.0),
        cg_m=st.floats(min_value=0.1, max_value=1.5),
    )
    def test_always_positive(
        self, head_g: float, shaft_g: float, length_m: float, cg_m: float
    ) -> None:
        """Moments of inertia are always positive for positive inputs."""
        i_alpha, i_gamma = calculate_moments_of_inertia(head_g, shaft_g, length_m, cg_m)
        assert i_alpha > 0
        assert i_gamma > 0

    @given(
        head_g=st.floats(min_value=1.0, max_value=1000.0),
        shaft_g=st.floats(min_value=1.0, max_value=500.0),
        length_m=st.floats(min_value=0.1, max_value=2.0),
        cg_m=st.floats(min_value=0.1, max_value=1.5),
    )
    def test_gamma_half_of_alpha(
        self, head_g: float, shaft_g: float, length_m: float, cg_m: float
    ) -> None:
        """I_gamma is always exactly half of I_alpha (model assumption)."""
        i_alpha, i_gamma = calculate_moments_of_inertia(head_g, shaft_g, length_m, cg_m)
        assert i_gamma == pytest.approx(0.5 * i_alpha, rel=1e-10)

    @given(
        head_g=st.floats(min_value=1.0, max_value=1000.0),
        shaft_g=st.floats(min_value=1.0, max_value=500.0),
        length_m=st.floats(min_value=0.1, max_value=2.0),
        cg_m=st.floats(min_value=0.1, max_value=1.5),
    )
    def test_monotonic_in_head_weight(
        self, head_g: float, shaft_g: float, length_m: float, cg_m: float
    ) -> None:
        """Increasing head weight increases I_alpha monotonically."""
        i1, _ = calculate_moments_of_inertia(head_g, shaft_g, length_m, cg_m)
        i2, _ = calculate_moments_of_inertia(head_g + 10.0, shaft_g, length_m, cg_m)
        assert i2 > i1


class TestTransmissionRatioProperties:
    """Hypothesis-based property tests for universal_joint_transmission_ratio."""

    @given(
        phi_rad=st.floats(min_value=-np.pi, max_value=np.pi),
        delta_rad=st.floats(min_value=-np.radians(85), max_value=np.radians(85)),
    )
    def test_power_conservation(self, phi_rad: float, delta_rad: float) -> None:
        """omega_ratio * tau_ratio == 1 (power conservation P = tau * omega)."""
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi_rad, delta_rad)
        assert (omega_ratio * tau_ratio) == pytest.approx(1.0, rel=1e-6)

    @given(phi_rad=st.floats(min_value=-np.pi, max_value=np.pi))
    def test_zero_bend_is_unity(self, phi_rad: float) -> None:
        """At zero bend angle, both ratios are exactly 1."""
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi_rad, 0.0)
        assert omega_ratio == pytest.approx(1.0, rel=1e-10)
        assert tau_ratio == pytest.approx(1.0, rel=1e-10)

    @given(
        phi_rad=st.floats(min_value=-np.pi, max_value=np.pi),
        delta_rad=st.floats(min_value=-np.radians(85), max_value=np.radians(85)),
    )
    def test_ratios_are_positive(self, phi_rad: float, delta_rad: float) -> None:
        """Both transmission ratios are always positive."""
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi_rad, delta_rad)
        assert omega_ratio > 0
        assert tau_ratio > 0


class TestTorqueDistributionProperties:
    """Hypothesis-based property tests for distribute_torque_by_grip_angle."""

    @given(
        torque=st.floats(min_value=-100.0, max_value=100.0),
        theta=st.floats(min_value=0.0, max_value=np.pi / 2),
    )
    def test_pythagorean_conservation(self, torque: float, theta: float) -> None:
        """Total torque magnitude is conserved: sqrt(alpha^2 + gamma^2) == |torque|."""
        t_alpha, t_gamma = distribute_torque_by_grip_angle(torque, theta)
        total = np.sqrt(float(t_alpha) ** 2 + float(t_gamma) ** 2)
        assert total == pytest.approx(abs(torque), abs=1e-10)

    @given(torque=st.floats(min_value=-100.0, max_value=100.0))
    def test_zero_angle_all_gamma(self, torque: float) -> None:
        """At theta=0, all torque goes to gamma axis."""
        t_alpha, t_gamma = distribute_torque_by_grip_angle(torque, 0.0)
        assert float(t_alpha) == pytest.approx(0.0, abs=1e-10)
        assert float(t_gamma) == pytest.approx(torque, abs=1e-10)

    @given(torque=st.floats(min_value=-100.0, max_value=100.0))
    def test_90_angle_all_alpha(self, torque: float) -> None:
        """At theta=pi/2, all torque goes to alpha axis."""
        t_alpha, t_gamma = distribute_torque_by_grip_angle(torque, np.pi / 2)
        assert float(t_alpha) == pytest.approx(torque, abs=1e-10)
        assert float(t_gamma) == pytest.approx(0.0, abs=1e-10)


# ─── Integration Tests ───────────────────────────────────────


class TestWristModelIntegration:
    """Integration tests for the full wrist model pipeline."""

    def test_end_to_end_torque_pipeline(self) -> None:
        """Test the full pipeline: MOI -> transmission -> distribution -> acceleration."""
        # Step 1: Calculate moments of inertia
        i_alpha, i_gamma = calculate_moments_of_inertia(200.0, 100.0, 1.0, 0.85)

        # Step 2: Generate input torque
        t = np.linspace(0, 1, 500)
        input_torque, error = generate_sample_torque("Sinusoidal", t)
        assert error is None

        # Step 3: Apply transmission ratio
        grip_rad = np.radians(30.0)
        wrist_rad = np.radians(10.0)
        _omega_ratio, tau_ratio = universal_joint_transmission_ratio(wrist_rad, grip_rad)
        transmitted = input_torque * tau_ratio

        # Step 4: Distribute torque to axes
        t_alpha, t_gamma = distribute_torque_by_grip_angle(transmitted, grip_rad)

        # Step 5: Calculate accelerations
        accel_alpha = t_alpha / i_alpha
        accel_gamma = t_gamma / i_gamma

        # Validate pipeline outputs
        assert np.all(np.isfinite(accel_alpha))
        assert np.all(np.isfinite(accel_gamma))
        assert accel_alpha.shape == t.shape
        assert accel_gamma.shape == t.shape
        # Gamma has lower MOI, so acceleration magnitudes should be higher
        assert np.mean(np.abs(accel_gamma)) > np.mean(np.abs(accel_alpha))

    def test_sweep_over_wrist_angles(self) -> None:
        """Test that transmission sweep produces smooth, continuous output."""
        grip_rad = np.radians(30.0)
        phi_sweep = np.linspace(-60, 60, 200)
        phi_sweep_rad = np.radians(phi_sweep)

        tau_ratios: list[float] = []
        for phi_rad in phi_sweep_rad:
            _omega_r, tau_r = universal_joint_transmission_ratio(phi_rad, grip_rad)
            tau_ratios.append(tau_r)

        tau_arr = np.array(tau_ratios)

        # All positive
        assert np.all(tau_arr > 0)
        # Smooth: no sudden jumps (max derivative bounded)
        diffs = np.abs(np.diff(tau_arr))
        assert np.all(diffs < 0.1), "Transmission ratio should vary smoothly"

    @given(
        grip_deg=grip_angles_deg,
        wrist_deg=wrist_angles_deg,
    )
    def test_dbc_preconditions_hold_for_valid_ranges(
        self, grip_deg: float, wrist_deg: float
    ) -> None:
        """DbC preconditions in the pipeline never fire for valid input ranges."""
        grip_rad = np.radians(grip_deg)
        wrist_rad = np.radians(wrist_deg)

        # These should never raise for valid ranges
        _omega, tau = universal_joint_transmission_ratio(wrist_rad, grip_rad)
        _ta, _tg = distribute_torque_by_grip_angle(1.0 * tau, grip_rad)
