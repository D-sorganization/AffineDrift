"""Property-based tests for physics invariants using Hypothesis.

Every test in this module encodes a physical or mathematical invariant
that must hold for *all* valid inputs, not just hand-picked examples.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.affine_control.ddp import adaptive_timestep_ddp_mock
from src.affine_control.residuals import ResidualMonitor
from src.tools.wrist_universal_joint.torque_calculator import (
    calculate_moments_of_inertia,
    distribute_torque_by_grip_angle,
    generate_sample_torque,
    universal_joint_transmission_ratio,
)

# ---------------------------------------------------------------------------
# Reusable strategies
# ---------------------------------------------------------------------------

# Positive floats suitable for physical quantities (mass, length, etc.)
positive_physical = st.floats(min_value=0.01, max_value=1e4, allow_nan=False, allow_infinity=False)

# Angles in radians: stay well within [-88, 88] degrees to avoid singularity region
safe_angle_deg = st.floats(min_value=-88.0, max_value=88.0, allow_nan=False, allow_infinity=False)

# Rotation angle phi -- full circle is fine
rotation_angle_rad = st.floats(
    min_value=-2 * np.pi,
    max_value=2 * np.pi,
    allow_nan=False,
    allow_infinity=False,
)

# Bend angle delta -- must avoid the 89-degree singularity clamp
bend_angle_rad = st.floats(
    min_value=-np.radians(85.0),
    max_value=np.radians(85.0),
    allow_nan=False,
    allow_infinity=False,
)

# Grip angle in [0, pi/2] -- physically meaningful range
grip_angle_rad = st.floats(
    min_value=0.0,
    max_value=np.pi / 2,
    allow_nan=False,
    allow_infinity=False,
)

# Positive torque values
positive_torque = st.floats(min_value=0.01, max_value=1e3, allow_nan=False, allow_infinity=False)


# ---------------------------------------------------------------------------
# Universal Joint -- Power Conservation
# ---------------------------------------------------------------------------


@pytest.mark.property_test
class TestUniversalJointPowerConservation:
    """Property: tau_ratio * omega_ratio must equal 1 (power conservation)."""

    @given(phi=rotation_angle_rad, delta=bend_angle_rad)
    @settings(max_examples=200)
    def test_tau_times_omega_equals_one(self, phi: float, delta: float) -> None:
        """Power conservation: P_in = P_out implies tau_ratio * omega_ratio = 1.

        For a lossless universal joint, the product of the torque transmission
        ratio and the angular velocity ratio must be unity at every
        configuration.
        """
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi, delta)
        product = omega_ratio * tau_ratio
        msg = f"Power conservation violated: {omega_ratio} * {tau_ratio} = {product}"
        assert product == pytest.approx(1.0, rel=1e-6), msg


# ---------------------------------------------------------------------------
# Torque Distribution -- Energy Conservation
# ---------------------------------------------------------------------------


@pytest.mark.property_test
class TestTorqueDistributionEnergyConservation:
    """Property: torque_alpha^2 + torque_gamma^2 == torque_transmitted^2."""

    @given(torque=positive_torque, theta=grip_angle_rad)
    @settings(max_examples=200)
    def test_torque_component_magnitudes(
        self,
        torque: float,
        theta: float,
    ) -> None:
        """Energy conservation in torque decomposition.

        When a transmitted torque is decomposed into alpha and gamma axes
        via sin/cos of the grip angle, the Pythagorean identity ensures
        that the sum of squares equals the original torque squared.
        """
        t_alpha, t_gamma = distribute_torque_by_grip_angle(torque, theta)
        sum_sq = t_alpha**2 + t_gamma**2
        msg = f"Energy violated: {t_alpha}^2 + {t_gamma}^2 = {sum_sq} != {torque**2}"
        assert sum_sq == pytest.approx(torque**2, rel=1e-6), msg


# ---------------------------------------------------------------------------
# Moments of Inertia -- Physical Constraints
# ---------------------------------------------------------------------------


@pytest.mark.property_test
class TestMomentsOfInertiaConstraints:
    """Property: moments of inertia are always positive and I_gamma < I_alpha."""

    @given(
        head_g=positive_physical,
        shaft_g=positive_physical,
        length_m=st.floats(min_value=0.3, max_value=2.0, allow_nan=False, allow_infinity=False),
        cg_m=st.floats(min_value=0.1, max_value=1.5, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=200)
    def test_moments_always_positive(
        self,
        head_g: float,
        shaft_g: float,
        length_m: float,
        cg_m: float,
    ) -> None:
        """Moments of inertia must always be strictly positive for any
        valid club configuration.
        """
        i_alpha, i_gamma = calculate_moments_of_inertia(
            head_g,
            shaft_g,
            length_m,
            cg_m,
        )
        assert i_alpha > 0, f"I_alpha must be positive, got {i_alpha}"
        assert i_gamma > 0, f"I_gamma must be positive, got {i_gamma}"

    @given(
        head_g=positive_physical,
        shaft_g=positive_physical,
        length_m=st.floats(min_value=0.3, max_value=2.0, allow_nan=False, allow_infinity=False),
        cg_m=st.floats(min_value=0.1, max_value=1.5, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=200)
    def test_gamma_less_than_alpha(
        self,
        head_g: float,
        shaft_g: float,
        length_m: float,
        cg_m: float,
    ) -> None:
        """I_gamma must always be less than I_alpha (by design, I_gamma = 0.5 * I_alpha)."""
        i_alpha, i_gamma = calculate_moments_of_inertia(
            head_g,
            shaft_g,
            length_m,
            cg_m,
        )
        assert i_gamma < i_alpha, f"I_gamma ({i_gamma}) must be < I_alpha ({i_alpha})"


# ---------------------------------------------------------------------------
# Angle Conversions -- Round-Trip Identity
# ---------------------------------------------------------------------------


@pytest.mark.property_test
class TestAngleConversionRoundTrip:
    """Property: converting radians -> degrees -> radians must be identity."""

    @given(
        x=st.floats(
            min_value=-1e6,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False,
        ),
    )
    @settings(max_examples=300)
    def test_radians_degrees_roundtrip(self, x: float) -> None:
        """np.radians(np.degrees(x)) must equal x for all finite x.

        This is a fundamental identity that the numpy conversion functions
        must satisfy.
        """
        roundtripped = np.radians(np.degrees(x))
        msg = f"Round-trip failed: {x} -> {np.degrees(x)} -> {roundtripped}"
        assert roundtripped == pytest.approx(x, rel=1e-10, abs=1e-15), msg


# ---------------------------------------------------------------------------
# Signal Generation -- Output Length
# ---------------------------------------------------------------------------


@pytest.mark.property_test
class TestSignalGenerationLength:
    """Property: all signal types produce arrays of correct length."""

    @given(
        signal_type=st.sampled_from(
            [
                "Step",
                "Pulse",
                "Burst",
                "Sinusoidal",
                "Random",
                "Golf-like Random",
            ]
        ),
        n=st.integers(min_value=500, max_value=1000),
    )
    @settings(max_examples=50)
    def test_signal_length_matches_time_array(
        self,
        signal_type: str,
        n: int,
    ) -> None:
        """For any signal type, the generated torque array must have the same
        length as the input time array.
        """
        t = np.linspace(0, 1, n)
        torque, error = generate_sample_torque(signal_type, t)
        assert error is None, f"Unexpected error for signal type '{signal_type}': {error}"
        msg = f"Signal '{signal_type}' produced {len(torque)} samples, expected {n}"
        assert len(torque) == n, msg

    @given(
        n=st.integers(min_value=500, max_value=1000),
    )
    @settings(max_examples=20)
    def test_polynomial_signal_length(self, n: int) -> None:
        """Polynomial signal type must produce an array of the correct length.

        The polynomial evaluator may return an error for certain expressions
        (e.g., when simpleeval cannot handle numpy power operations), but the
        fallback always produces an array of the correct length.
        """
        t = np.linspace(0, 1, n)
        torque, error = generate_sample_torque("Polynomial", t, "sin(t)")
        assert error is None
        assert len(torque) == n

    @given(
        n=st.integers(min_value=500, max_value=1000),
    )
    @settings(max_examples=20)
    def test_polynomial_fallback_preserves_length(self, n: int) -> None:
        """When polynomial evaluation fails, the fallback array must still
        have the correct length.
        """
        t = np.linspace(0, 1, n)
        torque, _error = generate_sample_torque("Polynomial", t, "t**2 - t")
        # Regardless of whether _error is None or a message, length must match
        assert len(torque) == n


# ---------------------------------------------------------------------------
# DDP Mock -- Output Shape Preservation
# ---------------------------------------------------------------------------


@pytest.mark.property_test
class TestDDPOutputShapePreservation:
    """Property: DDP output trajectory has same state dimension as input."""

    @given(
        n_steps=st.integers(min_value=5, max_value=20),
    )
    @settings(max_examples=10, deadline=10000)
    def test_output_state_dim_matches_input(self, n_steps: int) -> None:
        """The DDP mock must preserve state dimensionality: if x0 has n
        elements, every row of x_traj must also have n elements.
        """

        def double_integrator(
            x: np.ndarray[Any, Any],
            u: np.ndarray[Any, Any],
        ) -> np.ndarray[Any, Any]:
            return np.array([x[1], u[0]])

        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((n_steps, 1))

        x_traj, u_traj, t_traj = adaptive_timestep_ddp_mock(
            double_integrator,
            x0,
            xf,
            u_init,
            eps_residual=0.01,
            max_iters=3,
        )
        msg = f"State dim mismatch: {x_traj.shape[1]} != {x0.shape[0]}"
        assert x_traj.shape[1] == x0.shape[0], msg
        assert len(t_traj) == len(x_traj)
        assert len(u_traj) == len(t_traj) - 1


# ---------------------------------------------------------------------------
# Residual Monitoring -- Non-Negative Residuals
# ---------------------------------------------------------------------------


@pytest.mark.property_test
class TestResidualMonitorNonNegative:
    """Property: residuals reported by the monitor are always non-negative."""

    @given(
        x_meas_val=st.floats(
            min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False
        ),
        x_nom_val=st.floats(
            min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(max_examples=200)
    def test_residual_always_non_negative(
        self,
        x_meas_val: float,
        x_nom_val: float,
    ) -> None:
        """The residual r returned by monitor.update must always be >= 0.

        The residual is a norm, which by definition is non-negative.
        """
        monitor = ResidualMonitor(
            eps_warning=0.01,
            eps_critical=0.05,
            n_hysteresis=3,
        )
        x_meas = np.array([x_meas_val])
        x_nom = np.array([x_nom_val])
        mode, r = monitor.update(x_meas, x_nom)
        assert r >= 0, f"Residual must be non-negative, got {r}"
        assert isinstance(mode, str)


# ---------------------------------------------------------------------------
# Transmission Ratio -- Physical Bounds
# ---------------------------------------------------------------------------


@pytest.mark.property_test
class TestTransmissionRatioPhysicalBounds:
    """Property: transmission ratio lies in a physically meaningful range."""

    @given(phi=rotation_angle_rad, delta=bend_angle_rad)
    @settings(max_examples=200)
    def test_omega_ratio_is_positive(self, phi: float, delta: float) -> None:
        """The angular velocity ratio must always be positive (no reversal
        in a lossless universal joint).
        """
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi, delta)
        assert omega_ratio > 0, f"omega_ratio must be positive, got {omega_ratio}"
        assert tau_ratio > 0, f"tau_ratio must be positive, got {tau_ratio}"

    @given(phi=rotation_angle_rad, delta=bend_angle_rad)
    @settings(max_examples=200)
    def test_transmission_ratio_finite(self, phi: float, delta: float) -> None:
        """Both omega_ratio and tau_ratio must be finite for all valid angles.

        The singularity at delta=90 degrees is clamped internally, so
        the outputs must always be finite.
        """
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi, delta)
        assert np.isfinite(omega_ratio), f"omega_ratio is not finite: {omega_ratio}"
        assert np.isfinite(tau_ratio), f"tau_ratio is not finite: {tau_ratio}"

    @given(phi=rotation_angle_rad, delta=bend_angle_rad)
    @settings(max_examples=200)
    def test_transmission_ratio_bounded(self, phi: float, delta: float) -> None:
        """The transmission ratio must be bounded within a physically
        reasonable range.  For a universal joint with delta < 89 degrees,
        both ratios remain between roughly 0.01 and 100.
        """
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi, delta)
        assert 0.0 < omega_ratio < 200.0, f"omega_ratio out of bounds: {omega_ratio}"
        assert 0.0 < tau_ratio < 200.0, f"tau_ratio out of bounds: {tau_ratio}"
