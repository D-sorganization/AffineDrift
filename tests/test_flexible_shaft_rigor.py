"""Independent mechanics and paired-publication checks for the shaft chapter."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp
from scipy.linalg import expm
from scipy.optimize import brentq

BOOK = Path(__file__).resolve().parents[1] / "articles/The_Physics_of_Golf"


def test_cantilever_shape_has_consistent_tip_slope_and_energy() -> None:
    length, rigidity, force = 1.0, 40.0, 2.0
    tip = force * length**3 / (3 * rigidity)
    # Curvature comes directly from the static bending-moment diagram.
    energy = quad(lambda z: (force * (length - z)) ** 2 / (2 * rigidity), 0, length)[0]
    assert energy == pytest.approx(force * tip / 2)
    slope = quad(lambda z: force * (length - z) / rigidity, 0, length)[0]
    assert slope == pytest.approx(3 * tip / (2 * length))
    mass_factor = quad(lambda s: ((3 * s**2 - s**3) / 2) ** 2, 0, 1)[0]
    assert mass_factor == pytest.approx(33 / 140)


def test_mode_rescaling_preserves_physical_energy_and_frequency() -> None:
    modal_mass, stiffness, amplitude, velocity, scale = 0.2, 80, 0.02, 0.3, 4
    original = (modal_mass * velocity**2 + stiffness * amplitude**2) / 2
    rescaled = (
        scale**2 * (modal_mass * (velocity / scale) ** 2 + stiffness * (amplitude / scale) ** 2) / 2
    )
    assert rescaled == pytest.approx(original)
    assert scale**2 * stiffness / (scale**2 * modal_mass) == stiffness / modal_mass


def test_unactuated_elastic_coordinate_has_nonzero_acceleration_input() -> None:
    base_mass, head_mass = 1.0, 0.2
    mass = np.array([[base_mass + head_mass, head_mass], [head_mass, head_mass]])
    input_map = np.linalg.solve(mass, [1, 0])
    np.testing.assert_allclose(input_map, [1, -1])
    acceleration = input_map * 2
    assert acceleration[0] == pytest.approx(2)
    assert np.sum(acceleration) == pytest.approx(0)


def test_coupled_energy_and_momentum_follow_external_input() -> None:
    mass = np.array([[1.2, 0.2], [0.2, 0.2]])
    velocity = np.array([0.7, -0.2])
    bend, stiffness, damping, force = 0.03, 80.0, 0.64, 2.0
    acceleration = np.linalg.solve(mass, [force, -stiffness * bend - damping * velocity[1]])
    energy_rate = velocity @ mass @ acceleration + stiffness * bend * velocity[1]
    assert energy_rate == pytest.approx(force * velocity[0] - damping * velocity[1] ** 2)
    assert 1.2 * acceleration[0] + 0.2 * acceleration[1] == pytest.approx(force)
    reduced_mass = 1.0 * 0.2 / 1.2
    assert np.sqrt(stiffness / reduced_mass) == pytest.approx(21.9089023)


def test_force_and_displacement_controls_reverse_storage_order() -> None:
    stiffness = np.array([80, 160])
    np.testing.assert_allclose(stiffness * 0.02**2 / 2, [0.016, 0.032])
    np.testing.assert_allclose(1.6**2 / (2 * stiffness), [0.016, 0.008])


def test_parameter_set_and_frequency_units_are_consistent() -> None:
    modal_mass, stiffness, damping = 0.2, 80.0, 0.64
    frequency = np.sqrt(stiffness / modal_mass)
    assert frequency == 20
    assert damping / (2 * modal_mass * frequency) == pytest.approx(0.08)
    np.testing.assert_allclose(np.array([240, 280]) / 60, [4, 14 / 3])
    assert np.sqrt(7000 / 0.2) == pytest.approx(187.0828693)


def test_prescribed_base_solution_matches_matrix_exponential_and_work() -> None:
    amplitude, omega = 0.02, np.pi / 0.2
    system = np.array(
        [[0, 1, 0, 0], [-400, -3.2, amplitude * omega**2, 0], [0, 0, 0, omega], [0, 0, -omega, 0]]
    )
    initial = np.array([0, 0, 0, 1])
    solution = solve_ivp(
        lambda t, state: system @ state,
        [0, 0.4],
        initial,
        rtol=1e-11,
        atol=1e-13,
        dense_output=True,
    )
    assert solution.success and solution.sol is not None
    for time in [0.05, 0.1, 0.2, 0.3, 0.4]:
        np.testing.assert_allclose(solution.sol(time), expm(system * time) @ initial, atol=2e-11)

    def power(time: float) -> float:
        bend, velocity = solution.sol(time)[:2]
        base_velocity = amplitude * omega * np.cos(omega * time)
        return float(-(80 * bend + 0.64 * velocity) * base_velocity - 0.64 * velocity**2)

    bend, velocity = solution.sol(0.4)[:2]
    initial_energy = 0.2 * (amplitude * omega) ** 2 / 2
    final_energy = 0.2 * (amplitude * omega + velocity) ** 2 / 2 + 80 * bend**2 / 2
    assert quad(power, 0, 0.4, epsabs=1e-11)[0] == pytest.approx(
        final_energy - initial_energy, abs=2e-12
    )


def test_time_varying_stiffness_requires_parameter_power() -> None:
    bend, velocity, stiffness, stiffness_rate = 0.02, 0.1, 80, 10
    delta = 1e-6
    energies = [
        0.5 * (stiffness + stiffness_rate * t) * (bend + velocity * t) ** 2 for t in [-delta, delta]
    ]
    derivative = (energies[1] - energies[0]) / (2 * delta)
    assert derivative == pytest.approx(stiffness * bend * velocity + stiffness_rate * bend**2 / 2)


def test_rotating_frame_velocity_requires_rotation_of_deflection() -> None:
    omega, tip, bend_rate, delta = 3.0, np.array([1.0, 0.02]), 0.1, 1e-6

    def point(time: float) -> np.ndarray:
        angle = omega * time
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        return rotation @ (tip + [0, bend_rate * time])

    derivative = (point(delta) - point(-delta)) / (2 * delta)
    np.testing.assert_allclose(derivative, [-omega * tip[1], omega * tip[0] + bend_rate])


def test_decay_envelope_is_distinct_from_first_zero() -> None:
    omega, damping = 12.0, 0.05
    damped = omega * np.sqrt(1 - damping**2)
    envelope_time = 1 / (omega * damping)
    first_zero = (np.pi / 2 + np.arctan(damping * omega / damped)) / damped
    assert envelope_time == pytest.approx(1.6666666667)
    root = brentq(
        lambda t: np.cos(damped * t) + damping * omega / damped * np.sin(damped * t), 0.1, 0.2
    )
    assert first_zero == pytest.approx(root)
    assert first_zero < envelope_time / 10


@pytest.mark.parametrize(
    "edition", ["chapters/ch11_flexible_shaft.tex", "quarto/ch11_flexible_shaft.qmd"]
)
def test_paired_chapter_explains_coupling_and_bounded_evidence(edition: str) -> None:
    text = (BOOK / edition).read_text(encoding="utf-8").lower()
    for false_claim in [
        "belongs entirely in the drift field",
        "5--15\\% extra",
        "fails spectacularly",
        "why flexible shafts help slower golfers more",
    ]:
        assert false_claim not in text
    for concept in [
        "33/140",
        "1.6667",
        "virtual work",
        "fixed force",
        "fixed deflection",
        "reduced mass",
        "matrix exponential",
        "worked answers",
        "equivalence",
        "mackenzie2017shaft",
        "prescribed base",
        "parameter power",
    ]:
        assert concept in text
    for figure in ["shaft_bending_shape", "shaft_base_response"]:
        assert figure in text
