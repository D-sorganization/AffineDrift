"""Property tests for the ch08 golf model.

Issue #3518 found that chapter 8's printed mass matrix did not follow from its
own formulas, that the assembled blocks were not positive definite, and that the
resulting indefinite Schur complement was explained as a "kinematic
singularity". These tests assert the properties that make the explanation
impossible, so the same class of error cannot recur silently.
"""

from __future__ import annotations

import numpy as np
import pytest

from scripts.generate_worked_examples import CH08_CONFIGURATION_DEGREES, CH08_VELOCITY
from src.affine_control.golf_model import SEGMENTS, GolfModel

# A coarse shaft quadrature keeps the sweeps fast; the blocks converge well
# before this resolution.
SAMPLES = 401

CONFIGURATIONS = [
    np.deg2rad(np.array(CH08_CONFIGURATION_DEGREES)),
    np.zeros(3),
    np.deg2rad(np.array([120.0, -80.0, -60.0])),
    np.deg2rad(np.array([-45.0, 90.0, 30.0])),
    np.array([np.pi, -np.pi / 2, np.pi / 3]),
]


@pytest.mark.parametrize("q", CONFIGURATIONS)
def test_rigid_mass_matrix_is_symmetric_positive_definite(q: np.ndarray) -> None:
    matrix = SEGMENTS.rigid_mass_matrix(q)
    np.testing.assert_allclose(matrix, matrix.T, atol=1e-12)
    assert np.min(np.linalg.eigvalsh(matrix)) > 0.0


@pytest.mark.parametrize("q", CONFIGURATIONS)
def test_full_mass_matrix_is_positive_definite(q: np.ndarray) -> None:
    """The property the published blocks violated."""
    matrix = SEGMENTS.full_mass_matrix(q, samples=SAMPLES)
    assert np.min(np.linalg.eigvalsh(matrix)) > 0.0


@pytest.mark.parametrize("q", CONFIGURATIONS)
def test_schur_complement_is_positive_definite(q: np.ndarray) -> None:
    """Equivalent to the full matrix being positive definite, since M_etaeta is."""
    schur = SEGMENTS.schur_complement(q, samples=SAMPLES)
    assert np.min(np.linalg.eigvalsh(schur)) > 0.0


@pytest.mark.parametrize("q", CONFIGURATIONS)
def test_schur_equivalence_holds_both_ways(q: np.ndarray) -> None:
    """eq:ch8:schur-iff -- the statement that makes the old explanation impossible."""
    full = SEGMENTS.full_mass_matrix(q, samples=SAMPLES)
    schur = SEGMENTS.schur_complement(q, samples=SAMPLES)
    assert (np.min(np.linalg.eigvalsh(full)) > 0) == (np.min(np.linalg.eigvalsh(schur)) > 0)


def test_positive_definite_across_a_random_sweep() -> None:
    """No configuration anywhere makes the inertia indefinite. That is the point."""
    rng = np.random.default_rng(3)
    worst = np.inf
    for _ in range(300):
        q = rng.uniform(-np.pi, np.pi, 3)
        worst = min(worst, np.min(np.linalg.eigvalsh(SEGMENTS.full_mass_matrix(q, SAMPLES))))
    assert worst > 0.0


@pytest.mark.parametrize("q", CONFIGURATIONS)
def test_kinetic_energy_is_positive_for_every_velocity(q: np.ndarray) -> None:
    """The physical content of positive definiteness."""
    matrix = SEGMENTS.full_mass_matrix(q, samples=SAMPLES)
    rng = np.random.default_rng(5)
    for _ in range(50):
        velocity = rng.normal(size=5)
        assert velocity @ matrix @ velocity > 0.0


def test_m33_matches_its_closed_form() -> None:
    """The entry the published matrix got wrong: I3 + m3 l3^2 / 4, i.e. 0.12 not 0.18."""
    q = np.deg2rad(np.array(CH08_CONFIGURATION_DEGREES))
    inertia = SEGMENTS.inertias[2]
    mass = SEGMENTS.lengths[2]
    expected = inertia + SEGMENTS.masses[2] * mass**2 / 4
    assert SEGMENTS.rigid_mass_matrix(q)[2, 2] == pytest.approx(expected, abs=1e-12)
    assert expected == pytest.approx(0.12, abs=1e-9)


def test_modal_mass_matrix_is_diagonal() -> None:
    """Clamped-free bending modes are orthogonal, so the coupling vanishes."""
    _, modal = SEGMENTS.shaft_blocks(np.zeros(3), samples=8001)
    assert abs(modal[0, 1]) < 1e-6 * modal[0, 0]


@pytest.mark.parametrize("q", CONFIGURATIONS)
def test_coriolis_preserves_skew_symmetry(q: np.ndarray) -> None:
    """Mdot - 2C skew-symmetric, so the rigid block conserves energy unforced."""
    qd = np.array([0.7, -1.1, 1.9])
    step = 1e-6
    mdot = np.zeros((3, 3))
    for k in range(3):
        forward, backward = q.copy(), q.copy()
        forward[k] += step
        backward[k] -= step
        derivative = SEGMENTS.rigid_mass_matrix(forward) - SEGMENTS.rigid_mass_matrix(backward)
        mdot += derivative / (2 * step) * qd[k]
    residual = mdot - 2.0 * SEGMENTS.coriolis(q, qd)
    np.testing.assert_allclose(residual, -residual.T, atol=1e-6)


def test_gravity_torque_matches_the_potential_gradient() -> None:
    """Independent check: work done against gravity over a small displacement."""
    q = np.deg2rad(np.array(CH08_CONFIGURATION_DEGREES))
    direction = np.array([0.3, -0.5, 0.8])
    step = 1e-6
    numeric = (
        SEGMENTS.potential_energy(q + step * direction)
        - SEGMENTS.potential_energy(q - step * direction)
    ) / (2 * step)
    assert SEGMENTS.gravity_torque(q) @ direction == pytest.approx(numeric, rel=1e-5)


def test_published_velocities_are_physically_plausible() -> None:
    """Peak segment rates in a real downswing are tens, not hundreds, of rad/s."""
    assert max(abs(v) for v in CH08_VELOCITY) < 40.0
    # The wrist should be the fastest segment, which is what uncocking means.
    assert abs(CH08_VELOCITY[2]) == max(abs(v) for v in CH08_VELOCITY)


def test_alternative_parameters_still_give_a_valid_mass_matrix() -> None:
    """The guarantee is structural, not a property of one parameter set."""
    model = GolfModel(
        masses=(7.5, 3.2, 1.1),
        lengths=(0.32, 0.30, 0.45),
        inertias=(0.19, 0.05, 0.03),
        shaft_mass=0.22,
    )
    rng = np.random.default_rng(9)
    for _ in range(50):
        q = rng.uniform(-np.pi, np.pi, 3)
        assert np.min(np.linalg.eigvalsh(model.full_mass_matrix(q, SAMPLES))) > 0.0
