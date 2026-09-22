"""Independent impulse, rolling, calibration and capture checks for putting."""

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp

GRAVITY_M_S2 = 9.81
BALL_RADIUS_M = 0.021335
BALL_MASS_KG = 0.04593
INERTIA_RATIO = 0.4


@pytest.mark.parametrize("spin_ratio", [-0.5, 0.0, 0.5, 1.5])
def test_sliding_transition_and_heat_from_integrated_balances(spin_ratio: float) -> None:
    initial_speed = 2.0
    initial_spin = spin_ratio * initial_speed / BALL_RADIUS_M
    slip = initial_speed - BALL_RADIUS_M * initial_spin
    friction_acceleration = 0.4 * GRAVITY_M_S2
    direction = np.sign(slip)
    duration = INERTIA_RATIO * abs(slip) / ((1 + INERTIA_RATIO) * friction_acceleration)
    inertia = INERTIA_RATIO * BALL_MASS_KG * BALL_RADIUS_M**2

    def balances(_time: float, state: np.ndarray) -> list[float]:
        speed, spin, _, _ = state
        return [
            -direction * friction_acceleration,
            direction * friction_acceleration / (INERTIA_RATIO * BALL_RADIUS_M),
            speed,
            BALL_MASS_KG * friction_acceleration * abs(speed - BALL_RADIUS_M * spin),
        ]

    solution = solve_ivp(
        balances, (0, duration), [initial_speed, initial_spin, 0, 0], rtol=1e-11, atol=1e-12
    )
    speed, spin, displacement, heat = solution.y[:, -1]
    predicted = (initial_speed + INERTIA_RATIO * BALL_RADIUS_M * initial_spin) / (1 + INERTIA_RATIO)
    assert speed == pytest.approx(predicted)
    assert speed == pytest.approx(BALL_RADIUS_M * spin)
    assert displacement == pytest.approx(
        initial_speed * duration - direction * friction_acceleration * duration**2 / 2
    )
    initial_energy = (BALL_MASS_KG * initial_speed**2 + inertia * initial_spin**2) / 2
    final_energy = (BALL_MASS_KG * speed**2 + inertia * spin**2) / 2
    assert initial_energy - final_energy == pytest.approx(heat)
    assert heat == pytest.approx(BALL_MASS_KG * INERTIA_RATIO * slip**2 / (2 + 2 * INERTIA_RATIO))


def test_face_tangential_impulse_can_produce_topspin() -> None:
    normal_impulse = 0.1
    tangential_impulse = 0.01
    impulse = np.array([normal_impulse, tangential_impulse, 0])
    contact_offset = np.array([-BALL_RADIUS_M, 0, 0])
    inertia = INERTIA_RATIO * BALL_MASS_KG * BALL_RADIUS_M**2
    velocity = impulse / BALL_MASS_KG
    angular_velocity = np.cross(contact_offset, impulse) / inertia
    forward_spin = -angular_velocity[2]
    assert forward_spin > 0
    assert BALL_RADIUS_M * forward_spin / velocity[0] == pytest.approx(0.25)


@pytest.mark.parametrize("grade", [0.0, 0.02, 0.05])
def test_rolling_acceleration_from_separate_force_and_moment_balances(grade: float) -> None:
    angle = np.arctan(grade)
    level_deceleration = 1.83**2 / (2 * 0.3048 * 12)
    inertia = INERTIA_RATIO * BALL_MASS_KG * BALL_RADIUS_M**2
    rolling_moment = (
        BALL_MASS_KG * (1 + INERTIA_RATIO) * BALL_RADIUS_M * level_deceleration * np.cos(angle)
    )
    matrix = np.array([[BALL_MASS_KG, -1], [inertia / BALL_RADIUS_M, BALL_RADIUS_M]])
    loads = np.array([BALL_MASS_KG * GRAVITY_M_S2 * np.sin(angle), -rolling_moment])
    acceleration, _contact_force = np.linalg.solve(matrix, loads)
    expected = GRAVITY_M_S2 * np.sin(angle) / (1 + INERTIA_RATIO) - level_deceleration * np.cos(
        angle
    )
    assert acceleration == pytest.approx(expected)
    assert acceleration < 0  # Even the 5% example decelerates under these assumptions.


