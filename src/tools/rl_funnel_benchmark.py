"""Benchmark classical setpoint control against trajectory-tracking control."""

from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Callable
from typing import Any, cast

import numpy as np
import numpy.typing as npt
from scipy.integrate import solve_ivp
from scipy.linalg import solve_continuous_are

from src.core.contracts import check_positive, require
from src.tools.rl_funnel_reporting import BenchmarkResult, format_results
from src.tools.rl_funnel_support import (
    DEFAULT_CONTROL_SATURATION,
    GRAVITY_M_S2,
    PENDULUM_LINK_1_M,
    PENDULUM_LINK_2_M,
    PENDULUM_MASS_1_KG,
    PENDULUM_MASS_2_KG,
    double_pendulum_mass_matrix,
    validate_reference_trajectory,
    validate_state_vector,
    validate_time_span,
    validate_weight_matrix,
)

logger = logging.getLogger(__name__)


def double_pendulum_drift(
    t: float, x: npt.NDArray[Any], g: float = GRAVITY_M_S2
) -> npt.NDArray[Any]:
    """Passive dynamics of a double pendulum (drift term f(x,0)).

    State: x = [theta1, theta2, dtheta1, dtheta2]
    Parameters: m1=m2=1kg, L1=L2=0.5m
    """
    validate_state_vector(x, "x")
    check_positive(g, "g")
    th1, th2, dth1, dth2 = x
    s12 = np.sin(th1 - th2)
    M = double_pendulum_mass_matrix(th1, th2)
    rhs = np.array(
        [
            -PENDULUM_MASS_2_KG * PENDULUM_LINK_1_M * PENDULUM_LINK_2_M * dth2**2 * s12
            - (PENDULUM_MASS_1_KG + PENDULUM_MASS_2_KG) * g * PENDULUM_LINK_1_M * np.sin(th1),
            PENDULUM_MASS_2_KG * PENDULUM_LINK_1_M * PENDULUM_LINK_2_M * dth1**2 * s12
            - PENDULUM_MASS_2_KG * g * PENDULUM_LINK_2_M * np.sin(th2),
        ]
    )
    ddth = np.linalg.solve(M, rhs)
    return np.array([dth1, dth2, ddth[0], ddth[1]])


def double_pendulum_B(x: npt.NDArray[Any]) -> npt.NDArray[Any]:
    """Control input matrix g(x): torques applied at both joints."""
    validate_state_vector(x, "x")
    th1, th2, _, _ = x
    M_inv = np.linalg.inv(double_pendulum_mass_matrix(th1, th2))
    B_full = np.zeros((4, 2))
    B_full[2:, :] = M_inv  # torques affect angular accelerations
    return B_full


def generate_reference_trajectory(
    t_span: tuple[float, float],
    dt: float = 0.01,
    x0: npt.NDArray[Any] | None = None,
) -> tuple[npt.NDArray[Any], npt.NDArray[Any]]:
    """Generate reference trajectory via passive simulation from backswing position."""
    validate_time_span(t_span)
    check_positive(dt, "dt")
    if x0 is None:
        x0 = np.array([np.pi / 2, np.pi / 4, 0.0, 0.0])
    validate_state_vector(x0, "x0")

    sol = solve_ivp(
        double_pendulum_drift,
        t_span,
        x0,
        max_step=dt,
        dense_output=True,
    )
    t_ref = np.arange(t_span[0], t_span[1], dt)
    x_ref = sol.sol(t_ref)
    return t_ref, x_ref


