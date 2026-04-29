"""Core performance benchmarks for AffineDrift.

Measures the hot paths in:
- iLQR trajectory optimisation (backward pass, rollout, linearisation)
- Affine control swing optimisation (cost evaluation, trajectory cost)
- Golf ball flight dynamics (RK4 step, full flight simulation)
- Putting simulator (single putt roll-out, slope/contour evaluation)
- Residual bounding (Hessian norm, predict_residual_bound)
- DDP adaptive-timestep iteration

Run with::

    pytest benchmarks/ --benchmark-only
    pytest benchmarks/ --benchmark-compare

Each test is grouped in ``TestCorePerformance`` so benchmark reports are
easy to filter by class.
"""

from __future__ import annotations

import warnings
from typing import Any

import numpy as np
import pytest

# Silence the mock-solver warning in benchmarks — we're explicitly
# exercising the placeholder DDP path as a CPU-throughput proxy.
pytestmark = [pytest.mark.filterwarnings("ignore::UserWarning")]


# ---------------------------------------------------------------------------
# Helpers shared across tests
# ---------------------------------------------------------------------------


def _make_double_integrator(n_joints: int):  # type: ignore[return]
    """Return a double-integrator dynamics closure for *n_joints*."""

    def dynamics(
        x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
    ) -> np.ndarray[Any, Any]:
        dq = x[n_joints:]
        ddq = u
        return np.concatenate([dq, ddq])

    return dynamics


