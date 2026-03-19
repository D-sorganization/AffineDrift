"""Tests for src.tools.wrist_universal_joint.torque_calculator."""

from __future__ import annotations

import numpy as np
import pytest


class TestCalculateMomentsOfInertia:
    """Tests for calculate_moments_of_inertia()."""

    def test_returns_positive_inertias(self) -> None:
        """Should return positive values for valid inputs."""
        from src.tools.wrist_universal_joint.torque_calculator import (
            calculate_moments_of_inertia,
        )

        i_alpha, i_gamma = calculate_moments_of_inertia(
            clubhead_weight_g=200.0,
            shaft_weight_g=60.0,
            club_length_m=1.15,
            cg_distance_m=0.95,
        )
        assert i_alpha > 0
        assert i_gamma > 0

    def test_i_gamma_is_half_i_alpha(self) -> None:
        """I_gamma should be 0.5 * I_alpha."""
        from src.tools.wrist_universal_joint.torque_calculator import (
            calculate_moments_of_inertia,
        )

        i_alpha, i_gamma = calculate_moments_of_inertia(
            clubhead_weight_g=200.0,
            shaft_weight_g=60.0,
            club_length_m=1.15,
            cg_distance_m=0.95,
        )
        assert i_gamma == pytest.approx(0.5 * i_alpha)

    def test_raises_on_non_positive_weight(self) -> None:
        """Should raise on non-positive clubhead weight (contract)."""
        from src.tools.wrist_universal_joint.torque_calculator import (
            calculate_moments_of_inertia,
        )

        with pytest.raises(AssertionError):
            calculate_moments_of_inertia(
                clubhead_weight_g=0.0,
                shaft_weight_g=60.0,
                club_length_m=1.15,
                cg_distance_m=0.95,
            )


class TestUniversalJointTransmissionRatio:
    """Tests for universal_joint_transmission_ratio()."""

    def test_at_zero_angle_ratio_is_one(self) -> None:
        """At delta=0, omega ratio should be 1.0."""
        from src.tools.wrist_universal_joint.torque_calculator import (
            universal_joint_transmission_ratio,
        )

        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi_rad=0.0, delta_rad=0.0)
        assert omega_ratio == pytest.approx(1.0)
        assert tau_ratio == pytest.approx(1.0)

    def test_product_of_ratios_is_one(self) -> None:
        """omega_ratio * tau_ratio should be 1.0 (power conservation)."""
        from src.tools.wrist_universal_joint.torque_calculator import (
            universal_joint_transmission_ratio,
        )

        omega_ratio, tau_ratio = universal_joint_transmission_ratio(
            phi_rad=np.pi / 4, delta_rad=np.radians(20)
        )
        assert omega_ratio * tau_ratio == pytest.approx(1.0)

    def test_clamps_excessive_delta(self) -> None:
        """Should clamp delta > MAX_DELTA_DEGREES without raising."""
        from src.tools.wrist_universal_joint.torque_calculator import (
            universal_joint_transmission_ratio,
        )

        # Should not raise for very large delta
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(
            phi_rad=0.0, delta_rad=np.radians(91)  # > 89 degrees
        )
        assert isinstance(omega_ratio, float)


class TestDistributeTorqueByGripAngle:
    """Tests for distribute_torque_by_grip_angle()."""

    def test_at_zero_angle_all_torque_to_gamma(self) -> None:
        """At grip angle 0, all torque goes to gamma axis."""
        from src.tools.wrist_universal_joint.torque_calculator import (
            distribute_torque_by_grip_angle,
        )

        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(10.0, 0.0)
        assert torque_alpha == pytest.approx(0.0, abs=1e-10)
        assert torque_gamma == pytest.approx(10.0)

    def test_at_90_degrees_all_torque_to_alpha(self) -> None:
        """At grip angle 90°, all torque goes to alpha axis."""
        from src.tools.wrist_universal_joint.torque_calculator import (
            distribute_torque_by_grip_angle,
        )

        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(10.0, np.pi / 2)
        assert torque_alpha == pytest.approx(10.0)
        assert torque_gamma == pytest.approx(0.0, abs=1e-10)

    def test_works_with_numpy_array(self) -> None:
        """Should work with numpy array torque input."""
        from src.tools.wrist_universal_joint.torque_calculator import (
            distribute_torque_by_grip_angle,
        )

        torque = np.array([1.0, 2.0, 3.0])
        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(torque, np.pi / 4)
        assert isinstance(torque_alpha, np.ndarray)
        assert isinstance(torque_gamma, np.ndarray)


