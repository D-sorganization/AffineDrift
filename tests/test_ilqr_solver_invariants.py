"""Property-based postcondition/invariant tests for ``ILQRSolver.optimize`` (issue #3181).

The A-O audit asked for optimizer *invariants* to be encoded as property tests
rather than relying on hand-picked happy-path examples. ``optimize`` returns
``(state_trajectory, control_trajectory, time_grid)``; regardless of the input
horizon or dynamics, the following must hold for every valid run:

* the state trajectory has exactly ``N + 1`` knots where ``N`` is the number of
  control steps (``u_init`` rows);
* the time grid has ``N + 1`` entries, starts at 0, and is strictly increasing
  with uniform spacing ``dt``;
* the returned state trajectory begins exactly at ``x0``;
* every returned array is finite.
"""

from __future__ import annotations

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st
from numpy.typing import NDArray

from src.core.optimizers.ilqr_solver import ILQRSolver


def _linear_dynamics(x: NDArray, u: NDArray) -> NDArray:
    """Stable, well-posed linear dynamics: dx/dt = -x + u (per dimension)."""
    return -np.asarray(x, dtype=np.float64) + np.asarray(u, dtype=np.float64)


@settings(max_examples=40, deadline=None)
@given(
    n_dim=st.integers(min_value=1, max_value=3),
    n_steps=st.integers(min_value=1, max_value=6),
    dt=st.floats(min_value=0.01, max_value=0.5),
    max_iters=st.integers(min_value=1, max_value=4),
)
def test_optimize_output_shape_and_time_grid_invariants(
    n_dim: int, n_steps: int, dt: float, max_iters: int
) -> None:
    x0 = np.zeros(n_dim, dtype=np.float64)
    xf = np.ones(n_dim, dtype=np.float64)
    u_init = np.zeros((n_steps, n_dim), dtype=np.float64)

    solver = ILQRSolver()
    x_traj, u_traj, t_traj = solver.optimize(
        _linear_dynamics, x0, xf, u_init, dt=dt, max_iters=max_iters
    )

    # Shape invariants: N control steps -> N+1 state/time knots.
    assert x_traj.shape[0] == n_steps + 1
    assert t_traj.shape[0] == n_steps + 1
    assert u_traj.shape[0] == n_steps

    # The trajectory must start exactly at the initial state.
    np.testing.assert_allclose(x_traj[0], x0)

    # Time grid: starts at 0, strictly increasing, uniform spacing dt.
    assert t_traj[0] == 0.0
    diffs = np.diff(t_traj)
    assert np.all(diffs > 0.0)
    np.testing.assert_allclose(diffs, dt, rtol=1e-6, atol=1e-9)

    # All outputs finite.
    assert np.all(np.isfinite(x_traj))
    assert np.all(np.isfinite(u_traj))
    assert np.all(np.isfinite(t_traj))


@settings(max_examples=25, deadline=None)
@given(
    n_steps=st.integers(min_value=1, max_value=8),
    dt=st.floats(min_value=0.01, max_value=0.2),
)
def test_optimize_diagnostics_iteration_count_is_bounded(n_steps: int, dt: float) -> None:
    """Reported iteration count never exceeds the requested ``max_iters``."""
    x0 = np.zeros(1, dtype=np.float64)
    xf = np.ones(1, dtype=np.float64)
    u_init = np.zeros((n_steps, 1), dtype=np.float64)
    max_iters = 5

    solver = ILQRSolver()
    solver.optimize(_linear_dynamics, x0, xf, u_init, dt=dt, max_iters=max_iters)

    diag = solver.last_diagnostics
    assert 1 <= diag.iterations <= max_iters
    assert diag.final_cost is not None
    assert np.isfinite(diag.final_cost)
