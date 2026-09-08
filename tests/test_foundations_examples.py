"""Independent numerical checks for tangent-space foundations."""

import numpy as np
import pytest
from scipy.linalg import expm

from src.tools.foundations_examples import central_jacobian, pendulum_field, residual_table


def test_dimensioned_pendulum_and_torque_equilibrium() -> None:
    """A nonunit length/inertia exposes the omitted dimensional factors."""
    parameters = (2.0, 3.0, 10.0, 0.6)  # mass, length, gravity, damping
    angle = np.pi / 6
    torque = 30.0
    np.testing.assert_allclose(
        pendulum_field(np.array([angle, 0.0]), torque, parameters), 0, atol=1e-14
    )

    def field(state: np.ndarray) -> np.ndarray:
        return pendulum_field(state, torque, parameters)

    actual = central_jacobian(field, np.array([angle, 0.0]), np.array([1e-5, 1e-5]))
    expected = np.array([[0.0, 1.0], [-10 / 3 * np.cos(angle), -0.6 / 18]])
    np.testing.assert_allclose(actual, expected, atol=1e-9)
    changed = pendulum_field(np.array([angle, 0.0]), torque + 18, parameters)
    np.testing.assert_allclose(changed, [0, 1], atol=1e-14)


def test_nonsquare_derivative_and_bad_steps() -> None:
    """Use a polynomial whose finite-difference truncation is exactly zero."""

    def field(state: np.ndarray) -> np.ndarray:
        x, y = state
        return np.array([x * y, x**2 + y, 3 * x - 2 * y])

    actual = central_jacobian(field, np.array([2.0, 3.0]), np.array([1e-4, 2e-4]))
    np.testing.assert_allclose(actual, [[3, 2], [4, 1], [3, -2]], atol=1e-10)
    with pytest.raises(ValueError, match="positive"):
        central_jacobian(field, np.zeros(2), np.array([0.0, 1.0]))
    with pytest.raises(ValueError, match="shape"):
        central_jacobian(field, np.zeros(2), np.ones(3))
    with pytest.raises(ValueError, match="representable"):
        central_jacobian(field, np.array([1e20, 1e20]), np.ones(2))


def test_pendulum_residuals_against_trigonometric_identity() -> None:
    """A cancellation-resistant identity checks direct residual subtraction."""
    angle = np.pi / 6

    def field(state: np.ndarray) -> np.ndarray:
        return pendulum_field(state, 5.0, (1.0, 1.0, 10.0, 0.1))

    jacobian = np.array([[0.0, 1.0], [-10 * np.cos(angle), -0.1]])
    sizes = np.array([0.1, 0.01, 0.001, 0.0001])
    table = residual_table(
        field, jacobian, np.array([angle, 0.0]), np.column_stack((sizes, np.zeros(4)))
    )
    expected = 10 * (
        2 * np.sin(angle) * np.sin(sizes / 2) ** 2 + np.cos(angle) * (sizes - np.sin(sizes))
    )
    np.testing.assert_allclose(table[:, 1], expected, atol=2e-15)
    assert table[-1, 2] == pytest.approx(2.5, rel=1e-4)


def test_directional_derivatives_do_not_supply_uniform_remainder() -> None:
    """All fixed-ray derivatives vanish, while a curved approach has ratio 1/2."""
    size = np.array([1e-2, 1e-3, 1e-4])
    values = size / 2  # f(x,x^3) for f=x^4 y/(x^6+y^2)
    ratios = values / np.sqrt(size**2 + size**6)
    np.testing.assert_allclose(ratios, 0.5, atol=3e-9)
    for direction in [(1.0, 0.0), (0.0, 1.0), (1.0, 2.0), (-3.0, 1.0)]:
        x, y = 1e-5 * np.array(direction)
        value = x**4 * y / (x**6 + y**2) if x or y else 0.0
        assert abs(value / 1e-5) < 1e-8


def test_moving_coordinate_jacobian_for_a_time_independent_chart() -> None:
    """xdot=1, z=exp(x) gives Az=1 although Ax=0."""
    start, duration = 0.2, 0.7
    tx0, tx1 = np.exp(start), np.exp(start + duration)
    assert tx1 / tx0 == pytest.approx(np.exp(duration))
    delta = 1e-6
    derivative = np.exp(start + delta + duration) - np.exp(start - delta + duration)
    derivative /= 2 * delta * tx0
    assert derivative == pytest.approx(np.exp(duration), rel=1e-9)


