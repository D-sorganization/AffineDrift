"""Independent checks for the reference's control and mechanical case studies."""

from math import cos, exp, sin, sqrt
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp
from scipy.linalg import expm, solve

GRAVITY_M_S2 = 9.80665
SOURCE = (
    Path(__file__).resolve().parents[1]
    / "articles/tangent-hyperplane-articles/Tangent_Hyperplanes_Unified_Thesis.qmd"
)


def test_costate_variation_enforces_the_complete_dynamic_residual() -> None:
    # x=t^2, u=3t, dynamics x_dot=u, lambda variation eta=t.
    def augmented(amplitude: float) -> float:
        return quad(lambda t: amplitude * t * (3 * t - 2 * t), 0, 1)[0]

    step = 1e-5
    derivative = (augmented(step) - augmented(-step)) / (2 * step)
    assert derivative == pytest.approx(1 / 3)
    missing_state_rate = quad(lambda t: t * 3 * t, 0, 1)[0]
    assert missing_state_rate == pytest.approx(1.0)


def test_minimum_time_double_integrator_uses_the_minimizing_sign() -> None:
    for time in [0.0, 0.3, 0.9, 1.1, 1.7, 2.0]:
        costate_velocity = time - 1
        control = -np.sign(costate_velocity)
        velocity = time if time < 1 else 2 - time
        hamiltonian = 1 - velocity + costate_velocity * control
        assert hamiltonian == pytest.approx(0.0)
        assert costate_velocity * control < costate_velocity * (-control)
    displacement = quad(lambda t: t if t < 1 else 2 - t, 0, 2)[0]
    assert displacement == pytest.approx(1.0)


def test_box_constrained_quadratic_requires_a_weighted_projection() -> None:
    weight = np.array([[2.0, 1.0], [1.0, 2.0]])
    unconstrained = np.array([2.0, 0.0])
    clipped = np.clip(unconstrained, -1, 1)
    optimum = np.array([1.0, 0.5])
    gradient = weight @ (optimum - unconstrained)
    assert gradient == pytest.approx([-1.5, 0.0])
    upper_multiplier = np.array([1.5, 0.0])
    assert gradient + upper_multiplier == pytest.approx([0.0, 0.0])
    assert np.dot(upper_multiplier, 1 - optimum) == pytest.approx(0.0)
    assert (optimum - unconstrained) @ weight @ (optimum - unconstrained) < (
        clipped - unconstrained
    ) @ weight @ (clipped - unconstrained)


def test_minimum_squared_input_solution_matches_endpoint_and_cost() -> None:
    duration, displacement = 2.0, 3.0

    def control(time: float) -> float:
        return 6 * displacement / duration**2 - 12 * displacement * time / duration**3

    velocity = quad(control, 0, duration)[0]
    position = quad(lambda t: (duration - t) * control(t), 0, duration)[0]
    cost = 0.5 * quad(lambda t: control(t) ** 2, 0, duration)[0]
    assert velocity == pytest.approx(0.0, abs=1e-12)
    assert position == pytest.approx(displacement)
    assert cost == pytest.approx(6 * displacement**2 / duration**3)


def test_exact_sampled_input_gain_differs_from_euler_gain() -> None:
    interval = 0.2
    generator = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0]])
    transition = expm(interval * generator)
    assert transition[:2, 2] == pytest.approx([interval**2 / 2, interval])
    assert transition[:2, 2] != pytest.approx([0.0, interval])


def test_euler_converges_even_when_the_physical_solution_grows() -> None:
    errors = [abs((1 + 1 / steps) ** steps - exp(1)) for steps in [100, 200, 400]]
    assert errors[0] / errors[1] == pytest.approx(2, rel=0.01)
    assert errors[1] / errors[2] == pytest.approx(2, rel=0.01)


