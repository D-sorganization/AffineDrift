from typing import Any

import numpy as np

from src.affine_control.ddp import adaptive_timestep_ddp


def double_integrator(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    """Double integrator dynamics."""
    # x = [p, v], u = [a]
    # dx = [v, a]
    return np.array([x[1], u[0]])


def test_adaptive_timestep_ddp_smoke() -> None:
    """Test adaptive timestep DDP (smoke test)."""
    x0 = np.array([0.0, 0.0])
    xf = np.array([1.0, 0.0])
    u_init = np.zeros((10, 1))

    # Mock Hessian bound function
    def mock_hessian(f: Any, x: Any, u: Any) -> float:
        """Mock Hessian bound."""
        return 1.0

    x_traj, u_traj, t_traj = adaptive_timestep_ddp(
        double_integrator,
        x0,
        xf,
        u_init,
        compute_hessian_bound_func=mock_hessian,
    )

    # Check outputs
    assert len(x_traj) > 0
    assert len(u_traj) > 0
    assert len(t_traj) == len(x_traj)
    # Time should be increasing
    assert np.all(np.diff(t_traj) > 0)
