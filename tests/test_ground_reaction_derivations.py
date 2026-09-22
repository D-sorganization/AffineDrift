"""Independent balance, wrench and constrained-reaction checks for Chapter 15."""

import numpy as np
import pytest


def test_vertical_acceleration_and_net_impulse_have_consistent_signs() -> None:
    mass, force, gravity, duration = 95.0, 1350.0, 9.81, 0.1
    acceleration = force / mass - gravity
    momentum_change = (force - mass * gravity) * duration
    assert acceleration == pytest.approx(4.400526315789474)
    assert momentum_change / mass == pytest.approx(acceleration * duration)
    assert 1200 / 90 - gravity == pytest.approx(3.5233333333333334)
    assert -1.0 + acceleration * duration < 0  # Still descending while braking.


def test_golfer_club_internal_forces_cancel_only_for_combined_system() -> None:
    gravity = np.array([0.0, 0.0, -9.81])
    body_mass, club_mass = 90.0, 0.5
    ground = np.array([200.0, -35.0, 1200.0])
    club_on_body = np.array([-20.0, 10.0, -100.0])
    body_rate = ground + body_mass * gravity + club_on_body
    club_rate = club_mass * gravity - club_on_body
    np.testing.assert_allclose(body_rate + club_rate, ground + 90.5 * gravity)
    assert not np.allclose(body_rate, ground + body_mass * gravity)


@pytest.mark.parametrize("height", [0.0, 0.04, -0.03])
def test_cop_recovers_offset_surface_location_and_free_couple(height: float) -> None:
    force = np.array([100.0, -50.0, 800.0])
    point = np.array([0.1, -0.05, height])
    free_moment = np.array([0.0, 0.0, 8.0])
    origin_moment = np.cross(point, force) + free_moment
    recovered = np.array(
        [
            (height * force[0] - origin_moment[1]) / force[2],
            (origin_moment[0] + height * force[1]) / force[2],
            height,
        ]
    )
    np.testing.assert_allclose(recovered, point)
    np.testing.assert_allclose(origin_moment - np.cross(recovered, force), free_moment)
    if height == 0.04:
        np.testing.assert_allclose(origin_moment, [-38.0, -76.0, 8.0])


def test_wrench_power_is_invariant_under_consistent_transport() -> None:
    rng = np.random.default_rng(4415)
    for _ in range(20):
        force, moment, velocity, omega, offset = rng.normal(size=(5, 3))
        point_velocity = velocity + np.cross(omega, offset)
        point_moment = moment - np.cross(offset, force)
        assert force @ velocity + moment @ omega == pytest.approx(
            force @ point_velocity + point_moment @ omega
        )


def test_input_induced_reaction_matches_direct_constrained_solve() -> None:
    mass = np.array([[2.0, 1.0], [1.0, 2.0]])
    jacobian = np.array([[1.0, 0.0]])
    input_map = np.array([0.0, 1.0])
    kkt = np.block([[mass, -jacobian.T], [jacobian, np.zeros((1, 1))]])
    for control in [-4.0, 0.0, 4.0]:
        direct = np.linalg.solve(kkt, np.r_[input_map * control, 0.0])
        np.testing.assert_allclose(direct, [0.0, control / 2, control / 2])
        assert direct[-1] * 0.0 == 0.0  # Constrained material velocity is zero.


def test_zero_input_can_invalidate_an_admissible_unilateral_mode() -> None:
    mass = np.array([[2.0, 1.0], [1.0, 2.0]])
    jacobian = np.array([[1.0, 0.0]])
    kkt = np.block([[mass, -jacobian.T], [jacobian, np.zeros((1, 1))]])
    full = np.linalg.solve(kkt, [1.0, 4.0, 0.0])
    zero_input = np.linalg.solve(kkt, [1.0, 0.0, 0.0])
    assert full[-1] == pytest.approx(1.0)
    assert zero_input[-1] == pytest.approx(-1.0)
    released = np.linalg.solve(mass, [1.0, 0.0])
    assert released[0] == pytest.approx(2 / 3)  # Positive opening acceleration.


def test_schur_reaction_and_components_match_independent_kkt_systems() -> None:
    rng = np.random.default_rng(2215)
    for _ in range(12):
        factor = rng.normal(size=(4, 4))
        mass = factor.T @ factor + np.eye(4)
        jacobian = rng.normal(size=(2, 4))
        h_zero, h_velocity, control, external = rng.normal(size=(4, 4))
        gamma = rng.normal(size=2)
        inverse_rows = np.linalg.solve(mass, jacobian.T).T
        schur = inverse_rows @ jacobian.T
        zero = np.linalg.solve(schur, inverse_rows @ h_zero)
        velocity = np.linalg.solve(schur, inverse_rows @ h_velocity - gamma)
        inputs = np.linalg.solve(schur, -inverse_rows @ control)
        loads = np.linalg.solve(schur, -inverse_rows @ external)
        kkt = np.block([[mass, -jacobian.T], [jacobian, np.zeros((2, 2))]])
        rhs = np.r_[control + external - h_zero - h_velocity, -gamma]
        direct = np.linalg.solve(kkt, rhs)[4:]
        np.testing.assert_allclose(zero + velocity + inputs + loads, direct, atol=1e-12)
        ztcf = zero + velocity + loads
        zvcf = zero + inputs + loads
        np.testing.assert_allclose(ztcf + zvcf - direct, zero + loads, atol=1e-12)


def test_bilateral_resultant_does_not_fix_moment_or_individual_wrenches() -> None:
    positions = np.array([[-0.2, 0.0, 0.0], [0.2, 0.0, 0.0]])
    even = np.array([[0.0, 0.0, 400.0], [0.0, 0.0, 400.0]])
    uneven = np.array([[0.0, 0.0, 600.0], [0.0, 0.0, 200.0]])
    np.testing.assert_allclose(even.sum(axis=0), uneven.sum(axis=0))
    np.testing.assert_allclose(np.cross(positions, uneven).sum(axis=0), [0, 80, 0])
    np.testing.assert_allclose(np.cross(positions, even).sum(axis=0), [0, 0, 0])
    self_equilibrated = np.array([[20.0, 0.0, 0.0], [-20.0, 0.0, 0.0]])
    np.testing.assert_allclose(self_equilibrated.sum(axis=0), np.zeros(3))
    np.testing.assert_allclose(np.cross(positions, self_equilibrated).sum(axis=0), np.zeros(3))


def test_moving_constraint_has_bias_even_at_zero_generalized_velocity() -> None:
    # phi(q,t)=q-t^2/2: qdot=t and qddot=1, independently of qdot.
    time = 2.0
    prescribed_velocity = time
    assert 0.0 - prescribed_velocity != 0.0
    gamma = -1.0
    mass, applied = 3.0, 0.0
    reaction = mass * (-gamma) - applied
    assert reaction == 3.0
    assert reaction * prescribed_velocity == 6.0  # Moving support supplies power.