def test_rk4_global_order_is_distinct_from_single_step_order() -> None:
    def stability(z: float) -> float:
        return 1 + z + z**2 / 2 + z**3 / 6 + z**4 / 24

    global_errors = [abs(stability(-1 / n) ** n - exp(-1)) for n in [10, 20, 40]]
    local_errors = [abs(stability(-h) - exp(-h)) for h in [0.1, 0.05, 0.025]]
    assert global_errors[1] / global_errors[2] == pytest.approx(16, rel=0.03)
    assert local_errors[1] / local_errors[2] == pytest.approx(32, rel=0.01)


def test_stiff_decay_distinguishes_absolute_stability_and_damping() -> None:
    z = -100.0
    euler = 1 + z
    backward = 1 / (1 - z)
    trapezoidal = (1 + z / 2) / (1 - z / 2)
    assert abs(euler) > 1
    assert 0 < backward < 0.01
    assert -1 < trapezoidal < -0.95


def test_ddp_retains_all_value_weighted_transition_hessians() -> None:
    point = np.array([0.3, -0.2])

    def objective(z: np.ndarray) -> float:
        x, u = z
        transition = x * x + x * u + u * u
        return 0.5 * (x * x + u * u) + 0.2 * x * u + 0.5 * transition**2

    x, u = point
    transition = x * x + x * u + u * u
    gradient = np.array([2 * x + u, x + 2 * u])
    cost_hessian = np.array([[1.0, 0.2], [0.2, 1.0]])
    transition_hessian = np.array([[2.0, 1.0], [1.0, 2.0]])
    full = cost_hessian + np.outer(gradient, gradient) + transition * transition_hessian
    step = 1e-4
    numerical = np.empty((2, 2))
    for i in range(2):
        for j in range(2):
            first, second = np.eye(2)[i] * step, np.eye(2)[j] * step
            numerical[i, j] = (
                objective(point + first + second)
                - objective(point + first - second)
                - objective(point - first + second)
                + objective(point - first - second)
            ) / (4 * step**2)
    assert full == pytest.approx(numerical, abs=1e-7)
    assert full == pytest.approx(np.array([[1.3, 0.23], [0.23, 1.15]]))


def cw_matrices() -> tuple[np.ndarray, np.ndarray]:
    """Return the declared circular-reference model in SI units."""
    orbital_rate, mass = 0.001, 100.0
    state = np.zeros((6, 6))
    state[:3, 3:] = np.eye(3)
    state[3, 0], state[3, 4] = 3 * orbital_rate**2, 2 * orbital_rate
    state[4, 3], state[5, 2] = -2 * orbital_rate, -(orbital_rate**2)
    control = np.zeros((6, 3))
    control[3:] = np.eye(3) / mass
    return state, control


def test_cw_riccati_solution_matches_a_condensed_quadratic_program() -> None:
    continuous, input_matrix = cw_matrices()
    interval, steps = 20.0, 50
    augmented = np.zeros((9, 9))
    augmented[:6, :6], augmented[:6, 6:] = continuous, input_matrix
    exact = expm(interval * augmented)
    transition, gain = exact[:6, :6], exact[:6, 6:]
    terminal_cost = np.diag([1e4] * 3 + [1e2] * 3)
    value = terminal_cost.copy()
    gains = []
    for _ in range(steps):
        hessian = interval * np.eye(3) + gain.T @ value @ gain
        feedback = -solve(hessian, gain.T @ value @ transition, assume_a="pos")
        gains.append(feedback)
        value = transition.T @ value @ transition + transition.T @ value @ gain @ feedback
        value = (value + value.T) / 2
    initial = np.array([100.0, 50.0, 20.0, 0.01, 0.02, 0.0])
    state, controls = initial.copy(), []
    for feedback in reversed(gains):
        control = feedback @ state
        controls.append(control)
        state = transition @ state + gain @ control
    controls = np.array(controls)
    endpoint_gain = np.hstack(
        [np.linalg.matrix_power(transition, steps - 1 - k) @ gain for k in range(steps)]
    )
    free_endpoint = np.linalg.matrix_power(transition, steps) @ initial
    hessian = interval * np.eye(3 * steps) + endpoint_gain.T @ terminal_cost @ endpoint_gain
    linear = endpoint_gain.T @ terminal_cost @ free_endpoint
    independent = solve(hessian, -linear, assume_a="pos").reshape(steps, 3)
    assert controls == pytest.approx(independent, abs=2e-8)
    assert state == pytest.approx(
        [1.66617103e-6, 3.04858641e-7, 1.48659828e-7, -0.0507126798, 0.0117397985, -0.00839609917],
        abs=1e-9,
    )
    cost = 0.5 * state @ terminal_cost @ state + 0.5 * interval * np.sum(controls**2)
    assert cost == pytest.approx(1.2279677534473972, rel=1e-9)
    assert cost == pytest.approx(0.5 * initial @ value @ initial, rel=1e-9)
    assert interval * np.linalg.norm(controls, axis=1).sum() == pytest.approx(39.3975087381)
    assert np.linalg.norm(state[3:]) > 0.05


