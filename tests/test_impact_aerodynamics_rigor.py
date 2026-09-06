"""Independent force, flight, inference and evidence checks for the long reference."""

from math import exp, log, pi, radians
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp

GRAVITY_M_S2 = 9.81
RADIUS_M = 0.02135
MASS_KG = 0.0456
INERTIA_KG_M2 = 8.10e-6
AIR_DENSITY_KG_M3 = 1.2
KINEMATIC_VISCOSITY_M2_S = 1.5e-5
ARTICLE = Path(__file__).resolve().parents[1] / "articles/impact-mechanics-and-ball-flight.qmd"


def force_components(
    velocity: np.ndarray, wind: np.ndarray, spin: np.ndarray, lift_coefficient: float
) -> tuple[np.ndarray, np.ndarray]:
    relative = velocity - wind
    speed = np.linalg.norm(relative)
    load = 0.5 * AIR_DENSITY_KG_M3 * pi * RADIUS_M**2 * speed**2
    drag = -load * 0.25 * relative / speed
    axis = np.cross(spin, relative)
    lift = load * lift_coefficient * axis / np.linalg.norm(axis)
    return drag, lift


def test_forces_are_invariant_under_common_inertial_velocity_shift() -> None:
    velocity, wind, spin = np.array([40, 5, 2]), np.array([3, -1, 0]), np.array([0, 0, 200])
    shift = np.array([15, -4, 7])
    before = force_components(velocity, wind, spin, 0.2)
    after = force_components(velocity + shift, wind + shift, spin, 0.2)
    assert np.array(before) == pytest.approx(np.array(after))


@pytest.mark.parametrize("coefficient", [0.2, -0.1])
def test_signed_lift_is_perpendicular_to_relative_flow_and_spin(coefficient: float) -> None:
    velocity, wind, spin = np.array([40, 5, 2]), np.array([3, -1, 0]), np.array([0, 0, 200])
    drag, lift = force_components(velocity, wind, spin, coefficient)
    relative = velocity - wind
    assert lift @ relative == pytest.approx(0, abs=1e-13)
    assert lift @ spin == pytest.approx(0, abs=1e-13)
    assert drag @ relative < 0
    assert np.sign(lift @ np.cross(spin, relative)) == np.sign(coefficient)


def test_tailwind_can_do_positive_ground_frame_work() -> None:
    velocity, wind, spin = np.array([10, 0, 0]), np.array([20, 0, 0]), np.array([0, 0, 200])
    drag, _ = force_components(velocity, wind, spin, 0)
    assert drag @ velocity > 0
    assert drag @ (velocity - wind) < 0


def test_headwind_raises_reynolds_number_and_lowers_spin_ratio() -> None:
    speeds = np.array([40.0, 50.0])
    reynolds = 2 * RADIUS_M * speeds / KINEMATIC_VISCOSITY_M2_S
    spin_ratio = 200 * RADIUS_M / speeds
    assert reynolds[1] / reynolds[0] == pytest.approx(1.25)
    assert spin_ratio[1] / spin_ratio[0] == pytest.approx(0.8)


def test_moist_air_is_less_dense_at_fixed_total_pressure_and_temperature() -> None:
    pressure, temperature = 101325.0, 293.15
    dry_constant, vapour_constant = 287.05, 461.5
    vapour_pressure = 1169.4
    dry = pressure / (dry_constant * temperature)
    humid = (pressure - vapour_pressure) / (dry_constant * temperature)
    humid += vapour_pressure / (vapour_constant * temperature)
    assert humid < dry
    assert (dry - humid) / dry == pytest.approx(0.004362, abs=1e-6)


def test_velocity_proportional_spin_decay_is_exponential_in_air_distance() -> None:
    beta, omega0, duration = 2e-5, 300.0, 4.0

    def dynamics(time: float, state: np.ndarray) -> list[float]:
        speed = 60 * exp(-0.1 * time)
        return [-beta * speed * state[0] / RADIUS_M, speed]

    result = solve_ivp(dynamics, [0, duration], [omega0, 0], rtol=1e-11, atol=1e-11)
    omega, distance = result.y[:, -1]
    assert omega == pytest.approx(omega0 * exp(-beta * distance / RADIUS_M), rel=1e-10)
    assert omega != pytest.approx(omega0 * exp(-beta * 60 * duration / RADIUS_M), rel=1e-3)


def test_fraction_per_second_and_continuous_decay_rate_are_distinct() -> None:
    loss_fraction, duration = 0.04, 6.0
    continuous_rate = -log(1 - loss_fraction)
    assert exp(-continuous_rate * duration) == pytest.approx(0.96**6)
    assert exp(-0.04 * duration) != pytest.approx(0.96**6, rel=1e-4)


