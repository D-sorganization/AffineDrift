"""Independent mechanics checks of the multibody comparison's published example."""

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scipy.linalg import expm

ARTICLE = (
    Path(__file__).resolve().parents[1]
    / "articles/calculation-framework-comparison/multibody-drift-control-v3.qmd"
)
GRAVITY_M_S2 = 9.81
LENGTHS = np.array([0.8, 0.6])
MASSES = np.array([1.4, 0.5])


@pytest.fixture(scope="module")
def example() -> dict[str, Any]:
    """Execute the exact independently runnable program offered to readers."""
    text = ARTICLE.read_text(encoding="utf-8")
    block = re.search(r"```python\n(# Multibody equivalence example\n.*?)\n```", text, re.S)
    assert block is not None, "Publish the complete multibody verification example"
    namespace: dict[str, Any] = {}
    exec(compile(block.group(1), str(ARTICLE), "exec"), namespace)
    return namespace


def positions(q: np.ndarray) -> np.ndarray:
    """Compute Cartesian point-mass positions independently."""
    angles = np.cumsum(q)
    segments = LENGTHS[:, None] * np.column_stack((np.sin(angles), -np.cos(angles)))
    return np.cumsum(segments, axis=0)


@pytest.mark.parametrize("q", [[0.4, -0.7], [0.0, 0.0], [0.2, np.pi]])
def test_inertia_and_cartesian_kinematics(example: dict[str, Any], q: list[float]) -> None:
    """Check the kinetic metric and curvature against perturbed Cartesian geometry."""
    state = np.array(q)
    velocity = np.array([2.1, -0.8])
    data = example["pendulum_data"](state, velocity, LENGTHS, MASSES)
    step = 1e-5
    jac = np.stack(
        [
            (positions(state + step * e) - positions(state - step * e)) / (2 * step)
            for e in np.eye(2)
        ],
        axis=-1,
    )
    curvature = (
        positions(state + step * velocity)
        - 2 * positions(state)
        + positions(state - step * velocity)
    ) / step**2
    np.testing.assert_allclose(data["jacobians"], jac, atol=1e-9)
    np.testing.assert_allclose(data["curvature"], curvature, atol=8e-6)
    metric = sum(mass * body.T @ body for mass, body in zip(MASSES, jac, strict=True))
    np.testing.assert_allclose(data["mass"], metric, atol=1e-9)
    expected_det = MASSES[1] * LENGTHS.prod() ** 2 * (MASSES[0] + MASSES[1] * np.sin(state[1]) ** 2)
    assert np.linalg.det(data["mass"]) == pytest.approx(expected_det)
    assert np.linalg.eigvalsh(data["mass"]).min() > 0


@pytest.mark.parametrize("torque", [[0.0, 0.0], [2.0, -0.3], [-1.0, 0.8]])
def test_body_balances_recover_joint_torques_and_power(
    example: dict[str, Any], torque: list[float]
) -> None:
    """Recover efforts from Cartesian inertial loads and balance each body's energy."""
    q = np.array([0.4, -0.7])
    velocity = np.array([3.0, -2.0])
    tau = np.array(torque)
    data = example["pendulum_data"](q, velocity, LENGTHS, MASSES)
    acceleration = np.linalg.solve(data["mass"], tau - data["bias"])
    jac = data["jacobians"]
    point_velocity = jac @ velocity
    point_acceleration = jac @ acceleration + data["curvature"]
    gravity = np.array([0.0, -GRAVITY_M_S2])
    inertial_loads = MASSES[:, None] * (point_acceleration - gravity)
    recovered = sum(j.T @ force for j, force in zip(jac, inertial_loads, strict=True))
    np.testing.assert_allclose(recovered, tau, atol=1e-12)
    internal_force = inertial_loads[1]
    force_transfer = internal_force @ point_velocity[0]
    gravity_power = MASSES * (point_velocity @ gravity)
    angular_velocity = np.cumsum(velocity)
    power = np.array(
        [
            tau[0] * angular_velocity[0]
            - tau[1] * angular_velocity[0]
            - force_transfer
            + gravity_power[0],
            tau[1] * angular_velocity[1] + force_transfer + gravity_power[1],
        ]
    )
    kinetic_rate = MASSES * np.sum(point_velocity * point_acceleration, axis=1)
    np.testing.assert_allclose(power, kinetic_rate, atol=1e-12)
    assert np.sum(kinetic_rate - gravity_power) == pytest.approx(tau @ velocity, abs=1e-12)


