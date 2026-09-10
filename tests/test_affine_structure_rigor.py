"""Independent mechanics and optimality controls for the affine chapter."""

from importlib import import_module
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad

from src.affine_control.rnea import PlanarChain, PlanarLink


@pytest.fixture
def model():
    return import_module("docs.development.technical-review.build_affine_structure_figures")


@pytest.mark.parametrize(
    "angles,rates", [([0, 0], [0, 0]), ([0.7, -0.5], [5, 0]), ([2.6, -1.2], [3, -7])]
)
def test_complete_dynamics_against_independent_newton_euler(model, angles, rates):
    q, velocity = np.array(angles), np.array(rates)
    chain = PlanarChain((PlanarLink(2.5, 0.35, 0.175, 0.025), PlanarLink(0.4, 1.0, 0.5, 0.03)))
    horizontal = q - np.array([np.pi / 2, 0])
    mass, bias, gravity = model.operators(q, velocity)
    np.testing.assert_allclose(mass, chain.mass_matrix(horizontal), atol=1e-13)
    np.testing.assert_allclose(
        bias + gravity, chain.inverse_dynamics(horizontal, velocity, np.zeros(2)), atol=1e-12
    )
    assert np.linalg.eigvalsh(mass).min() > 0


def test_bias_power_is_kinetic_metric_derivative(model):
    q, velocity = np.array([0.8, -0.6]), np.array([3.0, -5.0])
    mass, bias, _ = model.operators(q, velocity)
    step = 1e-6
    derivative = (
        model.operators(q + step * velocity, velocity)[0]
        - model.operators(q - step * velocity, velocity)[0]
    ) / (2 * step)
    assert velocity @ bias == pytest.approx(0.5 * velocity @ derivative @ velocity, abs=1e-9)
    assert mass.shape == (2, 2)


def test_free_and_locked_response_are_distinct(model):
    mass = model.operators(np.array([0.0, 0.0]), np.zeros(2))[0]
    free = np.linalg.solve(mass, [1.0, 0.0])[0]
    schur = mass[0, 0] - mass[0, 1] ** 2 / mass[1, 1]
    assert free == pytest.approx(1 / schur)
    assert free > 3 / mass[0, 0]
    folded = model.operators(np.array([0.0, np.pi / 2]), np.zeros(2))[0]
    assert np.linalg.solve(folded, [1.0, 0.0])[0] < free


def test_locked_drift_trajectory_converges_and_conserves_energy(model):
    coarse, fine = model.locked_trajectory(False), model.locked_trajectory(True)
    assert coarse.success and fine.success
    np.testing.assert_allclose(coarse.y, fine.y, atol=1e-8)
    energies = model.locked_energy(fine.y)
    assert np.ptp(energies) < 1e-9


@pytest.mark.parametrize("rate", [-2.0, 0.0, 2.0])
def test_minimum_energy_control_obeys_endpoint_and_energy_bound(model, rate):
    def control(t):
        return model.minimum_energy_input(t, rate)

    endpoint = quad(lambda t: np.exp(rate * (1 - t)) * control(t), 0, 1)[0]
    energy = quad(lambda t: control(t) ** 2, 0, 1)[0]
    gramian = quad(lambda t: np.exp(2 * rate * (1 - t)), 0, 1)[0]
    assert endpoint == pytest.approx(1, abs=1e-12)
    assert energy == pytest.approx(1 / gramian, abs=1e-12)
    if rate < 0:
        assert control(1) > control(0)
    if rate > 0:
        assert control(1) < control(0)


@pytest.mark.parametrize(
    "edition", ["chapters/ch05_affine_structure.tex", "quarto/ch05_affine_structure.qmd"]
)
def test_paired_affine_chapter_has_energy_capacity_and_optimality_boundaries(edition):
    text = (Path(__file__).parents[1] / "articles/The_Physics_of_Golf" / edition).read_text(
        encoding="utf-8"
    )
    for phrase in (
        "Schur",
        "input origin",
        "capacity",
        "necessary conditions",
        "Hamilton",
        "7. Compare Golf With Throwing",
        "not a work fraction",
    ):
        assert phrase in text
    for phrase in (
        "180 $g$",
        "maximizes DCR while maintaining control",
        "No more muscular effort needed",
        "technique matters more than strength",
    ):
        assert phrase not in text
