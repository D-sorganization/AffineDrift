"""Unit tests for the wrist universal joint computation module.

Tests cover:
- compute_transmission_pipeline: output dict keys and value types
- compute_angular_accelerations: zero-inertia safety guard
- format_plot_axes: verifies it does not raise on a mock axes
"""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest

from src.tools.wrist_universal_joint.computation import (
    compute_angular_accelerations,
    compute_transmission_pipeline,
    format_plot_axes,
)

# ---------------------------------------------------------------------------
# compute_transmission_pipeline
# ---------------------------------------------------------------------------


class TestComputeTransmissionPipeline:
    """Tests for compute_transmission_pipeline output structure."""

    EXPECTED_KEYS = {
        "theta_grip_rad",
        "phi_wrist_rad",
        "omega_ratio",
        "tau_ratio",
        "torque_transmitted",
        "torque_alpha",
        "torque_gamma",
    }

    def test_output_has_all_expected_keys(self) -> None:
        """The result dictionary must contain exactly the documented keys."""
        result = compute_transmission_pipeline(
            grip_angle_deg=30.0,
            wrist_angle_deg=15.0,
            input_torque=5.0,
        )
        assert set(result.keys()) == self.EXPECTED_KEYS

    def test_scalar_input_produces_scalar_values(self) -> None:
        """When input_torque is a scalar, all values must be scalar floats."""
        result = compute_transmission_pipeline(
            grip_angle_deg=45.0,
            wrist_angle_deg=10.0,
            input_torque=10.0,
        )
        for key in self.EXPECTED_KEYS:
            val = result[key]
            msg = f"Key '{key}' should be a float, got {type(val)}"
            assert isinstance(val, (float, np.floating)), msg

    def test_array_input_produces_array_torque_values(self) -> None:
        """When input_torque is an array, torque-related values must be arrays."""
        torque_arr = np.array([1.0, 2.0, 3.0])
        result = compute_transmission_pipeline(
            grip_angle_deg=30.0,
            wrist_angle_deg=15.0,
            input_torque=torque_arr,
        )
        assert isinstance(result["torque_transmitted"], np.ndarray)
        assert isinstance(result["torque_alpha"], np.ndarray)
        assert isinstance(result["torque_gamma"], np.ndarray)
        assert len(result["torque_transmitted"]) == 3
        assert len(result["torque_alpha"]) == 3
        assert len(result["torque_gamma"]) == 3

    def test_zero_grip_angle(self) -> None:
        """At grip_angle=0, all torque goes to gamma axis."""
        result = compute_transmission_pipeline(
            grip_angle_deg=0.0,
            wrist_angle_deg=10.0,
            input_torque=5.0,
        )
        assert result["torque_alpha"] == pytest.approx(0.0, abs=1e-10)
        # tau_ratio depends on wrist angle, so torque_gamma is nonzero
        assert abs(result["torque_gamma"]) > 1e-10

    def test_90_degree_grip_angle(self) -> None:
        """At grip_angle=90, all torque goes to alpha axis."""
        result = compute_transmission_pipeline(
            grip_angle_deg=90.0,
            wrist_angle_deg=10.0,
            input_torque=5.0,
        )
        assert result["torque_gamma"] == pytest.approx(0.0, abs=1e-10)
        assert abs(result["torque_alpha"]) > 1e-10

    def test_zero_grip_angle_gives_unit_ratios(self) -> None:
        """At grip_angle=0, delta_rad=0 in the transmission ratio function,
        which corresponds to a straight shaft.  Both ratios should be ~1.0.

        Note: compute_transmission_pipeline passes theta_grip_rad as the
        delta (bend) parameter to universal_joint_transmission_ratio.
        """
        result = compute_transmission_pipeline(
            grip_angle_deg=0.0,
            wrist_angle_deg=45.0,
            input_torque=5.0,
        )
        assert result["omega_ratio"] == pytest.approx(1.0, rel=1e-6)
        assert result["tau_ratio"] == pytest.approx(1.0, rel=1e-6)

    def test_all_values_finite(self) -> None:
        """All output values must be finite for reasonable inputs."""
        result = compute_transmission_pipeline(
            grip_angle_deg=60.0,
            wrist_angle_deg=30.0,
            input_torque=7.5,
        )
        for key, val in result.items():
            if isinstance(val, np.ndarray):
                assert np.all(np.isfinite(val)), f"Key '{key}' contains non-finite values"
            else:
                assert np.isfinite(val), f"Key '{key}' is not finite: {val}"


# ---------------------------------------------------------------------------
# compute_angular_accelerations
# ---------------------------------------------------------------------------


