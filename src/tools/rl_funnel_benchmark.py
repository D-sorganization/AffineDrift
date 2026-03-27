"""Benchmark classical setpoint control against trajectory-tracking control."""

from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, cast

import numpy as np
import numpy.typing as npt
from scipy.integrate import solve_ivp
from scipy.linalg import solve_continuous_are

from src.core.constants import GRAVITY_M_S2
from src.core.contracts.definitions import require
from src.core.contracts.validators import check_finite_array, check_positive


def validate_state_vector(x: npt.NDArray[Any], name: str) -> None:
    check_finite_array(x, name)


def validate_weight_matrix(Q: npt.NDArray[Any], shape: tuple[int, int], name: str) -> None:
    check_finite_array(Q, name)


def format_results(results: list["BenchmarkResult"]) -> str:
    return "\n".join([f"{r.name}: error={r.tracking_error:.4f}" for r in results])


def double_pendulum_mass_matrix(th1: float, th2: float) -> npt.NDArray[Any]:
    return np.eye(2)
# Default control saturation limits for the double-pendulum benchmark (N*m).
# The value 50 N*m is appropriate for a 1 kg, 0.5 m double pendulum; adjust
# for different systems by passing `control_limits` to run_benchmark().
DEFAULT_CONTROL_SATURATION = 50.0
CONTROL_SATURATION_DEFAULT: tuple[float, float] = (-50.0, 50.0)

# Double pendulum physical parameters (2-DoF golf swing proxy)
PENDULUM_M1 = 1.0  # kg, mass of upper link
PENDULUM_M2 = 1.0  # kg, mass of lower link
PENDULUM_L1 = 0.5  # m, length of upper link
PENDULUM_L2 = 0.5  # m, length of lower link

logger = logging.getLogger(__name__)


def double_pendulum_drift(
    t: float, x: npt.NDArray[Any], g: float = GRAVITY_M_S2
) -> npt.NDArray[Any]:
    """Passive dynamics of a double pendulum (drift term f(x,0)).

    State: x = [theta1, theta2, dtheta1, dtheta2]
    Parameters: m1=m2=1kg, L1=L2=0.5m
    """
    require(
        isinstance(x, np.ndarray) and x.shape == (4,),
        "x must be a numpy array of shape (4,)",
        x,
    )
    check_finite_array(x, "x")
    check_positive(g, "g")

    # m1, m2, L1, L2 unused
    th1, th2, dth1, dth2 = x
    s12 = np.sin(th1 - th2)
    M = double_pendulum_mass_matrix(th1, th2)
    rhs = np.array(
        [
            -PENDULUM_M2 * PENDULUM_L1 * PENDULUM_L2 * dth2**2 * s12
            - (PENDULUM_M1 + PENDULUM_M2) * g * PENDULUM_L1 * np.sin(th1),
            PENDULUM_M2 * PENDULUM_L1 * PENDULUM_L2 * dth1**2 * s12
            - PENDULUM_M2 * g * PENDULUM_L2 * np.sin(th2),
        ]
    )
    ddth = np.linalg.solve(M, rhs)
    return np.array([dth1, dth2, ddth[0], ddth[1]])


