"""Independent mechanics checks for the paired Lagrangian chapter."""

import importlib

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from src.core.constants import GRAVITY_M_S2


@pytest.fixture
def examples():
    return importlib.import_module("src.tools.lagrangian_examples")


@pytest.fixture
def model(examples):
    return examples.RodPair(masses=(1.3, 0.8), lengths=(1.2, 0.7), gravity=GRAVITY_M_S2)


def rod_quadrature(model, angles, rates):
    """Integrate particle kinetic energy over each uniform rod independently."""
    nodes, weights = np.polynomial.legendre.leggauss(3)
    distances = (nodes + 1) / 2
    tangent = np.column_stack((np.cos(angles), np.sin(angles)))
    first_velocity = distances[:, None] * model.lengths[0] * rates[0] * tangent[0]
    second_velocity = model.lengths[0] * rates[0] * tangent[0]
    second_velocity = (
        second_velocity + distances[:, None] * model.lengths[1] * rates[1] * tangent[1]
    )
    return sum(
        mass * np.dot(weights, np.sum(velocity**2, axis=1)) / 4
        for mass, velocity in zip(model.masses, (first_velocity, second_velocity), strict=True)
    )


@pytest.mark.parametrize("angles", [(0, 0), (0.4, -0.9), (1.0, 1.0 + np.pi)])
@pytest.mark.parametrize("rates", [(1, 0), (0, 1), (0.6, -1.4)])
def test_mass_matches_distributed_particle_energy(model, angles, rates):
    rates = np.array(rates)
    matrix = model.mass_matrix(np.array(angles))
    assert np.linalg.eigvalsh(matrix).min() > 0
    assert rates @ matrix @ rates / 2 == pytest.approx(rod_quadrature(model, angles, rates))


def test_old_published_mass_can_give_negative_kinetic_energy():
    """The original unit-link code is not a physical inertia model."""
    old = np.array([[1.5, 1.0], [1.0, 0.5]])
    assert np.linalg.det(old) == pytest.approx(-0.25)
    assert np.array([1, -2]) @ old @ np.array([1, -2]) / 2 == pytest.approx(-0.25)


@pytest.mark.parametrize("rates", [(0.4, -0.8), (1.3, 0.2), (0, 0)])
def test_bias_and_skew_property_from_independent_mass_derivatives(model, rates):
    angles, rates = np.array([0.3, -0.7]), np.array(rates)
    step = 1e-6
    derivatives = np.array(
        [
            (model.mass_matrix(angles + step * axis) - model.mass_matrix(angles - step * axis))
            / (2 * step)
            for axis in np.eye(2)
        ]
    )
    mass_rate = np.einsum("k,kij->ij", rates, derivatives)
    kinetic_gradient = np.einsum("i,kij,j->k", rates, derivatives, rates) / 2
    coriolis = model.coriolis_matrix(angles, rates)
    np.testing.assert_allclose(coriolis @ rates, mass_rate @ rates - kinetic_gradient, atol=1e-10)
    skew = mass_rate - 2 * coriolis
    np.testing.assert_allclose(skew + skew.T, 0, atol=1e-10)


def test_gravity_is_positive_potential_gradient(model):
    angles, step = np.array([0.2, -0.8]), 1e-6
    finite = [
        (model.potential(angles + step * axis) - model.potential(angles - step * axis)) / (2 * step)
        for axis in np.eye(2)
    ]
    np.testing.assert_allclose(model.gravity_vector(angles), finite, atol=2e-9)


def test_physical_motor_mapping_preserves_power(examples, model):
    state, motor = np.array([0.2, -0.6, 0.8, -1.1]), np.array([0.7, -0.3])
    generalized = examples.motor_generalized(motor)
    np.testing.assert_allclose(generalized, [1.0, -0.3])
    relative_rates = np.array([state[2], state[3] - state[2]])
    assert generalized @ state[2:] == pytest.approx(motor @ relative_rates)
    acceleration = model.acceleration(state, motor)
    direction, step = np.r_[state[2:], acceleration], 1e-6
    energy_rate = (
        model.energy(state + step * direction) - model.energy(state - step * direction)
    ) / (2 * step)
    assert energy_rate == pytest.approx(motor @ relative_rates, abs=2e-9)


def test_relative_arm_inertia_matches_independent_uniform_rod_formula(model):
    angles, rates = np.array([0.4, 0.8]), np.array([0.7, -0.2])
    first, second = model.masses
    length, distal = model.lengths
    coupling = second * length * distal * np.cos(angles[1]) / 2
    expected = np.array(
        [
            [
                (first / 3 + second) * length**2 + second * distal**2 / 3 + 2 * coupling,
                second * distal**2 / 3 + coupling,
            ],
            [second * distal**2 / 3 + coupling, second * distal**2 / 3],
        ]
    )
    mass, coriolis, gravity = model.relative_arm_terms(angles, rates)
    np.testing.assert_allclose(mass, expected)
    coefficient = second * length * distal * np.sin(angles[1]) / 2
    np.testing.assert_allclose(
        coriolis @ rates,
        [-coefficient * (2 * rates[0] * rates[1] + rates[1] ** 2), coefficient * rates[0] ** 2],
    )
    common = second * model.gravity * distal * np.cos(sum(angles)) / 2
    np.testing.assert_allclose(
        gravity,
        [(first / 2 + second) * model.gravity * length * np.cos(angles[0]) + common, common],
    )


