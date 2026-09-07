"""Independent checks of the hybrid reference's executable and derived examples."""

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/tangent-hyperplane-articles/Advanced/Hybrid_Tangent_Spaces.qmd"
GRAVITY_M_S2 = 9.81


@pytest.fixture(scope="module")
def example() -> dict[str, Any]:
    """Execute the exact self-contained example published to readers."""
    text = ARTICLE.read_text(encoding="utf-8")
    block = re.search(r"```python\n(# Event-resolved bounce example\n.*?)\n```", text, re.S)
    assert block is not None, "Publish the executable event-resolved example"
    namespace: dict[str, Any] = {}
    exec(compile(block.group(1), str(ARTICLE), "exec"), namespace)
    return namespace


@pytest.mark.parametrize(
    "height,velocity,final_time", [(1.0, 0.0, 0.7), (0.6, -1.2, 0.5), (0.8, 1.0, 0.8)]
)
def test_published_bounce_jacobian_matches_relocated_events(
    example: dict[str, Any], height: float, velocity: float, final_time: float
) -> None:
    state = np.array([height, velocity])
    rollout = example["one_bounce"]
    terminal, jacobian, _ = rollout(state, final_time, 0.8)
    epsilon = 1e-6
    finite = np.column_stack(
        [
            (
                rollout(state + epsilon * d, final_time, 0.8)[0]
                - rollout(state - epsilon * d, final_time, 0.8)[0]
            )
            / (2 * epsilon)
            for d in np.eye(2)
        ]
    )
    np.testing.assert_allclose(jacobian, finite, rtol=2e-7, atol=2e-8)
    speed = np.sqrt(velocity**2 + 2 * GRAVITY_M_S2 * height)
    impact_time = (velocity + speed) / GRAVITY_M_S2
    elapsed = final_time - impact_time
    np.testing.assert_allclose(
        terminal,
        [
            0.8 * speed * elapsed - GRAVITY_M_S2 * elapsed**2 / 2,
            0.8 * speed - GRAVITY_M_S2 * elapsed,
        ],
    )


def test_published_restitution_derivative(example: dict[str, Any]) -> None:
    rollout = example["one_bounce"]
    state = np.array([1.0, 0.0])
    _, _, derivative = rollout(state, 0.7, 0.8)
    epsilon = 1e-6
    finite = (rollout(state, 0.7, 0.8 + epsilon)[0] - rollout(state, 0.7, 0.8 - epsilon)[0]) / (
        2 * epsilon
    )
    np.testing.assert_allclose(derivative, finite, rtol=1e-8, atol=1e-8)


@pytest.mark.parametrize(
    "state,time,restitution",
    [
        ([1.0, 0.0], 0.1, 0.8),
        ([1.0, 0.0], 2.0, 0.8),
        ([1.0, 0.0], 0.7, 0.0),
        ([-1.0, 0.0], 0.7, 0.8),
        ([np.nan, 0.0], 0.7, 0.8),
    ],
)
def test_published_example_rejects_unsupported_event_branches(
    example: dict[str, Any], state: list[float], time: float, restitution: float
) -> None:
    with pytest.raises(ValueError):
        example["one_bounce"](np.array(state), time, restitution)


def test_mass_metric_impact_and_loss() -> None:
    mass = np.array([[3.0, 0.4], [0.4, 1.0]])
    normal = np.array([[1.0, 2.0]])
    velocity = np.array([-1.0, -2.0])
    mobility = np.linalg.solve(mass, normal.T)
    compliance = normal @ mobility
    projection = mobility @ np.linalg.solve(compliance, normal)
    np.testing.assert_allclose(projection @ projection, projection)
    np.testing.assert_allclose(projection.T @ mass, mass @ projection)
    restitution = 0.65
    post = velocity - (1 + restitution) * projection @ velocity
    np.testing.assert_allclose(normal @ post, -restitution * normal @ velocity)
    loss = (velocity @ mass @ velocity - post @ mass @ post) / 2
    expected = (
        (1 - restitution**2)
        * float((normal @ velocity) @ np.linalg.solve(compliance, normal @ velocity))
        / 2
    )
    assert loss == pytest.approx(expected)


def test_dissipative_ball_saltation_can_amplify_scaled_errors() -> None:
    restitution, incoming = 0.8, -5.0
    saltation = np.array(
        [[-restitution, 0], [-GRAVITY_M_S2 * (1 + restitution) / incoming, -restitution]]
    )
    assert max(abs(np.linalg.eigvals(saltation))) == pytest.approx(0.8)
    assert np.linalg.norm(saltation, 2) > 3.5
    # Units: 1 m and 1 m/s define the numerical state scaling here.
    assert np.linalg.norm(saltation @ np.array([1.0, 0.0])) > 1


def test_noncommuting_uniform_contractions_converge() -> None:
    a = 0.8 * np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
    b = 0.8 * np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])
    assert not np.allclose(a @ b, b @ a)
    product = np.eye(3)
    for index in range(50):
        product = (a if index % 2 else b) @ product
    assert np.linalg.norm(product, 2) == pytest.approx(0.8**50)
    count = 1000
    strict_only = np.prod([1 - 1 / (k + 1) ** 2 for k in range(1, count + 1)])
    assert strict_only == pytest.approx((count + 2) / (2 * (count + 1)))