def double_pendulum_B(x: npt.NDArray[Any]) -> npt.NDArray[Any]:
    """Control input matrix g(x): torques applied at both joints."""
    require(
        isinstance(x, np.ndarray) and x.shape == (4,),
        "x must be a numpy array of shape (4,)",
        x,
    )
    check_finite_array(x, "x")

    # m1, m2, L1, L2 unused
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
    require(
        len(t_span) == 2 and t_span[1] > t_span[0],
        "t_span must be (t0, tf) with tf > t0",
        t_span,
    )
    check_positive(dt, "dt")
    if x0 is not None:
        require(
            isinstance(x0, np.ndarray) and x0.shape == (4,),
            "x0 must be a numpy array of shape (4,)",
            x0,
        )
        check_finite_array(x0, "x0")

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
    x_target: npt.NDArray[Any],
    Q_sp: npt.NDArray[Any] | None = None,
    R_sp: npt.NDArray[Any] | None = None,
) -> Callable[[float, npt.NDArray[Any]], npt.NDArray[Any]]:
    """Classical setpoint LQR controller.

    Minimizes integral (x - x_target)' Q (x - x_target) + u' R u.
    Linearizes around x_target.
    """
    require(
        isinstance(x_target, np.ndarray) and x_target.shape == (4,),
        "x_target must be a numpy array of shape (4,)",
        x_target,
    )
    check_finite_array(x_target, "x_target")

    n = 4
    m = 2
    validate_state_vector(x_target, "x_target")
    if Q_sp is None:
        Q_sp = np.diag([10.0, 10.0, 1.0, 1.0])
    if R_sp is None:
        R_sp = 0.1 * np.eye(m)
    validate_weight_matrix(Q_sp, (n, n), "Q_sp")
    validate_weight_matrix(R_sp, (m, m), "R_sp")

    # Linearize at target using central differences
    eps = 1e-6
    A = np.zeros((n, n))
    for j in range(n):
        ej = np.zeros(n)
        ej[j] = eps
        A[:, j] = (
            double_pendulum_drift(0.0, x_target + ej) - double_pendulum_drift(0.0, x_target - ej)
        ) / (2 * eps)

    B0 = double_pendulum_B(x_target)

    P = solve_continuous_are(A, B0, Q_sp, R_sp)
    K = np.linalg.solve(R_sp, B0.T @ P)

    def controller(t: float, x: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """Apply setpoint LQR control law u = -K(x - x_target)."""
        return cast(npt.NDArray[Any], -K @ (x - x_target))

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


def _validate_ttcf_inputs(t_ref: np.ndarray, x_ref: np.ndarray) -> None:
    """Validate reference trajectory inputs for the TTCF controller."""
    require(
        isinstance(t_ref, np.ndarray) and t_ref.ndim == 1 and len(t_ref) >= 2,
        "t_ref must be a 1D numpy array with at least 2 elements",
        t_ref,
    )
    require(
        isinstance(x_ref, np.ndarray)
        and x_ref.ndim == 2
        and x_ref.shape[0] == 4
        and x_ref.shape[1] == len(t_ref),
        "x_ref must be a numpy array of shape (4, len(t_ref))",
        x_ref,
    )
    check_finite_array(t_ref, "t_ref")
    check_finite_array(x_ref, "x_ref")


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
    Validation is delegated to ``_validate_ttcf_inputs``.
    """
    from scipy.interpolate import interp1d

    _validate_ttcf_inputs(t_ref, x_ref)

    n, m = 4, 2
    Q_tt = Q_tt if Q_tt is not None else np.diag([10.0, 10.0, 1.0, 1.0])
    R_tt = R_tt if R_tt is not None else 0.1 * np.eye(m)
    gains_array = _precompute_lqr_gains(t_ref, x_ref, n, m, Q_tt, R_tt)
    x_ref_interp = interp1d(t_ref, x_ref, kind="linear", fill_value="extrapolate")
    def get_K(t: float) -> np.ndarray:
        """Look up precomputed LQR gain at time t via nearest-index interpolation."""
        idx = np.clip(np.searchsorted(t_ref, t) - 1, 0, len(t_ref) - 2)
        return cast(npt.NDArray[Any], gains_array[idx])

    def controller(t: float, x: np.ndarray) -> np.ndarray:
        """Apply time-varying TTCF control law u = -K(t)(x - x*(t))."""
        return cast(npt.NDArray[Any], -get_K(t) @ (x - x_ref_interp(t)))

    return controller


# ---------------------------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------------------------


def _compute_tracking_metrics(
    controller: Callable[[float, np.ndarray], np.ndarray],
    x_sim: np.ndarray,
    t_eval: np.ndarray,
    t_ref: np.ndarray,
    x_ref: np.ndarray,
) -> tuple[float, float]:
    """Compute mean tracking error and control effort from a simulated trajectory.

    Args:
        controller: Callable ``(t, x) -> u`` for control effort computation.
        x_sim: Simulated state trajectory of shape ``(n, T)``.
        t_eval: Time grid of shape ``(T,)``.
        t_ref: Reference time array of shape ``(T_ref,)``.
        x_ref: Reference trajectory of shape ``(n, T_ref)``.

    Returns:
        ``(tracking_error, control_effort)`` as scalar floats.
    """
    from scipy.interpolate import interp1d

    x_ref_interp = interp1d(t_ref, x_ref, kind="linear", fill_value="extrapolate")
    x_star = x_ref_interp(t_eval)
    tracking_error = float(np.mean(np.linalg.norm(x_sim - x_star, axis=0) ** 2))
    u_all = np.array([controller(t, x_sim[:, i]) for i, t in enumerate(t_eval)])
    control_effort = float(np.mean(np.sum(u_all**2, axis=1)))
    return tracking_error, control_effort


def _validate_benchmark_inputs(
    controller: object,
    x0_perturbed: np.ndarray,
    t_span: tuple[float, float],
    dt: float,
) -> None:
    """Validate inputs for run_benchmark."""
    require(callable(controller), "controller must be callable", type(controller))
    require(
        isinstance(x0_perturbed, np.ndarray) and x0_perturbed.shape == (4,),
        "x0_perturbed must be a numpy array of shape (4,)",
        x0_perturbed,
    )
    check_finite_array(x0_perturbed, "x0_perturbed")
    require(
        len(t_span) == 2 and t_span[1] > t_span[0],
        "t_span must be (t0, tf) with tf > t0",
        t_span,
    )
    check_positive(dt, "dt")


def run_benchmark(
    controller: Callable[[float, npt.NDArray[Any]], npt.NDArray[Any]],
    x0_perturbed: npt.NDArray[Any],
    t_span: tuple[float, float],
    t_ref: npt.NDArray[Any],
    x_ref: npt.NDArray[Any],
    name: str,
    dt: float = 0.001,
    control_limits: tuple[float, float] = CONTROL_SATURATION_DEFAULT,
) -> BenchmarkResult:
    """Simulate closed-loop system and compute performance metrics.

    Validation delegated to ``_validate_benchmark_inputs``.
    Metrics delegated to ``_compute_tracking_metrics``.
    ``control_limits``: ``(lower, upper)`` saturation bounds; defaults to
    ``CONTROL_SATURATION_DEFAULT`` (``-50.0``, ``50.0``) N*m.
    """
    _validate_benchmark_inputs(controller, x0_perturbed, t_span, dt)

    start = time.perf_counter()

    def closed_loop(t: float, x: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """Closed-loop ODE: drift + controlled input with saturation."""
        u = controller(t, x)
        # Clip control to prevent divergence; bounds are system-specific
        u = np.clip(u, control_limits[0], control_limits[1])
        return cast(npt.NDArray[Any], double_pendulum_drift(t, x) + double_pendulum_B(x) @ u)

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
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Validate inputs and build reference trajectory + perturbed initial condition.

    Returns:
        ``(x0_perturbed, t_ref, x_ref, x_target)``
    """
    check_positive(perturbation_scale, "perturbation_scale")
    require(
        len(t_span) == 2 and t_span[1] > t_span[0],
        "t_span must be (t0, tf) with tf > t0",
        t_span,
    )
    check_positive(dt, "dt")
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
    x0_perturbed, t_ref, x_ref, x_target = _setup_comparison(perturbation_scale, t_span, dt, seed)

    def passive_ctrl(t: float, x: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """Return zero torque (passive baseline, no active control)."""
        return np.zeros(2)

    def _rb(ctrl: Callable[[float, np.ndarray], np.ndarray], label: str) -> BenchmarkResult:
        """Run a single named benchmark and return its result."""
        logger.info("Running %s benchmark...", label)
        return run_benchmark(ctrl, x0_perturbed, t_span, t_ref, x_ref, label, dt=dt)

    return [
        _rb(setpoint_lqr_controller(x_target), "Setpoint LQR"),
        _rb(trajectory_tracking_lqr(t_ref, x_ref), "Trajectory Tracking (TTCF)"),
        _rb(passive_ctrl, "Passive (no control)"),
    ]


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