class TestCorePerformance:
    """Performance benchmarks for AffineDrift critical paths."""

    # ------------------------------------------------------------------
    # 1. iLQR – rollout (Euler integration over a 50-step horizon)
    # ------------------------------------------------------------------

    def test_ilqr_rollout_50_steps(self, benchmark: Any, ilqr_solver: Any) -> None:
        """Measure RK4-like Euler rollout across a 50-step horizon (4-DOF system)."""
        n_joints = 2
        dynamics = _make_double_integrator(n_joints)
        x0 = np.array([0.1, 0.2, 0.0, 0.0], dtype=np.float64)
        u_traj = np.random.default_rng(42).standard_normal((50, n_joints)) * 0.5

        result = benchmark(ilqr_solver._rollout, dynamics, x0, u_traj, 0.01)
        assert result.shape == (51, 4)

    # ------------------------------------------------------------------
    # 2. iLQR – linearize_dynamics (finite-difference Jacobians)
    # ------------------------------------------------------------------

    def test_ilqr_linearize_dynamics(self, benchmark: Any, ilqr_solver: Any) -> None:
        """Measure finite-difference linearisation of a 4-state / 2-control system."""
        n_joints = 2
        dynamics = _make_double_integrator(n_joints)
        x = np.array([0.3, -0.1, 0.5, 0.2], dtype=np.float64)
        u = np.array([0.1, -0.2], dtype=np.float64)

        A, B = benchmark(ilqr_solver._linearize_dynamics, dynamics, x, u, 4, 2, 0.01)
        assert A.shape == (4, 4)
        assert B.shape == (4, 2)

    # ------------------------------------------------------------------
    # 3. iLQR – full backward pass (10-step horizon, 2-DOF)
    # ------------------------------------------------------------------

    def test_ilqr_backward_pass_10_steps(self, benchmark: Any, ilqr_solver: Any) -> None:
        """Measure a complete iLQR backward pass on a short 10-step horizon."""
        n_joints = 2
        dynamics = _make_double_integrator(n_joints)
        rng = np.random.default_rng(7)
        x0 = np.zeros(4)
        xf = np.array([1.0, 1.0, 0.0, 0.0])
        u_traj = rng.standard_normal((10, n_joints)) * 0.1
        x_traj = ilqr_solver._rollout(dynamics, x0, u_traj, 0.01)

        Q = np.eye(4)
        R = np.eye(2) * 0.01
        Q_f = np.eye(4) * 100.0

        k_traj, K_traj, max_k = benchmark(
            ilqr_solver._backward_pass,
            x_traj,
            u_traj,
            xf,
            0.01,
            4,
            2,
            Q,
            R,
            Q_f,
            dynamics,
        )
        assert k_traj.shape == (10, 2)
        assert K_traj.shape == (10, 2, 4)

    # ------------------------------------------------------------------
    # 4. iLQR – trajectory cost evaluation
    # ------------------------------------------------------------------

    def test_ilqr_trajectory_cost(self, benchmark: Any, ilqr_solver: Any) -> None:
        """Measure quadratic trajectory cost summation over a 50-step horizon."""
        n_joints = 2
        dynamics = _make_double_integrator(n_joints)
        rng = np.random.default_rng(13)
        x0 = np.zeros(4)
        u_traj = rng.standard_normal((50, n_joints)) * 0.3
        x_traj = ilqr_solver._rollout(dynamics, x0, u_traj, 0.01)
        xf = np.zeros(4)
        Q = np.eye(4)
        R = np.eye(2) * 0.01
        Q_f = np.eye(4) * 100.0

        cost = benchmark(ilqr_solver._trajectory_cost, x_traj, u_traj, xf, Q, R, Q_f)
        assert np.isfinite(cost)

    # ------------------------------------------------------------------
    # 5. Swing optimizer – instantaneous cost computation
    # ------------------------------------------------------------------

    def test_swing_optimizer_compute_cost(
        self, benchmark: Any, swing_optimizer_config_3j: Any
    ) -> None:
        """Measure a single instantaneous quadratic cost call (3-joint, 6-D state)."""
        from src.affine_control.swing_optimizer import SwingOptimizer

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            optimizer = SwingOptimizer(swing_optimizer_config_3j)

        state = np.array([0.1, -0.05, 0.2, 45.0, 48.0, 52.0], dtype=np.float64)
        control = np.array([0.5, -0.3, 0.8], dtype=np.float64)

        cost = benchmark(optimizer.compute_cost, state, control)
        assert cost >= 0.0

    # ------------------------------------------------------------------
    # 6. Swing optimizer – full trajectory cost (20-step horizon)
    # ------------------------------------------------------------------

    def test_swing_optimizer_trajectory_cost_20_steps(
        self, benchmark: Any, swing_optimizer_config_3j: Any
    ) -> None:
        """Measure trajectory cost over a 20-step horizon (3 joints)."""
        from src.affine_control.swing_optimizer import SwingOptimizer

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            optimizer = SwingOptimizer(swing_optimizer_config_3j)

        n_steps = 20
        state_dim = swing_optimizer_config_3j.state_dim  # 6
        ctrl_dim = swing_optimizer_config_3j.control_dim  # 3
        rng = np.random.default_rng(99)
        trajectory = [rng.standard_normal(state_dim) * 0.5 for _ in range(n_steps + 1)]
        controls = [rng.standard_normal(ctrl_dim) * 0.3 for _ in range(n_steps)]

        cost = benchmark(optimizer.compute_trajectory_cost, trajectory, controls)
        assert cost >= 0.0

    # ------------------------------------------------------------------
    # 7. Ball flight – single RK4 integration step
    # ------------------------------------------------------------------

    def test_ball_flight_single_rk4_step(
        self,
        benchmark: Any,
        ball_flight_dynamics: Any,
        driver_initial_state: Any,
    ) -> None:
        """Measure a single RK4 step for the full 9-D aerodynamic ball model."""
        state_vec = driver_initial_state.state_vector
        u = np.zeros(3)

        result = benchmark(ball_flight_dynamics._rk4_step, state_vec, u, 0.001)
        assert result.shape == (9,)
        assert np.all(np.isfinite(result))

    # ------------------------------------------------------------------
    # 8. Ball flight – full driver trajectory simulation
    # ------------------------------------------------------------------

    def test_ball_flight_driver_trajectory(
        self,
        benchmark: Any,
        ball_flight_dynamics: Any,
        driver_initial_state: Any,
    ) -> None:
        """Measure a complete driver ball-flight simulation (dt=0.01, ~5-7 s)."""
        trajectory = benchmark(
            ball_flight_dynamics.simulate,
            driver_initial_state,
            0.01,  # dt
            10.0,  # max_time
        )
        assert len(trajectory) > 10

    # ------------------------------------------------------------------
    # 9. Ball flight – linearization (finite-difference Jacobians, 9-D)
    # ------------------------------------------------------------------

    def test_ball_flight_linearize(
        self,
        benchmark: Any,
        ball_flight_dynamics: Any,
        driver_initial_state: Any,
    ) -> None:
        """Measure finite-difference Jacobian computation for the 9-D ball model."""
        x = driver_initial_state.state_vector
        u = np.zeros(3)

        A, B = benchmark(ball_flight_dynamics.linearize, x, u)
        assert A.shape == (9, 9)
        assert B.shape == (9, 3)

    # ------------------------------------------------------------------
    # 10. Putting – flat green roll-out (10-foot putt)
    # ------------------------------------------------------------------

    def test_putting_flat_green_10ft_putt(
        self, benchmark: Any, flat_green_simulator: Any
    ) -> None:
        """Measure full putt roll-out on a flat green (3 m, medium speed)."""
        trajectory = benchmark(
            flat_green_simulator.simulate,
            5.0,   # start_x (m, near center)
            5.0,   # start_y
            2.5,   # velocity_x  (approx 10-ft putt)
            0.0,   # velocity_y
        )
        assert len(trajectory) > 5

    # ------------------------------------------------------------------
    # 11. Putting – contoured green elevation evaluation (batch)
    # ------------------------------------------------------------------

    def test_green_surface_elevation_batch(
        self, benchmark: Any, contoured_green_simulator: Any
    ) -> None:
        """Measure 200 elevation queries on a multi-control-point contoured green."""
        surface = contoured_green_simulator.surface
        xs = np.linspace(0.5, 19.5, 20)
        ys = np.linspace(0.5, 19.5, 10)

        def evaluate_all() -> list[float]:
            return [surface.evaluate_elevation(float(x), float(y)) for x in xs for y in ys]

        results = benchmark(evaluate_all)
        assert len(results) == 200

    # ------------------------------------------------------------------
    # 12. Residuals – Hessian norm (finite-difference, small system)
    # ------------------------------------------------------------------

    def test_hessian_norm_2state(self, benchmark: Any) -> None:
        """Measure numerical Hessian norm for a 2-state pendulum dynamics."""
        from src.affine_control.residuals import compute_hessian_norm

        def pendulum_dyn(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
            g = 9.81
            theta, omega = x[0], x[1]
            return np.array([omega, -g * np.sin(theta) + u[0]])

        x = np.array([0.3, 0.5])
        u = np.array([0.1])

        norm = benchmark(compute_hessian_norm, pendulum_dyn, x, u)
        assert np.isfinite(norm)
        assert norm >= 0.0

    # ------------------------------------------------------------------
    # 13. Residuals – predict_residual_bound (vectorised)
    # ------------------------------------------------------------------

    def test_predict_residual_bound_100steps(self, benchmark: Any) -> None:
        """Measure vectorised residual bound prediction over a 100-step trajectory."""
        from src.affine_control.residuals import predict_residual_bound

        rng = np.random.default_rng(3)
        N = 100
        M_traj = rng.uniform(0.5, 5.0, N)
        delta_x_traj = rng.uniform(0.01, 0.1, N)
        dt_traj = np.full(N, 0.01)

        r_bound = benchmark(predict_residual_bound, M_traj, delta_x_traj, dt_traj)
        assert r_bound >= 0.0

    # ------------------------------------------------------------------
    # 14. DDP – estimate_perturbation_size (hot inner-loop call)
    # ------------------------------------------------------------------

    def test_estimate_perturbation_size(self, benchmark: Any) -> None:
        """Measure perturbation-size estimation for a moderate-magnitude state."""
        from src.affine_control.ddp import estimate_perturbation_size

        x = np.array([1.2, -0.8, 3.4, -0.2, 0.9, -1.5])
        u = np.zeros(2)

        size = benchmark(estimate_perturbation_size, x, u)
        assert size >= 0.0

    # ------------------------------------------------------------------
    # 15. DDP – adaptive timestep computation (10-step trajectory)
    # ------------------------------------------------------------------

    def test_ddp_adaptive_timesteps_10_steps(self, benchmark: Any) -> None:
        """Measure adaptive timestep selection over a 10-step DDP iteration."""
        from src.affine_control.ddp import _compute_adaptive_timesteps
        from src.affine_control.residuals import compute_hessian_bound

        def linear_dyn(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
            A = np.array([[0.0, 1.0], [-1.0, -0.1]])
            B = np.array([[0.0], [1.0]])
            return A @ x + B @ u

        N = 10
        rng = np.random.default_rng(5)
        x_traj = rng.standard_normal((N + 1, 2))
        u_traj = rng.standard_normal((N, 1)) * 0.3

        dt_arr = benchmark(
            _compute_adaptive_timesteps,
            linear_dyn,
            x_traj,
            u_traj,
            1e-3,
            compute_hessian_bound,
        )
        assert dt_arr.shape == (N,)
        assert np.all(dt_arr > 0)
