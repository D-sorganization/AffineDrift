import unittest

import numpy as np
from typing import Any

from src.affine_control.ddp import adaptive_timestep_ddp


class TestAdaptiveDDP(unittest.TestCase):
    def test_adaptive_timestep_basic(self) -> None:
        """
        Test that adaptive timestep DDP runs without errors on a simple double integrator.
        """

        def double_integrator(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
            # x = [pos, vel]
            # dx = [vel, u]
            return np.array([x[1], u[0]])

        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((10, 1))  # 10 steps of zero control

        x_traj, u_traj, t_traj = adaptive_timestep_ddp(
            double_integrator, x0, xf, u_init, eps_residual=0.01, max_iters=5
        )

        # Check outputs
        self.assertEqual(
            len(t_traj), len(x_traj), "Time and state trajectories should match length"
        )
        self.assertEqual(len(t_traj) - 1, len(u_traj), "Control trajectory should be N-1")
        self.assertTrue(t_traj[-1] > 0, "Time should advance")

        # Check that timesteps are within bounds (0.001 to 0.1 as per implementation)
        dts = np.diff(t_traj)
        self.assertTrue(np.all(dts >= 0.001), "Min timestep violation")
        if not np.all(dts <= 0.1):
            print(f"Max dt found: {dts.max()}")
        self.assertTrue(np.all(dts <= 0.1 + 1e-9), "Max timestep violation")


if __name__ == "__main__":
    unittest.main()