def test_cw_sampled_transition_matches_continuous_integration() -> None:
    state_matrix, input_matrix = cw_matrices()
    initial = np.array([100.0, 50.0, 20.0, 0.01, 0.02, 0.0])
    control = np.array([0.1, -0.2, 0.05])
    generator = np.zeros((9, 9))
    generator[:6, :6], generator[:6, 6:] = state_matrix, input_matrix
    exact = (expm(20 * generator) @ np.concatenate([initial, control]))[:6]
    solution = solve_ivp(
        lambda _t, x: state_matrix @ x + input_matrix @ control,
        (0, 20),
        initial,
        rtol=1e-11,
        atol=1e-12,
    )
    assert solution.y[:, -1] == pytest.approx(exact, rel=1e-10, abs=1e-10)


def test_impulse_to_propellant_conversion_has_correct_units() -> None:
    impulse_ns, specific_impulse_s = 12.4, 300.0
    propellant_kg = impulse_ns / (specific_impulse_s * GRAVITY_M_S2)
    assert propellant_kg == pytest.approx(0.004214827013642104)
    assert propellant_kg != pytest.approx(0.124)


def arm_position(q: np.ndarray) -> np.ndarray:
    """Unit-length links; angles measured counterclockwise from world +x."""
    return np.array([cos(q[0]) + cos(q.sum()), sin(q[0]) + sin(q.sum())])


def test_arm_inverse_kinematics_and_printed_coordinates() -> None:
    for target, degrees in [
        ([0.5, 0.5], [-24.29518895, 138.59037789]),
        ([0.3, 0.8], [4.73396255, 129.41998447]),
    ]:
        radius_sq = np.dot(target, target)
        elbow = np.arccos((radius_sq - 2) / 2)
        shoulder = np.arctan2(target[1], target[0]) - np.arctan2(sin(elbow), 1 + cos(elbow))
        angles = np.array([shoulder, elbow])
        assert arm_position(angles) == pytest.approx(target, abs=1e-12)
        assert np.rad2deg(angles) == pytest.approx(degrees, abs=1e-7)
    assert arm_position(np.deg2rad([30, 60])) == pytest.approx([sqrt(3) / 2, 1.5])


def test_arm_point_mass_inertia_and_gravity_use_the_same_placement() -> None:
    q = np.array([0.3, -0.7])
    first = np.array([[-sin(q[0]), 0], [cos(q[0]), 0]])
    second = first + np.array([[-sin(q.sum())] * 2, [cos(q.sum())] * 2])
    inertia = first.T @ first + second.T @ second
    assert inertia == pytest.approx(
        np.array([[3 + 2 * cos(q[1]), 1 + cos(q[1])], [1 + cos(q[1]), 1]])
    )
    assert np.linalg.eigvalsh(inertia).min() > 0

    def potential(configuration: np.ndarray) -> float:
        return GRAVITY_M_S2 * (2 * sin(configuration[0]) + sin(configuration.sum()))

    step = 1e-6
    gradient = np.array(
        [
            (potential(q + step * direction) - potential(q - step * direction)) / (2 * step)
            for direction in np.eye(2)
        ]
    )
    expected = GRAVITY_M_S2 * np.array([2 * cos(q[0]) + cos(q.sum()), cos(q.sum())])
    assert gradient == pytest.approx(expected, rel=1e-9)