def test_nonnormal_growth_is_not_given_by_eigenvalues() -> None:
    """A stable triangular system can strongly amplify a unit initial variation."""
    matrix = np.array([[-1.0, 10.0], [0.0, -1.0]])
    flow = expm(matrix)
    np.testing.assert_allclose(flow, np.exp(-1) * np.array([[1.0, 10.0], [0.0, 1.0]]))
    assert max(abs(np.linalg.eigvals(flow))) < 1
    assert np.linalg.norm(flow @ np.array([0.0, 1.0])) > 3.69
    assert np.linalg.svd(flow, compute_uv=False)[0] > 3.71


@pytest.mark.parametrize("step", [0.1, 0.01, 0.001])
def test_transverse_switch_sensitivity_includes_changed_event_time(step: float) -> None:
    """Cross x=0 at speed 1 then speed 2: common-time sensitivity is 2."""

    def final(start: float) -> float:
        return 2 * (2 + start)  # start<0, initial time0, final time2

    derivative = (final(-1 + step) - final(-1 - step)) / (2 * step)
    assert derivative == pytest.approx(2.0)


def test_invalid_residual_inputs_fail_explicitly() -> None:
    def field(state: np.ndarray) -> np.ndarray:
        return state**2

    with pytest.raises(ValueError, match="nonzero"):
        residual_table(field, np.eye(2), np.ones(2), np.zeros((1, 2)))
    with pytest.raises(ValueError, match="shape"):
        residual_table(field, np.ones((1, 2)), np.ones(2), np.ones((1, 2)))
    with pytest.raises(ValueError, match="positive"):
        pendulum_field(np.zeros(2), 0.0, (0.0, 1.0, 10.0, 0.1))


@pytest.mark.parametrize("state", [np.array([]), np.array([np.nan, 0.0]), np.ones((1, 2))])
def test_nonfinite_or_nonvector_states_are_rejected(state: np.ndarray) -> None:
    with pytest.raises(ValueError, match="finite vector"):
        pendulum_field(state, 0.0, (1.0, 1.0, 10.0, 0.1))


def test_changed_field_shape_and_nonfinite_residual_data() -> None:
    def changing(state: np.ndarray) -> np.ndarray:
        return np.ones(1 if state[0] == 0 else 2)

    with pytest.raises(ValueError, match="shape"):
        central_jacobian(changing, np.zeros(1), np.ones(1))
    with pytest.raises(ValueError, match="shape"):
        residual_table(changing, np.ones((1, 1)), np.zeros(1), np.ones((1, 1)))
    with pytest.raises(ValueError, match="finite"):
        residual_table(changing, np.full((1, 1), np.nan), np.zeros(1), np.ones((1, 1)))
    with pytest.raises(ValueError, match="shapes"):
        pendulum_field(np.ones(3), 0.0, (1.0, 1.0, 10.0, 0.1))


def test_two_link_mass_and_velocity_terms_follow_lagrange_equations() -> None:
    """Symbolic differentiation is independent of the printed matrix assembly."""
    import sympy as sp

    q1, q2, v1, v2, a1, a2 = sp.symbols("q1 q2 v1 v2 a1 a2", real=True)
    m1, m2, l1, l2, gravity = sp.symbols("m1 m2 l1 l2 gravity", positive=True)
    position = sp.Matrix(
        [
            l1 * sp.sin(q1),
            -l1 * sp.cos(q1),
            l1 * sp.sin(q1) + l2 * sp.sin(q2),
            -l1 * sp.cos(q1) - l2 * sp.cos(q2),
        ]
    )
    velocity = position.jacobian([q1, q2]) * sp.Matrix([v1, v2])
    kinetic = (
        m1 * velocity[:2, :].dot(velocity[:2, :]) + m2 * velocity[2:, :].dot(velocity[2:, :])
    ) / 2
    potential = gravity * (m1 * position[1] + m2 * position[3])
    mass = sp.Matrix(
        [
            [(m1 + m2) * l1**2, m2 * l1 * l2 * sp.cos(q1 - q2)],
            [m2 * l1 * l2 * sp.cos(q1 - q2), m2 * l2**2],
        ]
    )
    bias = sp.Matrix(
        [m2 * l1 * l2 * sp.sin(q1 - q2) * v2**2, -m2 * l1 * l2 * sp.sin(q1 - q2) * v1**2]
    )
    expected = (
        mass * sp.Matrix([a1, a2])
        + bias
        + sp.Matrix([sp.diff(potential, q1), sp.diff(potential, q2)])
    )
    for index, (q, v) in enumerate([(q1, v1), (q2, v2)]):
        momentum = sp.diff(kinetic, v)
        total = sum(sp.diff(momentum, z) * dz for z, dz in [(q1, v1), (q2, v2), (v1, a1), (v2, a2)])
        assert (
            sp.simplify(sp.trigsimp(total - sp.diff(kinetic - potential, q) - expected[index])) == 0
        )
