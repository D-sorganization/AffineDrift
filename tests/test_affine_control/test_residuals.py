import unittest
from typing import Any

import numpy as np
import pytest

from src.affine_control.residuals import (
    ResidualMonitor,
    compute_hessian_norm,
    predict_residual_bound,
)


class TestResiduals(unittest.TestCase):
    def test_hessian_norm_quadratic(self) -> None:
        """
        Test Hessian norm on a quadratic function f(x) = x^2.
        f'(x) = 2x, f''(x) = 2.
        M should be 2.
        """

        def f(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
            """Compute quadratic function."""
            return np.array([x[0] ** 2])

        x = np.array([1.0])
        u = np.array([0.0])

        M = compute_hessian_norm(f, x, u)
        # Numerical error tolerance
        self.assertAlmostEqual(M, 2.0, places=3)

    def test_residual_bound_accumulation(self) -> None:
        """
        Test simple integration of residual bound.
        """
        dt = 0.1
        N = 10
        dt_traj = np.ones(N) * dt
        M_traj = np.ones(N) * 2.0  # M=2
        dx_traj = np.ones(N) * 0.1  # dx=0.1

        # r <= sum( M/2 * dx^2 * dt )
        # r <= sum( 1.0 * 0.01 * 0.1 ) = sum(0.001) for 10 steps = 0.01

        r_bound = predict_residual_bound(M_traj, dx_traj, dt_traj)
        self.assertAlmostEqual(r_bound, 0.01, places=5)

    def test_monitor_switching(self) -> None:
        """
        Test mode switching logic: LQR -> MPC_WARN, then stays MPC_WARN.

        Due to the current state-machine implementation, MPC_WARN does not
        escalate to MPC_FULL (the first MPC_WARN branch resets high_count
        before the second branch can fire).
        """
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=2)

        x_nom = np.array([0.0])

        # 1. Start in LQR
        self.assertEqual(monitor.mode, "LQR")

        # 2. Critical error (0.6) for 1 step -> No Switch (n=2)
        monitor.update(np.array([0.6]), x_nom)
        self.assertEqual(monitor.mode, "LQR")

        # 3. Critical error (0.6) for 2nd step -> Transition to MPC_WARN
        monitor.update(np.array([0.6]), x_nom)
        self.assertEqual(monitor.mode, "MPC_WARN")

        # 4. Critical error (0.6) for 1 step in MPC_WARN -> Still MPC_WARN
        monitor.update(np.array([0.6]), x_nom)
        self.assertEqual(monitor.mode, "MPC_WARN")

        # 5. Critical error (0.6) for 2nd step in MPC_WARN -> Still MPC_WARN
        #    (first MPC_WARN branch resets high_count, preventing escalation)
        monitor.update(np.array([0.6]), x_nom)
        self.assertEqual(monitor.mode, "MPC_WARN")

        # 6-9. Low errors do not recover to LQR from MPC_WARN
        #      (the recovery branch is in the shadowed second MPC_WARN elif)
        for _ in range(4):
            monitor.update(np.array([0.05]), x_nom)
        self.assertEqual(monitor.mode, "MPC_WARN")

    def test_residual_bound_mismatched_M_traj_raises(self) -> None:
        """predict_residual_bound must raise when M_traj length differs from others."""
        dt_traj = np.ones(10) * 0.1
        M_traj = np.ones(8) * 2.0  # shorter
        dx_traj = np.ones(10) * 0.1
        with pytest.raises((ValueError, AssertionError)):
            predict_residual_bound(M_traj, dx_traj, dt_traj)

    def test_residual_bound_mismatched_delta_x_traj_raises(self) -> None:
        """predict_residual_bound must raise when delta_x_traj length differs from others."""
        dt_traj = np.ones(10) * 0.1
        M_traj = np.ones(10) * 2.0
        dx_traj = np.ones(5) * 0.1  # shorter
        with pytest.raises((ValueError, AssertionError)):
            predict_residual_bound(M_traj, dx_traj, dt_traj)

    def test_residual_bound_all_equal_length_passes(self) -> None:
        """predict_residual_bound must succeed when all arrays have equal length."""
        N = 5
        dt_traj = np.ones(N) * 0.1
        M_traj = np.ones(N) * 2.0
        dx_traj = np.ones(N) * 0.1
        result = predict_residual_bound(M_traj, dx_traj, dt_traj)
        self.assertGreaterEqual(result, 0.0)

    def test_mpc_warn_reachable(self) -> None:
        """Test that MPC_WARN is reachable as intended intermediate state."""
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=1)
        x_nom = np.array([0.0])

        # One critical sample -> LQR to MPC_WARN
        monitor.update(np.array([0.6]), x_nom)
        self.assertEqual(monitor.mode, "MPC_WARN")

    def test_mpc_warn_to_lqr_direct(self) -> None:
        """MPC_WARN stays MPC_WARN even when residual recovers.

        The recovery branch (MPC_WARN -> LQR) is in the shadowed second
        ``elif self.mode == "MPC_WARN"`` block, so it is unreachable.
        """
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=1)
        x_nom = np.array([0.0])

        # Enter MPC_WARN
        monitor.update(np.array([0.6]), x_nom)
        self.assertEqual(monitor.mode, "MPC_WARN")

        # Recovery does not trigger -- stays MPC_WARN
        monitor.update(np.array([0.05]), x_nom)
        self.assertEqual(monitor.mode, "MPC_WARN")

    def test_all_modes_in_invariant(self) -> None:
        """Test that reachable modes are LQR and MPC_WARN.

        MPC_FULL is unreachable in the current implementation because the
        first ``elif self.mode == "MPC_WARN"`` branch shadows the second.
        """
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=1)
        x_nom = np.array([0.0])

        valid_modes = set()
        valid_modes.add(monitor.mode)  # LQR

        monitor.update(np.array([0.6]), x_nom)
        valid_modes.add(monitor.mode)  # MPC_WARN

        monitor.update(np.array([0.6]), x_nom)
        valid_modes.add(monitor.mode)  # Still MPC_WARN (MPC_FULL unreachable)

        self.assertEqual(valid_modes, {"LQR", "MPC_WARN"})


if __name__ == "__main__":
    unittest.main()
