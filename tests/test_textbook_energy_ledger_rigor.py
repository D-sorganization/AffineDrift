"""Independent checks for the textbook's energy and interface-work ledgers."""

from pathlib import Path

import numpy as np
import pytest

from src.tools.lagrangian_examples import RodPair

ROOT = Path(__file__).resolve().parents[1]
GRAVITY_M_S2 = 9.81


def test_passive_power_reverses_with_geometry() -> None:
    from src.tools.energy_ledger_examples import rod_energy_ledger

    for angle, expected in [(-np.pi / 2, 1.0), (np.pi / 2, -1.0)]:
        ledger = rod_energy_ledger(RodPair(gravity=0), np.array([0, angle, 2, 2]), np.zeros(2))
        assert ledger.force_power == pytest.approx(expected)
        assert ledger.mechanical_rates == pytest.approx([-expected, expected])
        assert sum(ledger.kinetic) == pytest.approx(10 / 3)


def test_joint_motor_power_is_relative_while_club_moment_power_is_absolute() -> None:
    from src.tools.energy_ledger_examples import rod_energy_ledger

    model = RodPair(masses=(1.3, 0.4), lengths=(0.6, 1.1), gravity=GRAVITY_M_S2)
    state = np.array([0.4, -0.7, 2, 5])
    motors = np.array([7, 3])
    ledger = rod_energy_ledger(model, state, motors)
    assert ledger.club_moment_power == pytest.approx(15)
    assert ledger.actuator_power == pytest.approx(23)
    assert sum(ledger.mechanical_rates) == pytest.approx(23)
    assert ledger.mechanical_rates[1] == pytest.approx(ledger.force_power + 15)
    assert ledger.mechanical_rates[0] == pytest.approx(14 - ledger.force_power - 6)


def test_mechanical_rates_match_directional_energy_derivatives() -> None:
    from src.tools.energy_ledger_examples import rod_energy_ledger

    model = RodPair(masses=(1.3, 0.4), lengths=(0.6, 1.1), gravity=7.2)
    state = np.array([0.4, -0.7, 2, -1.3])
    torques = np.array([2.1, -0.8])
    ledger = rod_energy_ledger(model, state, torques)
    direction = np.r_[state[2:], model.acceleration(state, torques)]
    step = 1e-6
    states = [
        rod_energy_ledger(model, state + sign * step * direction, torques) for sign in [-1, 1]
    ]
    energies = [np.array(s.kinetic) + s.potential for s in states]
    assert (energies[1] - energies[0]) / (2 * step) == pytest.approx(
        ledger.mechanical_rates, abs=1e-8
    )


def test_angular_acceleration_can_coexist_with_club_energy_loss() -> None:
    from src.tools.energy_ledger_examples import rod_energy_ledger

    model, state = RodPair(gravity=0), np.array([0, 0, 2, 2])
    torques = np.array([-1, 0])
    acceleration = model.acceleration(state, torques)
    ledger = rod_energy_ledger(model, state, torques)
    assert acceleration == pytest.approx([-12 / 7, 18 / 7])
    assert ledger.mechanical_rates == pytest.approx([-8 / 7, -6 / 7])
    assert acceleration[1] > 0 > ledger.mechanical_rates[1]


def test_coriolis_contraction_is_not_zero_but_metric_terms_cancel() -> None:
    model = RodPair(gravity=0)
    angles, rates = np.array([0.4, -0.8]), np.array([2, 3])
    step = 1e-6
    mdot = (model.mass_matrix(angles + step * rates) - model.mass_matrix(angles - step * rates)) / (
        2 * step
    )
    contraction = rates @ model.coriolis_matrix(angles, rates) @ rates
    assert abs(contraction) > 1
    assert contraction == pytest.approx(rates @ mdot @ rates / 2, abs=1e-8)


