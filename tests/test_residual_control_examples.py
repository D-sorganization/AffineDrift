"""Check teaching calculations against independent differential equations."""

import math

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from scipy.stats import fisher_exact

from src.tools.residual_control_examples import residual_step_limit, scalar_nonlinear_flow


@pytest.mark.parametrize("growth", [0.0, 1e-12, 2.0])
def test_step_limit_reaches_comparison_budget(growth: float) -> None:
    """Integrate the comparison ODE independently to verify the time inversion."""
    forcing, budget = 0.005, 0.001
    step = residual_step_limit(forcing, budget, growth)
    solution = solve_ivp(
        lambda time, state: growth * state + forcing,
        (0.0, step),
        [0.0],
        rtol=1e-11,
        atol=1e-14,
    )
    assert solution.success
    assert solution.y[0, -1] == pytest.approx(budget, rel=1e-9)


def test_step_limit_scales_as_time() -> None:
    """A change of time unit scales both rates and the resulting interval."""
    seconds = residual_step_limit(0.005, 0.001, 2.0)
    milliseconds = residual_step_limit(0.005 / 1000, 0.001, 2.0 / 1000)
    assert milliseconds == pytest.approx(seconds * 1000)
    assert residual_step_limit(0.0, 0.001, 2.0) == math.inf
    assert residual_step_limit(0.005, 0.0, 2.0) == 0.0


def test_step_limit_does_not_overflow_an_intermediate_ratio() -> None:
    """A finite solution must survive a large budget/forcing intermediate value."""
    assert residual_step_limit(1e-200, 1e200, 1e-200) == pytest.approx(200 * math.log(10) / 1e-200)
    assert residual_step_limit(1e308, 1.0, 1e-308) == pytest.approx(1e-308, abs=0.0)
    with pytest.raises(ValueError, match="representable"):
        residual_step_limit(1e-308, 1e308, 0.0)


def test_scalar_flow_retains_large_initial_state_at_zero_time() -> None:
    """Rescaling x=initial*y, tau=initial*t gives y'=y/initial+y^2."""
    initial = 1e16
    actual = scalar_nonlinear_flow(initial, np.array([0.0, 1e-18]))
    assert actual[0] == initial
    assert actual[1] == pytest.approx(initial / 0.99, rel=1e-14)
    with pytest.raises(ValueError, match="representable"):
        scalar_nonlinear_flow(1e308, np.array([5e-309]))


@pytest.mark.parametrize(
    "arguments", [(-1, 1, 1), (1, -1, 1), (1, 1, -1), (math.nan, 1, 1), (1, math.inf, 1)]
)
def test_invalid_step_contract(arguments: tuple[float, float, float]) -> None:
    """The helper implements only the stated non-negative-growth convention."""
    with pytest.raises(ValueError, match="finite and non-negative"):
        residual_step_limit(*arguments)


@pytest.mark.parametrize("initial", [0.0, 0.01, 0.1])
def test_scalar_flow_against_numerical_integration(initial: float) -> None:
    """The closed form solves x'=x+x^2 before its finite-time pole."""
    times = np.linspace(0, 1, 11)
    solution = solve_ivp(
        lambda time, state: state + state**2,
        (0.0, 1.0),
        [initial],
        t_eval=times,
        rtol=1e-11,
        atol=1e-14,
    )
    assert solution.success
    np.testing.assert_allclose(scalar_nonlinear_flow(initial, times), solution.y[0], rtol=1e-9)


@pytest.mark.parametrize(
    "initial,times", [(-1, [0]), (0.1, [-1]), (1, [1]), (0.1, [math.nan]), (math.inf, [0])]
)
def test_flow_domain_excludes_the_pole(initial: float, times: list[float]) -> None:
    """Do not continue an exact formula through loss of solution existence."""
    with pytest.raises(ValueError):
        scalar_nonlinear_flow(initial, np.array(times))


def test_pendulum_hessian_sign_and_units() -> None:
    """Central differences independently check the torque-driven acceleration Hessian."""
    from src.core.constants import GRAVITY_M_S2

    length = 1.0
    theta = 0.7
    perturbation = 1e-4

    def acceleration(angle: float) -> float:
        return float(-GRAVITY_M_S2 / length * np.sin(angle))

    second = (
        acceleration(theta + perturbation)
        - 2 * acceleration(theta)
        + acceleration(theta - perturbation)
    ) / perturbation**2
    assert second == pytest.approx(GRAVITY_M_S2 / length * np.sin(theta), rel=1e-6)


def test_scalar_tube_boundary_is_inward_under_all_disturbances() -> None:
    """A Taylor-validity radius alone does not establish this invariance condition."""
    disturbance_limit = 0.1
    radius = 0.1
    # Affine dependence on w means the two endpoint disturbances suffice.
    disturbance = np.array([-disturbance_limit, disturbance_limit])
    assert np.all(-2 * radius + radius**2 + disturbance < 0)
    assert np.all(2 * radius + radius**2 + disturbance > 0)
    too_small = 0.01
    assert -2 * too_small + too_small**2 + disturbance_limit > 0


def test_hypothetical_fisher_table_from_hypergeometric_probabilities() -> None:
    """The critique must state the correct test and cannot invent an experiment."""
    probabilities = np.array([math.comb(20, k) * math.comb(20, 4 - k) for k in range(5)])
    probabilities = probabilities / math.comb(40, 4)
    expected = float(probabilities[[0, 1, 3, 4]].sum())
    result = fisher_exact([[3, 17], [1, 19]])
    assert result.pvalue == pytest.approx(expected)
    assert expected == pytest.approx(0.604989604989605)
    assert fisher_exact([[3, 17], [1, 19]], alternative="greater").pvalue == pytest.approx(
        probabilities[3:].sum()
    )


def test_rk4_can_destabilize_a_decaying_mode_with_a_large_step() -> None:
    """Direct RK4 stages refute the critique's proposed lower stability bound."""

    def step(duration: float) -> float:
        first = -1.0
        second = -(1 + duration * first / 2)
        third = -(1 + duration * second / 2)
        fourth = -(1 + duration * third)
        return 1 + duration * (first + 2 * second + 2 * third + fourth) / 6

    assert step(1.0) == pytest.approx(3 / 8)
    assert step(3.0) == pytest.approx(11 / 8)


def test_stable_eigenvalues_do_not_prevent_transient_amplification() -> None:
    """The article's non-normal example requires a propagator norm bound."""
    matrix = np.array([[-1.0, 10.0], [0.0, -1.0]])
    duration = 0.2
    transition = expm(duration * matrix)
    expected = math.exp(-duration) * np.array([[1.0, 10 * duration], [0.0, 1.0]])
    np.testing.assert_allclose(transition, expected)
    assert np.linalg.norm(transition, ord=2) > 1


def test_maximum_component_hessian_is_not_euclidean_output_bound() -> None:
    """Two identical quadratic outputs need a root-sum-square component factor."""
    hessians = np.array([[[2.0]], [[2.0]]])
    direction = np.ones(1)
    vector_value = np.einsum("kij,i,j->k", hessians, direction, direction)
    assert np.linalg.norm(vector_value) == pytest.approx(2 * math.sqrt(2))
    assert np.linalg.norm(vector_value) > 2
