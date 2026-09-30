"""Independent compatibility, power and impulse controls for Chapter 7."""

from importlib import import_module
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def model():
    return import_module("docs.development.technical-review.build_constraint_forces_figures")


def test_multiplier_matches_independent_saddle_point_solve(model):
    q, velocity = np.deg2rad([45, 70]), np.array([8.0, -8.0])
    mass, bias, gravity = model.operators(q, velocity)
    jacobian = np.array([[1.0, 1.0]])
    force = -bias - gravity
    acceleration, reaction = model.constrained_acceleration(mass, force, jacobian, np.zeros(1))
    kkt = np.block([[mass, -jacobian.T], [jacobian, np.zeros((1, 1))]])
    reference = np.linalg.solve(kkt, np.r_[force, 0.0])
    np.testing.assert_allclose(np.r_[acceleration, reaction], reference, atol=1e-12)
    np.testing.assert_allclose(jacobian @ acceleration, 0, atol=1e-12)
    assert float(reaction @ jacobian @ velocity) == pytest.approx(0, abs=1e-12)


def test_curved_constraint_requires_normal_acceleration(model):
    # Unit circle at (1,0), tangential speed 3: x acceleration is -9.
    acceleration, reaction = model.constrained_acceleration(
        2 * np.eye(2), np.zeros(2), np.array([[1.0, 0.0]]), np.array([9.0])
    )
    np.testing.assert_allclose(acceleration, [-9, 0], atol=1e-12)
    np.testing.assert_allclose(reaction, [-18], atol=1e-12)


def test_constraint_rescaling_preserves_acceleration_and_generalized_load(model):
    mass = np.array([[3.0, 0.4], [0.4, 1.0]])
    force, jacobian, gamma = np.array([2.0, -3.0]), np.array([[1.0, 2.0]]), np.array([0.7])
    acceleration, reaction = model.constrained_acceleration(mass, force, jacobian, gamma)
    scaled_acceleration, scaled_reaction = model.constrained_acceleration(
        mass, force, -5 * jacobian, -5 * gamma
    )
    np.testing.assert_allclose(scaled_acceleration, acceleration, atol=1e-12)
    np.testing.assert_allclose(-5 * jacobian.T @ scaled_reaction, jacobian.T @ reaction)


def test_plastic_engagement_obeys_impulse_momentum_and_exact_energy_loss(model):
    q, before = np.deg2rad([45, 70]), np.array([8.0, 12.0])
    mass = model.operators(q, before)[0]
    jacobian = np.array([[1.0, 1.0]])
    after, impulse = model.plastic_engagement(mass, before, jacobian)
    np.testing.assert_allclose(jacobian @ after, 0, atol=1e-12)
    np.testing.assert_allclose(mass @ (after - before), jacobian.T @ impulse, atol=1e-12)
    loss = 0.5 * (after @ mass @ after - before @ mass @ before)
    schur = jacobian @ np.linalg.solve(mass, jacobian.T)
    expected = -0.5 * (jacobian @ before) @ np.linalg.solve(schur, jacobian @ before)
    assert loss == pytest.approx(float(expected), abs=1e-12)
    assert loss < 0


@pytest.mark.parametrize("velocity", [[8.0, -8.0], [8.0, 12.0], [-2.0, 5.0]])
def test_physical_segment_energies_sum_to_full_mass_matrix_energy(model, velocity):
    q, velocity = np.array([0.4, -0.9]), np.array(velocity)
    mass = model.operators(q, velocity)[0]
    assert sum(model.segment_kinetic(q, velocity)) == pytest.approx(
        0.5 * velocity @ mass @ velocity, abs=1e-12
    )


@pytest.mark.parametrize("mode", ["free", "guide", "lock"])
def test_trajectories_converge_and_conserve_energy(model, mode):
    coarse, fine = model.trajectory(mode, False), model.trajectory(mode, True)
    np.testing.assert_allclose(coarse, fine, atol=1e-9)
    energy = np.array([model.total_energy(row[:2], row[2:]) for row in fine])
    assert np.ptp(energy) < 1e-9
    if mode == "guide":
        np.testing.assert_allclose(fine[:, :2].sum(axis=1), np.deg2rad(115), atol=1e-12)
        np.testing.assert_allclose(fine[:, 2:].sum(axis=1), 0, atol=1e-12)
    if mode == "lock":
        np.testing.assert_allclose(fine[:, 1], np.deg2rad(70), atol=1e-12)
        np.testing.assert_allclose(fine[:, 3], 0, atol=1e-12)