@pytest.mark.integration
def test_simulation_energy_and_work_balance(model):
    initial = np.array([0.6, -0.2, 0.3, -0.4])
    for motor in (np.zeros(2), np.array([0.2, -0.1])):
        result = solve_ivp(
            lambda time, state, torque=motor: np.r_[state[2:], model.acceleration(state, torque)],
            (0, 2),
            initial,
            rtol=1e-10,
            atol=1e-12,
            t_eval=np.linspace(0, 2, 101),
        )
        assert result.success
        energies = np.array([model.energy(state) for state in result.y.T])
        relative = np.vstack((result.y[0], result.y[1] - result.y[0]))
        work = motor @ (relative - relative[:, :1])
        assert np.max(np.abs(energies - energies[0] - work)) < 2e-8


def test_skew_coriolis_factor_is_not_unique():
    velocity = np.array([0.3, -0.7, 1.2])
    x, y, z = velocity
    addition = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    np.testing.assert_allclose(addition @ velocity, 0, atol=1e-16)
    np.testing.assert_allclose(addition + addition.T, 0)
    assert np.linalg.norm(addition) > 0


def test_nonseparable_symplectic_step_preserves_area(examples):
    state, step, delta = np.array([0.2, 0.4]), 0.1, 1e-6
    jacobian = np.column_stack(
        [
            (
                examples.variable_mass_step(state + delta * axis, step)
                - examples.variable_mass_step(state - delta * axis, step)
            )
            / (2 * delta)
            for axis in np.eye(2)
        ]
    )
    assert np.linalg.det(jacobian) == pytest.approx(1, abs=1e-9)
    result = examples.variable_mass_step(state, step)
    scale = np.exp(-2 * state[0])
    assert result[1] == pytest.approx(state[1] + step * scale * result[1] ** 2)
    assert result[0] == pytest.approx(state[0] + step * scale * result[1])


def test_old_nonseparable_update_is_not_symplectic():
    coordinate, momentum, step = 0.2, 0.4, 0.1
    scale = np.exp(-2 * coordinate)
    dimensionless = step * scale * momentum
    # Direct differentiation of the original old-p momentum update.
    determinant = 1 - 6 * dimensionless**2 - 4 * dimensionless**3
    assert abs(determinant - 1) > 0.004


@pytest.mark.parametrize(
    "masses,lengths", [((0, 1), (1, 1)), ((1, 1), (-1, 1)), ((1,), (1, 1)), ((np.inf, 1), (1, 1))]
)
def test_invalid_rod_models_rejected(examples, masses, lengths):
    with pytest.raises(ValueError):
        examples.RodPair(masses=masses, lengths=lengths)


@pytest.mark.parametrize("state", [np.zeros(3), np.array([0, 0, np.nan, 0])])
def test_invalid_state_rejected(model, state):
    with pytest.raises(ValueError):
        model.energy(state)


def test_invalid_symplectic_branch_rejected(examples):
    with pytest.raises(ValueError):
        examples.variable_mass_step(np.array([0.0, 1.0]), 1.0)
    with pytest.raises(ValueError):
        examples.variable_mass_step(np.zeros(2), -0.1)


@pytest.mark.parametrize("gravity", [-1.0, np.inf])
def test_invalid_gravity_rejected(examples, gravity):
    with pytest.raises(ValueError):
        examples.RodPair(gravity=gravity)


def test_invalid_motor_vector_rejected(examples):
    with pytest.raises(ValueError):
        examples.motor_generalized(np.zeros(3))


def test_unrepresentable_variable_mass_rejected(examples):
    with pytest.raises(ValueError):
        examples.variable_mass_step(np.array([-1000.0, 1.0]), 0.1)


@pytest.mark.parametrize("step", [0.2, 1.5, 2.5])
def test_symplecticity_does_not_imply_stability(step):
    matrix = np.array([[1 - step**2, step], [-step, 1]])
    metric = np.array([[1, -step / 2], [-step / 2, 1]])
    assert np.linalg.det(matrix) == pytest.approx(1)
    np.testing.assert_allclose(matrix.T @ metric @ matrix, metric, atol=1e-14)
    if step < 2:
        assert np.linalg.eigvalsh(metric).min() > 0
    else:
        assert max(abs(np.linalg.eigvals(matrix))) > 1
