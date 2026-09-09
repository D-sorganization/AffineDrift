"""Independent mechanics counterexamples and paired-publication guards for #4315."""

from pathlib import Path

import numpy as np
import pytest
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "articles/The_Physics_of_Golf"
GRAVITY_M_S2 = 9.81


def test_original_oscillator_parameters_are_overdamped() -> None:
    mass, stiffness, damping = 1.0, 5000.0, 200.0
    ratio = damping / (2 * np.sqrt(mass * stiffness))
    assert ratio == pytest.approx(np.sqrt(2))
    roots = np.roots([mass, damping, stiffness])
    assert np.sort(roots) == pytest.approx([-170.71067811865, -29.28932188135])
    solution = solve_ivp(
        lambda _t, y: [y[1], -(damping * y[1] + stiffness * y[0]) / mass],
        (0, 0.3),
        [0.01, 0.0],
        t_eval=np.linspace(0, 0.3, 601),
        rtol=1e-10,
        atol=1e-12,
    )
    assert solution.success
    assert np.all(solution.y[0] > 0)
    assert np.all(np.diff(solution.y[0]) < 0)


@pytest.mark.parametrize("damping", [0.0, 200.0])
def test_closed_two_mass_model_preserves_momentum_and_work(damping: float) -> None:
    rigid, soft, stiffness = 1.5, 1.0, 5000.0

    def dynamics(time: float, state: np.ndarray) -> list[float]:
        xr, vr, xw, vw = state[:4]
        force = 10 * np.sin(2 * np.pi * time)
        coupling = stiffness * (xw - xr) + damping * (vw - vr)
        return [
            vr,
            (force + coupling) / rigid,
            vw,
            -coupling / soft,
            force * vr,
            damping * (vw - vr) ** 2,
            force,
        ]

    result = solve_ivp(
        dynamics,
        (0, 1),
        np.zeros(7),
        t_eval=np.linspace(0, 1, 1001),
        rtol=1e-10,
        atol=1e-12,
    )
    assert result.success
    xr, vr, xw, vw, work, heat, impulse = result.y
    energy = 0.5 * (rigid * vr**2 + soft * vw**2 + stiffness * (xw - xr) ** 2)
    np.testing.assert_allclose(rigid * vr + soft * vw, impulse, atol=1e-9)
    np.testing.assert_allclose(energy + heat, work, atol=1e-8)
    assert np.all(heat >= -1e-12)


def test_relative_mode_uses_reduced_mass_when_both_bodies_are_free() -> None:
    rigid, soft, stiffness = 1.5, 1.0, 5000.0
    eigenvalues = np.linalg.eigvals(
        np.linalg.solve(np.diag([rigid, soft]), stiffness * np.array([[1, -1], [-1, 1]]))
    )
    reduced = rigid * soft / (rigid + soft)
    assert np.sort(eigenvalues) == pytest.approx([0, stiffness / reduced], abs=1e-10)
    assert np.sqrt(stiffness / reduced) == pytest.approx(91.2870929175)
    assert np.sqrt(stiffness / soft) == pytest.approx(70.71067811865)


@pytest.mark.parametrize("frequency", [1.0, 11.25, 40.0])
def test_harmonic_dynamic_mass_matches_ode_and_dissipation(frequency: float) -> None:
    rigid, soft, stiffness, damping, amplitude = 1.5, 1.0, 5000.0, 200.0, 0.001
    omega = 2 * np.pi * frequency
    coupling = stiffness + 1j * omega * damping
    transfer = coupling / (coupling - soft * omega**2)

    def dynamics(time: float, state: np.ndarray) -> list[float]:
        base = amplitude * np.cos(omega * time)
        speed = -amplitude * omega * np.sin(omega * time)
        return [state[1], -(stiffness * (state[0] - base) + damping * (state[1] - speed)) / soft]

    time = np.linspace(0, 2 / frequency, 1001)
    response = solve_ivp(
        dynamics,
        (time[0], time[-1]),
        [amplitude * transfer.real, (1j * omega * amplitude * transfer).real],
        t_eval=time,
        rtol=1e-10,
        atol=1e-12,
    )
    assert response.success
    expected = amplitude * np.real(transfer * np.exp(1j * omega * time))
    np.testing.assert_allclose(response.y[0], expected, atol=1e-10)
    dynamic_mass = rigid + soft * transfer
    force = -(omega**2) * rigid * amplitude + coupling * amplitude * (1 - transfer)
    assert force == pytest.approx(-(omega**2) * dynamic_mass * amplitude)
    power = 0.5 * np.real(force * np.conj(1j * omega * amplitude))
    dissipation = 0.5 * damping * omega**2 * abs(amplitude * (transfer - 1)) ** 2
    assert power == pytest.approx(dissipation)
    assert power > 0


def test_marker_acceleration_depends_on_frequency_and_is_not_identifiable() -> None:
    amplitude, frequency = 0.01, 10.0
    assert amplitude * (2 * np.pi * frequency) ** 2 == pytest.approx(39.4784176044)
    time = np.linspace(0, 1, 1001)
    measured = 0.03 * np.sin(2 * np.pi * 2 * time)
    bone_a = 0.02 * np.sin(2 * np.pi * 2 * time)
    bone_b = 0.025 * np.sin(2 * np.pi * 2 * time)
    np.testing.assert_allclose(bone_a + (measured - bone_a), measured)
    np.testing.assert_allclose(bone_b + (measured - bone_b), measured)
    assert not np.allclose(bone_a, bone_b)


