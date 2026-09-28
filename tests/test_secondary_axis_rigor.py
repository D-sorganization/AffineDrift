"""Manufactured rigid-body checks and source regressions for #4467."""

from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parents[1]
SPECTRA = np.array([[0.00023, 0.00113, 0.00133], [0.00023, 0.00062, 0.00072]])


def _field(spin: NDArray[np.float64], inertia: NDArray[np.float64]) -> NDArray[np.float64]:
    """Use the vector Euler balance, independently of component linearization."""
    return -np.cross(spin, inertia * spin) / inertia


@pytest.mark.parametrize("inertia", SPECTRA)
@pytest.mark.parametrize("axis", [0, 1, 2])
def test_euler_linearization_distinguishes_principal_axes(
    inertia: NDArray[np.float64], axis: int
) -> None:
    """Central differences recover real intermediate and imaginary extreme modes."""
    spin = np.eye(3)[axis]  # Manufactured unit spin, in rad/s.
    step = 1e-6
    columns = [
        (_field(spin + step * unit, inertia) - _field(spin - step * unit, inertia)) / (2 * step)
        for unit in np.eye(3)
    ]
    jacobian = np.column_stack(columns)
    transverse = [index for index in range(3) if index != axis]
    eigenvalues = np.linalg.eigvals(jacobian[np.ix_(transverse, transverse)])
    assert np.allclose(jacobian[:, axis], 0.0)
    if axis == 1:
        low, middle, high = inertia
        rate = np.sqrt((high - middle) * (middle - low) / (low * high))
        assert np.sort(eigenvalues) == pytest.approx([-rate, rate])
    else:
        assert eigenvalues.real == pytest.approx([0.0, 0.0], abs=1e-12)
        assert np.prod(eigenvalues.imag) < 0.0


def test_synthetic_inertia_rates_depend_on_comparison_condition() -> None:
    """Exact integer ratios verify the table and reverse its fixed-momentum ranking."""
    low, middle, high = SPECTRA.T
    assert np.all(low + middle > high)
    rates = np.sqrt((high - middle) * (middle - low) / (low * high))
    assert rates**2 == pytest.approx([1800 / 3059, 65 / 276])
    assert rates[1] / rates[0] == pytest.approx(0.6326385077447322)
    momentum_rates = rates / middle
    assert momentum_rates[1] / momentum_rates[0] == pytest.approx(1.1530346995992697)
    assert (high[1] - middle[1]) / (high[0] - middle[0]) == pytest.approx(0.5)
    scaled = 7 * SPECTRA  # Uniform mass scaling leaves fixed-spin growth unchanged.
    assert np.sqrt(
        (scaled[:, 2] - scaled[:, 1])
        * (scaled[:, 1] - scaled[:, 0])
        / (scaled[:, 0] * scaled[:, 2])
    ) == pytest.approx(rates)


def test_gyroscopic_moment_does_no_work() -> None:
    """Nonprincipal angular velocity has a nonzero moment but zero gyro power."""
    spin = np.array([1.0, 2.0, -3.0])
    gyro = np.cross(spin, SPECTRA[0] * spin)
    assert np.linalg.norm(gyro) > 0.0
    assert spin @ gyro == pytest.approx(0.0, abs=1e-16)
    assert (SPECTRA[0] * spin) @ _field(spin, SPECTRA[0]) == pytest.approx(0.0)