def test_stationary_constraint_has_curvature_and_input_reaction(example: dict[str, Any]) -> None:
    """Check a particle constrained to a circle against radial/tangential mechanics."""
    mass = 2 * np.eye(2)
    jacobian = np.array([[2.0, 0.0]])
    curvature = np.array([9.0])
    zero, reaction_zero = example["constrained_acceleration"](
        mass, np.zeros(2), jacobian, curvature
    )
    forced, reaction = example["constrained_acceleration"](
        mass, np.array([4.0, 6.0]), jacobian, curvature
    )
    np.testing.assert_allclose(zero, [-4.5, 0.0])
    np.testing.assert_allclose(forced, [-4.5, 3.0])
    np.testing.assert_allclose(reaction_zero, [-4.5])
    np.testing.assert_allclose(reaction, [-6.5])
    np.testing.assert_allclose(jacobian @ (forced - zero), 0.0, atol=1e-12)
    assert float((jacobian.T @ reaction) @ np.array([0.0, 3.0])) == 0.0


def test_task_rank_loss_does_not_singularize_joint_inertia(example: dict[str, Any]) -> None:
    """At straight-down posture there is radial bias but no radial input increment."""
    data = example["pendulum_data"](np.zeros(2), np.array([2.0, 0.0]), LENGTHS, MASSES)
    jacobian = data["jacobians"][1]
    mobility = jacobian @ np.linalg.solve(data["mass"], jacobian.T)
    assert np.linalg.matrix_rank(mobility) == 1
    assert np.linalg.matrix_rank(data["mass"]) == 2
    assert data["curvature"][1, 1] == pytest.approx(4 * LENGTHS.sum())
    np.testing.assert_allclose(jacobian[1], 0.0)


def test_space_twist_requires_cross_position_term() -> None:
    """Use the actual downward-vertical home geometry rather than an x-axis home."""
    q = np.array([0.4, -0.7])
    velocity = np.array([3.0, -2.0])
    points = positions(q)
    pivot = np.r_[points[0], 0.0]
    endpoint = np.r_[points[1], 0.0]
    axis = np.array([0.0, 0.0, 1.0])
    space_jacobian = np.column_stack(
        (np.r_[axis, np.zeros(3)], np.r_[axis, -np.cross(axis, pivot)])
    )
    twist = space_jacobian @ velocity
    actual = twist[3:] + np.cross(twist[:3], endpoint)
    step = 1e-6
    finite_difference = (positions(q + step * velocity) - positions(q - step * velocity)) / (
        2 * step
    )
    np.testing.assert_allclose(actual[:2], finite_difference[1], atol=1e-9)
    assert not np.allclose(twist[3:5], finite_difference[1])


def test_full_controlled_linearization_includes_input_map_derivative() -> None:
    """A variable-inertia scalar model exposes the omitted nominal-input term."""
    q, velocity, input_value = 0.6, 0.8, 2.0
    mass = 1 + q**2
    drift = -q * velocity**2 / mass
    full_derivative = (-(velocity**2) * mass - 2 * q * (input_value - q * velocity**2)) / mass**2
    step = 1e-6
    actual = (
        (input_value - (q + step) * velocity**2) / (1 + (q + step) ** 2)
        - (input_value - (q - step) * velocity**2) / (1 + (q - step) ** 2)
    ) / (2 * step)
    drift_derivative = -(velocity**2) / mass - 2 * q * drift / mass
    assert actual == pytest.approx(full_derivative, abs=1e-9)
    assert full_derivative - drift_derivative == pytest.approx(-2 * q * input_value / mass**2)


def test_hurwitz_instantaneous_matrices_can_have_growing_transition_product() -> None:
    """Separate frozen eigenvalues from the stability of time-varying dynamics."""
    first = np.array([[-1.0, 4.0], [0.0, -1.0]])
    second = first.T
    np.testing.assert_allclose(np.linalg.eigvals(first), [-1.0, -1.0])
    np.testing.assert_allclose(np.linalg.eigvals(second), [-1.0, -1.0])
    transition = expm(second) @ expm(first)
    assert np.max(np.abs(np.linalg.eigvals(transition))) > 2.0


