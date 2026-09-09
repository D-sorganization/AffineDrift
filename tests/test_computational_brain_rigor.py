"""Independent checks for the computational-brain chapter's worked models."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp

BOOK = Path(__file__).resolve().parents[1] / "articles" / "The_Physics_of_Golf"


@pytest.mark.parametrize(
    "edition", ["chapters/ch26_remarkable_brain.tex", "quarto/ch26_remarkable_brain.qmd"]
)
def test_published_schedule_count_matches_independent_logarithm(edition: str) -> None:
    """Catch the original 10^4000 arithmetic error in either published edition."""
    exponent = 200 * 30 * np.log10(7)
    source = (BOOK / edition).read_text(encoding="utf-8")
    assert f"{exponent:.5f}" in source
    assert "10^{4000}" not in source


@pytest.mark.parametrize("perturbation_time", [0.04, 0.18, 0.22, 0.26])
def test_delayed_activation_rotor_matches_ode_and_convolution(perturbation_time: float) -> None:
    """Three independent forms agree, including a response arriving after impact."""
    horizon, latency, activation_time = 0.3, 0.06, 0.04
    inertia, command = 0.05, 0.5
    remaining = max(horizon - perturbation_time - latency, 0.0)
    if remaining == 0:
        assert perturbation_time + latency >= horizon
        return

    def dynamics(_time: float, state: np.ndarray) -> list[float]:
        return [state[1], state[2] / inertia, (command - state[2]) / activation_time]

    solution = solve_ivp(dynamics, (0, remaining), [0, 0, 0], rtol=1e-11, atol=1e-13)
    assert solution.success
    closed_form = (
        command
        / inertia
        * (
            remaining**2 / 2
            - activation_time * remaining
            - activation_time**2 * np.expm1(-remaining / activation_time)
        )
    )
    convolution = quad(
        lambda time: (remaining - time) * command * (-np.expm1(-time / activation_time)) / inertia,
        0,
        remaining,
    )[0]
    assert solution.y[0, -1] == pytest.approx(closed_form, abs=1e-12)
    assert convolution == pytest.approx(closed_form, abs=1e-12)
    assert 0 < closed_form < command * remaining**2 / (2 * inertia)


def test_activation_time_is_not_an_additional_dead_time() -> None:
    """First-order force starts changing immediately after transmission delay."""
    time_constant = 0.04
    early_response = -np.expm1(-0.001 / time_constant)
    assert early_response == pytest.approx(0.0246900879716673)
    assert -np.expm1(-1) == pytest.approx(0.6321205588285577)


@pytest.mark.parametrize("frequency", [1.0, 3.0, 5.0])
def test_delay_and_activation_have_distinct_frequency_responses(frequency: float) -> None:
    """Complex frequency response checks phase and attenuation independently."""
    latency, activation_time = 0.06, 0.04
    omega = 2 * np.pi * frequency
    response = np.exp(-1j * omega * latency) / (1 + 1j * omega * activation_time)
    phase = -omega * latency - np.arctan(omega * activation_time)
    assert response == pytest.approx(
        np.exp(1j * phase) / np.sqrt(1 + (omega * activation_time) ** 2)
    )
    assert np.abs(response) < 1


def test_large_drift_does_not_remove_terminal_input_gain() -> None:
    """An affine unstable scalar has large gain despite tiny input/drift ratio."""
    growth, horizon, step = 10.0, 0.3, 1e-4

    def endpoint(command: float) -> float:
        result = solve_ivp(
            lambda _time, state: 1 + growth * state + command,
            (0, horizon),
            [0],
            rtol=1e-11,
            atol=1e-13,
        )
        assert result.success
        return float(result.y[0, -1])

    difference = (endpoint(step) - endpoint(-step)) / (2 * step)
    gain = np.expm1(growth * horizon) / growth
    assert difference == pytest.approx(gain, rel=1e-8)
    assert gain > horizon
    assert (1 + growth * endpoint(0)) / step > 200_000


def test_increasing_stiffness_can_add_energy_at_zero_motion() -> None:
    """A clamped error gains stored energy from stiffness modulation, not motion."""
    error, low, high, duration = 0.1, 10.0, 30.0, 0.2
    energy_change = (high - low) * error**2 / 2
    modulation_power = (high - low) / duration * error**2 / 2
    assert energy_change == pytest.approx(0.1)
    assert modulation_power * duration == pytest.approx(energy_change)


def test_fixed_impedance_storage_balance_includes_moving_reference_work() -> None:
    """Differentiate a moving spring potential and compare with port power."""
    stiffness, damping = 20.0, 0.4
    q, reference, velocity, reference_velocity = 0.2, 0.1, 0.3, 0.05
    error, rate_error = q - reference, velocity - reference_velocity
    torque = -stiffness * error - damping * rate_error
    storage_rate = stiffness * error * rate_error
    assert torque * velocity + storage_rate == pytest.approx(
        -damping * rate_error**2 + torque * reference_velocity
    )


def test_equal_antagonist_activation_need_not_cancel_joint_torque() -> None:
    """Moment arms and force capacities matter even in an isometric toy model."""
    moment_arms = np.array([0.04, -0.03])
    maximum_forces = np.array([1000.0, 800.0])
    activation = np.array([0.2, 0.2])
    assert moment_arms @ (maximum_forces * activation) == pytest.approx(3.2)


def test_synergy_restriction_can_destroy_a_feasible_direction() -> None:
    """Nonnegative activation geometry differs from rank and explained variance."""
    torque_map = np.array([[1.0, -1.0]])
    synergy = np.array([[1.0], [1.0]])
    assert np.linalg.matrix_rank(synergy) == 1
    np.testing.assert_allclose(torque_map @ synergy, 0)
    assert (torque_map @ np.array([1.0, 0.0]))[0] == 1


def test_low_rank_length_changes_do_not_require_grouped_neural_commands() -> None:
    """A two-coordinate mechanical map limits four muscle-length perturbations."""
    length_jacobian = np.array([[1, 0], [0, 1], [1, 1], [1, -1]], dtype=float)
    perturbations = np.array([[1, 0, -1, 0], [0, 1, 0, -1]], dtype=float)
    length_changes = length_jacobian @ perturbations
    assert np.linalg.matrix_rank(length_changes) == 2
    assert length_changes.shape[0] == 4


def test_energy_boundaries_cannot_be_substituted_for_each_other() -> None:
    """Separate illustrative processor energy, head energy and head gravity work."""
    power, duration, head_mass, head_speed, height_drop, gravity = 20, 0.3, 0.2, 50, 1, 9.81
    processor_energy = power * duration
    head_energy = head_mass * head_speed**2 / 2
    gravity_work = head_mass * gravity * height_drop
    assert processor_energy == 6
    assert head_energy == 250
    assert gravity_work == pytest.approx(1.962)
    assert gravity_work / head_energy == pytest.approx(0.007848)