def setpoint_lqr_controller(
    x_target: npt.NDArray[Any],
    Q_sp: npt.NDArray[Any] | None = None,
    R_sp: npt.NDArray[Any] | None = None,
) -> Callable[[float, npt.NDArray[Any]], npt.NDArray[Any]]:
    """Classical setpoint LQR controller.

    Minimizes integral (x - x_target)' Q (x - x_target) + u' R u.
    Linearizes around x_target.
    """
    n = 4
    m = 2
    validate_state_vector(x_target, "x_target")
    if Q_sp is None:
        Q_sp = np.diag([10.0, 10.0, 1.0, 1.0])
    if R_sp is None:
        R_sp = 0.1 * np.eye(m)
    validate_weight_matrix(Q_sp, (n, n), "Q_sp")
    validate_weight_matrix(R_sp, (m, m), "R_sp")

    # Linearize at target
    eps = 1e-6
    A = np.zeros((n, n))
    f0 = double_pendulum_drift(0.0, x_target)
    for j in range(n):
        ej = np.zeros(n)
        ej[j] = eps
        A[:, j] = (double_pendulum_drift(0.0, x_target + ej) - f0) / eps

    B0 = double_pendulum_B(x_target)

    P = solve_continuous_are(A, B0, Q_sp, R_sp)
    K = np.linalg.solve(R_sp, B0.T @ P)

    def controller(t: float, x: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """Apply setpoint LQR control law u = -K(x - x_target)."""
        return cast(npt.NDArray[Any], -K @ (x - x_target))

    return controller


def _precompute_lqr_gains(
    t_ref: npt.NDArray[Any],
    x_ref: npt.NDArray[Any],
    n: int,
    m: int,
    Q_tt: npt.NDArray[Any],
    R_tt: npt.NDArray[Any],
) -> npt.NDArray[Any]:
    """Precompute frozen-time LQR gains at every reference timestep.

    Returns gains_array of shape (T, m, n).
    """
    gains = []
    for i, t in enumerate(t_ref):
        x_ref_i = x_ref[:, i]
        eps = 1e-6
        A = np.zeros((n, n))
        f0 = double_pendulum_drift(t, x_ref_i)
        for j in range(n):
            ej = np.zeros(n)
            ej[j] = eps
            A[:, j] = (double_pendulum_drift(t, x_ref_i + ej) - f0) / eps
        B0 = double_pendulum_B(x_ref_i)
        try:
            P = solve_continuous_are(A, B0, Q_tt, R_tt)
            K = np.linalg.solve(R_tt, B0.T @ P)
        except (np.linalg.LinAlgError, ValueError):
            K = np.zeros((m, n))
        gains.append(K)
    return cast(npt.NDArray[Any], np.array(gains))


def trajectory_tracking_lqr(
    t_ref: npt.NDArray[Any],
    x_ref: npt.NDArray[Any],
    Q_tt: npt.NDArray[Any] | None = None,
    R_tt: npt.NDArray[Any] | None = None,
) -> Callable[[float, npt.NDArray[Any]], npt.NDArray[Any]]:
    """Trajectory Tracking Cost Functional (TTCF) controller.

    Time-varying LQR tracking x*(t). Gain precomputation delegated to
    ``_precompute_lqr_gains``.
    """
    from scipy.interpolate import interp1d

    n, m = 4, 2
    validate_reference_trajectory(t_ref, x_ref)
    Q_tt = Q_tt if Q_tt is not None else np.diag([10.0, 10.0, 1.0, 1.0])
    R_tt = R_tt if R_tt is not None else 0.1 * np.eye(m)
    validate_weight_matrix(Q_tt, (n, n), "Q_tt")
    validate_weight_matrix(R_tt, (m, m), "R_tt")

    gains_array = _precompute_lqr_gains(t_ref, x_ref, n, m, Q_tt, R_tt)
    x_ref_interp = interp1d(t_ref, x_ref, kind="linear", fill_value="extrapolate")

    def get_K(t: float) -> npt.NDArray[Any]:
        """Look up precomputed LQR gain at time t via nearest-index interpolation."""
        idx = np.clip(np.searchsorted(t_ref, t) - 1, 0, len(t_ref) - 2)
        return cast(npt.NDArray[Any], gains_array[idx])

    def controller(t: float, x: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """Apply time-varying TTCF control law u = -K(t)(x - x*(t))."""
        x_star = cast(npt.NDArray[Any], x_ref_interp(t))
        return cast(npt.NDArray[Any], -get_K(t) @ (x - x_star))

    return controller


def _compute_tracking_metrics(
    controller: Callable[[float, npt.NDArray[Any]], npt.NDArray[Any]],
    x_sim: npt.NDArray[Any],
    t_eval: npt.NDArray[Any],
    t_ref: npt.NDArray[Any],
    x_ref: npt.NDArray[Any],
) -> tuple[float, float]:
    """Compute mean tracking error and control effort from a simulated trajectory.

    Returns:
        (tracking_error, control_effort) as scalar floats.
    """
    from scipy.interpolate import interp1d

    x_ref_interp = interp1d(t_ref, x_ref, kind="linear", fill_value="extrapolate")
    x_star = x_ref_interp(t_eval)
    tracking_error = float(np.mean(np.linalg.norm(x_sim - x_star, axis=0) ** 2))
    u_all = np.array([controller(float(t), x_sim[:, i]) for i, t in enumerate(t_eval)])
    control_effort = float(np.mean(np.sum(u_all**2, axis=1)))
    return tracking_error, control_effort


def run_benchmark(
    controller: Callable[[float, npt.NDArray[Any]], npt.NDArray[Any]],
    x0_perturbed: npt.NDArray[Any],
    t_span: tuple[float, float],
    t_ref: npt.NDArray[Any],
    x_ref: npt.NDArray[Any],
    name: str,
    dt: float = 0.001,
    control_limit: float = DEFAULT_CONTROL_SATURATION,
) -> BenchmarkResult:
    """Simulate closed-loop system and compute performance metrics."""
    require(callable(controller), "controller must be callable")
    validate_state_vector(x0_perturbed, "x0_perturbed")
    validate_time_span(t_span)
    validate_reference_trajectory(t_ref, x_ref)
    check_positive(dt, "dt")
    check_positive(control_limit, "control_limit")
    require(bool(name.strip()), "name must be non-empty", name)
    start = time.perf_counter()

    def closed_loop(t: float, x: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """Closed-loop ODE: drift + controlled input with saturation."""
        u = np.clip(controller(t, x), -control_limit, control_limit)
        return cast(npt.NDArray[Any], double_pendulum_drift(t, x) + double_pendulum_B(x) @ u)

    sol = solve_ivp(closed_loop, t_span, x0_perturbed, max_step=dt, dense_output=True)
    elapsed = time.perf_counter() - start
    t_eval = np.arange(t_span[0], t_span[1], dt)
    x_sim = sol.sol(t_eval)
    tracking_error, control_effort = _compute_tracking_metrics(
        controller, x_sim, t_eval, t_ref, x_ref
    )
    return BenchmarkResult(
        name=name,
        tracking_error=tracking_error,
        control_effort=control_effort,
        runtime_sec=elapsed,
        trajectory=x_sim,
        t_grid=t_eval,
    )


# ---------------------------------------------------------------------------
# Main benchmark comparison
# ---------------------------------------------------------------------------


def _setup_comparison(
    perturbation_scale: float,
    t_span: tuple[float, float],
    dt: float,
    seed: int,
    control_limit: float,
) -> tuple[npt.NDArray[Any], npt.NDArray[Any], npt.NDArray[Any], npt.NDArray[Any]]:
    """Validate inputs and build reference + perturbed initial conditions.

    Returns:
        (x0_perturbed, t_ref, x_ref, x_target)
    """
    check_positive(control_limit, "control_limit")
    check_positive(dt, "dt")
    require(perturbation_scale >= 0, "perturbation_scale must be non-negative", perturbation_scale)
    validate_time_span(t_span)
    rng = np.random.default_rng(seed)
    logger.info("Generating reference trajectory...")
    x0_nominal = np.array([np.pi / 2, np.pi / 4, 0.0, 0.0])
    t_ref, x_ref = generate_reference_trajectory(t_span, dt=0.01, x0=x0_nominal)
    x0_perturbed = x0_nominal + perturbation_scale * rng.standard_normal(4)
    return x0_perturbed, t_ref, x_ref, x_ref[:, -1]


def run_comparison(
    perturbation_scale: float = 0.1,
    t_span: tuple[float, float] = (0.0, 0.5),
    dt: float = 0.001,
    seed: int = 42,
    control_limit: float = DEFAULT_CONTROL_SATURATION,
) -> list[BenchmarkResult]:
    """Run full benchmark comparison: setpoint vs TTCF vs passive."""
    x0_perturbed, t_ref, x_ref, x_target = _setup_comparison(
        perturbation_scale, t_span, dt, seed, control_limit
    )

    def passive_ctrl(t: float, x: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """Return zero torque (passive baseline, no active control)."""
        return np.zeros(2)

    def _rb(
        ctrl: Callable[[float, npt.NDArray[Any]], npt.NDArray[Any]], label: str
    ) -> BenchmarkResult:
        logger.info("Running %s benchmark...", label)
        return run_benchmark(
            ctrl, x0_perturbed, t_span, t_ref, x_ref, label, dt=dt, control_limit=control_limit
        )

    return [
        _rb(setpoint_lqr_controller(x_target), "Setpoint LQR"),
        _rb(trajectory_tracking_lqr(t_ref, x_ref), "Trajectory Tracking (TTCF)"),
        _rb(passive_ctrl, "Passive (no control)"),
    ]


def main() -> None:
    """CLI entry point: parse arguments and run benchmark comparison."""
    parser = argparse.ArgumentParser(
        description="RL and Funnel Benchmark: Compare setpoint vs trajectory tracking control"
    )
    parser.add_argument(
        "--perturbation",
        type=float,
        default=0.1,
        help="Initial condition perturbation scale (default: 0.1 rad)",
    )
    parser.add_argument(
        "--horizon", type=float, default=0.5, help="Simulation horizon in seconds (default: 0.5)"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for perturbation")
    parser.add_argument(
        "--control-limit",
        type=float,
        default=DEFAULT_CONTROL_SATURATION,
        help="Symmetric control saturation limit in N·m (default: 50.0)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    results = run_comparison(
        perturbation_scale=args.perturbation,
        t_span=(0.0, args.horizon),
        seed=args.seed,
        control_limit=args.control_limit,
    )
    logger.warning("\n%s", format_results(results))


if __name__ == "__main__":
    main()
