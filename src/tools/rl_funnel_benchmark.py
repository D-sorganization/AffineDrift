"""RL and Funnel Benchmark: Compare classical setpoint control vs trajectory tracking cost.

This module implements the benchmark described in issue #1269:
  - Classical setpoint RL: reward = -||x - x_target||^2
  - Trajectory Tracking Cost Functional (TTCF): reward = -||x - x*(t)||^2 - alpha*||u||^2
  - Funnel-verified control: track trajectory AND certify convergence rate

Run:
  python3 -m src.tools.rl_funnel_benchmark --help

Reference:
  Vol I, Ch 5-8; Vol II, Ch 4 (Funnel Synthesis)
"""

from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import solve_continuous_are

from src.core.constants import GRAVITY_M_S2

# Default control saturation limits for the double-pendulum benchmark (N*m).
# The value 50 N*m is appropriate for a 1 kg, 0.5 m double pendulum; adjust
# for different systems by passing `control_limits` to run_benchmark().
CONTROL_SATURATION_DEFAULT: tuple[float, float] = (-50.0, 50.0)


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System definition: double pendulum (2-DoF golf swing proxy)
# ---------------------------------------------------------------------------


def double_pendulum_drift(t: float, x: np.ndarray, g: float = GRAVITY_M_S2) -> np.ndarray:
    """Passive dynamics of a double pendulum (drift term f(x,0)).

    State: x = [theta1, theta2, dtheta1, dtheta2]
    Parameters: m1=m2=1kg, L1=L2=0.5m
    """
    m1, m2, L1, L2 = 1.0, 1.0, 0.5, 0.5
    th1, th2, dth1, dth2 = x
    c12 = np.cos(th1 - th2)
    s12 = np.sin(th1 - th2)

    M = np.array([[(m1 + m2) * L1**2, m2 * L1 * L2 * c12], [m2 * L1 * L2 * c12, m2 * L2**2]])
    rhs = np.array(
        [
            -m2 * L1 * L2 * dth2**2 * s12 - (m1 + m2) * g * L1 * np.sin(th1),
            m2 * L1 * L2 * dth1**2 * s12 - m2 * g * L2 * np.sin(th2),
        ]
    )
    ddth = np.linalg.solve(M, rhs)
    return np.array([dth1, dth2, ddth[0], ddth[1]])


def double_pendulum_B(x: np.ndarray) -> np.ndarray:
    """Control input matrix g(x): torques applied at both joints."""
    m1, m2, L1, L2 = 1.0, 1.0, 0.5, 0.5
    th1, th2, _, _ = x
    c12 = np.cos(th1 - th2)
    M = np.array([[(m1 + m2) * L1**2, m2 * L1 * L2 * c12], [m2 * L1 * L2 * c12, m2 * L2**2]])
    M_inv = np.linalg.inv(M)
    B_full = np.zeros((4, 2))
    B_full[2:, :] = M_inv  # torques affect angular accelerations
    return B_full


# ---------------------------------------------------------------------------
# Reference trajectory generation
# ---------------------------------------------------------------------------


