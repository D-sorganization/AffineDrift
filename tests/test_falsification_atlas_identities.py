"""Synthetic counterexamples for the atlas; these do not validate human motion."""

import numpy as np
import pytest


@pytest.mark.parametrize("increment,delta_moment", [([7, 0, 0], 0), ([0, 7, 0], -2.8)])
def test_equal_resultant_need_not_preserve_moment(
    increment: list[int], delta_moment: float
) -> None:
    """Recompute both contact moments independently of the increment formula."""
    positions = np.array([[-0.2, 0, 0], [0.2, 0, 0]])
    forces = np.array([[0.0, 10, 0], [0, 5, 0]])
    changed = forces + np.array([increment, -np.array(increment)])
    np.testing.assert_allclose(changed.sum(axis=0), forces.sum(axis=0))
    moment = np.cross(positions, forces).sum(axis=0)
    changed_moment = np.cross(positions, changed).sum(axis=0)
    np.testing.assert_allclose(changed_moment - moment, [0, 0, delta_moment])


def test_internal_load_pair_has_zero_rigid_body_power() -> None:
    """Contact power equals wrench power, including a nonzero internal load."""
    positions = np.array([[-0.2, 0, 0], [0.2, 0, 0]])
    forces = np.array([[0.0, 10, 0], [0, 5, 0]])
    velocity = np.array([1.5, -2, 3])
    omega = np.array([0.5, 1, -1.5])
    contact_velocities = velocity + np.cross(omega, positions)
    contact_power = np.sum(forces * contact_velocities)
    wrench_power = forces.sum(axis=0) @ velocity + np.cross(positions, forces).sum(axis=0) @ omega
    assert contact_power == pytest.approx(wrench_power)
    internal_forces = np.array([[12, 0, 0], [-12, 0, 0]])
    assert np.linalg.norm(internal_forces) > 0
    assert np.sum(internal_forces * contact_velocities) == pytest.approx(0)
    # Contact loads are not an estimate of metabolic cost or muscle effort.


@pytest.mark.parametrize("scale", [np.diag([2.0, 1]), np.array([[2.0, 1], [0, 1]])])
def test_covector_metric_preserves_least_squares_fit(scale: np.ndarray) -> None:
    """Include a shear so transpose-order errors cannot hide in diagonal scaling."""
    jacobian_transpose = np.array([[1.0], [1]])
    torque = np.array([1.0, 0])
    transformed_map = scale.T @ jacobian_transpose
    transformed_torque = scale.T @ torque
    fit = np.linalg.lstsq(jacobian_transpose, torque, rcond=None)[0]
    unweighted = np.linalg.lstsq(transformed_map, transformed_torque, rcond=None)[0]
    assert fit.item() == pytest.approx(0.5)
    assert unweighted.item() != pytest.approx(fit.item())
    if np.array_equal(scale, np.diag([2.0, 1])):
        assert unweighted.item() == pytest.approx(0.8)
    inverse = np.linalg.inv(scale)
    metric = inverse @ inverse.T
    weighted = np.linalg.solve(
        transformed_map.T @ metric @ transformed_map,
        transformed_map.T @ metric @ transformed_torque,
    )
    np.testing.assert_allclose(weighted, fit)
    velocity_z = np.array([1.5, -2.5])
    assert torque @ (scale @ velocity_z) == pytest.approx(transformed_torque @ velocity_z)


@pytest.mark.parametrize("velocity", [-1.2, 1.2])
def test_equal_spring_energy_allows_opposite_energy_flow(velocity: float) -> None:
    """A finite difference checks the energy rate rather than repeating its formula."""
    stiffness, displacement, step = 50.0, 0.25, 1e-5
    energy = 0.5 * stiffness * displacement**2
    energy_before = 0.5 * stiffness * (displacement - velocity * step) ** 2
    energy_after = 0.5 * stiffness * (displacement + velocity * step) ** 2
    numerical_rate = (energy_after - energy_before) / (2 * step)
    assert energy == pytest.approx(1.5625)
    assert numerical_rate == pytest.approx(stiffness * displacement * velocity)
    assert np.sign(numerical_rate) == np.sign(velocity)
