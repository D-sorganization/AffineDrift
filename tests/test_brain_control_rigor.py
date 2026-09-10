"""Independent numerical controls for the motor-control brain chapter."""

from importlib import import_module
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp
from scipy.linalg import expm

MODULE = "docs.development.technical-review.build_brain_control_figures"


@pytest.fixture
def model():
    return import_module(MODULE)


def test_forward_step_has_state_and_time_and_first_order_convergence(model):
    matrix = np.array([[0.0, 1.0], [-2.0, -0.3]])
    state = np.array([0.4, -0.2])
    errors = []
    for step in (0.02, 0.01):
        actual = model.euler_prediction(state, matrix @ state, step)
        errors.append(np.linalg.norm(actual - expm(matrix * step) @ state))
    assert 3.9 < errors[0] / errors[1] < 4.1
    np.testing.assert_array_equal(model.euler_prediction(state, matrix @ state, 0), state)


def test_rectangular_inverse_preserves_feasibility_residual(model):
    control, residual = model.bounded_inverse_example()
    np.testing.assert_allclose(control, [1.0], atol=1e-9)
    np.testing.assert_allclose(residual, [0.0, 1.0, 2.0, -1.0], atol=1e-9)
    matrix = np.array([[0.0], [0.0], [1.0], [1.0]])
    unconstrained = np.linalg.lstsq(matrix, [0, 1, 3, 0], rcond=None)[0]
    np.testing.assert_allclose(unconstrained, [1.5])
    assert np.linalg.norm(matrix @ unconstrained - [0, 1, 3, 0]) > 0


@pytest.mark.parametrize("remaining", [0.0, 0.01, 0.04, 0.1])
def test_activation_impulse_matches_integrated_response(model, remaining):
    tau = 0.05
    expected = quad(lambda t: 1 - np.exp(-t / tau), 0, remaining)[0]
    assert model.activation_impulse(remaining, tau) == pytest.approx(expected, abs=1e-13)
    if remaining:
        solution = solve_ivp(
            lambda t, x: [(1 - x[0]) / tau, x[0]],
            [0, remaining],
            [0, 0],
            rtol=1e-11,
            atol=1e-13,
        )
        assert solution.y[1, -1] == pytest.approx(expected, abs=1e-11)


def test_noise_projection_depends_on_correlation(model):
    values = model.projected_variances()
    np.testing.assert_allclose(values, [4e-4, 1e-4, 7.6e-4], atol=1e-14)
    # Equal marginal variability gives different task variability through covariance.
    assert values[1] < values[0] < values[2]


def test_delay_phase_is_not_a_sampling_rate(model):
    assert model.delay_phase_degrees(5.0, 0.05) == pytest.approx(-90)
    assert model.delay_phase_degrees(10.0, 0.05) == pytest.approx(-180)
    assert abs(np.exp(-1j * 2 * np.pi * 5 * 0.05)) == pytest.approx(1)


def test_free_energy_identity_and_wrong_belief_penalty(model):
    likelihood_joint = np.array([0.12, 0.18])
    posterior = likelihood_joint / likelihood_joint.sum()
    assert model.variational_free_energy(posterior, likelihood_joint) == pytest.approx(-np.log(0.3))
    belief = np.array([0.8, 0.2])
    kl = np.sum(belief * np.log(belief / posterior))
    assert model.variational_free_energy(belief, likelihood_joint) == pytest.approx(
        kl - np.log(0.3)
    )


@pytest.mark.parametrize(
    "edition", ["chapters/ch24_motor_control_brain.tex", "quarto/ch24_motor_control_brain.qmd"]
)
def test_paired_brain_chapter_has_correct_model_and_evidence_boundaries(edition):
    source = (Path(__file__).parents[1] / "articles/The_Physics_of_Golf" / edition).read_text(
        encoding="utf-8"
    )
    for term in (
        "feasibility residual",
        "sensory prediction error",
        "reward prediction error",
        "covariance",
        "event time",
        "not a neural clock",
        "Schur",
        "10. What Would Establish",
    ):
        assert term in source
    for term in (
        r"\hat{G}(\bm{x}(t))^{-1}",
        "Patients with cerebellar ataxia cannot",
        "This takes time---typically 100--500",
        "the brain performs roughly",
    ):
        assert term not in source
