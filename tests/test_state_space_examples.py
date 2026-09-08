"""Independent mechanics and control counterexamples for textbook issue #4272."""

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from src.tools.state_space_examples import TankParameters, motor_matrices, zoh_matrices


def test_motor_is_controllable_but_current_does_not_reveal_angle() -> None:
    a, b = motor_matrices()
    controllability = np.column_stack((b, a @ b, a @ a @ b))
    current = np.array([[1.0, 0.0, 0.0]])
    observability = np.vstack((current, current @ a, current @ a @ a))
    assert np.linalg.matrix_rank(controllability) == 3
    assert np.linalg.matrix_rank(observability) == 2
    np.testing.assert_allclose(a @ [0, 1, 0], 0)
    np.testing.assert_allclose(np.sort(np.linalg.eigvals(a)), [-99.594296, -1.405704, 0], atol=1e-6)


def test_motor_electrical_and_mechanical_power_balance() -> None:
    a, b = motor_matrices()
    state, voltage = np.array([2.0, 0.5, -3.0]), 4.0
    rate = a @ state + b[:, 0] * voltage
    stored_rate = 0.01 * state[0] * rate[0] + 0.001 * state[2] * rate[2]
    assert stored_rate == pytest.approx(voltage * state[0] - state[0] ** 2 - 0.001 * state[2] ** 2)


@pytest.mark.parametrize("heights", [[0.5, 0.2], [0.2, 0.5], [0, 0.5], [0.5, 0], [0, 0]])
def test_tank_direction_and_volume_conservation(heights: list[float]) -> None:
    model = TankParameters()
    h = np.array(heights)
    rate = model.rate(h, 0.01)
    assert model.area * rate.sum() == pytest.approx(0.01 - model.outflow * np.sqrt(h[1]))
    if h[0] == 0:
        assert rate[0] >= 0
    if h[1] == 0:
        assert rate[1] >= 0
    if h[0] < h[1]:
        assert model.area * rate[0] > 0.01


def test_tank_equilibrium_satisfies_both_balances() -> None:
    model = TankParameters()
    equilibrium = np.array([(0.01 / 0.03) ** 2 + (0.01 / 0.05) ** 2, (0.01 / 0.03) ** 2])
    np.testing.assert_allclose(model.rate(equilibrium, 0.01), 0, atol=1e-15)


@pytest.mark.parametrize("parameters", [{"area": 0}, {"transfer": -1}, {"outflow": np.inf}])
def test_tank_rejects_nonphysical_parameters(parameters: dict) -> None:
    with pytest.raises(ValueError):
        TankParameters(**parameters)


@pytest.mark.parametrize(
    ("heights", "inflow"), [([-1, 1], 0), ([1], 0), ([1, np.nan], 0), ([1, 1], -1)]
)
def test_tank_rejects_invalid_state_or_inflow(heights: list[float], inflow: float) -> None:
    with pytest.raises(ValueError):
        TankParameters().rate(np.array(heights), inflow)


def test_singular_double_integrator_has_exact_hold_matrices() -> None:
    period = 0.2
    a = np.array([[0.0, 1.0], [0.0, 0.0]])
    b = np.array([[0.0], [1.0]])
    ad, bd = zoh_matrices(a, b, period)
    np.testing.assert_allclose(ad, [[1, period], [0, 1]])
    np.testing.assert_allclose(bd, [[period**2 / 2], [period]])


def test_exact_open_loop_sampling_and_held_feedback_are_distinct() -> None:
    a, b = np.array([[-1.0]]), np.array([[1.0]])
    for period in (0.1, 1.0, 10.0):
        ad, bd = zoh_matrices(a, b, period)
        assert 0 < ad.item() < 1
        held = (ad - 2 * bd).item()
        assert held == pytest.approx(3 * np.exp(-period) - 2)
        assert (abs(held) < 1) == (period < np.log(3))


