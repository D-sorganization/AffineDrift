"""Counterexamples for residual baselines and second-variation transport."""

from math import exp, expm1
from pathlib import Path

import pytest


def test_evolving_free_motion_is_required_even_for_linear_systems() -> None:
    initial, growth, duration = 2.0, 0.5, 1.3

    def terminal(force: float) -> float:
        return initial * exp(growth * duration) + force * expm1(growth * duration) / growth

    corrected = terminal(3.0) - terminal(1.0) - terminal(2.0) + terminal(0.0)
    incorrect = terminal(3.0) - terminal(1.0) - terminal(2.0) + initial
    assert corrected == pytest.approx(0.0, abs=1e-12)
    assert incorrect == pytest.approx(initial * (1 - exp(growth * duration)))
    assert abs(incorrect) > 1.0


def test_flat_state_space_has_nonlinear_input_interactions() -> None:
    # x_dot = u^2 on the Euclidean line, from x(0) = 0.
    first, second, duration = 1.0, 2.0, 3.0
    residual = ((first + second) ** 2 - first**2 - second**2) * duration
    assert residual == pytest.approx(2 * first * second * duration)


def test_jacobian_transport_can_amplify_a_constant_hessian_source() -> None:
    # x_dot = a*x + u^2. The interaction includes exp(a*(T-t)).
    growth, duration = 2.0, 1.0
    exact_mixed_response = 2 * expm1(growth * duration) / growth
    untransported_source = 2 * duration
    assert exact_mixed_response > 3 * untransported_source


def test_thesis_uses_the_evolved_baseline_and_mixed_variation() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "articles/tangent-hyperplane-articles/Tangent_Hyperplanes_Unified_Thesis.qmd"
    ).read_text(encoding="utf-8")
    assert "x_{12}(t_1) - x_1(t_1) - x_2(t_1) + x(t_0)" not in source
    assert "any smooth cost function is quadratic to leading order" not in source
    assert "They accumulate **linearly** in time" not in source
    assert "mixed second variation" in source
