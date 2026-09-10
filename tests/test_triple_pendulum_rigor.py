"""Independent mechanics and source controls for the complete three-link chapter."""

import runpy
from pathlib import Path

import numpy as np
import pytest

from src.affine_control.dynamics import christoffel_coriolis

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "articles/The_Physics_of_Golf"


@pytest.fixture(scope="module")
def examples() -> dict:
    return runpy.run_path(
        str(ROOT / "docs/development/technical-review/build_triple_pendulum_figures.py")
    )


def explicit_mass(q: np.ndarray) -> np.ndarray:
    """Closed entries independent of the production COM-Jacobian assembly."""
    a, b, d = 0.03925, 0.054, 0.02
    e, f = 0.015, 0.0225
    x, y, z = np.cos(q[1]), np.cos(q[1] + q[2]), np.cos(q[2])
    m22 = a + f + 2 * e * z
    m11 = 0.242 + m22 + 2 * b * x + 2 * d * y
    m12 = m22 + b * x + d * y
    m13 = f + d * y + e * z
    return np.array([[m11, m12, m13], [m12, m22, f + e * z], [m13, f + e * z, f]])


def test_mass_entries_match_com_assembly_and_remain_positive(examples: dict) -> None:
    model = examples["MODEL"]
    for q in np.random.default_rng(4345).uniform(-np.pi, np.pi, (20, 3)):
        mass = model.rigid_mass_matrix(examples["horizontal_angles"](q))
        np.testing.assert_allclose(mass, explicit_mass(q), atol=2e-16)
        assert np.linalg.eigvalsh(mass).min() > 0
    old = np.array([[0.5, 0.15, 0.1], [0.15, 0.08, 0.05], [0.1, 0.05, 0.02]])
    assert np.linalg.eigvalsh(old).min() < 0


def test_newton_euler_matches_christoffel_bias(examples: dict) -> None:
    q = np.deg2rad([50.0, 80.0, 100.0])
    velocity = np.array([12.0, 20.0, 25.0])
    horizontal = examples["horizontal_angles"](q)
    chain = examples["CHAIN"]
    bias = chain.inverse_dynamics(horizontal, velocity, np.zeros(3), gravity=0.0)
    christoffel = christoffel_coriolis(explicit_mass, q, velocity) @ velocity
    np.testing.assert_allclose(bias, christoffel, rtol=1e-8, atol=1e-7)
    c3 = 0.02 * np.sin(q[1] + q[2]) * velocity[0] ** 2
    c3 += 0.015 * np.sin(q[2]) * (velocity[0] + velocity[1]) ** 2
    assert bias[2] == pytest.approx(c3)


def test_zero_false_derivative_and_energy_identity(examples: dict) -> None:
    q = np.deg2rad([50.0, 90.0, 100.0])
    velocity = np.array([15.0, 20.0, 30.0])
    step = 1e-6
    delta = np.array([0.0, step, 0.0])
    assert (explicit_mass(q + delta)[1, 2] - explicit_mass(q - delta)[1, 2]) == 0
    mdot = (explicit_mass(q + step * velocity) - explicit_mass(q - step * velocity)) / (2 * step)
    bias = examples["CHAIN"].inverse_dynamics(
        examples["horizontal_angles"](q), velocity, np.zeros(3), gravity=0.0
    )
    assert velocity @ bias == pytest.approx(0.5 * velocity @ mdot @ velocity, rel=1e-8)


def test_constraint_release_preserves_state_and_changes_acceleration(examples: dict) -> None:
    q = np.deg2rad([50.0, 80.0, 100.0])
    velocity = np.array([12.0, 20.0, 0.0])
    locked, free, reaction = examples["release_accelerations"](q, velocity)
    assert locked[2] == pytest.approx(0, abs=1e-12)
    assert abs(free[2]) > 1
    mass = explicit_mass(q)
    np.testing.assert_allclose(mass @ (locked - free), [0, 0, reaction], atol=1e-12)
    assert reaction * velocity[2] == 0


def test_segment_energy_equals_generalized_energy(examples: dict) -> None:
    q = np.deg2rad([50.0, 80.0, 100.0])
    velocity = np.array([12.0, 20.0, 25.0])
    segments = examples["segment_energies"](q, velocity)
    assert sum(segments) == pytest.approx(0.5 * velocity @ explicit_mass(q) @ velocity)
    incorrect = 0.5 * np.array([0.05, 0.01, 0.01]) * velocity**2
    assert not np.allclose(segments, incorrect)


def test_trajectory_converges_and_conserves_energy(examples: dict) -> None:
    solution = examples["trajectory"]()
    refined = examples["trajectory"](refined=True)
    assert solution.success and refined.success
    np.testing.assert_allclose(solution.y, refined.y, rtol=0, atol=2e-8)
    energy = np.array([examples["total_energy"](state) for state in solution.y.T])
    assert np.ptp(energy) < 1e-7
    # The example must integrate radians; even the first derivative moves
    # q1 about 0.6 radians in 50 ms, not 0.6 degrees.
    assert abs(solution.y[0, -1] - solution.y[0, 0]) > 0.1


@pytest.mark.parametrize(
    "edition", ["chapters/ch08_triple_pendulum.tex", "quarto/ch08_triple_pendulum.qmd"]
)
def test_editions_require_energy_and_inference_boundaries(edition: str) -> None:
    text = (CHAPTER / edition).read_text(encoding="utf-8")
    for phrase in ("Christoffel", "Schur", "manufactured", "no impulse", "active wrist torque"):
        assert phrase in text
    for obsolete in ("minimum model needed", "800--1000", "800–1000", "DCR = 50", "q_2 + q_3 = "):
        assert obsolete not in text
