"""Independent geometry, energy and input checks for the complete Chapter 3 review."""

import importlib
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def model():
    return importlib.import_module(
        "docs.development.technical-review.build_double_pendulum_figures"
    )


@pytest.mark.parametrize("q", [[0.0, 0.0], [0.6, -0.8], [2.4, 1.3]])
def test_mass_matches_independent_com_velocity_energy(model, q):
    q = np.asarray(q)
    v = np.array([1.7, -2.3])
    tangent1 = np.array([np.cos(q[0]), np.sin(q[0])])
    tangent2 = np.array([np.cos(q.sum()), np.sin(q.sum())])
    speed1 = 0.175 * v[0] * tangent1
    speed2 = 0.35 * v[0] * tangent1 + 0.5 * v.sum() * tangent2
    energy = 0.5 * (2.5 * speed1 @ speed1 + 0.025 * v[0] ** 2)
    energy += 0.5 * (0.4 * speed2 @ speed2 + 0.03 * v.sum() ** 2)
    mass, _, _ = model.AFFINE.operators(q, v)
    assert 0.5 * v @ mass @ v == pytest.approx(energy, abs=1e-13)
    assert np.linalg.eigvalsh(mass).min() > 0


@pytest.mark.parametrize("q", [[0.0, 0.0], [0.6, -0.8], [2.4, 1.3]])
def test_coriolis_factor_and_skew_identity(model, q):
    q, v = np.asarray(q), np.array([1.7, -2.3])
    _, bias, _ = model.AFFINE.operators(q, v)
    coriolis = model.coriolis_matrix(q, v)
    np.testing.assert_allclose(coriolis @ v, bias, atol=1e-13)
    step = 1e-6
    mass_dot = (
        model.AFFINE.operators(q + step * v, v)[0] - model.AFFINE.operators(q - step * v, v)[0]
    ) / (2 * step)
    residual = mass_dot - 2 * coriolis
    np.testing.assert_allclose(residual + residual.T, 0, atol=1e-10)


def test_gravity_and_generalized_power_from_energy(model):
    q, v, torque = np.array([0.8, -0.4]), np.array([1.3, -0.7]), np.array([3.0, -2.0])
    mass, bias, gravity = model.AFFINE.operators(q, v)
    acceleration = np.linalg.solve(mass, torque - bias - gravity)
    step = 1e-6
    gradient = np.array(
        [
            (model.potential(q + step * e) - model.potential(q - step * e)) / (2 * step)
            for e in np.eye(2)
        ]
    )
    np.testing.assert_allclose(gradient, gravity, atol=1e-9)
    derivative = (
        model.energy(q + step * v, v + step * acceleration)
        - model.energy(q - step * v, v - step * acceleration)
    ) / (2 * step)
    assert derivative == pytest.approx(torque @ v, abs=1e-8)


def test_endpoint_jacobian_and_curvature_from_position(model):
    q, v, acceleration = np.array([0.6, -0.8]), np.array([1.7, -2.3]), np.array([2.0, -3.0])
    step = 1e-4
    forward = model.endpoint(q + step * v + 0.5 * step**2 * acceleration)
    backward = model.endpoint(q - step * v + 0.5 * step**2 * acceleration)
    first = (forward - backward) / (2 * step)
    second = (forward - 2 * model.endpoint(q) + backward) / step**2
    np.testing.assert_allclose(model.endpoint_jacobian(q) @ v, first, atol=1e-7)
    np.testing.assert_allclose(model.endpoint_acceleration(q, v, acceleration), second, atol=1e-7)


def test_straight_chain_has_tangential_family_and_normal_acceleration(model):
    q, v = np.zeros(2), np.array([10.0, 9.0])
    jacobian = model.endpoint_jacobian(q)
    assert np.linalg.matrix_rank(jacobian) == 1
    for first in (0.0, 20.0, 50 / 1.35):
        acceleration = np.array([first, 50 - 1.35 * first])
        np.testing.assert_allclose(jacobian @ acceleration, [50, 0], atol=1e-12)
        np.testing.assert_allclose(model.endpoint_acceleration(q, v, acceleration), [50, 396])


def test_absolute_coordinate_torques_preserve_virtual_work(model):
    q, v, torque = np.array([0.7, -0.5]), np.array([2.0, -3.0]), np.array([4.0, 7.0])
    transform = np.array([[1.0, 0.0], [1.0, 1.0]])
    inverse = np.linalg.inv(transform)
    absolute_torque = inverse.T @ torque
    assert absolute_torque @ (transform @ v) == pytest.approx(torque @ v)
    mass = model.AFFINE.operators(q, v)[0]
    absolute_mass = inverse.T @ mass @ inverse
    assert 0.5 * (transform @ v) @ absolute_mass @ (transform @ v) == pytest.approx(
        0.5 * v @ mass @ v
    )


def test_free_distal_response_differs_from_locked_inertia(model):
    mass = model.AFFINE.operators(np.deg2rad([0, -5]), np.zeros(2))[0]
    effective = mass[0, 0] - mass[0, 1] ** 2 / mass[1, 1]
    assert np.linalg.solve(mass, [1, 0])[0] == pytest.approx(1 / effective)
    assert effective < mass[0, 0]


def test_downward_small_oscillations_are_stable_not_inevitably_chaotic(model):
    frequencies = model.small_oscillation_frequencies()
    assert len(frequencies) == 2
    assert np.all(frequencies > 0)
    mass = model.AFFINE.operators(np.zeros(2), np.zeros(2))[0]
    stiffness = model.gravity_stiffness()
    for frequency in frequencies:
        assert abs(np.linalg.det(stiffness - frequency**2 * mass)) < 1e-10


@pytest.mark.parametrize(
    "edition", ["chapters/ch03_double_pendulum.tex", "quarto/ch03_double_pendulum.qmd"]
)
def test_paired_chapter_rejects_old_inertia_and_biological_inference(edition):
    text = (Path(__file__).parents[1] / "articles/The_Physics_of_Golf" / edition).read_text(
        encoding="utf-8"
    )
    for required in (
        "centroidal",
        "stationary action",
        "not a measured golfer",
        "6. Sensitivity Is Not a Chaos Diagnosis",
    ):
        assert required in text
    for unsupported in (
        "all that stored energy has been converted",
        "overcoming the inherent chaos",
        "wrist cocks and releases, but its effect",
        "muscles do the rest",
    ):
        assert unsupported not in text