def test_sampling_can_destroy_reachability_and_observability() -> None:
    a = np.array([[0.0, 1.0], [-1.0, 0.0]])
    b = np.array([[0.0], [1.0]])
    ad, bd = zoh_matrices(a, b, np.pi)
    c = np.array([[1.0, 0.0]])
    assert np.linalg.matrix_rank(np.column_stack((b, a @ b))) == 2
    assert np.linalg.matrix_rank(np.column_stack((bd, ad @ bd)), tol=1e-12) == 1
    assert np.linalg.matrix_rank(np.vstack((c, c @ ad)), tol=1e-12) == 1


@pytest.mark.parametrize("period", [-1.0, np.nan, np.inf])
def test_hold_rejects_invalid_period(period: float) -> None:
    with pytest.raises(ValueError):
        zoh_matrices(np.eye(2), np.ones((2, 1)), period)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ([[1, 2]], [[1]]),
        ([[1]], [[1, 2], [3, 4]]),
        ([[np.nan]], [[1]]),
        ([[1]], [[np.inf]]),
        ([1], [[1]]),
        ([], []),
        ([[1]], [[]]),
        ([[1j]], [[1]]),
        ([[1]], [[1j]]),
    ],
)
def test_hold_rejects_invalid_matrices(a: list, b: list) -> None:
    with pytest.raises(ValueError):
        zoh_matrices(np.array(a), np.array(b), 0.1)


def test_zero_period_is_identity_and_zero_input_effect() -> None:
    ad, bd = zoh_matrices(np.eye(2), np.ones((2, 1)), 0)
    np.testing.assert_array_equal(ad, np.eye(2))
    np.testing.assert_array_equal(bd, np.zeros((2, 1)))


def test_pbh_uses_left_eigenvectors_not_right_eigenvectors() -> None:
    a = np.array([[0.0, 1.0], [0.0, 0.0]])
    b = np.array([[0.0], [1.0]])
    right = np.array([1.0, 0.0])
    np.testing.assert_array_equal(a @ right, np.zeros(2))
    assert (right @ b).item() == 0
    assert np.linalg.matrix_rank(np.column_stack((b, a @ b))) == 2
    assert np.linalg.matrix_rank(np.column_stack((a, b))) == 2


def test_zero_eigenvalues_need_jordan_conditions() -> None:
    jordan = np.array([[0.0, 1.0], [0.0, 0.0]])
    np.testing.assert_array_equal(np.linalg.eigvals(jordan), [0, 0])
    np.testing.assert_allclose(expm(100 * jordan) @ [0, 1], [100, 1])


def test_critical_damping_does_not_imply_monotone_position() -> None:
    # q(0)=1, v(0)=-3, omega0=1 gives q=(1-2t)exp(-t).
    a = np.array([[0.0, 1.0], [-1.0, -2.0]])
    assert (expm(a) @ [1, -3])[0] < 0
    assert (expm(2 * a) @ [1, -3])[1] > 0


def test_coordinate_acceleration_contains_a_hessian_term() -> None:
    # q(t)=1+2t has zero acceleration; z=q^2 has zddot=8.
    q, velocity = 1.0, 2.0
    step = 0.001
    second_difference = (
        (q + velocity * step) ** 2 - 2 * q**2 + (q - velocity * step) ** 2
    ) / step**2
    assert second_difference == pytest.approx(8, abs=1e-8)


def test_oscillator_solution_and_energy_balance_are_independent() -> None:
    a = np.array([[0.0, 1.0], [-2.0, -0.5]])
    times = np.linspace(0, 10, 101)
    result = solve_ivp(
        lambda t, state: a @ state, (0, 10), [1, 0], t_eval=times, rtol=1e-11, atol=1e-13
    )
    assert result.success
    frequency = np.sqrt(2 - 0.25**2)
    position = np.exp(-0.25 * times) * (
        np.cos(frequency * times) + 0.25 / frequency * np.sin(frequency * times)
    )
    np.testing.assert_allclose(result.y[0], position, atol=1e-10)
    energy = result.y[0] ** 2 + result.y[1] ** 2 / 2
    assert np.all(np.diff(energy) <= 1e-12)
