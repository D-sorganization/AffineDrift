"""Worked-example arithmetic for the Forward Dynamics Matching book (#5607)."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

type Vector = NDArray[np.float64]


@dataclass(frozen=True)
class ScalarGradientExample:
    """Scalar rollout loss and gradients from ch.10."""

    x2: float
    grad_a: float
    grad_b: float
    rollout_x2: float


@dataclass(frozen=True)
class SinCollocationSummary:
    """Trapezoidal collocation on dot{x} = sin(omega t) over one period."""

    omega: float
    times: Vector
    states: Vector
    exact_mid: float
    half_period_increments: tuple[float, float] | None = None


def scalar_gradient_example(
    a: float = 0.5,
    b: float = 0.4,
    x0: float = 1.0,
    u0: float = 1.0,
    u1: float = 1.0,
    y2: float = 2.0,
) -> ScalarGradientExample:
    """Reproduce the worked scalar gradient example in 10_gradients.qmd."""
    x1 = a * x0 + b * u0
    rollout_x2 = a * x1 + b * u1
    closed_form_x2 = a**2 + a * b + b
    grad_a = (closed_form_x2 - y2) * (2.0 * a + b)
    grad_b = (closed_form_x2 - y2) * (a + 1.0)
    return ScalarGradientExample(
        x2=closed_form_x2,
        grad_a=grad_a,
        grad_b=grad_b,
        rollout_x2=rollout_x2,
    )


def _sin_forcing(omega: float, times: Vector) -> Vector:
    """Return sin(omega t) at each collocation node time."""
    return np.sin(omega * times)


def _trapezoid_collocation_states(omega: float, times: Vector) -> Vector:
    """Collocated states with trapezoidal defects and x(0)=0."""
    if len(times) < 2:
        msg = "need at least two nodes"
        raise ValueError(msg)
    forcing = _sin_forcing(omega, times)
    states = np.zeros(len(times), dtype=float)
    for index in range(len(times) - 1):
        step = times[index + 1] - times[index]
        states[index + 1] = states[index] + 0.5 * step * (forcing[index] + forcing[index + 1])
    return states


def three_node_trapezoid_collocation(omega: float = 1.0) -> SinCollocationSummary:
    """Three-node layout at period endpoints and midpoint (07_collocation.qmd)."""
    period = 2.0 * math.pi / omega
    mid = period / 2.0
    times = np.array([0.0, mid, period], dtype=float)
    states = _trapezoid_collocation_states(omega, times)
    half = mid
    exact_first = (1.0 - math.cos(omega * half)) / omega
    exact_second = (1.0 - math.cos(omega * period)) / omega - exact_first
    return SinCollocationSummary(
        omega=omega,
        times=times,
        states=states,
        exact_mid=exact_first,
        half_period_increments=(exact_first, exact_second),
    )


def quarter_period_trapezoid_collocation(omega: float = 1.0) -> SinCollocationSummary:
    """Quarter-period nodes resolve part of the interior excursion."""
    period = 2.0 * math.pi / omega
    quarter = period / 4.0
    times = np.array([0.0, quarter, 2.0 * quarter, 3.0 * quarter, period], dtype=float)
    states = _trapezoid_collocation_states(omega, times)
    exact_mid = (1.0 - math.cos(omega * (period / 2.0))) / omega
    return SinCollocationSummary(
        omega=omega,
        times=times,
        states=states,
        exact_mid=exact_mid,
    )


def format_scalar_report(example: ScalarGradientExample) -> str:
    """Human-readable report for scripts and CI checks."""
    lines = [
        "Scalar gradient example (10_gradients.qmd)",
        f"  x2 = {example.x2:.4f} (rollout {example.rollout_x2:.4f})",
        f"  grad_a = {example.grad_a:.4f}",
        f"  grad_b = {example.grad_b:.4f}",
    ]
    return "\n".join(lines)


def format_sin_report(summary: SinCollocationSummary, title: str) -> str:
    """Human-readable sin(omega t) collocation report."""
    state_text = ", ".join(f"{value:.3f}" for value in summary.states)
    lines = [
        title,
        f"  omega = {summary.omega}",
        f"  colocated states = [{state_text}]",
        f"  exact midpoint state = {summary.exact_mid:.3f}",
    ]
    if summary.half_period_increments is not None:
        inc_a, inc_b = summary.half_period_increments
        lines.append(f"  exact half-period increments = +{inc_a:.3f}, {inc_b:+.3f}")
    return "\n".join(lines)