def test_arm_coriolis_power_matches_inertia_derivative() -> None:
    angle, velocity = 0.7, np.array([0.8, -0.4])
    h = -sin(angle)
    coriolis = np.array([[h * velocity[1], h * velocity.sum()], [-h * velocity[0], 0]])
    mass_rate = np.array([[2 * h, h], [h, 0]]) * velocity[1]
    assert velocity @ (mass_rate - 2 * coriolis) @ velocity == pytest.approx(0, abs=1e-12)


def test_hover_balance_and_controllability_use_twelve_tangent_states() -> None:
    mass, arm, yaw_length = 1.2, 0.2, 0.01
    inertia = np.diag([0.02, 0.02, 0.04])
    allocation = np.array(
        [
            [1, 1, 1, 1],
            [0, arm, 0, -arm],
            [-arm, 0, arm, 0],
            [yaw_length, -yaw_length, yaw_length, -yaw_length],
        ]
    )
    hover = np.full(4, mass * GRAVITY_M_S2 / 4)
    wrench = allocation @ hover
    assert wrench[0] / mass - GRAVITY_M_S2 == pytest.approx(0)
    assert wrench[1:] == pytest.approx([0, 0, 0], abs=1e-12)
    state = np.zeros((12, 12))
    state[:3, 3:6] = np.eye(3)
    state[3, 7], state[4, 6] = GRAVITY_M_S2, -GRAVITY_M_S2
    state[6:9, 9:12] = np.eye(3)
    control = np.zeros((12, 4))
    control[5] = allocation[0] / mass
    control[9:12] = np.linalg.solve(inertia, allocation[1:])
    assert np.linalg.matrix_rank(control) == 4
    controllability = np.hstack([np.linalg.matrix_power(state, k) @ control for k in range(12)])
    assert np.linalg.matrix_rank(controllability) == 12


def test_body_quaternion_rate_preserves_norm_and_sampling_arithmetic() -> None:
    quaternion = np.array([0.9, 0.1, 0.2, -0.3])
    quaternion /= np.linalg.norm(quaternion)
    omega = np.array([0.3, -0.2, 0.5])
    rate = 0.5 * np.concatenate(
        [
            [-np.dot(quaternion[1:], omega)],
            quaternion[0] * omega + np.cross(quaternion[1:], omega),
        ]
    )
    assert quaternion @ rate == pytest.approx(0, abs=1e-12)
    assert 50 / 40 == pytest.approx(1.25)
    assert 80 / 40 == pytest.approx(2.0)


@pytest.mark.parametrize(
    "required,forbidden",
    [
        ("A Consistent Minimization Convention", r"u^* = \text{sign}(\lambda_2)"),
        (
            "Differentiate the Actual Discrete Transition",
            "linearization residuals remain $O(\\Delta t)$",
        ),
        (
            "One Quadratic Model for DDP and iLQR",
            "iLQR is a variant of DDP with first-order cost expansion",
        ),
        ("Reproducible Sampled LQR Result", "**Terminal state** (achieved)"),
        (
            "Placement Determines Both Gravity and Kinematics",
            "This is **impossible** with global linearization",
        ),
        ("Hover in a Consistent Frame", "Robust to 20% model uncertainty"),
    ],
)
def test_control_reference_removes_inconsistent_derivations(required: str, forbidden: str) -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert required in source
    assert forbidden not in source