def test_moving_boundary_power_has_the_declared_sign(model):
    mass, force, jacobian = np.eye(1), np.array([3.0]), np.ones((1, 1))
    _, reaction = model.constrained_acceleration(mass, force, jacobian, np.array([-2.0]))
    # Constraint q-t^2=0 at t=1: v=2, Phi_t=-2, gamma=-2.
    assert float(reaction[0] * 2) == pytest.approx(-2.0)


def test_input_changes_constraint_reaction_and_allowed_acceleration(model):
    mass, bias, gravity = model.operators(np.deg2rad([45, 70]), np.array([8.0, -8.0]))
    jacobian, gamma = np.array([[1.0, 1.0]]), np.zeros(1)
    base, reaction = model.constrained_acceleration(mass, -bias - gravity, jacobian, gamma)
    changed, changed_reaction = model.constrained_acceleration(
        mass, np.array([1.0, 0.0]) - bias - gravity, jacobian, gamma
    )
    assert not np.allclose(changed_reaction, reaction)
    assert not np.allclose(changed, base)
    np.testing.assert_allclose(jacobian @ changed, 0, atol=1e-12)


def test_wrench_reference_point_shift_preserves_power():
    force, moment = np.array([3.0, -2.0, 7.0]), np.array([4.0, 1.0, -3.0])
    velocity, omega = np.array([1.0, 4.0, -2.0]), np.array([-2.0, 5.0, 1.0])
    offset = np.array([0.2, -0.3, 0.5])
    old_power = force @ velocity + moment @ omega
    new_power = (
        force @ (velocity + np.cross(omega, offset)) + (moment - np.cross(offset, force)) @ omega
    )
    assert new_power == pytest.approx(old_power, abs=1e-12)


def test_guide_moment_and_hinge_force_close_physical_body_balances(model):
    q, velocity = np.deg2rad([45, 70]), np.array([8.0, -8.0])
    mass, bias, gravity = model.operators(q, velocity)
    acceleration, reaction = model.constrained_acceleration(
        mass, -bias - gravity, np.array([[1.0, 1.0]]), np.zeros(1)
    )
    tangent = np.array([np.cos(q[0]), np.sin(q[0])])
    radial = np.array([np.sin(q[0]), -np.cos(q[0])])
    distal_radial = np.array([np.sin(q.sum()), -np.cos(q.sum())])
    com_acceleration = 0.35 * (acceleration[0] * tangent - velocity[0] ** 2 * radial)
    force = 0.4 * (com_acceleration - np.array([0.0, -model.AFFINE.GRAVITY_M_S2]))
    lever = 0.5 * distal_radial
    moment_of_force = lever[0] * force[1] - lever[1] * force[0]
    assert reaction[0] == pytest.approx(moment_of_force, abs=1e-12)
    hinge_power = force @ (0.35 * velocity[0] * tangent)

    def body_energy(q_value, v_value):
        potential = (
            -0.4
            * model.AFFINE.GRAVITY_M_S2
            * (0.35 * np.cos(q_value[0]) + 0.5 * np.cos(q_value.sum()))
        )
        return model.segment_kinetic(q_value, v_value)[1] + potential

    step = 1e-6
    derivative = (
        body_energy(q + step * velocity, velocity + step * acceleration)
        - body_energy(q - step * velocity, velocity - step * acceleration)
    ) / (2 * step)
    assert derivative == pytest.approx(hinge_power, abs=1e-7)
    assert not np.isclose(hinge_power, reaction[0] * velocity[1])


@pytest.mark.parametrize(
    "edition", ["chapters/ch07_constraint_forces.tex", "quarto/ch07_constraint_forces.qmd"]
)
def test_both_editions_preserve_scientific_boundaries(edition):
    text = (Path(__file__).parents[1] / "articles/The_Physics_of_Golf" / edition).read_text(
        encoding="utf-8"
    )
    for phrase in (
        "Positive power adds mechanical energy",
        "not a locked wrist",
        "mass metric",
        "25.23860043",
        "944.8",
        "6. Account for Energy During Capture",
        "not a typical golfer value",
        "Choi2020GripKinetics",
        "OpenSimJointReactions2019",
    ):
        assert phrase in text
    for phrase in (
        "muscles are too weak",
        "downswing is passive—gravity and Coriolis drive acceleration",
        "forces that are model-independent",
        "positive work (removing",
        "inward centrifugal acceleration",
        "0.265",
    ):
        assert phrase not in text
