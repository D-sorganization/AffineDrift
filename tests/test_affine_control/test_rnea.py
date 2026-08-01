"""Tests for the planar RNEA (#3518).

The published worked example omitted its arithmetic and then stated an answer
prefaced by "might be". These tests check the recursion against an independent
Lagrangian computation and against cases whose answers are known in closed form,
so the numbers the chapter prints are backed by something.
"""

from __future__ import annotations

import numpy as np
import pytest

from scripts.generate_worked_examples import (
    VOL0_CH07_CHAIN,
    VOL0_CH07_Q,
    VOL0_CH07_QD,
    VOL0_CH07_QDD,
    VOL0_RNEA_TOLERANCE,
)
from src.affine_control.rnea import GRAVITY_M_S2, PlanarChain, PlanarLink

CHAINS = {
    "book_3link": VOL0_CH07_CHAIN,
    "uniform_2link": PlanarChain(
        (
            PlanarLink(mass=1.0, length=1.0, com_offset=0.5, inertia=1.0 / 12.0),
            PlanarLink(mass=1.0, length=1.0, com_offset=0.5, inertia=1.0 / 12.0),
        )
    ),
    "single_rod": PlanarChain((PlanarLink(mass=2.0, length=0.7, com_offset=0.35, inertia=0.08),)),
}


def random_state(size: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    return (
        rng.uniform(-np.pi, np.pi, size),
        rng.uniform(-3.0, 3.0, size),
        rng.uniform(-5.0, 5.0, size),
    )


@pytest.mark.parametrize("name", sorted(CHAINS))
def test_recursion_matches_the_lagrangian_route(name: str) -> None:
    """The chapter's own validation, executed.

    The two routes share no machinery: one propagates accelerations outward and
    forces inward without ever forming a mass matrix; the other assembles M from
    Jacobians and differentiates it for the Coriolis term.
    """
    chain = CHAINS[name]
    for seed in range(5):
        q, qd, qdd = random_state(chain.size, seed)
        recursive = chain.inverse_dynamics(q, qd, qdd)
        lagrangian = chain.inverse_dynamics_lagrangian(q, qd, qdd)
        np.testing.assert_allclose(recursive, lagrangian, atol=1e-6)


def test_single_rod_matches_the_closed_form() -> None:
    """One link: tau = (I + m c^2) qddot + m g c cos(q). Known exactly."""
    link = PlanarLink(mass=2.0, length=0.7, com_offset=0.35, inertia=0.08)
    chain = PlanarChain((link,))
    for angle in (0.0, 0.3, -1.2, np.pi / 2):
        for accel in (0.0, 1.5, -2.0):
            q = np.array([angle])
            expected = (link.inertia + link.mass * link.com_offset**2) * accel + (
                link.mass * GRAVITY_M_S2 * link.com_offset * np.cos(angle)
            )
            torque = chain.inverse_dynamics(q, np.array([0.0]), np.array([accel]))
            assert torque[0] == pytest.approx(expected, rel=1e-9)


def test_single_rod_torque_is_independent_of_velocity() -> None:
    """A single link has no Coriolis term -- nothing for it to couple to."""
    chain = CHAINS["single_rod"]
    q = np.array([0.4])
    qdd = np.array([1.0])
    baseline = chain.inverse_dynamics(q, np.array([0.0]), qdd)
    for rate in (1.0, -5.0, 12.0):
        assert chain.inverse_dynamics(q, np.array([rate]), qdd) == pytest.approx(baseline)


@pytest.mark.parametrize("name", sorted(CHAINS))
def test_torque_is_affine_in_acceleration(name: str) -> None:
    """tau(qddot) - tau(0) must be linear: it is M qddot."""
    chain = CHAINS[name]
    q, qd, qdd = random_state(chain.size, 11)
    bias = chain.inverse_dynamics(q, qd, np.zeros(chain.size))
    single = chain.inverse_dynamics(q, qd, qdd) - bias
    doubled = chain.inverse_dynamics(q, qd, 2.0 * qdd) - bias
    np.testing.assert_allclose(doubled, 2.0 * single, atol=1e-6)


@pytest.mark.parametrize("name", sorted(CHAINS))
def test_acceleration_term_is_the_mass_matrix(name: str) -> None:
    chain = CHAINS[name]
    q, qd, qdd = random_state(chain.size, 23)
    bias = chain.inverse_dynamics(q, qd, np.zeros(chain.size))
    response = chain.inverse_dynamics(q, qd, qdd) - bias
    np.testing.assert_allclose(response, chain.mass_matrix(q) @ qdd, atol=1e-6)


@pytest.mark.parametrize("name", sorted(CHAINS))
def test_zero_gravity_zero_motion_gives_zero_torque(name: str) -> None:
    chain = CHAINS[name]
    q, _, _ = random_state(chain.size, 5)
    zero = np.zeros(chain.size)
    torque = chain.inverse_dynamics(q, zero, zero, gravity=0.0)
    np.testing.assert_allclose(torque, zero, atol=1e-9)


@pytest.mark.parametrize("name", sorted(CHAINS))
def test_static_torque_equals_the_gravity_gradient(name: str) -> None:
    """At rest, tau must be dV/dq exactly."""
    chain = CHAINS[name]
    q, _, _ = random_state(chain.size, 7)
    zero = np.zeros(chain.size)
    np.testing.assert_allclose(
        chain.inverse_dynamics(q, zero, zero), chain.gravity_torque(q), atol=1e-5
    )


def test_velocity_product_term_vanishes_for_a_planar_chain() -> None:
    """The claim the chapter now makes: V x S qdot is zero, not "(0.1,0,0) approx".

    Both vectors lie along the out-of-plane axis for every link of a planar arm.
    """
    velocity = np.array([0.0, 0.0, 0.5])
    axis_rate = np.array([0.0, 0.0, 0.2])
    np.testing.assert_allclose(np.cross(velocity, axis_rate), np.zeros(3), atol=0.0)


def test_published_agreement_bound_actually_holds() -> None:
    """The chapter publishes a bound rather than the measured residual.

    The residual is a difference of nearly-equal floats, so its exact value is
    machine-dependent -- pinning it made the generated fragment fail the
    freshness gate on CI after passing locally. The bound must therefore be
    enforced rather than observed.
    """
    recursive = VOL0_CH07_CHAIN.inverse_dynamics(VOL0_CH07_Q, VOL0_CH07_QD, VOL0_CH07_QDD)
    lagrangian = VOL0_CH07_CHAIN.inverse_dynamics_lagrangian(
        VOL0_CH07_Q, VOL0_CH07_QD, VOL0_CH07_QDD
    )
    assert np.abs(recursive - lagrangian).max() < VOL0_RNEA_TOLERANCE


def test_published_torques_are_far_from_the_stipulated_ones() -> None:
    """Guards the regression: [2.3, 1.1, 0.08] was not a computed result."""
    computed = VOL0_CH07_CHAIN.inverse_dynamics(VOL0_CH07_Q, VOL0_CH07_QD, VOL0_CH07_QDD)
    stipulated = np.array([2.3, 1.1, 0.08])
    assert abs(computed[0] - stipulated[0]) > 5.0
    assert computed[0] / stipulated[0] > 4.0


def test_mass_matrix_is_symmetric_positive_definite() -> None:
    for chain in CHAINS.values():
        q, _, _ = random_state(chain.size, 3)
        mass = chain.mass_matrix(q)
        np.testing.assert_allclose(mass, mass.T, atol=1e-12)
        assert np.min(np.linalg.eigvalsh(mass)) > 0.0
