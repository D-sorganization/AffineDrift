"""Tests for wave-6 extracted helper functions (issue #1635).

Covers the helpers extracted from rl_funnel_benchmark.py:
- _validate_ttcf_inputs
- _validate_benchmark_inputs
- _compute_tracking_metrics
- _precompute_lqr_gains
- _setup_comparison
"""

from __future__ import annotations

import unittest

import numpy as np

from src.core.contracts import ContractViolationError
from src.tools.rl_funnel_benchmark import (
    _compute_tracking_metrics,
    _precompute_lqr_gains,
    _setup_comparison,
    _validate_benchmark_inputs,
    _validate_ttcf_inputs,
)


class TestValidateTtcfInputs(unittest.TestCase):
    def test_accepts_valid_inputs(self) -> None:
        t_ref = np.linspace(0.0, 0.5, 10)
        x_ref = np.zeros((4, 10))
        _validate_ttcf_inputs(t_ref, x_ref)  # should not raise

    def test_rejects_t_ref_not_array(self) -> None:
        with self.assertRaises(ContractViolationError):
            _validate_ttcf_inputs([0.0, 0.5], np.zeros((4, 2)))  # type: ignore[arg-type]

    def test_rejects_wrong_state_dim(self) -> None:
        t_ref = np.linspace(0.0, 0.5, 5)
        x_ref = np.zeros((3, 5))  # wrong: should be (4, T)
        with self.assertRaises(ContractViolationError):
            _validate_ttcf_inputs(t_ref, x_ref)

    def test_rejects_mismatched_time_length(self) -> None:
        t_ref = np.linspace(0.0, 0.5, 5)
        x_ref = np.zeros((4, 10))  # T mismatch
        with self.assertRaises(ContractViolationError):
            _validate_ttcf_inputs(t_ref, x_ref)


class TestValidateBenchmarkInputs(unittest.TestCase):
    def test_accepts_valid_inputs(self) -> None:
        def ctrl(t: float, x: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
            return np.zeros(2)

        _validate_benchmark_inputs(ctrl, np.zeros(4), (0.0, 0.5), 0.01)

    def test_rejects_non_callable_controller(self) -> None:
        with self.assertRaises(ContractViolationError):
            _validate_benchmark_inputs(None, np.zeros(4), (0.0, 0.5), 0.01)  # type: ignore

    def test_rejects_wrong_state_shape(self) -> None:
        def ctrl(t: float, x: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
            return np.zeros(2)

        with self.assertRaises(ContractViolationError):
            _validate_benchmark_inputs(ctrl, np.zeros(3), (0.0, 0.5), 0.01)

    def test_rejects_reversed_tspan(self) -> None:
        def ctrl(t: float, x: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
            return np.zeros(2)

        with self.assertRaises(ContractViolationError):
            _validate_benchmark_inputs(ctrl, np.zeros(4), (1.0, 0.0), 0.01)


class TestPrecomputeLqrGains(unittest.TestCase):
    def test_returns_correct_shape(self) -> None:
        n, m = 4, 2
        t_ref = np.linspace(0.0, 0.1, 5)
        x_ref = np.zeros((4, 5))
        gains = _precompute_lqr_gains(t_ref, x_ref, n, m, np.eye(n), np.eye(m))
        assert gains.shape == (5, m, n)

    def test_gains_finite_at_equilibrium(self) -> None:
        n, m = 4, 2
        t_ref = np.linspace(0.0, 0.1, 3)
        x_ref = np.zeros((4, 3))
        Q = np.diag([10.0, 10.0, 1.0, 1.0])
        R = 0.1 * np.eye(m)
        gains = _precompute_lqr_gains(t_ref, x_ref, n, m, Q, R)
        assert np.all(np.isfinite(gains))


class TestComputeTrackingMetrics(unittest.TestCase):
    def test_zero_error_when_tracking_perfectly(self) -> None:
        t_ref = np.linspace(0.0, 0.1, 5)
        x_ref = np.zeros((4, 5))

        def ctrl(t: float, x: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
            return np.zeros(2)

        err, effort = _compute_tracking_metrics(ctrl, np.zeros((4, 5)), t_ref, t_ref, x_ref)
        assert err == 0.0
        assert effort == 0.0

    def test_nonzero_error_when_off_track(self) -> None:
        t_ref = np.linspace(0.0, 0.1, 5)
        x_ref = np.zeros((4, 5))
        x_sim = np.ones((4, 5))

        def ctrl(t: float, x: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
            return np.zeros(2)

        err, _ = _compute_tracking_metrics(ctrl, x_sim, t_ref, t_ref, x_ref)
        assert err > 0.0

    def test_nonzero_effort_for_active_controller(self) -> None:
        t_ref = np.linspace(0.0, 0.1, 5)
        x_ref = np.zeros((4, 5))

        def ctrl(t: float, x: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
            return np.ones(2)

        _, effort = _compute_tracking_metrics(ctrl, np.zeros((4, 5)), t_ref, t_ref, x_ref)
        assert effort > 0.0


class TestSetupComparison(unittest.TestCase):
    def test_returns_correct_shapes(self) -> None:
        x0_p, t_ref, x_ref, x_target = _setup_comparison(
            perturbation_scale=0.1,
            t_span=(0.0, 0.2),
            dt=0.01,
            seed=0,
        )
        assert x0_p.shape == (4,)
        assert t_ref.ndim == 1
        assert x_ref.shape == (4, len(t_ref))
        assert x_target.shape == (4,)

    def test_x_target_is_last_ref_state(self) -> None:
        _, _, x_ref, x_target = _setup_comparison(
            perturbation_scale=0.1,
            t_span=(0.0, 0.2),
            dt=0.01,
            seed=0,
        )
        np.testing.assert_array_equal(x_target, x_ref[:, -1])

    def test_uses_requested_dt_for_reference_grid(self) -> None:
        _, t_ref, x_ref, _ = _setup_comparison(
            perturbation_scale=0.1,
            t_span=(0.0, 0.2),
            dt=0.05,
            seed=0,
        )

        np.testing.assert_allclose(np.diff(t_ref), 0.05)
        assert len(t_ref) == 4
        assert x_ref.shape == (4, len(t_ref))

    def test_rejects_zero_dt(self) -> None:
        with self.assertRaises(ContractViolationError):
            _setup_comparison(0.1, (0.0, 0.2), dt=0.0, seed=0)
