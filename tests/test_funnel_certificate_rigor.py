"""Independent calculations for finite-horizon nonlinear funnel claims."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp

ROOT = Path(__file__).resolve().parents[1]


def test_robust_scalar_boundary_is_attainable_and_may_expand() -> None:
    times = np.linspace(0, 4, 101)
    for initial in (0.1, 0.8):
        radius = initial * np.exp(-times) + 0.25 * (1 - np.exp(-times))
        solution = solve_ivp(
            lambda _t, e: -e + 0.25,
            (0, 4),
            [initial],
            t_eval=times,
            rtol=1e-10,
            atol=1e-12,
        )
        assert solution.success
        assert solution.y[0] == pytest.approx(radius, abs=2e-10)
        assert (radius[-1] > radius[0]) == (initial < 0.25)


def test_saturation_prevents_fixed_tube_against_stronger_disturbance() -> None:
    radius, maximum_input, disturbance = 1.0, 0.2, 0.25
    for gain in (1, 10, 1000):
        outward_velocity = -min(gain * radius, maximum_input) + disturbance
        assert outward_velocity == pytest.approx(0.05)
        assert outward_velocity > 0


def test_exponential_attraction_does_not_give_finite_time_equality() -> None:
    solution = solve_ivp(lambda _t, e: -e, (0, 2), [0.3], rtol=1e-11, atol=1e-13)
    assert solution.success
    assert solution.y[0, -1] == pytest.approx(0.3 * np.exp(-2))
    assert solution.y[0, -1] > 0.04


def test_phase_speed_enters_moving_boundary_derivative() -> None:
    # V=xi^2, rho=exp(-tau), xi'= -xi/2, tau'=nu.
    tau = 0.4
    radius_squared = np.exp(-tau)
    for speed in (0.5, 2.0):
        derivative = -radius_squared + radius_squared * speed
        assert (derivative > 0) == (speed > 1)


def test_policy_cost_bound_requires_correct_normalization() -> None:
    initial, horizon = 0.8, 1.7
    integrated = quad(lambda t: (initial * np.exp(-t)) ** 2, 0, horizon)[0]
    value = initial**2 * (1 - np.exp(-2 * horizon)) / 2
    assert integrated == pytest.approx(value)
    assert 0.1 * value < integrated


def test_sos_equality_multiplier_has_exact_positive_remainder() -> None:
    radius = 0.5
    errors = np.linspace(-2, 2, 81)
    derivative = -2 * errors**2 + 2 * errors**4
    multiplier = 2 * (1 - radius**2 - errors**2)
    remainder = -derivative - multiplier * (errors**2 - radius**2)
    margin = radius**2 * (1 - radius**2)
    assert remainder == pytest.approx(np.full_like(errors, 2 * margin))
    assert np.all(remainder - margin > 0)
    assert multiplier[-1] < 0


def test_strict_inward_flow_and_boundary_attraction_are_distinct() -> None:
    for radius in (0.5, 1.0, 1.2):
        outward_velocity = -radius + radius**3
        assert (outward_velocity < 0) == (radius < 1)
        assert (outward_velocity > 0) == (radius > 1)
    boundary = solve_ivp(lambda _t, e: -e + e**3, (0, 2), [1.0])
    assert boundary.success
    assert boundary.y[0] == pytest.approx(np.ones_like(boundary.t))


def test_time_endpoint_checks_miss_escape_between_nodes() -> None:
    def coefficient(time: float) -> float:
        return float(-1 + 4 * np.sin(np.pi * time) ** 2)

    assert coefficient(0) < 0 and coefficient(1) < 0
    assert coefficient(0.5) > 0
    integral = quad(coefficient, 0, 1)[0]
    solution = solve_ivp(lambda t, e: coefficient(t) * e, (0, 1), [1.0], rtol=1e-10, atol=1e-12)
    assert solution.success
    assert integral == pytest.approx(1)
    assert solution.y[0, -1] == pytest.approx(np.e, rel=1e-8)


def test_omitted_remainder_reverses_the_boundary_conclusion() -> None:
    error = 0.5
    approximate_velocity = -error
    exact_velocity = -error + 8 * error**3
    gradient = 2 * error
    assert approximate_velocity < 0 < exact_velocity
    assert gradient * exact_velocity == pytest.approx(0.5)
    assert gradient * (exact_velocity - approximate_velocity) == pytest.approx(16 * error**4)
    critical_radius = 1 / np.sqrt(8)
    assert -critical_radius + 8 * critical_radius**3 == pytest.approx(0)


def test_ellipsoid_axes_and_volume_use_inverse_eigenvalues() -> None:
    eigenvalues = np.array([1.0, 4.0])
    axes = np.sqrt(1 / eigenvalues)
    area = np.pi / np.sqrt(np.prod(eigenvalues))
    assert axes == pytest.approx([1, 0.5])
    assert area == pytest.approx(np.pi / 2)
    assert np.sqrt(9 / (9 * eigenvalues)) == pytest.approx(axes)
    assert np.pi / np.sqrt(np.prod(9 * eigenvalues)) == pytest.approx(area / 9)
    output = np.array([1.0, 0.0])
    shapes = (np.diag([1.0, 100.0]), np.diag([100.0, 1.0]))
    assert np.linalg.det(shapes[0]) == pytest.approx(np.linalg.det(shapes[1]))
    bounds = [np.sqrt(output @ np.linalg.solve(shape, output)) for shape in shapes]
    assert bounds == pytest.approx([1, 0.1])


def test_negative_logdet_maximization_is_not_concave() -> None:
    first, second = np.diag([1.0, 4.0]), np.diag([4.0, 1.0])
    endpoint_mean = (-np.linalg.slogdet(first)[1] - np.linalg.slogdet(second)[1]) / 2
    midpoint_value = -np.linalg.slogdet((first + second) / 2)[1]
    assert midpoint_value < endpoint_mean


def test_shape_matrix_polytope_support_constraint_is_exact() -> None:
    shape = np.diag([2.0, 0.5])
    center = np.array([0.2, -0.1])
    normal = np.array([0.6, 0.8])
    unit_direction = shape @ normal / np.linalg.norm(shape @ normal)
    support_point = shape @ unit_direction + center
    bound = np.linalg.norm(shape @ normal) + normal @ center
    assert normal @ support_point == pytest.approx(bound)


def test_small_negative_polynomial_coefficient_is_not_global_positivity() -> None:
    assert 1 + 1**2 - 1e-8 * 1**4 > 0
    large_state = 20_000.0
    assert 1 + large_state**2 - 1e-8 * large_state**4 < 0


def test_reset_composition_requires_full_image_containment() -> None:
    incoming_radius, reset_error = 0.3, 0.05
    required_radius = 2 * incoming_radius + reset_error
    samples = np.array([-incoming_radius, incoming_radius])
    reset_images = 2 * samples[:, None] + np.array([-reset_error, reset_error])
    assert np.max(np.abs(reset_images)) == pytest.approx(required_radius)
    assert np.max(np.abs(reset_images)) > incoming_radius


@pytest.mark.parametrize(
    "source",
    [
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch07_funnel_synthesis.tex",
        "articles/motion-control/chapter7.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ],
)
def test_all_editions_distinguish_certificates_from_uncomputed_golf_claims(source: str) -> None:
    text = (ROOT / source).read_text(encoding="utf-8")
    if source.endswith("volume2_content.qmd"):
        text = text.split("## Funnel Synthesis", 1)[1].split("## Phase-Variable Control", 1)[0]
    else:
        text = text.split(r"\chapter{Funnel Synthesis}", 1)[1].split(
            r"\chapter{Phase-Variable Control}", 1
        )[0]
    for required in [
        r"\dot\rho",
        "outer bound",
        "inner subset",
        "unrestricted in sign",
        "not a whole-interval proof",
        "not a convex optimization problem",
        "a controller",
        "https://arxiv.org/abs/1010.3013",
    ]:
        assert required in text
    for incorrect in [
        "exact structural limits",
        "true numerical portrait of athletic consistency",
        "migrating out of the time domain entirely",
        "forces $-\\dot{V} > 0$",
    ]:
        assert incorrect not in text