def test_acceleration_chart_hessian_cancels_only_in_same_state_difference() -> None:
    """A nonlinear chart changes drift acceleration even for a free particle."""
    q, velocity = 2.0, 3.0
    force_acceleration = 5.0
    drift_new = 2 * velocity**2
    forced_new = 2 * q * force_acceleration + 2 * velocity**2
    assert drift_new != 0.0
    assert forced_new - drift_new == 2 * q * force_acceleration


def test_mass_metric_projection_and_schur_solve_agree(example: dict[str, Any]) -> None:
    """Compare the block solve with the derived affine projection for coupled inertia."""
    mass = np.array([[3.0, 0.7, 0.2], [0.7, 2.0, 0.1], [0.2, 0.1, 1.0]])
    jacobian = np.array([[1.0, -2.0, 0.5]])
    curvature = np.array([0.4])
    force = np.array([1.0, 2.0, -0.3])
    mobility = np.linalg.solve(mass, jacobian.T)
    normal_metric = jacobian @ mobility
    projection = np.eye(3) - mobility @ np.linalg.solve(normal_metric, jacobian)
    np.testing.assert_allclose(projection @ projection, projection, atol=1e-12)
    np.testing.assert_allclose(projection.T @ mass, mass @ projection, atol=1e-12)
    projected = projection @ np.linalg.solve(mass, force) - mobility @ np.linalg.solve(
        normal_metric, curvature
    )
    actual, reaction = example["constrained_acceleration"](mass, force, jacobian, curvature)
    np.testing.assert_allclose(actual, projected, atol=1e-12)
    np.testing.assert_allclose(mass @ actual, force + jacobian.T @ reaction, atol=1e-12)


def test_redundant_task_effect_is_unique_but_joint_allocation_is_not() -> None:
    """Check the dynamically weighted effort decomposition with coupled inertia."""
    mass = np.array([[2.0, 0.3, 0.0], [0.3, 1.0, 0.2], [0.0, 0.2, 1.4]])
    jacobian = np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 1.0]])
    torque = np.array([0.4, -0.3, 1.0])
    task_mobility = jacobian @ np.linalg.solve(mass, jacobian.T)
    effect = jacobian @ np.linalg.solve(mass, torque)
    effective_force = np.linalg.solve(task_mobility, effect)
    null_torque = torque - jacobian.T @ effective_force
    np.testing.assert_allclose(
        jacobian @ np.linalg.solve(mass, null_torque), np.zeros(2), atol=1e-12
    )
    assert np.linalg.norm(null_torque) > 0.1
    for scale in [-2.0, 0.0, 3.0]:
        np.testing.assert_allclose(
            jacobian @ np.linalg.solve(mass, jacobian.T @ effective_force + scale * null_torque),
            effect,
            atol=1e-12,
        )


def test_fast_aligned_pendulum_can_have_zero_drift_acceleration(
    example: dict[str, Any],
) -> None:
    """High speed alone is not a lower bound on the pointwise generalized drift."""
    data = example["pendulum_data"](np.zeros(2), np.array([100.0, -20.0]), LENGTHS, MASSES)
    np.testing.assert_allclose(np.linalg.solve(data["mass"], -data["bias"]), 0.0)
    assert np.linalg.norm(data["curvature"]) > 1000


def test_body_twist_wrench_power_matches_kinetic_energy_rate() -> None:
    """Verify the stated angular-first adjoint sign in a body COM frame."""
    omega = np.array([0.3, -0.4, 0.8])
    linear = np.array([1.0, 0.7, -0.2])

    def cross_matrix(vector: np.ndarray) -> np.ndarray:
        """Return the skew operator for a three-vector."""
        x, y, z = vector
        return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])

    adjoint = np.block(
        [[cross_matrix(omega), np.zeros((3, 3))], [cross_matrix(linear), cross_matrix(omega)]]
    )
    inertia = np.diag([0.8, 1.2, 1.5, 2.0, 2.0, 2.0])
    twist = np.r_[omega, linear]
    derivative = np.array([0.1, 0.4, -0.3, 0.2, -0.8, 0.6])
    wrench = inertia @ derivative - adjoint.T @ inertia @ twist
    expected_moment = inertia[:3, :3] @ derivative[:3] + np.cross(omega, inertia[:3, :3] @ omega)
    expected_force = 2 * (derivative[3:] + np.cross(omega, linear))
    np.testing.assert_allclose(wrench, np.r_[expected_moment, expected_force], atol=1e-12)
    assert wrench @ twist == pytest.approx(twist @ inertia @ derivative)