def generate_reference_trajectory(
    t_span: tuple[float, float],
    dt: float = 0.01,
    x0: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate reference trajectory via passive simulation from backswing position."""
    if x0 is None:
        x0 = np.array([np.pi / 2, np.pi / 4, 0.0, 0.0])

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


# ---------------------------------------------------------------------------
# Controllers
# ---------------------------------------------------------------------------


@dataclass
class BenchmarkResult:
    """Container for the output of a single benchmark run.

    Attributes:
        name: Human-readable controller name used in reports.
        tracking_error: Integrated squared state-tracking error.
        control_effort: Integrated squared control input norm.
        runtime_sec: Wall-clock time for the benchmark run in seconds.
        trajectory: State trajectory array, shape ``(T, n)``.
        t_grid: Time grid corresponding to *trajectory*, shape ``(T,)``.
    """

    name: str
    tracking_error: float
    control_effort: float
    runtime_sec: float
    trajectory: np.ndarray = field(repr=False)
    t_grid: np.ndarray = field(repr=False)


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
    if Q_sp is None:
        Q_sp = np.diag([10.0, 10.0, 1.0, 1.0])
    if R_sp is None:
        R_sp = 0.1 * np.eye(m)

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
        return -K @ (x - x_target)

    return controller


def _precompute_lqr_gains(
    t_ref: np.ndarray,
    x_ref: np.ndarray,
    n: int,
    m: int,
    Q_tt: np.ndarray,
    R_tt: np.ndarray,
) -> np.ndarray:
    """Precompute time-varying LQR gains at each reference time step.

    For each step, linearises the double-pendulum dynamics via finite differences,
    then solves the continuous algebraic Riccati equation (CARE) to obtain the
    feedback gain matrix.  Falls back to a zero-gain matrix when the CARE is
    infeasible.

    Args:
        t_ref: Reference time array of shape (T,).
        x_ref: Reference state trajectory of shape (n, T).
        n: State dimension.
        m: Input dimension.
        Q_tt: State cost matrix of shape (n, n).
        R_tt: Input cost matrix of shape (m, m).

    Returns:
        Gains array of shape (T, m, n).
    """
    gains = []
    eps = 1e-6
    for _i, t in enumerate(t_ref):
        x_ref_i = x_ref[:, _i]
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
    return np.array(gains)


def trajectory_tracking_lqr(
    t_ref: np.ndarray,
    x_ref: np.ndarray,
    Q_tt: np.ndarray | None = None,
    R_tt: np.ndarray | None = None,
) -> Callable[[float, np.ndarray], np.ndarray]:
    """Trajectory Tracking Cost Functional (TTCF) controller.

    Time-varying LQR that tracks x*(t) with time-varying linearization.
    Uses frozen-time LQR at each point (approximation; exact requires Riccati ODE).

    Gain precomputation is delegated to ``_precompute_lqr_gains``.
    """
    from scipy.interpolate import interp1d

    n = 4
    m = 2
    if Q_tt is None:
        Q_tt = np.diag([10.0, 10.0, 1.0, 1.0])
    if R_tt is None:
        R_tt = 0.1 * np.eye(m)

    gains_array = _precompute_lqr_gains(t_ref, x_ref, n, m, Q_tt, R_tt)

    def get_K(t: float) -> np.ndarray:
        """Look up precomputed LQR gain at time t via nearest-index interpolation."""
        idx = np.clip(np.searchsorted(t_ref, t) - 1, 0, len(t_ref) - 2)
        return gains_array[idx]

    x_ref_interp = interp1d(t_ref, x_ref, kind="linear", fill_value="extrapolate")

    def controller(t: float, x: np.ndarray) -> np.ndarray:
        """Apply time-varying TTCF control law u = -K(t)(x - x*(t))."""
        x_star = x_ref_interp(t)
        K = get_K(t)
        return -K @ (x - x_star)

    return controller


# ---------------------------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------------------------


def run_benchmark(
    controller: Callable[[float, np.ndarray], np.ndarray],
    x0_perturbed: np.ndarray,
    t_span: tuple[float, float],
    t_ref: np.ndarray,
    x_ref: np.ndarray,
    name: str,
    dt: float = 0.001,
    control_limits: tuple[float, float] = CONTROL_SATURATION_DEFAULT,
) -> BenchmarkResult:
    """Simulate closed-loop system and compute performance metrics.

    Args:
        controller: Callable ``(t, x) -> u`` returning control input.
        x0_perturbed: Perturbed initial state of shape ``(n,)``.
        t_span: Integration interval ``(t0, tf)``.
        t_ref: Reference time array of shape ``(T,)``.
        x_ref: Reference state trajectory of shape ``(n, T)``.
        name: Human-readable label for this run.
        dt: Maximum integration step size in seconds.
        control_limits: ``(lower, upper)`` saturation bounds applied to the
            control input at every time step.  Defaults to
            ``CONTROL_SATURATION_DEFAULT`` (``-50.0``, ``50.0``) N*m, which is
            appropriate for the built-in double-pendulum benchmark.  Override
            this for systems with different actuator constraints.
    """
    start = time.perf_counter()

    def closed_loop(t: float, x: np.ndarray) -> np.ndarray:
        """Closed-loop ODE: drift + controlled input with saturation."""
        u = controller(t, x)
        # Clip control to prevent divergence; bounds are system-specific
        u = np.clip(u, control_limits[0], control_limits[1])
        return double_pendulum_drift(t, x) + double_pendulum_B(x) @ u

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
) -> list[BenchmarkResult]:
    """Run full benchmark comparison: setpoint vs TTCF vs passive."""
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
        run_benchmark(sp_ctrl, x0_perturbed, t_span, t_ref, x_ref, "Setpoint LQR", dt=dt)
    )

    # 2. Trajectory Tracking Cost Functional
    logger.info("Running TTCF benchmark...")
    tt_ctrl = trajectory_tracking_lqr(t_ref, x_ref)
    results.append(
        run_benchmark(
            tt_ctrl, x0_perturbed, t_span, t_ref, x_ref, "Trajectory Tracking (TTCF)", dt=dt
        )
    )

    # 3. Passive (no control) — baseline
    logger.info("Running passive baseline...")

    def passive_ctrl(t: float, x: np.ndarray) -> np.ndarray:
        """Return zero torque (passive baseline, no active control)."""
        return np.zeros(2)

    results.append(
        run_benchmark(
            passive_ctrl, x0_perturbed, t_span, t_ref, x_ref, "Passive (no control)", dt=dt
        )
    )

    return results


def print_results(results: list[BenchmarkResult]) -> None:
    """Log formatted benchmark comparison table using the module logger."""
    logger.info("\n" + "=" * 70)
    logger.info(f"{'Controller':<30} {'Tracking Error':>15} {'Control Effort':>15}")
    logger.info("=" * 70)
    for r in results:
        logger.info(
            f"{r.name:<30} {r.tracking_error:>15.4f} {r.control_effort:>15.4f}"
            f"  ({r.runtime_sec:.2f}s)"
        )
    logger.info("=" * 70)

    if len(results) >= 2:
        sp = next(r for r in results if "Setpoint" in r.name)
        tt = next(r for r in results if "Trajectory" in r.name)
        improvement = (sp.tracking_error - tt.tracking_error) / sp.tracking_error * 100
        logger.info(f"\nTTCF tracking improvement over setpoint: {improvement:.1f}%")
        if improvement > 0:
            logger.info("Trajectory tracking cost functional outperforms setpoint control.")
        else:
            logger.info("Setpoint control outperforms TTCF in this scenario.")


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
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    results = run_comparison(
        perturbation_scale=args.perturbation,
        t_span=(0.0, args.horizon),
        seed=args.seed,
    )
    print_results(results)


if __name__ == "__main__":
    main()
