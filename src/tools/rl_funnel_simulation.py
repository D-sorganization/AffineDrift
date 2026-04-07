"""Simulation logic for RL funnel benchmarking."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, cast

import numpy as np
import numpy.typing as npt
from scipy.integrate import solve_ivp

from src.core.contracts.definitions import require
from src.core.contracts.validators import check_finite_array, check_positive
from src.tools.rl_funnel_dynamics import (
    CONTROL_SATURATION_DEFAULT,
    double_pendulum_B,
    double_pendulum_drift,
)


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
    # Vectorized tracking error: mean of squared norms along time axis
    state_errors = x_sim - x_star
    tracking_error = float(np.mean(np.sum(state_errors**2, axis=0)))
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