def test_cross_slope_first_order_solution_retains_lateral_resistance() -> None:
    initial_speed, deceleration, final_time = 2.0, 0.55, 2.0
    weak_slope_acceleration = 0.001

    def equations(_time: float, state: np.ndarray) -> np.ndarray:
        velocity = state[2:]
        acceleration = -deceleration * velocity / np.linalg.norm(velocity)
        return np.r_[velocity, acceleration + [0, weak_slope_acceleration]]

    solution = solve_ivp(
        equations, (0, final_time), [0, 0, initial_speed, 0], rtol=1e-11, atol=1e-13
    )
    remaining_speed = initial_speed - deceleration * final_time
    bracket = (initial_speed**2 - remaining_speed**2) / 4 - remaining_speed**2 / 2 * np.log(
        initial_speed / remaining_speed
    )
    predicted = weak_slope_acceleration * bracket / deceleration**2
    assert solution.y[1, -1] == pytest.approx(predicted, rel=2e-6)
    assert predicted < weak_slope_acceleration * final_time**2 / 2


def test_one_stimp_distance_does_not_identify_a_speed_dependent_loss_law() -> None:
    release_speed, constant_deceleration = 1.83, 0.55
    boundary = release_speed / 2

    def alternate_integrand(speed: float) -> float:
        loss = 2 * constant_deceleration if speed < boundary else 6 * constant_deceleration / 7
        return speed / loss

    alternate_distance = quad(alternate_integrand, 0, release_speed, points=[boundary])[0]
    nominal_distance = release_speed**2 / (2 * constant_deceleration)
    assert alternate_distance == pytest.approx(nominal_distance)
    alternate_short = quad(alternate_integrand, 0, boundary)[0]
    constant_short = boundary**2 / (2 * constant_deceleration)
    assert alternate_short == pytest.approx(constant_short / 2)


def test_v_groove_contact_lever_arm_follows_its_opening_angle() -> None:
    opening = np.deg2rad(145)
    lever = BALL_RADIUS_M * np.sin(opening / 2)
    assert lever / BALL_RADIUS_M == pytest.approx(0.9537169507)
    height = 0.762 * np.sin(np.deg2rad(20))
    ideal_speed = np.sqrt(
        2 * GRAVITY_M_S2 * height / (1 + INERTIA_RATIO * (BALL_RADIUS_M / lever) ** 2)
    )
    assert ideal_speed == pytest.approx(1.884547, rel=1e-5)
    assert abs(ideal_speed - 1.83) > 0.05


def test_finite_ball_free_fall_criterion_differs_from_full_hole_chord() -> None:
    hole_radius = 0.10795 / 2
    time_to_drop = np.sqrt(2 * BALL_RADIUS_M / GRAVITY_M_S2)
    free_fall_limit = (2 * hole_radius - BALL_RADIUS_M) / time_to_drop
    full_diameter_guess = 2 * hole_radius / time_to_drop
    assert free_fall_limit == pytest.approx(1.313307, rel=1e-5)
    assert full_diameter_guess > free_fall_limit
    # This is a separately labeled historical fit that includes lip interactions.
    fitted_half_width = hole_radius * np.sqrt(1 - 1.5 / 1.63)
    assert fitted_half_width * 1000 == pytest.approx(15.243, rel=1e-4)


@pytest.mark.parametrize(
    "stimp, launch", [(8, 2.6294556075), (10, 2.3864324811), (12, 2.2003372211)]
)
def test_worked_three_metre_putts_from_contact_phase_integration(stimp: int, launch: float) -> None:
    friction = 0.4 * GRAVITY_M_S2
    rolling_loss = 1.83**2 / (2 * 0.3048 * stimp)

    def sliding(_time: float, state: np.ndarray) -> list[float]:
        return [state[1], -friction, friction / (INERTIA_RATIO * BALL_RADIUS_M)]

    def zero_slip(_time: float, state: np.ndarray) -> float:
        return float(state[1] - BALL_RADIUS_M * state[2])

    solution = solve_ivp(
        sliding, (0, 0.25), [0, launch, 0], events=zero_slip, rtol=1e-11, atol=1e-12
    )
    displacement, speed, spin = solution.y_events[0][0]
    assert speed == pytest.approx(BALL_RADIUS_M * spin)
    assert displacement + speed**2 / (2 * rolling_loss) == pytest.approx(3, abs=1e-9)
