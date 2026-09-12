"""Independent constructed mechanics checks for the Chapter 16 review (#4369).

These examples verify derivations, not empirical golfer parameters. Source and
rendered-chapter reconciliation remain separate acceptance criteria.
"""

import numpy as np
import pytest
from scipy.optimize import linprog


def test_point_force_and_length_derivative_give_same_signed_torque() -> None:
    angle, radius, tension, step = 0.4, 0.25, 120.0, 1e-6
    anchor = np.array([0.0, 0.1, 0.0])
    angles = angle + np.array([-step, 0, step])
    insertion = radius * np.array([np.cos(angles), np.sin(angles), np.zeros(3)]).T
    lengths = np.linalg.norm(anchor - insertion, axis=1)
    length_derivative = (lengths[2] - lengths[0]) / (2 * step)
    force = tension * (anchor - insertion[1]) / lengths[1]
    physical_moment = np.cross(insertion[1], force)[2]
    assert physical_moment > 0  # Tension shortens this path as flexion increases.
    assert physical_moment == pytest.approx(-tension * length_derivative)
    assert physical_moment != pytest.approx(tension * length_derivative)


def test_nonsymmetric_muscle_rows_and_power_match_declared_anatomy() -> None:
    length_jacobian = np.array([[-0.05, 0], [-0.02, -0.04]])
    tensions, velocity = np.array([500, 300]), np.array([2, -3])
    moment_arms = -length_jacobian.T
    torque = moment_arms @ tensions
    np.testing.assert_allclose(torque, [31, 12])
    np.testing.assert_allclose(moment_arms[:, 0] * tensions[0], [25, 0])
    np.testing.assert_allclose(moment_arms[:, 1] * tensions[1], [6, 12])
    path_rates = length_jacobian @ velocity
    np.testing.assert_allclose(path_rates, [-0.1, 0.08])
    assert torque @ velocity == pytest.approx(26)
    assert torque @ velocity == pytest.approx(-tensions @ path_rates)


def test_biarticular_joint_powers_can_cancel_or_sum_to_absorption() -> None:
    moment_arms, tension = np.array([0.02, 0.04]), 300.0
    torque = moment_arms * tension
    transfer_powers = torque * [2, -1]
    np.testing.assert_allclose(transfer_powers, [12, -12])
    assert sum(transfer_powers) == pytest.approx(0)
    absorption_powers = torque * [2, -3]
    assert sum(absorption_powers) == pytest.approx(-24)
    assert -moment_arms @ np.array([2, -3]) == pytest.approx(0.08)


def test_nullspace_family_requires_nonnegative_capacity_bounds() -> None:
    moment_arms = np.array([[0.04, 0.02, -0.03], [0, 0.03, 0.02]])
    original, direction = np.array([100, 200, 50]), np.array([13, -8, 12])
    capacity = np.array([400, 300, 250])
    np.testing.assert_allclose(moment_arms @ direction, 0, atol=1e-15)
    for scale in [-25 / 6, 0, 10, 50 / 3]:
        forces = original + scale * direction
        assert np.all(forces >= -1e-12) and np.all(forces <= capacity + 1e-12)
        np.testing.assert_allclose(moment_arms @ forces, [6.5, 7])
    for scale in [-5, 20]:
        forces = original + scale * direction
        np.testing.assert_allclose(moment_arms @ forces, [6.5, 7])
        assert np.any(forces < 0) or np.any(forces > capacity)


def test_coordinatewise_torque_limits_do_not_define_joint_feasibility() -> None:
    moment_arms = np.array([[0.04, 0.02, -0.03], [0, 0.03, 0.02]])
    capacity = np.array([400, 300, 250])
    bounds = list(zip(np.zeros(3), capacity, strict=True))
    maxima = [-linprog(-row, bounds=bounds, method="highs").fun for row in moment_arms]
    np.testing.assert_allclose(maxima, [22, 14])
    simultaneous = linprog(
        np.zeros(3), A_eq=moment_arms, b_eq=maxima, bounds=bounds, method="highs"
    )
    assert simultaneous.status == 2  # Infeasible, not merely solver nonconvergence.
    feasible = linprog(np.zeros(3), A_eq=moment_arms, b_eq=[6.5, 7], bounds=bounds, method="highs")
    assert feasible.success
    np.testing.assert_allclose(moment_arms @ feasible.x, [6.5, 7])


def test_coupled_coordinate_preserves_work_but_changes_effective_moment() -> None:
    length_jacobian = np.array([[-0.05, 0], [-0.02, -0.04]])
    coupling, tensions = np.array([1, 2]), np.array([500, 300])
    original_torque = -length_jacobian.T @ tensions
    reduced_moment_arms = -(length_jacobian @ coupling)
    np.testing.assert_allclose(reduced_moment_arms, [0.05, 0.1])
    reduced_torque = reduced_moment_arms @ tensions
    assert reduced_torque == pytest.approx(55)
    assert reduced_torque == pytest.approx(original_torque @ coupling)
    assert reduced_torque != pytest.approx(original_torque[0])


def test_independently_fitted_moment_arms_can_violate_path_integrability() -> None:
    # r(q)=(.02+.01*q2, .01) cannot be minus the gradient of one smooth length.
    corners = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
    midpoints = (corners[1:] + corners[:-1]) / 2
    moment_arms = np.column_stack([0.02 + 0.01 * midpoints[:, 1], np.full(4, 0.01)])
    work_at_constant_tension = 100 * np.sum(moment_arms * np.diff(corners, axis=0))
    assert work_at_constant_tension == pytest.approx(-1)
    # A workless path returning to its initial length at fixed tension has zero work.
    assert work_at_constant_tension != pytest.approx(0)


def test_positive_tendon_stiffness_does_not_guarantee_joint_stability() -> None:
    # A taut spring joins a fixed anchor to a rotating point on the opposite side.
    anchor_radius, insertion_radius, stiffness, slack = 0.1, 0.2, 1000.0, 0.2
    step = 1e-4
    angles = np.pi + np.array([-step, 0, step])
    lengths = np.sqrt(
        anchor_radius**2
        + insertion_radius**2
        - 2 * anchor_radius * insertion_radius * np.cos(angles)
    )
    energies = 0.5 * stiffness * (lengths - slack) ** 2
    finite_joint_stiffness = (energies[2] - 2 * energies[1] + energies[0]) / step**2
    tension = stiffness * (lengths[1] - slack)
    length_curvature = -anchor_radius * insertion_radius / lengths[1]
    # The length derivative vanishes at pi, leaving only the geometric term.
    assert tension == pytest.approx(100)
    assert finite_joint_stiffness == pytest.approx(tension * length_curvature, rel=1e-6)
    assert finite_joint_stiffness == pytest.approx(-20 / 3, rel=1e-6)
    assert energies[1] > max(energies[0], energies[2])
