import logging
import os
import unittest
import warnings
from typing import Any
from unittest.mock import patch

import numpy as np

from src.affine_control.ddp import _DDP_MOCK_WARNING, adaptive_timestep_ddp_mock
from src.core.contracts import ContractViolationError

logger = logging.getLogger(__name__)


def _make_double_integrator() -> Any:
    """Return a double-integrator dynamics function for use in tests."""

    def double_integrator(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        """Compute double integrator dynamics: dx = [vel, u]."""
        return np.array([x[1], u[0]])

    return double_integrator


class TestAdaptiveDDP(unittest.TestCase):
    def test_adaptive_timestep_basic(self) -> None:
        """
        Test that adaptive timestep DDP runs without errors on a simple double integrator.
        """
        double_integrator = _make_double_integrator()
        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((10, 1))  # 10 steps of zero control

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            x_traj, u_traj, t_traj = adaptive_timestep_ddp_mock(
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
            logger.warning("Max dt found: %s", dts.max())
        self.assertTrue(np.all(dts <= 0.1 + 1e-9), "Max timestep violation")


class TestAdaptiveDDPMockWarning(unittest.TestCase):
    def test_emits_user_warning(self) -> None:
        """
        Verify that calling adaptive_timestep_ddp_mock raises a UserWarning
        identifying the function as a non-functional mock.
        """
        double_integrator = _make_double_integrator()
        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((5, 1))

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            adaptive_timestep_ddp_mock(double_integrator, x0, xf, u_init)

        user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
        self.assertGreater(len(user_warnings), 0, "Expected at least one UserWarning")
        warning_messages = [str(w.message) for w in user_warnings]
        self.assertTrue(
            any("non-functional mock" in msg for msg in warning_messages),
            f"Expected 'non-functional mock' in warning message. Got: {warning_messages}",
        )

    def test_warning_message_content(self) -> None:
        """
        Verify the warning message references the known issue document.
        """
        self.assertIn("ISSUE_Completist_Critical_DDPMock_2026-01-30.md", _DDP_MOCK_WARNING)
        self.assertIn("non-functional mock", _DDP_MOCK_WARNING)
        self.assertIn("mathematically incorrect", _DDP_MOCK_WARNING)

    def test_mock_solver_blocked_outside_test_or_demo_environment(self) -> None:
        """The direct mock entrypoint must fail closed outside test/demo environments."""
        double_integrator = _make_double_integrator()
        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((5, 1))

        with patch("src.affine_control.ddp._is_running_under_pytest", return_value=False):
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ContractViolationError):
                    adaptive_timestep_ddp_mock(double_integrator, x0, xf, u_init)

    def test_mock_solver_allows_explicit_demo_environment(self) -> None:
        """The direct mock entrypoint should run when the demo env flag is set."""
        double_integrator = _make_double_integrator()
        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((5, 1))

        with patch("src.affine_control.ddp._is_running_under_pytest", return_value=False):
            with patch.dict(os.environ, {"AFFINEDRIFT_ENABLE_MOCK_DDP": "1"}, clear=True):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    adaptive_timestep_ddp_mock(double_integrator, x0, xf, u_init)


if __name__ == "__main__":
    unittest.main()
