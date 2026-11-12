"""Tests for FDM worked-example reproduction (issue #5607)."""

from __future__ import annotations

import math

import pytest

from src.tools.fdm_worked_examples import (
    quarter_period_trapezoid_collocation,
    scalar_gradient_example,
    three_node_trapezoid_collocation,
)


def test_scalar_example_matches_gradients_chapter() -> None:
    result = scalar_gradient_example()
    assert result.x2 == pytest.approx(0.85)
    assert result.grad_a == pytest.approx(-1.61)
    assert result.grad_b == pytest.approx(-1.725)


def test_scalar_example_rollout_matches_closed_form() -> None:
    result = scalar_gradient_example()
    assert result.x2 == pytest.approx(result.rollout_x2)


def test_sin_three_node_trapezoid_misses_excursion() -> None:
    omega = 1.0
    summary = three_node_trapezoid_collocation(omega)
    assert summary.states[0] == pytest.approx(0.0)
    assert summary.states[-1] == pytest.approx(0.0)
    assert all(x == pytest.approx(0.0) for x in summary.states)
    assert summary.exact_mid == pytest.approx(2.0 / omega)
    assert summary.half_period_increments == (
        pytest.approx(2.0 / omega),
        pytest.approx(-2.0 / omega),
    )


def test_sin_quarter_period_trapezoid_partial_resolution() -> None:
    omega = 1.0
    summary = quarter_period_trapezoid_collocation(omega)
    mid = summary.states[2]
    assert mid == pytest.approx(math.pi / 2.0, rel=1e-12)
    assert summary.exact_mid == pytest.approx(2.0)
    relative_error = abs(mid - summary.exact_mid) / summary.exact_mid
    assert relative_error == pytest.approx(0.2146, rel=0.01)
