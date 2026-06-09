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

from src.core.contracts.definitions import require
from src.core.contracts.validators import check_finite_array, check_positive
from src.tools.rl_funnel_controllers import setpoint_lqr_controller, trajectory_tracking_lqr
from src.tools.rl_funnel_dynamics import (
    double_pendulum_B,
    double_pendulum_drift,
    generate_reference_trajectory,
)
from src.tools.rl_funnel_support import (
    CONTROL_SATURATION_DEFAULT,
    DEFAULT_CONTROL_SATURATION,
    GRAVITY_M_S2,
    PENDULUM_L1,
    PENDULUM_L2,
    PENDULUM_M1,
    PENDULUM_M2,
    BenchmarkResult,
    format_results,
)

logger = logging.getLogger(__name__)

__all__ = [
    "CONTROL_SATURATION_DEFAULT",
    "DEFAULT_CONTROL_SATURATION",
    "GRAVITY_M_S2",
    "PENDULUM_L1",
    "PENDULUM_L2",
    "PENDULUM_M1",
    "PENDULUM_M2",
    "BenchmarkResult",
    "double_pendulum_B",
    "double_pendulum_drift",
    "format_results",
    "generate_reference_trajectory",
    "main",
    "print_results",
    "run_benchmark",
    "run_comparison",
    "setpoint_lqr_controller",
    "trajectory_tracking_lqr",
]


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
    control_limits: tuple[float, float],
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
    require(
        len(control_limits) == 2 and control_limits[0] < control_limits[1],
        "control_limits must be (lower, upper) with lower < upper",
        control_limits,
    )


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
    _validate_benchmark_inputs(controller, x0_perturbed, t_span, dt, control_limits)

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
    check_positive(control_limit, "control_limit")
    x0_perturbed, t_ref, x_ref, x_target = _setup_comparison(perturbation_scale, t_span, dt, seed)
    control_limits = (-control_limit, control_limit)

    def passive_ctrl(t: float, x: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """Return zero torque (passive baseline, no active control)."""
        return np.zeros(2)

    def _rb(ctrl: Callable[[float, np.ndarray], np.ndarray], label: str) -> BenchmarkResult:
        """Run a single named benchmark and return its result."""
        logger.info("Running %s benchmark...", label)
        return run_benchmark(
            ctrl,
            x0_perturbed,
            t_span,
            t_ref,
            x_ref,
            label,
            dt=dt,
            control_limits=control_limits,
        )

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