def test_torque_reference_length_changes_coefficient_by_two() -> None:
    pressure_area, coefficient_diameter = 2.0, 0.003
    torque = pressure_area * (2 * RADIUS_M) * coefficient_diameter
    coefficient_radius = torque / (pressure_area * RADIUS_M)
    assert coefficient_radius == pytest.approx(2 * coefficient_diameter)
    angular_deceleration = torque / INERTIA_KG_M2
    revolutions_deceleration = torque / (2 * pi * INERTIA_KG_M2)
    assert angular_deceleration == pytest.approx(2 * pi * revolutions_deceleration)


def naruo_force_state(state: np.ndarray, drag_offset: float = 0) -> np.ndarray:
    """Use Horner evaluation and component forces independently of the article code."""
    vx, vy, angular_speed = state[2:]
    speed = np.hypot(vx, vy)
    ratio = RADIUS_M * angular_speed / speed
    drag = np.polyval([0.7510, -1.760, 1.098, 0.2148, 0.2049], ratio) + drag_offset
    lift = np.polyval([-0.2158, 1.006, -1.644, 1.250, 0.0616], ratio)
    moment = exp(3.780 * ratio - 6.707)
    dynamic_load = AIR_DENSITY_KG_M3 * pi * RADIUS_M**2 * speed**2 / 2
    ax = -dynamic_load * (drag * vx + lift * vy) / (MASS_KG * speed)
    ay = dynamic_load * (lift * vx - drag * vy) / (MASS_KG * speed) - GRAVITY_M_S2
    spin_acceleration = -dynamic_load * 2 * RADIUS_M * moment / INERTIA_KG_M2
    return np.array([vx, vy, ax, ay, spin_acceleration])


def integrate_rk4(step: float, drag_offset: float = 0) -> tuple[float, np.ndarray, np.ndarray]:
    """Fixed-step RK4 with a bracketed linearly interpolated descending contact."""
    angle = radians(12)
    state = np.array([0.0, 0.0, 40 * np.cos(angle), 40 * np.sin(angle), 2000 * pi / 30])
    states = [state.copy()]
    time = 0.0
    for _ in range(int(10 / step)):
        k1 = naruo_force_state(state, drag_offset)
        k2 = naruo_force_state(state + step * k1 / 2, drag_offset)
        k3 = naruo_force_state(state + step * k2 / 2, drag_offset)
        k4 = naruo_force_state(state + step * k3, drag_offset)
        updated = state + step * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        if updated[1] < 0:
            fraction = state[1] / (state[1] - updated[1])
            landed = state + fraction * (updated - state)
            states.append(landed)
            return time + fraction * step, landed, np.array(states)
        state = updated
        states.append(state.copy())
        time += step
    raise AssertionError("No descending landing within the integration horizon")


def test_independent_rk4_reproduces_published_landing_with_step_refinement() -> None:
    coarse = integrate_rk4(0.02)
    fine = integrate_rk4(0.0005)
    reference_carry = 85.43193196615502
    assert abs(fine[1][0] - reference_carry) < abs(coarse[1][0] - reference_carry)
    assert fine[1][0] == pytest.approx(reference_carry, abs=2e-6)
    assert fine[0] == pytest.approx(2.7206361612082426, abs=2e-7)
    assert fine[1][4] == pytest.approx(184.222033, abs=1e-6)
    assert fine[1][3] < 0


def test_example_remains_inside_the_reported_force_fit_rectangle() -> None:
    _, _, states = integrate_rk4(0.01)
    speeds = np.linalg.norm(states[:, 2:4], axis=1)
    reynolds = 2 * RADIUS_M * speeds / KINEMATIC_VISCOSITY_M2_S
    ratio = RADIUS_M * states[:, 4] / speeds
    assert reynolds.min() > 7.09e4 and reynolds.max() < 1.25e5
    assert ratio.min() > 0.03 and ratio.max() < 1.13


