"""Independent frame, force and analytic checks for the recursive chapter."""

import numpy as np
import pytest
from numpy.testing import assert_allclose
from numpy.typing import NDArray
from scipy.linalg import expm

from scripts.generate_worked_examples import (
    VOL0_CH07_CHAIN,
    VOL0_CH07_Q,
    VOL0_CH07_QD,
    VOL0_CH07_QDD,
)
from src.affine_control.dynamics import force_cross, motion_cross
from src.affine_control.rnea import PlanarChain, PlanarLink
from src.core.constants import GRAVITY_M_S2
from src.tools.articulated_body_examples import DynamicsLoads, PreparedTree, inverse_dynamics
from src.tools.articulated_chain_examples import cylinder_chain
from src.tools.screw_examples import adjoint

type Array = NDArray[np.float64]


def _two_rods() -> PlanarChain:
    """Two unit uniform rods; inertias follow the one-dimensional mass integral."""
    return PlanarChain((PlanarLink(1, 1, 0.5, 1 / 12),) * 2)


def _analytic_rod_terms(q: Array, velocity: Array) -> tuple[Array, Array, Array]:
    """Closed form independently differentiated from Cartesian kinetic energy."""
    cosine, sine = np.cos(q[1]), np.sin(q[1])
    mass = np.array([[5 / 3 + cosine, 1 / 3 + cosine / 2], [1 / 3 + cosine / 2, 1 / 3]])
    bias = (
        sine / 2 * np.array([-2 * velocity[0] * velocity[1] - velocity[1] ** 2, velocity[0] ** 2])
    )
    gravity = GRAVITY_M_S2 * np.array(
        [1.5 * np.cos(q[0]) + 0.5 * np.cos(sum(q)), 0.5 * np.cos(sum(q))]
    )
    return mass, bias, gravity


@pytest.mark.parametrize("q", [[0, 0], [0.4, -0.7], [-1.2, 2.1]])
def test_two_uniform_rods_match_closed_form(q: list[float]) -> None:
    angles, velocity, acceleration = np.array(q), np.array([1.0, 0.5]), np.array([0.5, 0.2])
    mass, bias, gravity = _analytic_rod_terms(angles, velocity)
    chain = _two_rods()
    assert_allclose(chain.mass_matrix(angles), mass, atol=1e-14)
    assert_allclose(
        chain.inverse_dynamics(angles, velocity, acceleration),
        mass @ acceleration + bias + gravity,
        atol=1e-13,
    )


def test_horizontal_two_rod_example_has_exact_published_torques() -> None:
    result = _two_rods().inverse_dynamics(np.zeros(2), np.array([1, 0.5]), np.array([0.5, 0.2]))
    assert_allclose(result, [2 * GRAVITY_M_S2 + 1.5, GRAVITY_M_S2 / 2 + 29 / 60])


def test_three_link_decomposition_and_finite_difference_energy() -> None:
    chain, q, velocity = VOL0_CH07_CHAIN, VOL0_CH07_Q, VOL0_CH07_QD
    zero = np.zeros(3)
    gravity = chain.inverse_dynamics(q, zero, zero)
    bias = chain.inverse_dynamics(q, velocity, zero) - gravity
    inertia = chain.mass_matrix(q) @ VOL0_CH07_QDD
    assert_allclose(gravity, [11.41120182, 1.21871320, 0.30467830], atol=5e-9)
    assert_allclose(bias, [-0.16285252, 0.08481902, 0.02120476], atol=5e-9)
    assert_allclose(inertia, [2.65565458, 1.10484637, 0.34408659], atol=5e-9)
    step = 1e-5
    mass_rate = chain.mass_matrix(q + step * velocity) - chain.mass_matrix(q - step * velocity)
    mass_rate /= 2 * step
    assert_allclose(velocity @ bias, velocity @ mass_rate @ velocity / 2, atol=1e-10)


def test_actual_planar_child_has_nonzero_spatial_acceleration_bias() -> None:
    tree = cylinder_chain(np.array([1.0, 0.8]), np.ones(2), VOL0_CH07_Q[:2], 0.025)
    joint_first, joint_second = tree.subspace * VOL0_CH07_QD[:2, None]
    second_velocity = tree.transform[1] @ joint_first + joint_second
    bias = motion_cross(second_velocity) @ joint_second
    expected = 0.15 * np.array([np.cos(VOL0_CH07_Q[1]), -np.sin(VOL0_CH07_Q[1])])
    assert_allclose(bias[3:5], expected, atol=1e-15)
    assert_allclose(bias[[0, 1, 2, 5]], 0)


