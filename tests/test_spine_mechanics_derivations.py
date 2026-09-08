"""Independent checks of the spine chapter's worked mechanical examples."""

import numpy as np
import pytest
import sympy as sp
from scipy.spatial.transform import Rotation

from src.core.constants import GRAVITY_M_S2


def test_euler_rate_map_matches_a_differentiated_rotation_and_power() -> None:
    """Differentiate SciPy's extrinsic rotation, independently of the rate map."""
    angles = np.array([0.3, -0.4, 0.7])  # gamma, beta, alpha
    rates = np.array([0.6, -0.8, 1.1])
    step = 1e-6
    rotation = Rotation.from_euler("xyz", angles).as_matrix()
    derivative = (
        Rotation.from_euler("xyz", angles + step * rates).as_matrix()
        - Rotation.from_euler("xyz", angles - step * rates).as_matrix()
    ) / (2 * step)
    skew = rotation.T @ derivative
    omega = np.array([skew[2, 1], skew[0, 2], skew[1, 0]])
    gamma, beta, _ = angles
    rate_map = np.array(
        [
            [1, 0, -np.sin(beta)],
            [0, np.cos(gamma), np.sin(gamma) * np.cos(beta)],
            [0, -np.sin(gamma), np.cos(gamma) * np.cos(beta)],
        ]
    )
    np.testing.assert_allclose(rate_map @ rates, omega, atol=2e-10)
    moment = np.array([2.0, -3.0, 4.0])
    assert (rate_map.T @ moment) @ rates == pytest.approx(moment @ omega, abs=1e-9)
    assert np.linalg.det(rate_map) == pytest.approx(np.cos(beta))


def test_tilted_spin_and_noncommuting_rotation_examples() -> None:
    """Use rotation actions to check axis projection and finite composition."""
    tilt = Rotation.from_euler("y", 30, degrees=True)
    local = tilt.inv().apply([0, 0, 4])
    np.testing.assert_allclose(local, [-2, 0, 2 * np.sqrt(3)], atol=1e-14)
    assert np.linalg.norm(local) == pytest.approx(4)
    around_x = Rotation.from_euler("x", 30, degrees=True)
    around_y = Rotation.from_euler("y", 20, degrees=True)
    forward = (around_x * around_y).apply([0, 0, 1])
    reverse = (around_y * around_x).apply([0, 0, 1])
    np.testing.assert_allclose(forward, [0.3420201433, -0.4698463104, 0.8137976813])
    np.testing.assert_allclose(reverse, [0.2961981327, -0.5, 0.8137976813])
    assert np.linalg.norm(forward - reverse) > 0.05


def test_beam_stresses_recover_the_declared_resultant_moments() -> None:
    """Integrate cross-sectional tractions to check the chapter's signs."""
    radius, angle = sp.symbols("radius angle", real=True)
    normal, bend_x, bend_y, torsion = sp.symbols("N M_x M_y T", real=True)
    coordinate_x = radius * sp.cos(angle)
    coordinate_y = radius * sp.sin(angle)
    second_moment, polar_moment = sp.pi / 4, sp.pi / 2  # unit-radius circle
    stress = (
        -normal / sp.pi
        + bend_x * coordinate_y / second_moment
        - bend_y * coordinate_x / second_moment
    )
    densities = [
        stress,
        coordinate_y * stress,
        -coordinate_x * stress,
        torsion * (coordinate_x**2 + coordinate_y**2) / polar_moment,
    ]
    for density, expected in zip(densities, [-normal, bend_x, bend_y, torsion], strict=True):
        integral = sp.integrate(density * radius, (radius, 0, 1), (angle, 0, 2 * sp.pi))
        assert sp.simplify(integral - expected) == 0


def test_load_normalization_and_principal_stresses() -> None:
    """Compare mean traction units and tensor eigenvalues with worked answers."""
    force = 8 * 75 * GRAVITY_M_S2
    assert force == pytest.approx(5886)
    assert force / 1800 == pytest.approx(3.27)  # N/mm^2 = MPa
    assert force / (0.8 * 1800) == pytest.approx(4.0875)
    principal = np.linalg.eigvalsh([[-3.0, 1.0], [1.0, 0.0]])
    np.testing.assert_allclose(principal, [-1.5 - np.sqrt(3.25), -1.5 + np.sqrt(3.25)])
    assert not np.isclose(principal, -3 + 1).any()


