"""Independent mechanics checks for the introductory articulated-body chapter."""

import importlib
from types import ModuleType

import numpy as np
import pytest
from numpy.testing import assert_allclose
from numpy.typing import NDArray

from src.core.constants import GRAVITY_M_S2
from src.tools.screw_examples import adjoint

type Array = NDArray[np.float64]
LENGTHS = np.array([0.4, 0.3, 0.25])
MASSES = np.array([2.0, 1.2, 0.6])
RADIUS = 0.025
STEP = 2e-6


@pytest.fixture
def dynamics() -> ModuleType:
    return importlib.import_module("src.tools.articulated_body_examples")


@pytest.fixture
def chains() -> ModuleType:
    return importlib.import_module("src.tools.articulated_chain_examples")


def _jacobians(angles: Array) -> list[Array]:
    """World COM velocity Jacobians from differentiated Cartesian positions."""
    cumulative = np.cumsum(angles)
    perpendicular = np.column_stack((-np.sin(cumulative), np.cos(cumulative)))
    jacobians = []
    for body in range(len(angles)):
        jacobian = np.zeros((2, len(angles)))
        for joint in range(body + 1):
            jacobian[:, joint] = LENGTHS[body] / 2 * perpendicular[body]
            for segment in range(joint, body):
                jacobian[:, joint] += LENGTHS[segment] * perpendicular[segment]
        jacobians.append(jacobian)
    return jacobians


def _mass(angles: Array) -> Array:
    """Assemble generalized inertia independently from Cartesian kinetic energy."""
    matrix = np.zeros((len(angles), len(angles)))
    for body, jacobian in enumerate(_jacobians(angles)):
        angular_jacobian = np.zeros(len(angles))
        angular_jacobian[: body + 1] = 1
        moment = MASSES[body] * (LENGTHS[body] ** 2 + 3 * RADIUS**2) / 12
        matrix += MASSES[body] * jacobian.T @ jacobian
        matrix += moment * np.outer(angular_jacobian, angular_jacobian)
    return matrix


def _lagrange_bias(angles: Array, velocity: Array) -> Array:
    """Christoffel forces from finite differences, plus Cartesian gravitational work."""
    count = len(angles)
    derivatives = np.stack(
        [
            (_mass(angles + STEP * axis) - _mass(angles - STEP * axis)) / (2 * STEP)
            for axis in np.eye(count)
        ]
    )
    bias = np.zeros(count)
    for first in range(count):
        for second in range(count):
            for third in range(count):
                coefficient = (
                    derivatives[third, first, second]
                    + derivatives[second, first, third]
                    - derivatives[first, second, third]
                ) / 2
                bias[first] += coefficient * velocity[second] * velocity[third]
    for body, jacobian in enumerate(_jacobians(angles)):
        bias += MASSES[body] * GRAVITY_M_S2 * jacobian[1]
    return bias


@pytest.mark.parametrize("angles", [[0, 0, 0], [0.4, -0.7, 0.2], [-1.2, 0.8, -0.5]])
def test_full_chain_matches_independent_lagrange(
    dynamics: ModuleType, chains: ModuleType, angles: list[float]
) -> None:
    configuration = np.array(angles)
    velocity = np.array([0.8, -0.5, 1.1])
    torque = np.array([4.0, -1.0, 0.3])
    tree = chains.cylinder_chain(LENGTHS, MASSES, configuration, RADIUS)
    loads = dynamics.DynamicsLoads(velocity, torque)
    expected = np.linalg.solve(
        _mass(configuration), torque - _lagrange_bias(configuration, velocity)
    )
    result = dynamics.forward_dynamics(tree, loads)
    assert_allclose(result.joint_acceleration, expected, atol=2e-7)
    assert_allclose(dynamics.inverse_dynamics(tree, loads, expected), torque, atol=2e-8)