def test_relative_coordinates_preserve_mass_and_gravity() -> None:
    rigid, soft, gravity = 1.5, 1.0, GRAVITY_M_S2
    transform = np.array([[1, 0], [1, 1]])
    mass = transform.T @ np.diag([rigid, soft]) @ transform
    np.testing.assert_allclose(mass, [[rigid + soft, soft], [soft, soft]])
    generalized = transform.T @ np.array([-rigid * gravity, -soft * gravity])
    np.testing.assert_allclose(generalized, [-(rigid + soft) * gravity, -soft * gravity])
    assert np.linalg.det(mass) == pytest.approx(rigid * soft)


def test_changing_inertia_is_not_dissipation() -> None:
    initial, final, momentum = 3.0, 3.18, 30.0
    speed = momentum / final
    assert speed == pytest.approx(9.43396226415)
    energy_change = momentum**2 / (2 * final) - momentum**2 / (2 * initial)
    assert energy_change == pytest.approx(-8.49056603774)
    reverse_change = momentum**2 / (2 * initial) - momentum**2 / (2 * final)
    assert reverse_change == pytest.approx(-energy_change)
    inertia_rate = (final - initial) / 0.2
    assert inertia_rate * 10 == pytest.approx(9.0)


def test_hemisphere_pressure_uses_projected_area() -> None:
    pressure, radius = 13332.2387415, 0.1
    nodes, weights = leggauss(24)
    cosine = (nodes + 1) / 2
    force = pressure * 2 * np.pi * radius**2 * np.dot(weights / 2, cosine)
    assert force == pytest.approx(pressure * np.pi * radius**2)
    assert force != pytest.approx(pressure * 2 * np.pi * radius**2)


def test_closed_pressure_boundary_has_zero_resultant_and_twist_work() -> None:
    nodes, weights = leggauss(20)
    angle = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    z, phi = np.meshgrid(nodes, angle, indexing="ij")
    normal = np.stack(
        [np.sqrt(1 - z**2) * np.cos(phi), np.sqrt(1 - z**2) * np.sin(phi), z], axis=-1
    )
    area = weights[:, None, None] * (2 * np.pi / len(angle))
    traction = 10000 * normal
    position = 0.1 * normal + np.array([0.3, -0.2, 0.7])
    force = np.sum(traction * area, axis=(0, 1))
    torque = np.sum(np.cross(position, traction) * area, axis=(0, 1))
    np.testing.assert_allclose(force, 0, atol=1e-9)
    np.testing.assert_allclose(torque, 0, atol=1e-9)
    twist_velocity = np.cross(np.array([0, 0, 2.0]), normal)
    np.testing.assert_allclose(np.sum(traction * twist_velocity, axis=-1), 0, atol=1e-10)


def test_fixed_force_and_fixed_deformation_reverse_stiffness_energy_comparison() -> None:
    low, high, angle, torque = 100.0, 200.0, 0.1, 10.0
    assert 0.5 * high * angle**2 > 0.5 * low * angle**2
    assert torque**2 / (2 * high) < torque**2 / (2 * low)
    assert 0.5 * (high - low) * angle**2 == pytest.approx(0.5)


def test_coordinate_dependent_mass_conserves_energy_without_extra_total_derivative() -> None:
    position, velocity = 1.0, 2.0
    mass = 1 + position**2
    mass_rate = 2 * position * velocity
    acceleration = -position * velocity**2 / mass
    assert acceleration == pytest.approx(-2.0)
    assert mass * velocity * acceleration + 0.5 * mass_rate * velocity**2 == 0
    doubled_acceleration = -(position * velocity**2 + mass_rate * velocity) / mass
    assert doubled_acceleration == pytest.approx(-6.0)
    assert mass * velocity * doubled_acceleration + 0.5 * mass_rate * velocity**2 != 0


@pytest.mark.parametrize(
    "relative", ["chapters/ch20_soft_tissue_pliable.tex", "quarto/ch20_soft_tissue_pliable.qmd"]
)
def test_publication_corrects_mechanics_and_keeps_evidence_bounded(relative: str) -> None:
    source = (BOOK / relative).read_text(encoding="utf-8")
    for required in [
        "1.4142",
        "projected area",
        "pressure difference",
        "relative angular momentum",
        "Worked Answers",
        "Pain2006Wobble",
        "Stokes2010AbdominalPressure",
    ]:
        assert required in source
    for unsupported in [
        "accurate to within 5--10",
        "partly exploiting this high-frequency inertia reduction",
        "prevents blood pressure spikes",
        "prevents the lungs from over-expanding",
        "Typical Error",
    ]:
        assert unsupported not in source


def test_publication_has_paired_scientific_figures() -> None:
    for name in ["soft_tissue_response", "soft_tissue_pressure"]:
        for extension in ["pdf", "svg"]:
            assert (BOOK / "figures" / f"{name}.{extension}").is_file()