def test_contact_acceleration_requires_jacobian_rate() -> None:
    # Unit circular bilateral constraint at (1,0), tangent speed 2.
    jacobian = np.array([[1.0, 0.0]])
    velocity = np.array([0.0, 2.0])
    jacobian_rate_velocity = velocity @ velocity
    reaction = np.linalg.solve(jacobian @ jacobian.T, np.array([-jacobian_rate_velocity]))
    acceleration = jacobian.T @ reaction
    np.testing.assert_allclose(acceleration, [-4.0, 0.0])
    assert float((jacobian @ acceleration)[0] + jacobian_rate_velocity) == pytest.approx(0)


def test_moving_event_cost_boundary_term() -> None:
    def cost(initial: float) -> float:
        crossing = 1 - initial  # xdot=1 until x=1, then xdot=2.
        return 3 * crossing + 5 * (2 - crossing) + 7

    epsilon = 1e-6
    finite = (cost(0.2 + epsilon) - cost(0.2 - epsilon)) / (2 * epsilon)
    # Event cost is c=7*x on x=1: its event-aligned derivative is zero.
    c_x, pre_rate, post_rate, pre_flow = 7, 3, 5, 1
    augmented_row = c_x - (pre_rate - post_rate + c_x * pre_flow) / pre_flow
    assert finite == pytest.approx(augmented_row)
    assert augmented_row == 2


def test_second_order_composition_needs_map_curvature() -> None:
    # F(x)=x^2, V(y)=y: V''=0 but (V o F)''=2.
    jacobian, value_gradient, value_hessian, map_hessian = 2.0, 1.0, 0.0, 2.0
    full = jacobian * value_hessian * jacobian + value_gradient * map_hessian
    assert full == 2


def test_golf_collision_momentum_energy_and_average_force() -> None:
    club_mass, ball_mass, speed, restitution = 0.2, 0.046, 50.0, 0.78
    ball = (1 + restitution) * club_mass * speed / (club_mass + ball_mass)
    club = speed - ball_mass * ball / club_mass
    reduced = club_mass * ball_mass / (club_mass + ball_mass)
    loss = 0.5 * reduced * (1 - restitution**2) * speed**2
    assert club_mass * club + ball_mass * ball == pytest.approx(club_mass * speed)
    assert (
        0.5 * club_mass * speed**2 - 0.5 * club_mass * club**2 - 0.5 * ball_mass * ball**2
        == pytest.approx(loss)
    )
    assert ball == pytest.approx(72.3577235772)
    assert 6600 < ball_mass * ball / 0.0005 < 6700


def test_article_withdraws_false_optimization_and_reset_claims() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    assert "x_plus = jnp.dot(S, x_minus)" not in text
    assert "Hybrid DDP converges in 5-10 iterations" not in text
    assert "The tangent space does not exist." not in text
    assert "# Event-resolved bounce example" in text


def test_moving_floor_sensitivity_uses_relative_approach_speed() -> None:
    """Independently relocate contact with an upward-moving floor."""
    floor_speed, restitution, final_time = 0.3, 0.8, 0.7

    def endpoint(state: np.ndarray) -> np.ndarray:
        height, velocity = state
        relative = velocity - floor_speed
        root = np.sqrt(relative**2 + 2 * GRAVITY_M_S2 * height)
        event = (relative + root) / GRAVITY_M_S2
        incoming = velocity - GRAVITY_M_S2 * event
        outgoing = floor_speed - restitution * (incoming - floor_speed)
        elapsed = final_time - event
        return np.array(
            [
                floor_speed * event + outgoing * elapsed - GRAVITY_M_S2 * elapsed**2 / 2,
                outgoing - GRAVITY_M_S2 * elapsed,
            ]
        )

    initial = np.array([1.0, 0.0])
    speed = np.sqrt(floor_speed**2 + 2 * GRAVITY_M_S2)
    event = (-floor_speed + speed) / GRAVITY_M_S2
    incoming = -GRAVITY_M_S2 * event
    saltation = np.array(
        [
            [-restitution, 0],
            [-GRAVITY_M_S2 * (1 + restitution) / (incoming - floor_speed), -restitution],
        ]
    )
    before = np.array([[1, event], [0, 1]])
    after = np.array([[1, final_time - event], [0, 1]])
    epsilon = 1e-6
    finite = np.column_stack(
        [
            (endpoint(initial + epsilon * d) - endpoint(initial - epsilon * d)) / (2 * epsilon)
            for d in np.eye(2)
        ]
    )
    np.testing.assert_allclose(after @ saltation @ before, finite, atol=1e-8)


def test_saltation_is_independent_of_guard_reset_extension() -> None:
    """Adding a multiple of the moving guard must cancel from sensitivity."""
    guard_x = np.array([1.0, 0.2])
    guard_t = -0.3
    incoming = np.array([-2.0, -1.0])
    outgoing = np.array([1.0, -1.0])
    reset_x = np.diag([1.0, -0.7])
    reset_t = np.array([0.0, 0.1])
    denominator = guard_t + guard_x @ incoming

    def matrix(jacobian: np.ndarray, time_derivative: np.ndarray) -> np.ndarray:
        return (
            jacobian
            + np.outer(outgoing - jacobian @ incoming - time_derivative, guard_x) / denominator
        )

    extension = np.array([0.4, -0.5])
    np.testing.assert_allclose(
        matrix(reset_x, reset_t),
        matrix(reset_x + np.outer(extension, guard_x), reset_t + extension * guard_t),
    )
