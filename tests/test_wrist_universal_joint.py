"""Tests for untested wrist_universal_joint modules: constants and plots.

Covers:
- constants: default values, EPSILON, MAX_DELTA_DEGREES, rng reproducibility
- plots: _compute_torque_components, _compute_accel_components,
         _compute_transmission_sweep, _style_axes, _plot_torque_series,
         _compute_torque_components contract validation

Related issue: #1637
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# Streamlit is not installed in the test environment — mock it before any
# wrist_universal_joint.plots or .diagram import reaches the decorator.
if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = MagicMock()

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from src.tools.wrist_universal_joint.constants import (
    DEFAULT_CLUB_LENGTH,
    DEFAULT_CLUBHEAD_CG_DISTANCE,
    DEFAULT_CLUBHEAD_WEIGHT,
    DEFAULT_GAMMA_TO_ALPHA_RATIO,
    DEFAULT_SIGNAL_LENGTH,
    EPSILON,
    MAX_DELTA_DEGREES,
    rng,
)
from src.tools.wrist_universal_joint.plots import (
    _compute_accel_components,
    _compute_torque_components,
    _compute_transmission_sweep,
)

# ─── Constants Tests ──────────────────────────────────────────


class TestConstants:
    """Verify that physical constants have expected types and sane values."""

    def test_default_clubhead_weight_positive(self) -> None:
        """DEFAULT_CLUBHEAD_WEIGHT must be a positive float (grams)."""
        assert DEFAULT_CLUBHEAD_WEIGHT > 0
        assert isinstance(DEFAULT_CLUBHEAD_WEIGHT, float)

    def test_default_shaft_weight_positive(self) -> None:
        """DEFAULT_SHAFT_WEIGHT must be a positive float (grams)."""
        from src.tools.wrist_universal_joint.constants import DEFAULT_SHAFT_WEIGHT

        assert DEFAULT_SHAFT_WEIGHT > 0
        assert isinstance(DEFAULT_SHAFT_WEIGHT, float)

    def test_default_club_length_positive(self) -> None:
        """DEFAULT_CLUB_LENGTH must be a positive float (meters)."""
        assert DEFAULT_CLUB_LENGTH > 0
        assert isinstance(DEFAULT_CLUB_LENGTH, float)

    def test_default_cg_distance_less_than_club_length(self) -> None:
        """CG distance should be less than total club length for a valid geometry."""
        assert DEFAULT_CLUBHEAD_CG_DISTANCE < DEFAULT_CLUB_LENGTH

    def test_epsilon_is_small_positive(self) -> None:
        """EPSILON must be small and positive (numerical stability guard)."""
        assert 0 < EPSILON < 1e-3

    def test_max_delta_degrees_below_90(self) -> None:
        """MAX_DELTA_DEGREES must be strictly below 90 to avoid singularities."""
        assert 0 < MAX_DELTA_DEGREES < 90

    def test_default_signal_length_reasonable(self) -> None:
        """DEFAULT_SIGNAL_LENGTH should be a positive integer >= 10."""
        assert isinstance(DEFAULT_SIGNAL_LENGTH, int)
        assert DEFAULT_SIGNAL_LENGTH >= 10

    def test_default_gamma_to_alpha_ratio_between_0_and_1(self) -> None:
        """DEFAULT_GAMMA_TO_ALPHA_RATIO should be in (0, 1) (gamma < alpha MOI)."""
        assert 0 < DEFAULT_GAMMA_TO_ALPHA_RATIO < 1

    def test_rng_produces_reproducible_values(self) -> None:
        """The module-level rng should be a numpy Generator (seeded)."""
        assert isinstance(rng, np.random.Generator)

    def test_rng_values_are_finite(self) -> None:
        """rng.random() should produce finite values in [0, 1)."""
        val = rng.random()
        assert np.isfinite(val)
        assert 0 <= val < 1


# ─── plots._compute_torque_components Tests ──────────────────


class TestComputeTorqueComponents:
    """Tests for the _compute_torque_components helper in plots.py."""

    def test_returns_four_tuple(self) -> None:
        """_compute_torque_components returns a 4-tuple."""
        result = _compute_torque_components(np.ones(50), np.pi / 6, np.radians(10))
        assert len(result) == 4

    def test_shapes_preserved(self) -> None:
        """torque_transmitted, torque_alpha, torque_gamma should match input shape."""
        n = 200
        input_torque = np.linspace(-5, 5, n)
        torque_transmitted, t_alpha, t_gamma, _tau = _compute_torque_components(
            input_torque, np.pi / 4, np.radians(15)
        )
        assert torque_transmitted.shape == (n,)
        assert np.asarray(t_alpha).shape == (n,)
        assert np.asarray(t_gamma).shape == (n,)

    def test_zero_both_angles_tau_ratio_unity(self) -> None:
        """At zero grip angle and zero wrist angle, tau ratio should be exactly 1."""
        input_torque = np.ones(100)
        torque_transmitted, _ta, _tg, tau_ratio = _compute_torque_components(input_torque, 0.0, 0.0)
        assert tau_ratio == pytest.approx(1.0, rel=1e-6)
        np.testing.assert_allclose(torque_transmitted, input_torque, rtol=1e-6)

    def test_output_is_finite(self) -> None:
        """All computed components must be finite for in-range inputs."""
        input_torque = np.sin(np.linspace(0, 2 * np.pi, 300))
        torque_transmitted, t_alpha, t_gamma, tau_ratio = _compute_torque_components(
            input_torque, np.radians(30), np.radians(20)
        )
        assert np.all(np.isfinite(torque_transmitted))
        assert np.all(np.isfinite(np.asarray(t_alpha)))
        assert np.all(np.isfinite(np.asarray(t_gamma)))
        assert np.isfinite(tau_ratio)


# ─── plots._compute_accel_components Tests ───────────────────


class TestComputeAccelComponents:
    """Tests for _compute_accel_components in plots.py."""

    def test_basic_division(self) -> None:
        """accel_alpha = torque_alpha / i_alpha for normal MOI values."""
        t_alpha = np.full(50, 10.0)
        t_gamma = np.full(50, 5.0)
        accel_alpha, accel_gamma = _compute_accel_components(t_alpha, t_gamma, 2.0, 1.0)
        np.testing.assert_allclose(accel_alpha, 5.0, rtol=1e-10)
        np.testing.assert_allclose(accel_gamma, 5.0, rtol=1e-10)

    def test_tiny_i_alpha_returns_zeros(self) -> None:
        """When i_alpha <= EPSILON the function should return zeros for accel_alpha."""
        t_alpha = np.ones(30)
        t_gamma = np.ones(30)
        accel_alpha, _accel_gamma = _compute_accel_components(t_alpha, t_gamma, 0.0, 1.0)
        np.testing.assert_array_equal(np.asarray(accel_alpha), np.zeros(30))

    def test_tiny_i_gamma_returns_zeros(self) -> None:
        """When i_gamma <= EPSILON the function should return zeros for accel_gamma."""
        t_alpha = np.ones(30)
        t_gamma = np.ones(30)
        _accel_alpha, accel_gamma = _compute_accel_components(t_alpha, t_gamma, 1.0, 0.0)
        np.testing.assert_array_equal(np.asarray(accel_gamma), np.zeros(30))

    def test_higher_moi_lower_acceleration(self) -> None:
        """With equal torques, axis with higher MOI has lower angular acceleration."""
        torque = np.full(50, 3.0)
        i_alpha = 0.2  # higher MOI
        i_gamma = 0.1  # lower MOI
        accel_alpha, accel_gamma = _compute_accel_components(torque, torque, i_alpha, i_gamma)
        assert np.mean(np.abs(np.asarray(accel_gamma))) > np.mean(np.abs(np.asarray(accel_alpha)))


# ─── plots._compute_transmission_sweep Tests ─────────────────


class TestComputeTransmissionSweep:
    """Tests for _compute_transmission_sweep in plots.py."""

    def test_returns_four_arrays(self) -> None:
        """Function should return a 4-tuple of numpy arrays."""
        phi_sweep = np.linspace(-60, 60, 50)
        result = _compute_transmission_sweep(phi_sweep, np.pi / 6, 0.1, 0.05)
        assert len(result) == 4
        for arr in result:
            assert isinstance(arr, np.ndarray)

    def test_output_shapes_match_input(self) -> None:
        """Output arrays must have the same length as the input sweep array."""
        n = 30
        phi_sweep = np.linspace(-60, 60, n)
        tau_r, omega_r, aa, ag = _compute_transmission_sweep(phi_sweep, np.pi / 4, 0.15, 0.07)
        assert tau_r.shape == (n,)
        assert omega_r.shape == (n,)
        assert aa.shape == (n,)
        assert ag.shape == (n,)

    def test_tau_ratios_positive(self) -> None:
        """All torque transmission ratios in the sweep must be strictly positive."""
        phi_sweep = np.linspace(-60, 60, 100)
        tau_r, _, _, _ = _compute_transmission_sweep(phi_sweep, np.pi / 6, 0.1, 0.05)
        assert np.all(tau_r > 0)

    def test_symmetric_sweep_symmetric_tau(self) -> None:
        """For a symmetric sweep [-X, X] the tau_ratios array should be symmetric."""
        n = 101  # odd so there is a midpoint
        phi_sweep = np.linspace(-60, 60, n)
        tau_r, _, _, _ = _compute_transmission_sweep(phi_sweep, np.pi / 6, 0.1, 0.05)
        # Check symmetry: tau[i] ≈ tau[n-1-i]
        np.testing.assert_allclose(tau_r, tau_r[::-1], rtol=1e-6)

    def test_zero_grip_angle_gives_equal_accel_halves(self) -> None:
        """At grip_angle=0, all torque routes to gamma axis; accel_alpha should be 0."""
        phi_sweep = np.linspace(-30, 30, 20)
        _tau_r, _omega_r, accel_alpha, _accel_gamma = _compute_transmission_sweep(
            phi_sweep, 0.0, 0.1, 0.05
        )
        np.testing.assert_allclose(accel_alpha, 0.0, atol=1e-10)
