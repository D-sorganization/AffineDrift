"""Benchmark classical setpoint control against trajectory-tracking control."""

from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Callable
from typing import cast

import numpy as np
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


def double_pendulum_drift(t: float, x: np.ndarray, g: float = GRAVITY_M_S2) -> np.ndarray:
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


def double_pendulum_B(x: np.ndarray) -> np.ndarray:
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
    x0: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
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
    x_target: np.ndarray,
    Q_sp: np.ndarray | None = None,
    R_sp: np.ndarray | None = None,
) -> Callable[[float, np.ndarray], np.ndarray]:
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

    def controller(t: float, x: np.ndarray) -> np.ndarray:
        """Apply setpoint LQR control law u = -K(x - x_target)."""
        return cast(np.ndarray, -K @ (x - x_target))

    return controller


def trajectory_tracking_lqr(
    t_ref: np.ndarray,
    x_ref: np.ndarray,
    Q_tt: np.ndarray | None = None,
    R_tt: np.ndarray | None = None,
) -> Callable[[float, np.ndarray], np.ndarray]:
    """Trajectory Tracking Cost Functional (TTCF) controller.

    Time-varying LQR that tracks x*(t) with time-varying linearization.
    Uses frozen-time LQR at each point (approximation; exact requires Riccati ODE).
    """
    from scipy.interpolate import interp1d

    n = 4
    m = 2
    validate_reference_trajectory(t_ref, x_ref)
    if Q_tt is None:
        Q_tt = np.diag([10.0, 10.0, 1.0, 1.0])
    if R_tt is None:
        R_tt = 0.1 * np.eye(m)
    validate_weight_matrix(Q_tt, (n, n), "Q_tt")
    validate_weight_matrix(R_tt, (m, m), "R_tt")

    # Precompute gains at each reference time step
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

    gains_array = np.array(gains)  # shape (T, m, n)

    # Interpolate gains and reference trajectory
    def get_K(t: float) -> np.ndarray:
        """Look up precomputed LQR gain at time t via nearest-index interpolation."""
        idx = np.clip(np.searchsorted(t_ref, t) - 1, 0, len(t_ref) - 2)
        return cast(np.ndarray, gains_array[idx])

    x_ref_interp = interp1d(t_ref, x_ref, kind="linear", fill_value="extrapolate")

    def controller(t: float, x: np.ndarray) -> np.ndarray:
        """Apply time-varying TTCF control law u = -K(t)(x - x*(t))."""
        x_star = cast(np.ndarray, x_ref_interp(t))
        K = get_K(t)
        return cast(np.ndarray, -K @ (x - x_star))

    return controller


def run_benchmark(
    controller: Callable[[float, np.ndarray], np.ndarray],
    x0_perturbed: np.ndarray,
    t_span: tuple[float, float],
    t_ref: np.ndarray,
    x_ref: np.ndarray,
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

    def closed_loop(t: float, x: np.ndarray) -> np.ndarray:
        """Closed-loop ODE: drift + controlled input with saturation."""
        u = controller(t, x)
        # Clip control to prevent divergence
        u = cast(np.ndarray, np.clip(u, -control_limit, control_limit))
        return cast(np.ndarray, double_pendulum_drift(t, x) + double_pendulum_B(x) @ u)

    sol = solve_ivp(
        closed_loop,
        t_span,
        x0_perturbed,
        max_step=dt,
        dense_output=True,
    )

    elapsed = time.perf_counter() - start
    t_eval = np.arange(t_span[0], t_span[1], dt)
    x_sim = sol.sol(t_eval)

    from scipy.interpolate import interp1d

    x_ref_interp = interp1d(t_ref, x_ref, kind="linear", fill_value="extrapolate")
    x_star = x_ref_interp(t_eval)

    tracking_error = np.mean(np.linalg.norm(x_sim - x_star, axis=0) ** 2)
    u_all = np.array([controller(t, x_sim[:, i]) for i, t in enumerate(t_eval)])
    control_effort = np.mean(np.sum(u_all**2, axis=1))

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


def run_comparison(
    perturbation_scale: float = 0.1,
    t_span: tuple[float, float] = (0.0, 0.5),
    dt: float = 0.001,
    seed: int = 42,
    control_limit: float = DEFAULT_CONTROL_SATURATION,
) -> list[BenchmarkResult]:
    """Run full benchmark comparison: setpoint vs TTCF vs passive."""
    check_positive(control_limit, "control_limit")
    check_positive(dt, "dt")
    require(perturbation_scale >= 0, "perturbation_scale must be non-negative", perturbation_scale)
    validate_time_span(t_span)
    rng = np.random.default_rng(seed)

    logger.info("Generating reference trajectory...")
    x0_nominal = np.array([np.pi / 2, np.pi / 4, 0.0, 0.0])
    t_ref, x_ref = generate_reference_trajectory(t_span, dt=0.01, x0=x0_nominal)

    # Perturbed initial condition
    x0_perturbed = x0_nominal + perturbation_scale * rng.standard_normal(4)

    results = []

    # 1. Classical setpoint LQR (targets final state = impact position)
    x_target = x_ref[:, -1]
    logger.info("Running setpoint LQR benchmark...")
    sp_ctrl = setpoint_lqr_controller(x_target)
    results.append(
        run_benchmark(
            sp_ctrl,
            x0_perturbed,
            t_span,
            t_ref,
            x_ref,
            "Setpoint LQR",
            dt=dt,
            control_limit=control_limit,
        )
    )

    # 2. Trajectory Tracking Cost Functional
    logger.info("Running TTCF benchmark...")
    tt_ctrl = trajectory_tracking_lqr(t_ref, x_ref)
    results.append(
        run_benchmark(
            tt_ctrl,
            x0_perturbed,
            t_span,
            t_ref,
            x_ref,
            "Trajectory Tracking (TTCF)",
            dt=dt,
            control_limit=control_limit,
        )
    )

    # 3. Passive (no control) — baseline
    logger.info("Running passive baseline...")

    def passive_ctrl(t: float, x: np.ndarray) -> np.ndarray:
        """Return zero torque (passive baseline, no active control)."""
        return np.zeros(2)

    results.append(
        run_benchmark(
            passive_ctrl,
            x0_perturbed,
            t_span,
            t_ref,
            x_ref,
            "Passive (no control)",
            dt=dt,
            control_limit=control_limit,
        )
    )

    return results


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