@pytest.mark.parametrize(
    ("count", "total_degrees", "expected_moment", "expected_energy"),
    [(5, 20, 48, 8 * np.pi / 3), (10, 20, 24, 4 * np.pi / 3), (10, 40, 48, 16 * np.pi / 3)],
)
def test_series_energy_by_summing_individual_spring_energies(
    count: int, total_degrees: float, expected_moment: float, expected_energy: float
) -> None:
    """A sum of individual energies independently checks the equivalent spring."""
    individual_stiffness = 12 * 180 / np.pi  # Nm/rad
    individual_angle = np.deg2rad(total_degrees) / count
    moment = individual_stiffness * individual_angle
    energy = count * 0.5 * individual_stiffness * individual_angle**2
    assert moment == pytest.approx(expected_moment)
    assert energy == pytest.approx(expected_energy)


def test_ligament_potential_tension_and_generalized_moment() -> None:
    """Differentiate the stretched-branch potential, retaining length units."""
    length, slack, coefficient = sp.symbols("L L0 k", positive=True)
    potential = coefficient * (length - slack) ** 3 / 3
    tension = sp.diff(potential, length)
    tangent = sp.diff(tension, length)
    values = {length: sp.Rational(22, 1000), slack: sp.Rational(20, 1000), coefficient: 20000000}
    assert float(tension.subs(values)) == pytest.approx(80)
    assert float(tangent.subs(values)) == pytest.approx(80000)
    assert float(potential.subs(values)) == pytest.approx(0.16 / 3)
    assert -float(tension.subs(values)) * 0.010 == pytest.approx(-0.8)
    assert tension.subs(length, slack) == 0
    assert potential.subs(length, slack) == 0


def test_controlled_spring_energy_identity_includes_parameter_work() -> None:
    """Total time differentiation catches omitted stiffness/reference work."""
    time = sp.symbols("t", real=True)
    angle, stiffness, reference = [sp.Function(name)(time) for name in ("theta", "k", "theta0")]
    inertia, damping, applied = sp.symbols("I d tau", real=True)
    velocity = sp.diff(angle, time)
    delta = angle - reference
    energy = inertia * velocity**2 / 2 + stiffness * delta**2 / 2
    acceleration = (applied - damping * velocity - stiffness * delta) / inertia
    derivative = sp.diff(energy, time).subs(sp.diff(angle, time, 2), acceleration)
    expected = (
        applied * velocity
        - damping * velocity**2
        + sp.diff(stiffness, time) * delta**2 / 2
        - stiffness * delta * sp.diff(reference, time)
    )
    assert sp.simplify(derivative - expected) == 0
    assert 0.5 * (200 - 100) * 0.1**2 == pytest.approx(0.5)


def test_signed_moments_muscle_redundancy_and_coupled_acceleration() -> None:
    """Check the examples against balances rather than unsigned magnitudes."""
    angle = np.pi / 6
    gravity_moment = -10 * GRAVITY_M_S2 * 0.30 * np.sin(angle)
    elastic_moment = -20 * angle
    assert gravity_moment == pytest.approx(-14.715)
    assert elastic_moment == pytest.approx(-10.47197551197)
    assert gravity_moment + elastic_moment == pytest.approx(-25.18697551197)
    tensions = np.array([300.0, 100.0])
    assert 0.05 * (tensions[0] - tensions[1]) == pytest.approx(10)
    assert 0.8 * tensions.sum() == pytest.approx(320)
    assert 0.8 * (tensions + 150).sum() == pytest.approx(560)
    assert 0.05 * ((tensions + 150)[0] - (tensions + 150)[1]) == pytest.approx(10)
    acceleration = np.linalg.solve([[2, 1], [1, 2]], [1, 0])
    np.testing.assert_allclose(acceleration, [2 / 3, -1 / 3])


def test_pressure_subsystem_and_peak_definitions() -> None:
    """Opposite closed-surface tractions cancel; asynchronous peaks do not add."""
    force = 5000 * 0.10
    assert force == pytest.approx(500)
    normals = np.vstack([np.eye(3), -np.eye(3)])
    np.testing.assert_allclose((force * normals).sum(axis=0), np.zeros(3))
    histories = np.array([[2, 6, 2], [2, 2, 6]])
    assert histories.mean(axis=0).max() == 4
    assert histories.max(axis=1).mean() == 6