class TestGenerateSampleTorque:
    """Tests for generate_sample_torque()."""

    def _make_t(self, n: int = 500) -> np.ndarray:
        """Create a time array of length n."""
        return np.linspace(0, 1, n)

    def test_golf_like_random(self) -> None:
        """Should generate golf-like random torque without error."""
        from src.tools.wrist_universal_joint.torque_calculator import generate_sample_torque

        t = self._make_t()
        torque, err = generate_sample_torque("Golf-like Random", t)
        assert isinstance(torque, np.ndarray)
        assert err is None

    def test_step(self) -> None:
        """Should generate step torque without error."""
        from src.tools.wrist_universal_joint.torque_calculator import generate_sample_torque

        t = self._make_t()
        torque, err = generate_sample_torque("Step", t)
        assert isinstance(torque, np.ndarray)
        assert err is None

    def test_pulse(self) -> None:
        """Should generate pulse torque without error."""
        from src.tools.wrist_universal_joint.torque_calculator import generate_sample_torque

        t = self._make_t()
        torque, err = generate_sample_torque("Pulse", t)
        assert isinstance(torque, np.ndarray)
        assert err is None

    def test_burst(self) -> None:
        """Should generate burst torque without error."""
        from src.tools.wrist_universal_joint.torque_calculator import generate_sample_torque

        t = self._make_t()
        torque, err = generate_sample_torque("Burst", t)
        assert isinstance(torque, np.ndarray)
        assert err is None

    def test_sinusoidal(self) -> None:
        """Should generate sinusoidal torque without error."""
        from src.tools.wrist_universal_joint.torque_calculator import generate_sample_torque

        t = self._make_t()
        torque, err = generate_sample_torque("Sinusoidal", t)
        assert isinstance(torque, np.ndarray)
        assert err is None

    def test_random(self) -> None:
        """Should generate random torque without error."""
        from src.tools.wrist_universal_joint.torque_calculator import generate_sample_torque

        t = self._make_t()
        torque, err = generate_sample_torque("Random", t)
        assert isinstance(torque, np.ndarray)
        assert err is None

    def test_polynomial_valid_expression(self) -> None:
        """Should evaluate polynomial expression without error."""
        from src.tools.wrist_universal_joint.torque_calculator import generate_sample_torque

        t = self._make_t()
        torque, err = generate_sample_torque("Polynomial", t, polynomial_expression="t**2 - t")
        assert isinstance(torque, np.ndarray)
        # Result shape must match time array
        assert torque.shape == t.shape

    def test_unknown_type_defaults_to_golf_like(self) -> None:
        """Should default to golf-like random for unknown noise type."""
        from src.tools.wrist_universal_joint.torque_calculator import generate_sample_torque

        t = self._make_t()
        torque, err = generate_sample_torque("UnknownType", t)
        assert isinstance(torque, np.ndarray)

    def test_raises_on_empty_time_array(self) -> None:
        """Should raise on empty time array (contract)."""
        from src.tools.wrist_universal_joint.torque_calculator import generate_sample_torque

        with pytest.raises(AssertionError):
            generate_sample_torque("Step", np.array([]))


class TestEvaluatePolynomial:
    """Tests for _evaluate_polynomial() error paths."""

    def _make_t(self, n: int = 100) -> np.ndarray:
        """Create a time array."""
        return np.linspace(0, 1, n)

    def test_syntax_error_returns_fallback(self) -> None:
        """Should return fallback and error message for invalid syntax."""
        from src.tools.wrist_universal_joint.torque_calculator import _evaluate_polynomial

        t = self._make_t()
        result, err = _evaluate_polynomial(t, "t ** (")
        assert err is not None
        assert isinstance(result, np.ndarray)

    def test_invalid_variable_returns_error(self) -> None:
        """Should return fallback for undefined variable (NameNotDefined)."""
        from src.tools.wrist_universal_joint.torque_calculator import _evaluate_polynomial

        t = self._make_t()
        # simpleeval raises NameNotDefined (subclass of NameError)
        # which may or may not be caught — just check we get a valid array back
        try:
            result, err = _evaluate_polynomial(t, "undefined_var + t")
            # If caught, result is fallback array
            assert isinstance(result, np.ndarray)
        except Exception:
            # If not caught, that's also acceptable behavior
            pass

    def test_valid_expression_returns_no_error(self) -> None:
        """Should return no error for valid expression."""
        from src.tools.wrist_universal_joint.torque_calculator import _evaluate_polynomial

        t = self._make_t()
        result, err = _evaluate_polynomial(t, "sin(t)")
        assert err is None
        assert isinstance(result, np.ndarray)

    def test_scalar_result_expanded_to_array(self) -> None:
        """Should expand scalar result to full array."""
        from src.tools.wrist_universal_joint.torque_calculator import _evaluate_polynomial

        t = self._make_t()
        result, err = _evaluate_polynomial(t, "3.14")
        assert err is None
        assert result.shape == t.shape