def test_external_wrench_damping_and_armature_enter_before_solve(
    dynamics: ModuleType, chains: ModuleType
) -> None:
    angles = np.array([0.4, -0.7, 0.2])
    velocity = np.array([0.8, -0.5, 1.1])
    torque = np.array([4.0, -1.0, 0.3])
    damping, armature = np.array([0.2, 0.1, 0.03]), np.array([0.04, 0.02, 0.01])
    external = np.zeros((3, 6))
    external[2] = [0, 0, 0.7, 1.2, -0.4, 0]
    angle = sum(angles)
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    # Wrench is about the distal joint origin, so remove its COM lever arm.
    origin_jacobian = _jacobians(angles)[2].copy()
    origin_jacobian -= LENGTHS[2] / 2 * np.array([[-np.sin(angle)], [np.cos(angle)]])
    generalized = origin_jacobian.T @ rotation @ external[2, 3:5] + external[2, 2]
    tree = chains.cylinder_chain(LENGTHS, MASSES, angles, RADIUS)
    loads = dynamics.DynamicsLoads(
        velocity, torque, external=external, damping=damping, armature=armature
    )
    expected = np.linalg.solve(
        _mass(angles) + np.diag(armature),
        torque - damping * velocity + generalized - _lagrange_bias(angles, velocity),
    )
    result = dynamics.forward_dynamics(tree, loads)
    assert_allclose(result.joint_acceleration, expected, atol=2e-7)
    assert_allclose(dynamics.inverse_dynamics(tree, loads, expected), torque, atol=2e-8)


def test_unactuated_distal_joint_changes_proximal_effective_inertia(
    dynamics: ModuleType, chains: ModuleType
) -> None:
    angles = np.array([0.3, 0.5, -0.8])
    tree = chains.cylinder_chain(LENGTHS, MASSES, angles, RADIUS)
    loads = dynamics.DynamicsLoads(np.zeros(3), np.array([1.0, 0, 0]), gravity=np.zeros(3))
    result = dynamics.forward_dynamics(tree, loads)
    matrix = _mass(angles)
    effective = matrix[0, 0] - matrix[0, 1:] @ np.linalg.solve(matrix[1:, 1:], matrix[1:, 0])
    assert_allclose(result.pivot[0], effective, atol=1e-12)
    assert_allclose(result.joint_acceleration[0], 1 / effective, atol=1e-11)
    assert effective < matrix[0, 0]


def test_mass_inverse_columns_and_dense_serial_coupling(
    dynamics: ModuleType, chains: ModuleType
) -> None:
    angles = np.array([0.2, -0.6, 0.3])
    tree = chains.cylinder_chain(LENGTHS, MASSES, angles, RADIUS)
    columns = [
        dynamics.forward_dynamics(
            tree, dynamics.DynamicsLoads(np.zeros(3), axis, gravity=np.zeros(3))
        ).joint_acceleration
        for axis in np.eye(3)
    ]
    assert_allclose(_mass(angles) @ np.column_stack(columns), np.eye(3), atol=1e-12)
    assert np.all(np.abs(_mass(angles)) > 0.001)


def test_one_link_exact_gravity_and_applied_torque(
    dynamics: ModuleType, chains: ModuleType
) -> None:
    angle = np.array([0.7])
    tree = chains.cylinder_chain(LENGTHS[:1], MASSES[:1], angle, RADIUS)
    loads = dynamics.DynamicsLoads(np.array([1.3]), np.array([0.8]))
    expected = 0.8 - MASSES[0] * GRAVITY_M_S2 * LENGTHS[0] / 2 * np.cos(angle[0])
    expected /= _mass(angle)[0, 0]
    assert_allclose(dynamics.forward_dynamics(tree, loads).joint_acceleration, [expected])