def _translated_frame() -> Array:
    """A nontrivial rotation and origin shift expose transpose-direction errors."""
    pose = np.eye(4)
    pose[:3, :3] = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
    pose[:3, 3] = [0.7, -0.2, 0.4]
    return pose


def test_adjoint_dual_preserves_power_and_force_moment_shift() -> None:
    pose = _translated_frame()
    rotation, offset = pose[:3, :3], pose[:3, 3]
    transform = adjoint(pose)
    motion_b = np.array([0.2, -0.3, 0.5, 1.0, -0.8, 0.4])
    wrench_b = np.array([0.7, 0.1, -0.2, 2.0, -3.0, 4.0])
    force_a = rotation @ wrench_b[3:]
    wrench_a = np.concatenate((rotation @ wrench_b[:3] + np.cross(offset, force_a), force_a))
    assert_allclose(np.linalg.solve(transform.T, wrench_b), wrench_a)
    assert_allclose(wrench_a @ (transform @ motion_b), wrench_b @ motion_b)
    assert_allclose(transform.T @ wrench_a, wrench_b)
    assert not np.allclose(np.linalg.solve(transform.T, wrench_a), wrench_b)


def test_group_adjoint_and_cross_product_duality() -> None:
    first = _translated_frame()
    second = np.eye(4)
    second[:3, 3] = [-0.4, 0.2, 0.8]
    assert_allclose(adjoint(first @ second), adjoint(first) @ adjoint(second))
    assert_allclose(adjoint(np.linalg.inv(first)) @ adjoint(first), np.eye(6), atol=1e-15)
    motion = np.array([0.1, -0.3, 0.8, 0.4, -0.7, 1.2])
    assert_allclose(force_cross(motion), -motion_cross(motion).T)


def test_external_loads_on_parent_and_both_children_follow_virtual_work() -> None:
    masses = np.array([2.0, 1.2, 0.6])
    inertia = np.array([np.diag([0.1, 0.1, 0.1, mass, mass, mass]) for mass in masses])
    direction = np.zeros((3, 6))
    direction[:, 3] = 1
    tree = PreparedTree((-1, 0, 0), np.tile(np.eye(6), (3, 1, 1)), direction, inertia)
    cartesian_map = np.array([[1, 0, 0], [1, 1, 0], [1, 0, 1]])
    external = np.zeros((3, 6))
    external[:, 3] = [0.4, -0.3, 1.1]
    acceleration = np.array([0.2, -0.7, 0.5])
    loads = DynamicsLoads(np.array([0.8, 0.2, -0.1]), np.zeros(3), external, np.zeros(3))
    expected = cartesian_map.T @ (masses * (cartesian_map @ acceleration) - external[:, 3])
    assert_allclose(inverse_dynamics(tree, loads, acceleration), expected, atol=1e-15)
    assert_allclose(
        external[:, 3] @ (cartesian_map @ loads.velocity),
        (cartesian_map.T @ external[:, 3]) @ loads.velocity,
    )


def test_mass_columns_require_subtracting_the_same_bias() -> None:
    chain, q = VOL0_CH07_CHAIN, VOL0_CH07_Q
    velocity = VOL0_CH07_QD
    bias = chain.inverse_dynamics(q, velocity, np.zeros(3))
    matrix = np.column_stack(
        [chain.inverse_dynamics(q, velocity, axis) - bias for axis in np.eye(3)]
    )
    assert_allclose(matrix, chain.mass_matrix(q), atol=5e-15)


def test_pure_translation_exponential_is_regular() -> None:
    generator = np.zeros((4, 4))
    generator[:3, 3] = [0.3, -0.7, 1.1]
    pose = expm(generator)
    assert_allclose(pose, np.eye(4) + generator)
    assert_allclose(np.linalg.det(pose), 1)
    assert_allclose(np.linalg.det(adjoint(pose)), 1)


def test_left_and_right_exponential_differentials_have_declared_order() -> None:
    generator = np.array(
        [[0, -0.4, 0.2, 0.7], [0.4, 0, -0.3, -0.2], [-0.2, 0.3, 0, 0.1], [0, 0, 0, 0]]
    )
    perturbation = np.zeros((4, 4))
    perturbation[:3, 3] = [0.1, 0.8, -0.6]
    nodes, weights = np.polynomial.legendre.leggauss(12)
    integral = sum(
        weight
        / 2
        * expm((1 - (node + 1) / 2) * generator)
        @ perturbation
        @ expm((node + 1) / 2 * generator)
        for node, weight in zip(nodes, weights, strict=True)
    )
    step = 1e-6
    derivative = (expm(generator + step * perturbation) - expm(generator - step * perturbation)) / (
        2 * step
    )
    assert_allclose(integral, derivative, atol=2e-10)
