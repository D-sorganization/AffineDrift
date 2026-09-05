"""Independent force, energy, and ODE checks for the aerodynamic chapter."""

from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from scipy.integrate import quad, solve_ivp

BOOK = Path(__file__).resolve().parents[1] / "articles/The_Physics_of_Golf"


def test_drag_uses_relative_air_velocity_and_can_add_body_energy() -> None:
    body_velocity = np.array([1.0, 0.0, 0.0])
    wind = np.array([3.0, 0.0, 0.0])
    relative = body_velocity - wind
    force = -np.linalg.norm(relative) * relative
    assert force @ relative == -8.0
    assert force @ body_velocity == 4.0
    assert force @ body_velocity == force @ relative + force @ wind
    np.testing.assert_allclose(-np.linalg.norm(np.zeros(3)) * np.zeros(3), 0.0)


def test_reference_area_and_coefficient_must_change_together() -> None:
    dynamic_pressure = 0.5 * 1.225 * 50**2
    assert dynamic_pressure * 0.4 * 0.005 == pytest.approx(3.0625)
    assert dynamic_pressure * 0.2 * 0.01 == pytest.approx(3.0625)
    assert 288.15 / 308.15 == pytest.approx(0.935096543891)


def test_distributed_shaft_moment_uses_the_actual_pivot_offset() -> None:
    density, coefficient, diameter, speed, length = 1.225, 0.5, 0.01, 25.0, 1.1
    prefactor = 0.5 * density * coefficient * diameter * speed**2
    for offset in [0.0, 0.6]:
        integrated_force = quad(lambda s, offset=offset: prefactor * (offset + s) ** 2, 0, length)[
            0
        ]
        integrated_moment = quad(lambda s, offset=offset: prefactor * (offset + s) ** 3, 0, length)[
            0
        ]
        assert integrated_force == pytest.approx(
            prefactor * ((offset + length) ** 3 - offset**3) / 3
        )
        assert integrated_moment == pytest.approx(
            prefactor * ((offset + length) ** 4 - offset**4) / 4
        )
    assert prefactor * length**4 / 4 == pytest.approx(0.7005947265625)


def test_generalized_drag_preserves_virtual_power() -> None:
    jacobian = np.array([[1.0, 2.0], [0.0, 1.0], [-1.0, 0.5]])
    velocity = np.array([2.0, -1.0])
    cartesian_velocity = jacobian @ velocity
    force = -0.3 * np.linalg.norm(cartesian_velocity) * cartesian_velocity
    generalized = jacobian.T @ force
    assert generalized @ velocity == pytest.approx(force @ cartesian_velocity)
    assert generalized @ velocity <= 0.0


def test_omitted_resisting_drag_underestimates_positive_applied_torque() -> None:
    inertia, acceleration, drag = 2.0, 3.0, -4.0
    true_torque = inertia * acceleration - drag
    omitted_torque = inertia * acceleration
    assert true_torque == 10.0
    assert omitted_torque == 6.0
    assert true_torque - omitted_torque == -drag


def test_input_independent_drag_does_not_change_the_input_coefficient() -> None:
    inertia, velocity = 2.0, 3.0
    for drag_coefficient in [0.0, 0.5, 2.0]:
        accelerations = [
            (u - drag_coefficient * velocity * abs(velocity)) / inertia for u in [0.0, 4.0]
        ]
        assert (accelerations[1] - accelerations[0]) / 4 == 1 / inertia


def _pendulum(
    drag_coefficient: float, initial_angle: float
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Integrate motion and dissipated work independently of the energy formula."""

    def rhs(_time: float, state: NDArray[np.float64]) -> list[float]:
        angle, speed, _loss = state
        return [
            speed,
            (-5 * np.sin(angle) - drag_coefficient * speed * abs(speed)) / 2,
            drag_coefficient * abs(speed) ** 3,
        ]

    def bottom(_time: float, state: NDArray[np.float64]) -> float:
        return float(state[0])

    result = solve_ivp(
        rhs, [0, 2], [initial_angle, 0, 0], events=bottom, rtol=1e-10, atol=1e-12, max_step=0.01
    )
    assert result.success
    return result.y, result.y_events[0]


def test_exact_equilibrium_does_not_generate_a_swing() -> None:
    states, _events = _pendulum(0.5, 0.0)
    np.testing.assert_allclose(states, 0.0, atol=1e-14)


@pytest.mark.parametrize("coefficient", [0.0, 0.5])
def test_forward_pendulum_matches_energy_and_an_independent_angle_integral(
    coefficient: float,
) -> None:
    states, crossings = _pendulum(coefficient, np.pi / 2)
    expected_squared_speed = (
        5 * quad(lambda angle: np.exp(-coefficient * angle) * np.sin(angle), 0, np.pi / 2)[0]
    )
    assert crossings[0, 1] ** 2 == pytest.approx(expected_squared_speed, rel=1e-9)
    energy = states[1] ** 2 + 5 * (1 - np.cos(states[0])) + states[2]
    np.testing.assert_allclose(energy, 5.0, atol=2e-9)
    assert crossings[0, 1] < 0.0
    assert abs(crossings[0, 1]) <= np.sqrt(5.0) + 1e-10


@pytest.mark.parametrize(
    "edition", ["chapters/ch19_aerodynamic_drag.tex", "quarto/ch19_aerodynamic_drag.qmd"]
)
def test_chapter_excludes_invalid_drag_conclusions(edition: str) -> None:
    text = (BOOK / edition).read_text(encoding="utf-8")
    for phrase in [
        "always too high",
        "This is why you feel tired",
        "control gain $G(",
        "control gain $G\\(",
        "aerodynamic_drag_golf",
        "the ratio further, reinforcing",
    ]:
        assert phrase not in text