def _point_inertia(
    masses: NDArray[np.float64], offsets: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Sum a manufactured cloud's second moments about the declared origin."""
    radii_squared = np.einsum("ij,ij->i", offsets, offsets)
    return np.sum(masses * radii_squared) * np.eye(3) - np.einsum(
        "i,ij,ik->jk", masses, offsets, offsets
    )


def test_parallel_axis_term_matches_direct_point_mass_sum() -> None:
    """A shifted tensor includes translation even when axis directions agree."""
    masses = np.array([0.1, 0.15, 0.1])
    points = np.array([[0.05, 0.02, -0.01], [-0.03, -0.01, 0.02], [0.01, 0.0, 0.03]])
    center = np.sum(masses[:, None] * points, axis=0) / masses.sum()
    origin = np.array([0.02, -0.03, 0.01])
    offset = center - origin
    translated = _point_inertia(masses, points - center) + masses.sum() * (
        (offset @ offset) * np.eye(3) - np.outer(offset, offset)
    )
    assert translated == pytest.approx(_point_inertia(masses, points - origin))
    assert not np.allclose(translated, _point_inertia(masses, points - center))


def test_coordinate_rotation_preserves_energy_and_torque_response() -> None:
    """Off-diagonal entries change with basis without changing the physical motion."""
    rotation = np.array([[1.0, -1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, np.sqrt(2)]])
    rotation /= np.sqrt(2)
    inertia = np.diag([0.001, 0.002, 0.0025])
    transformed = rotation @ inertia @ rotation.T
    spin = np.array([1.0, 2.0, 3.0])
    torque = np.array([0.001, 0.0, 0.0])
    assert (rotation @ spin) @ transformed @ (rotation @ spin) == pytest.approx(
        spin @ inertia @ spin
    )
    assert np.linalg.solve(transformed, rotation @ torque) == pytest.approx(
        rotation @ np.linalg.solve(inertia, torque)
    )
    # Holding physical torque components fixed instead is a different comparison.
    assert np.linalg.solve(transformed, torque) == pytest.approx([0.75, 0.25, 0.0])


def test_moving_body_point_balance_matches_particle_accelerations() -> None:
    """An accelerating reference point contributes a moment omitted by fixed pivots."""
    masses = np.array([0.1, 0.15, 0.1])
    offsets = np.array([[0.05, 0.02, -0.01], [-0.03, -0.01, 0.02], [0.01, 0.0, 0.03]])
    base_acceleration = np.array([0.4, -0.2, 0.8])
    spin = np.array([1.0, -2.0, 0.5])
    angular_acceleration = np.array([0.3, 0.7, -0.4])
    particle_accelerations = (
        base_acceleration
        + np.cross(angular_acceleration, offsets)
        + np.cross(spin, np.cross(spin, offsets))
    )
    direct_moment = np.sum(np.cross(offsets, masses[:, None] * particle_accelerations), axis=0)
    inertia = _point_inertia(masses, offsets)
    first_moment = np.sum(masses[:, None] * offsets, axis=0)
    fixed_point_terms = inertia @ angular_acceleration + np.cross(spin, inertia @ spin)
    assert direct_moment == pytest.approx(
        fixed_point_terms + np.cross(first_moment, base_acceleration)
    )
    assert not np.allclose(direct_moment, fixed_point_terms)


def test_zero_gravity_moment_does_not_determine_stability_or_damping() -> None:
    """Two zero-moment poses have opposite potential curvature; neither dissipates."""
    mass, gravity, length, pivot_inertia = 0.35, 9.81, 0.02, 0.002
    scale = mass * gravity * length
    angles = np.array([0.0, np.pi])
    assert -scale * np.sin(angles) == pytest.approx([0.0, 0.0], abs=1e-16)
    step = 1e-5
    derivative = -scale * (np.sin(angles + step) - np.sin(angles - step)) / (2 * step)
    assert -derivative == pytest.approx([0.06867, -0.06867])
    angle, velocity = 0.4, 2.0
    acceleration = -scale * np.sin(angle) / pivot_inertia
    power = pivot_inertia * velocity * acceleration + scale * np.sin(angle) * velocity
    assert power == pytest.approx(0.0, abs=1e-16)
    assert scale / (1e-4 * 5) == pytest.approx(137.34)  # Maximum, not every pose.


def test_angular_impulse_requires_full_tensor_unless_axis_decouples() -> None:
    """The scalar yaw estimate can fail even for a pure yaw angular impulse."""
    inertia = np.array([[0.002, 0.0, 0.0003], [0.0, 0.003, 0.0], [0.0003, 0.0, 0.004]])
    position = np.array([0.0, 0.02, 0.0])
    impulse = np.array([-0.1, 0.0, 0.0])
    angular_impulse = np.cross(position, impulse)
    change = np.linalg.solve(inertia, angular_impulse)
    assert inertia @ change == pytest.approx([0.0, 0.0, 0.002])
    assert change[0] != 0.0
    assert change[2] != pytest.approx(0.002 / inertia[2, 2])
    diagonal_change = np.linalg.solve(np.diag(np.diag(inertia)), angular_impulse)
    assert diagonal_change == pytest.approx([0.0, 0.0, 0.5])


@pytest.mark.parametrize(
    ("relative", "false_claim"),
    [
        ("articles/secondary-axis-stability.qmd", "homeomorphically bound"),
        ("articles/secondary-axis-stability.qmd", "Secondary-axis excursions are damped"),
        ("articles/secondary-axis-stability.qmd", "A uniform volumetric grid model was used"),
        ("articles/secondary-axis-stability.qmd", "single most correlated metric"),
        ("critiques/intermediate_axis_fallacy.md", "grip torque is in Newtons"),
        ("critiques/misattribution_of_stability_gravity.md", "must admit that for putting"),
    ],
)
def test_source_removes_specific_unjustified_claims(relative: str, false_claim: str) -> None:
    """Guard the identified claims in reader prose and the two critique companions."""
    assert false_claim not in (ROOT / relative).read_text(encoding="utf-8")