@pytest.mark.parametrize("bad", [[0, 0], [0, np.nan, 0]])
def test_invalid_loads_are_rejected(
    dynamics: ModuleType, chains: ModuleType, bad: list[float]
) -> None:
    tree = chains.cylinder_chain(LENGTHS, MASSES, np.zeros(3), RADIUS)
    with pytest.raises(ValueError):
        dynamics.forward_dynamics(tree, dynamics.DynamicsLoads(np.array(bad), np.zeros(3)))


@pytest.mark.parametrize("field", ["damping", "armature"])
def test_negative_passive_parameters_are_rejected(
    dynamics: ModuleType, chains: ModuleType, field: str
) -> None:
    tree = chains.cylinder_chain(LENGTHS, MASSES, np.zeros(3), RADIUS)
    with pytest.raises(ValueError):
        dynamics.forward_dynamics(
            tree,
            dynamics.DynamicsLoads(np.zeros(3), np.zeros(3), **{field: np.array([0, -0.1, 0])}),
        )


@pytest.mark.parametrize("lengths", [np.array([]), np.array([0.4, -0.3, 0.25])])
def test_nonphysical_chain_is_rejected(chains: ModuleType, lengths: Array) -> None:
    with pytest.raises(ValueError):
        chains.cylinder_chain(lengths, MASSES, np.zeros(3), RADIUS)


def test_constant_body_frame_changes_preserve_joint_acceleration(
    dynamics: ModuleType, chains: ModuleType
) -> None:
    tree = chains.cylinder_chain(LENGTHS, MASSES, np.array([0.4, -0.7, 0.2]), RADIUS)
    loads = dynamics.DynamicsLoads(np.array([0.8, -0.5, 1.1]), np.array([4.0, -1, 0.3]))
    changes = []
    for index in range(3):
        pose = np.eye(4)
        pose[:3, 3] = [0.07 * index, -0.03, 0.02]
        pose[:3, :3] = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
        changes.append(adjoint(pose))
    transform, inertia, direction = [], [], []
    for body, parent in enumerate(tree.parents):
        change = changes[body]
        inverse = np.linalg.inv(change)
        parent_inverse = np.eye(6) if parent == -1 else np.linalg.inv(changes[parent])
        transform.append(change @ tree.transform[body] @ parent_inverse)
        inertia.append(inverse.T @ tree.inertia[body] @ inverse)
        direction.append(change @ tree.subspace[body])
    changed = dynamics.PreparedTree(
        tree.parents, np.array(transform), np.array(direction), np.array(inertia)
    )
    assert_allclose(
        dynamics.forward_dynamics(changed, loads).joint_acceleration,
        dynamics.forward_dynamics(tree, loads).joint_acceleration,
        atol=1e-11,
    )


def test_branched_prismatic_tree_matches_cartesian_newton_equations(dynamics: ModuleType) -> None:
    # Three masses moving on the same horizontal axis; children share a moving parent.
    inertias = np.stack([np.diag([0.1, 0.1, 0.1, mass, mass, mass]) for mass in MASSES])
    direction = np.zeros((3, 6))
    direction[:, 3] = 1
    tree = dynamics.PreparedTree((-1, 0, 0), np.tile(np.eye(6), (3, 1, 1)), direction, inertias)
    cartesian_map = np.array([[1, 0, 0], [1, 1, 0], [1, 0, 1]])
    mass = cartesian_map.T @ np.diag(MASSES) @ cartesian_map
    torque = np.array([1.2, -0.4, 0.7])
    loads = dynamics.DynamicsLoads(np.array([0.3, 0.7, -0.2]), torque, gravity=np.zeros(3))
    expected = np.linalg.solve(mass, torque)
    assert_allclose(dynamics.forward_dynamics(tree, loads).joint_acceleration, expected)
    assert_allclose(dynamics.inverse_dynamics(tree, loads, expected), torque)