def test_balanced_mechanical_budget_does_not_count_gravity_twice() -> None:
    kinetic = np.array([0, 0, 80, 115, 115])
    gravity = np.array([0, 15, 5, 0, 0])
    elastic = np.array([0, 10, 2, 0, 0])
    cumulative_work = np.array([0, 25, 90, 120, 120])
    losses = np.array([0, 0, 3, 5, 5])
    assert kinetic + gravity + elastic == pytest.approx(cumulative_work - losses)
    assert np.diff(cumulative_work) == pytest.approx(
        np.diff(kinetic + gravity + elastic) + np.diff(losses)
    )


def test_relative_chart_derivation_matches_independent_absolute_rod_dynamics() -> None:
    model = RodPair(masses=(1.3, 0.4), lengths=(0.6, 1.1), gravity=7.2)
    m1, m2 = model.masses
    length, outer_length = model.lengths
    c1, c2 = length / 2, outer_length / 2
    a = m1 * length**2 / 3 + m2 * length**2
    b, d = m2 * outer_length**2 / 3, m2 * length * c2
    transform = np.array([[1, 0], [1, 1]])
    for q2 in [-1.7, -0.2, 0.0, 1.3]:
        q1, u, w = 0.4, 2.1, -0.8
        angles, rates = transform @ [q1, q2], transform @ [u, w]
        mass = np.array([[a + b + 2 * d * np.cos(q2), b + d * np.cos(q2)], [b + d * np.cos(q2), b]])
        bias = d * np.sin(q2) * np.array([-(2 * u * w + w**2), u**2])
        gravity = model.gravity * np.array(
            [
                (m1 * c1 + m2 * length) * np.sin(q1) + m2 * c2 * np.sin(q1 + q2),
                m2 * c2 * np.sin(q1 + q2),
            ]
        )
        assert mass == pytest.approx(transform.T @ model.mass_matrix(angles) @ transform)
        assert bias == pytest.approx(transform.T @ model.coriolis_matrix(angles, rates) @ rates)
        assert gravity == pytest.approx(transform.T @ model.gravity_vector(angles))


def test_declared_collision_closes_momentum_restitution_and_energy() -> None:
    head, ball, speed, restitution = 0.2, 0.04593, 45, 0.8
    matrix = np.array([[head, ball], [-1, 1]])
    outgoing = np.linalg.solve(matrix, [head * speed, restitution * speed])
    energies = np.array([head, ball]) * outgoing**2 / 2
    initial = head * speed**2 / 2
    reduced_mass = head * ball / (head + ball)
    lost = reduced_mass * (1 - restitution**2) * speed**2 / 2
    assert outgoing == pytest.approx([29.8724027162, 65.8724027162])
    assert energies == pytest.approx([89.2360444040, 99.6491180406])
    assert energies.sum() + lost == pytest.approx(initial)
    assert lost == pytest.approx(13.6148375554)


def test_physical_energy_matches_shared_total_without_mutating_input() -> None:
    from src.tools.energy_ledger_examples import rod_energy_ledger

    model = RodPair(masses=(1.7, 0.2), lengths=(0.3, 1.2), gravity=GRAVITY_M_S2)
    state, motors = np.array([0.6, -0.8, 2.3, -0.4]), np.array([1.0, -2.0])
    original = state.copy(), motors.copy()
    ledger = rod_energy_ledger(model, state, motors)
    assert np.sum(ledger.kinetic + ledger.potential) == pytest.approx(model.energy(state))
    np.testing.assert_array_equal(state, original[0])
    np.testing.assert_array_equal(motors, original[1])


@pytest.mark.parametrize(
    "relative", ["chapters/ch10_energy_transfer.tex", "quarto/ch10_energy_transfer.qmd"]
)
def test_both_editions_state_energy_and_inference_boundaries(relative: str) -> None:
    text = (ROOT / "articles/The_Physics_of_Golf" / relative).read_text(encoding="utf-8")
    for required in [
        "rod_energy_ledger",
        "moving support",
        "six worked",
        "positive work",
        "Monika",
    ]:
        assert required.casefold() in text.casefold(), required
    for wrong in ["system is essentially ballistic", "energy pump", "purely due to"]:
        assert wrong not in text
