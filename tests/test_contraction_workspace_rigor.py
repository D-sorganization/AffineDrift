"""Manufactured checks for the contraction development manuscript (#4465)."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "articles/tangent-hyperplane-contraction"


def test_finite_horizon_value_drop_does_not_imply_state_contraction() -> None:
    """An unpenalized terminal state grows despite a falling optimal value."""
    state_gain, input_gain, state_cost, input_cost, terminal = 2.0, 1.0, 1.0, 1.0, 0.0
    gain = input_gain * terminal * state_gain / (input_cost + input_gain**2 * terminal)
    riccati = (
        state_cost + state_gain**2 * terminal - gain**2 * (input_cost + input_gain**2 * terminal)
    )
    next_state = state_gain - input_gain * gain
    assert gain == 0.0
    assert riccati == 1.0
    assert next_state == 2.0
    assert terminal * next_state**2 - riccati == -state_cost


def test_two_stage_riccati_identity_and_metric_decay() -> None:
    """Check the backward solve against the Bellman minimum and forward energy."""
    riccati = np.zeros(3)
    gains = np.zeros(2)
    riccati[-1] = 1.0
    for stage in (1, 0):
        next_value = riccati[stage + 1]
        gains[stage] = next_value / (1.0 + next_value)
        riccati[stage] = 1.0 + next_value / (1.0 + next_value)
    states = np.concatenate(([1.0], np.cumprod(1.0 - gains)))
    energies = riccati * states**2
    stage_loss = 1.0 + gains**2
    np.testing.assert_allclose(riccati, [1.6, 1.5, 1.0])
    np.testing.assert_allclose(gains, [0.6, 0.5])
    np.testing.assert_allclose(states, [1.0, 0.4, 0.2])
    np.testing.assert_allclose(energies, [1.6, 0.24, 0.04])
    np.testing.assert_allclose(np.diff(energies), -stage_loss * states[:-1] ** 2)
    actual_cost = np.sum(states[:-1] ** 2 + (gains * states[:-1]) ** 2) + states[-1] ** 2
    assert actual_cost == pytest.approx(riccati[0])
    contraction_factor = 1.0 - np.min(stage_loss) / np.max(riccati)
    assert contraction_factor == pytest.approx(0.21875)
    assert np.all(energies[1:] <= contraction_factor * energies[:-1])


def test_coordinate_hessian_is_not_a_metric_pullback() -> None:
    """A nonlinear chart can make a positive scalar Hessian negative."""
    coordinate = np.exp(2.0)
    pulled_metric = 1.0 / coordinate**2
    coordinate_hessian = (1.0 - np.log(coordinate)) / coordinate**2
    step = 1e-3
    finite_difference = (
        0.5 * np.log(coordinate + step) ** 2
        - np.log(coordinate) ** 2
        + 0.5 * np.log(coordinate - step) ** 2
    ) / step**2
    assert pulled_metric > 0
    assert coordinate_hessian == pytest.approx(-pulled_metric)
    assert finite_difference == pytest.approx(coordinate_hessian, abs=1e-8)


def test_background_metric_must_transform_with_task_penalty() -> None:
    """Reusing identity in a rescaled chart silently changes the objective."""
    task_jacobian = np.array([[1.0, 0.0]])
    chart_jacobian = np.diag([2.0, 3.0])
    regularization = 0.1
    metric = task_jacobian.T @ task_jacobian + regularization * np.eye(2)
    transformed = chart_jacobian.T @ metric @ chart_jacobian
    task_in_new_chart = task_jacobian @ chart_jacobian
    naive = task_in_new_chart.T @ task_in_new_chart + regularization * np.eye(2)
    np.testing.assert_allclose(transformed, np.diag([4.4, 0.9]))
    np.testing.assert_allclose(naive, np.diag([4.1, 0.1]))
    direction = np.array([0.2, -0.4])
    old_direction = chart_jacobian @ direction
    assert direction @ transformed @ direction == pytest.approx(
        old_direction @ metric @ old_direction
    )


def test_sampled_contraction_can_miss_an_expanding_interior() -> None:
    """The polynomial derivative is negative at endpoints but positive inside."""
    endpoints = np.array([-1.0, 1.0])
    endpoint_jacobians = 1.0 - 4.0 * endpoints**2
    np.testing.assert_allclose(endpoint_jacobians, [-3.0, -3.0])
    assert 1.0 - 4.0 * 0.0**2 > 0.0


def test_state_dependent_input_field_contributes_to_jacobian() -> None:
    """The first variation differentiates the entire nominal vector field."""
    state, command, step = 2.0, 3.0, 1e-5
    upper = (state + step) ** 2 + (state + step) * command
    lower = (state - step) ** 2 + (state - step) * command
    assert (upper - lower) / (2.0 * step) == pytest.approx(7.0)
    assert 2.0 * state + command == 7.0


def test_nonautonomous_sampled_map_depends_on_start_time() -> None:
    """Integrating xdot=t*u under held input retains absolute start time."""
    duration, command = 0.2, 3.0
    start_times = np.array([0.0, 1.0])
    increments = command * (start_times * duration + duration**2 / 2.0)
    np.testing.assert_allclose(increments, [0.06, 0.66])


def test_lti_congruence_preserves_contraction_residual() -> None:
    """The dual LMI follows by congruence, with the negative-feedback sign."""
    dynamics = np.array([[0.0, 1.0], [-2.0, -0.5]])
    inputs = np.array([[0.0], [1.0]])
    gain = np.array([[1.0, 1.0]])
    metric = np.array([[2.0, 0.3], [0.3, 1.0]])
    rate = 0.1
    dual = np.linalg.inv(metric)
    transformed_gain = gain @ dual
    closed_loop = dynamics - inputs @ gain
    primal = closed_loop.T @ metric + metric @ closed_loop + 2.0 * rate * metric
    dual_residual = (
        dynamics @ dual
        + dual @ dynamics.T
        - inputs @ transformed_gain
        - transformed_gain.T @ inputs.T
        + 2.0 * rate * dual
    )
    np.testing.assert_allclose(dual_residual, dual @ primal @ dual)


@pytest.mark.parametrize(
    ("relative_path", "removed_claim"),
    [
        ("chapters/04-stability-optimality-duality.qmd", "contraction is guaranteed locally"),
        ("chapters/07-high-dimensional-applications.qmd", "infeasible beyond"),
        ("chapters/07-high-dimensional-applications.qmd", "one during flight"),
        ("chapters/01-foundations.qmd", "even 5%"),
        (
            "manuscript/tangent-hyperplane-contraction.tex",
            "local stabilizing core remains the same",
        ),
        (
            "manuscript/tangent-hyperplane-contraction.tex",
            "These constructions preserve the same physical interpretation",
        ),
    ],
)
def test_removed_overclaims(relative_path: str, removed_claim: str) -> None:
    """Prevent the specific unsupported theorem and physiological assertions."""
    assert removed_claim not in (WORKSPACE / relative_path).read_text(encoding="utf-8")