@pytest.mark.parametrize("parents", [(), (0,), (-1, 2), (-2,)])
def test_invalid_tree_order_is_rejected(dynamics: ModuleType, parents: tuple[int, ...]) -> None:
    count = len(parents)
    with pytest.raises(ValueError):
        dynamics.PreparedTree(
            parents, np.zeros((count, 6, 6)), np.zeros((count, 6)), np.zeros((count, 6, 6))
        )


@pytest.mark.parametrize("mode", ["zero-subspace", "asymmetric", "indefinite", "bad-transform"])
def test_invalid_tree_arrays_are_rejected(dynamics: ModuleType, mode: str) -> None:
    transform, inertia = np.eye(6)[None], np.eye(6)[None]
    direction = np.array([[0, 0, 1, 0, 0, 0]])
    if mode == "zero-subspace":
        direction[:] = 0
    elif mode == "asymmetric":
        inertia[0, 0, 1] = 1
    elif mode == "indefinite":
        inertia[0, 0, 0] = -1
    else:
        transform[0, 0, 0] = np.nan
    with pytest.raises(ValueError):
        dynamics.PreparedTree((-1,), transform, direction, inertia)


def test_contact_projection_is_mass_weighted_and_changes_torque_response() -> None:
    mass = _mass(np.array([0.4, -0.7, 0.2]))
    jacobian = np.array([[0.3, -0.4, 0.7]])
    inverse_action = np.linalg.solve(mass, jacobian.T)
    contact_mass = jacobian @ inverse_action
    free = np.array([2.0, -3.0, 1.0])
    drift = np.array([0.2])
    reaction = np.linalg.solve(contact_mass, -drift - jacobian @ free)
    constrained = free + inverse_action @ reaction
    assert_allclose(jacobian @ constrained + drift, 0, atol=1e-14)
    tangent = np.array([0.4, 0.3, 0])
    displacement = constrained - free
    assert_allclose(tangent @ mass @ displacement, 0, atol=1e-14)
    assert (displacement + tangent) @ mass @ (
        displacement + tangent
    ) > displacement @ mass @ displacement
    inverse_mass = np.linalg.solve(mass, np.eye(3))
    response = inverse_mass - inverse_action @ np.linalg.solve(contact_mass, inverse_action.T)
    assert_allclose(jacobian @ response, 0, atol=1e-13)


@pytest.mark.parametrize("restitution", [0.0, 0.5, 1.0])
def test_single_impact_velocity_and_energy_law(restitution: float) -> None:
    angles = np.array([0.4, -0.7])
    mass = _mass(angles)
    cumulative = np.cumsum(angles)
    normal = np.array([sum(LENGTHS[:2] * np.cos(cumulative)), LENGTHS[1] * np.cos(cumulative[1])])
    before = np.array([-0.8, -0.5])
    mobility = float(normal @ np.linalg.solve(mass, normal))
    normal_before = float(normal @ before)
    impulse = -(1 + restitution) * normal_before / mobility
    after = before + np.linalg.solve(mass, normal) * impulse
    assert impulse > 0
    assert_allclose(normal @ after, -restitution * normal_before, atol=1e-14)
    loss = (before @ mass @ before - after @ mass @ after) / 2
    assert_allclose(loss, (1 - restitution**2) * normal_before**2 / (2 * mobility), atol=1e-14)


def test_inertia_change_derivative_matches_resolved_acceleration() -> None:
    angles = np.array([0.4, -0.7, 0.2])
    direction = np.array([0.2, -0.3, 0.4])
    torque = np.array([1, -0.4, 0.2])
    mass = _mass(angles)
    acceleration = np.linalg.solve(mass, torque)
    plus, minus = _mass(angles + STEP * direction), _mass(angles - STEP * direction)
    derivative = (plus - minus) / (2 * STEP)
    predicted = -np.linalg.solve(mass, derivative @ acceleration)
    measured = (np.linalg.solve(plus, torque) - np.linalg.solve(minus, torque)) / (2 * STEP)
    assert_allclose(predicted, measured, atol=2e-7)