def test_flight_energy_loss_matches_drag_and_spin_torque_power() -> None:
    state = np.array([20.0, 5.0, 33.0, 2.0, 190.0])
    derivative = naruo_force_state(state)
    speed = np.linalg.norm(state[2:4])
    ratio = RADIUS_M * state[4] / speed
    cd = np.polyval([0.7510, -1.760, 1.098, 0.2148, 0.2049], ratio)
    cm = exp(3.780 * ratio - 6.707)
    load = AIR_DENSITY_KG_M3 * pi * RADIUS_M**2 * speed**2 / 2
    energy_gradient = np.array(
        [
            0,
            MASS_KG * GRAVITY_M_S2,
            MASS_KG * state[2],
            MASS_KG * state[3],
            INERTIA_KG_M2 * state[4],
        ]
    )
    predicted = -load * (cd * speed + 2 * RADIUS_M * cm * state[4])
    assert energy_gradient @ derivative == pytest.approx(predicted)
    assert predicted < 0


def test_spin_ratio_polynomial_must_not_be_extrapolated_to_zero_spin() -> None:
    assert np.polyval([-0.2158, 1.006, -1.644, 1.250, 0.0616], 0) == 0.0616
    assert exp(-6.707) > 0
    # Both positive intercepts require a separate zero-spin limit for a symmetric ball.


def test_drag_sensitivity_is_not_a_universal_yardage_conversion() -> None:
    lower = integrate_rk4(0.002, -0.01)[1][0]
    baseline = integrate_rk4(0.002)[1][0]
    upper = integrate_rk4(0.002, 0.01)[1][0]
    large = integrate_rk4(0.002, 0.06)[1][0]
    derivative = (upper - lower) / 0.02
    assert (upper - baseline) / 0.9144 == pytest.approx(-1.188284, abs=1e-5)
    assert abs(large - (baseline + derivative * 0.06)) > 0.5


def test_ballistic_landing_and_event_derivative_match_exact_solution() -> None:
    speed, angle = 40.0, radians(12)
    vx, vy = speed * np.cos(angle), speed * np.sin(angle)
    flight_time = 2 * vy / GRAVITY_M_S2
    carry = vx * flight_time
    assert carry == pytest.approx(speed**2 * np.sin(2 * angle) / GRAVITY_M_S2)
    # Perturb vertical launch speed, keeping horizontal launch speed fixed.
    fixed_time_vertical = flight_time
    landing_vertical_speed = -vy
    event_time_derivative = -fixed_time_vertical / landing_vertical_speed
    assert vx * event_time_derivative == pytest.approx(2 * vx / GRAVITY_M_S2)


def test_density_and_constant_drag_are_not_separately_identifiable_from_deceleration() -> None:
    times = np.linspace(0, 3, 101)
    speed0 = 40.0

    def trajectory(density: float, drag: float) -> np.ndarray:
        rate = density * pi * RADIUS_M**2 * drag / (2 * MASS_KG)
        return np.log1p(rate * speed0 * times) / rate

    assert trajectory(1.2, 0.25) == pytest.approx(trajectory(1.0, 0.3))


def test_matched_learning_comparison_has_twenty_eight_percent_reduction() -> None:
    assert (6.63 - 4.75) / 6.63 == pytest.approx(0.2835595777)
    assert (6.95 - 4.75) / 6.95 == pytest.approx(0.3165467626)


def test_covariance_terms_can_change_predicted_landing_variance() -> None:
    sensitivity = np.array([2.0, -1.0])
    covariance = np.array([[1.0, 0.8], [0.8, 1.0]])
    assert np.linalg.eigvalsh(covariance).min() > 0
    full = sensitivity @ covariance @ sensitivity
    independent = sensitivity @ np.diag(np.diag(covariance)) @ sensitivity
    assert full == pytest.approx(1.8)
    assert independent == pytest.approx(5.0)


def test_reference_defines_air_relative_forces_and_headwind_sign() -> None:
    source = ARTICLE.read_text(encoding="utf-8")
    assert "Air-Relative Velocity and Force Conventions" in source
    assert "headwind additionally raises the spin ratio" not in source
    assert "entirely supercritical" not in source


def test_reference_states_fit_domain_and_reproducible_flight() -> None:
    source = ARTICLE.read_text(encoding="utf-8")
    assert "A Reproducible Flight Within a Stated Fit Domain" in source
    assert "85.4319" in source
    assert "zero-spin limit" in source


def test_reference_corrects_evidence_comparison_and_regulatory_date() -> None:
    source = ARTICLE.read_text(encoding="utf-8")
    assert "6.63" in source and "4.75" in source
    assert "January 2030" in source
    assert "17 June 2026" in source
    assert "From 2028 these become" not in source


def test_reference_separates_repeatability_causality_and_conformance() -> None:
    source = ARTICLE.read_text(encoding="utf-8")
    assert "Precision, Repeatability, and Model Error" in source
    assert "from dimple geometry alone" not in source
    assert "Why the Tolerance Is 4.0 Yards" not in source
