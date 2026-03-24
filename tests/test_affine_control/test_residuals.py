import unittest
from typing import Any

import numpy as np

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
        Test mode switching logic with hysteresis.
        """
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=2)

        x_nom = np.array([0.0])

        # 1. Start in LQR
        self.assertEqual(monitor.mode, "LQR")

        # 2. Critical error (0.6) for 1 step -> No Switch (n=2)
        monitor.update(np.array([0.6]), x_nom)
        self.assertEqual(monitor.mode, "LQR")

        # 3. Critical error (0.6) for 2nd step -> Enter warning mode
        monitor.update(np.array([0.6]), x_nom)
        self.assertEqual(monitor.mode, "MPC_WARN")

        # 4. Two more critical steps -> Switch to full MPC
        monitor.update(np.array([0.6]), x_nom)
        monitor.update(np.array([0.6]), x_nom)
        self.assertEqual(monitor.mode, "MPC_FULL")

        # 5. Low error (0.05) for 1 step -> No Switch
        monitor.update(np.array([0.05]), x_nom)
        self.assertEqual(monitor.mode, "MPC_FULL")

        # 6. Low error (0.05) for 2nd step -> Back to warning mode
        monitor.update(np.array([0.05]), x_nom)
        self.assertEqual(monitor.mode, "MPC_WARN")

        # 7. Two more low-error steps -> Return to LQR
        monitor.update(np.array([0.05]), x_nom)
        monitor.update(np.array([0.05]), x_nom)
        self.assertEqual(monitor.mode, "LQR")

    def test_monitor_warning_band_transitions(self) -> None:
        """Residuals between warning and critical should activate MPC_WARN."""
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=2)
        x_nom = np.array([0.0])
        monitor.update(np.array([0.2]), x_nom)
        mode, _ = monitor.update(np.array([0.2]), x_nom)
        self.assertEqual(mode, "MPC_WARN")

    def test_predict_residual_bound_rejects_mismatched_lengths(self) -> None:
        """Mismatched trajectory lengths must fail fast instead of truncating."""
        with self.assertRaisesRegex(Exception, "equal length"):
            predict_residual_bound(
                np.array([1.0, 2.0]),
                np.array([0.1]),
                np.array([0.01, 0.01]),
            )


if __name__ == "__main__":
    unittest.main()