class TestComputeAngularAccelerations:
    """Tests for compute_angular_accelerations, especially zero-inertia safety."""

    def test_normal_computation(self) -> None:
        """Normal case: accel = torque / inertia."""
        accel_a, accel_g = compute_angular_accelerations(
            torque_alpha=10.0,
            torque_gamma=5.0,
            i_alpha=2.0,
            i_gamma=1.0,
        )
        assert accel_a == pytest.approx(5.0, rel=1e-6)
        assert accel_g == pytest.approx(5.0, rel=1e-6)

    def test_zero_inertia_alpha_returns_zero(self) -> None:
        """When i_alpha is effectively zero, accel_alpha must be zero (safety)."""
        accel_a, _accel_g = compute_angular_accelerations(
            torque_alpha=10.0,
            torque_gamma=5.0,
            i_alpha=0.0,
            i_gamma=1.0,
        )
        # i_alpha <= EPSILON triggers the safety guard
        assert accel_a == pytest.approx(0.0, abs=1e-10)

    def test_zero_inertia_gamma_returns_zero(self) -> None:
        """When i_gamma is effectively zero, accel_gamma must be zero (safety)."""
        _accel_a, accel_g = compute_angular_accelerations(
            torque_alpha=10.0,
            torque_gamma=5.0,
            i_alpha=1.0,
            i_gamma=0.0,
        )
        assert accel_g == pytest.approx(0.0, abs=1e-10)

    def test_both_inertias_zero(self) -> None:
        """When both inertias are zero, both accelerations must be zero."""
        accel_a, accel_g = compute_angular_accelerations(
            torque_alpha=10.0,
            torque_gamma=5.0,
            i_alpha=0.0,
            i_gamma=0.0,
        )
        assert accel_a == pytest.approx(0.0, abs=1e-10)
        assert accel_g == pytest.approx(0.0, abs=1e-10)

    def test_array_torque_input(self) -> None:
        """Array torque inputs must produce array accelerations."""
        t_alpha = np.array([10.0, 20.0, 30.0])
        t_gamma = np.array([5.0, 10.0, 15.0])
        accel_a, accel_g = compute_angular_accelerations(
            torque_alpha=t_alpha,
            torque_gamma=t_gamma,
            i_alpha=2.0,
            i_gamma=1.0,
        )
        expected_a = np.array([5.0, 10.0, 15.0])
        expected_g = np.array([5.0, 10.0, 15.0])
        np.testing.assert_allclose(accel_a, expected_a, rtol=1e-6)
        np.testing.assert_allclose(accel_g, expected_g, rtol=1e-6)

    def test_array_torque_with_zero_inertia(self) -> None:
        """Array torque with zero inertia must produce a zero array."""
        t_alpha = np.array([10.0, 20.0, 30.0])
        t_gamma = np.array([5.0, 10.0, 15.0])
        accel_a, accel_g = compute_angular_accelerations(
            torque_alpha=t_alpha,
            torque_gamma=t_gamma,
            i_alpha=0.0,
            i_gamma=0.0,
        )
        np.testing.assert_allclose(accel_a, np.zeros(3), atol=1e-10)
        np.testing.assert_allclose(accel_g, np.zeros(3), atol=1e-10)

    def test_tiny_inertia_triggers_safety(self) -> None:
        """An inertia value smaller than EPSILON must trigger the zero-guard."""
        from src.tools.wrist_universal_joint.constants import EPSILON as WUJ_EPSILON

        accel_a, accel_g = compute_angular_accelerations(
            torque_alpha=100.0,
            torque_gamma=100.0,
            i_alpha=WUJ_EPSILON / 10.0,
            i_gamma=WUJ_EPSILON / 10.0,
        )
        # Safety guard: should be zero, not a huge number
        assert accel_a == pytest.approx(0.0, abs=1e-10)
        assert accel_g == pytest.approx(0.0, abs=1e-10)


# ---------------------------------------------------------------------------
# format_plot_axes
# ---------------------------------------------------------------------------


class TestFormatPlotAxes:
    """Tests for format_plot_axes using a mock matplotlib axes."""

    def test_does_not_raise_on_mock_axes(self) -> None:
        """format_plot_axes must not raise when called with a mock axes object."""
        mock_ax = MagicMock()
        # Should not raise
        format_plot_axes(
            ax=mock_ax,
            title="Test Title",
            xlabel="X Label",
            ylabel="Y Label",
        )

    def test_calls_set_title(self) -> None:
        """format_plot_axes must call ax.set_title with the given title."""
        mock_ax = MagicMock()
        format_plot_axes(mock_ax, "My Title", "X", "Y")
        mock_ax.set_title.assert_called_once()
        args, _kwargs = mock_ax.set_title.call_args
        assert args[0] == "My Title"

    def test_calls_set_xlabel(self) -> None:
        """format_plot_axes must call ax.set_xlabel with the given label."""
        mock_ax = MagicMock()
        format_plot_axes(mock_ax, "T", "X Label", "Y")
        mock_ax.set_xlabel.assert_called_once()
        args, _kwargs = mock_ax.set_xlabel.call_args
        assert args[0] == "X Label"

    def test_calls_set_ylabel(self) -> None:
        """format_plot_axes must call ax.set_ylabel with the given label."""
        mock_ax = MagicMock()
        format_plot_axes(mock_ax, "T", "X", "Y Label")
        mock_ax.set_ylabel.assert_called_once()
        args, _kwargs = mock_ax.set_ylabel.call_args
        assert args[0] == "Y Label"

    def test_enables_grid(self) -> None:
        """format_plot_axes must call ax.grid to enable the grid."""
        mock_ax = MagicMock()
        format_plot_axes(mock_ax, "T", "X", "Y")
        mock_ax.grid.assert_called_once()

    def test_enables_legend(self) -> None:
        """format_plot_axes must call ax.legend to enable the legend."""
        mock_ax = MagicMock()
        format_plot_axes(mock_ax, "T", "X", "Y")
        mock_ax.legend.assert_called_once()
