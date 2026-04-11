"""Benchmark classical setpoint control against trajectory-tracking control."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from typing import Any

import numpy as np
import numpy.typing as npt

from src.core.constants import GRAVITY_M_S2
from src.core.contracts.definitions import require
from src.core.contracts.validators import check_positive
from src.tools.rl_funnel_controllers import (
    _precompute_lqr_gains,
    _validate_ttcf_inputs,
    setpoint_lqr_controller,
    trajectory_tracking_lqr,
)
from src.tools.rl_funnel_dynamics import (
    CONTROL_SATURATION_DEFAULT,
    DEFAULT_CONTROL_SATURATION,
    PENDULUM_L1,
    PENDULUM_L2,
    PENDULUM_M1,
    PENDULUM_M2,
    double_pendulum_B,
    double_pendulum_drift,
    double_pendulum_mass_matrix,
    generate_reference_trajectory,
    validate_state_vector,
)
from src.tools.rl_funnel_simulation import (
    BenchmarkResult,
    _compute_tracking_metrics,
    _validate_benchmark_inputs,
    run_benchmark,
)

__all__ = [
    "BenchmarkResult",
    "CONTROL_SATURATION_DEFAULT",
    "DEFAULT_CONTROL_SATURATION",
    "GRAVITY_M_S2",
    "PENDULUM_L1",
    "PENDULUM_L2",
    "PENDULUM_M1",
    "PENDULUM_M2",
    "_compute_tracking_metrics",
    "_precompute_lqr_gains",
    "double_pendulum_B",
    "double_pendulum_drift",
    "double_pendulum_mass_matrix",
    "format_results",
    "generate_reference_trajectory",
    "main",
    "print_results",
    "run_benchmark",
    "run_comparison",
    "setpoint_lqr_controller",
    "trajectory_tracking_lqr",
    "_validate_benchmark_inputs",
    "_validate_ttcf_inputs",
    "validate_state_vector",
]

logger = logging.getLogger(__name__)


def format_results(results: list[BenchmarkResult]) -> str:
    """Format benchmark results as a newline-separated string."""
    return "\n".join([f"{r.name}: error={r.tracking_error:.4f}" for r in results])


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
    t_ref, x_ref = generate_reference_trajectory(t_span, dt=dt, x0=x0_nominal)
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
        return run_benchmark(
            ctrl,
            x0_perturbed,
            t_span,
            t_ref,
            x_ref,
            label,
            dt=dt,
            control_limits=(-control_limit, control_limit),
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
