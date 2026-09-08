"""Independent mechanical and control counterexamples for the swing synthesis."""

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp

from src.affine_control.dynamics import constrained_affine_fields
from src.tools.state_space_examples import zoh_matrices

GRAVITY_M_S2 = 9.81


@pytest.mark.parametrize("speed", [0.0, 5.0, 30.0])
def test_velocity_bias_does_not_reduce_fixed_configuration_input_gain(speed: float) -> None:
    """Compare the reduced field with a direct constrained saddle-point solve."""
    mass = np.array([[2.0, 0.4], [0.4, 1.0]])
    jacobian = np.array([[1.0, 1.0]])
    bias = np.array([speed**2 + GRAVITY_M_S2, -0.3 * speed**2])
    drift, gain = constrained_affine_fields(mass, bias, np.eye(2), jacobian, np.zeros(1))
    saddle = np.block([[mass, -jacobian.T], [jacobian, np.zeros((1, 1))]])
    initial = np.linalg.solve(saddle, np.r_[-bias, 0])
    changed = np.linalg.solve(saddle, np.r_[np.array([10.0, 0.0]) - bias, 0])
    np.testing.assert_allclose(drift, initial[:2], atol=1e-12)
    np.testing.assert_allclose(changed[:2] - initial[:2], [10 / 2.2, -10 / 2.2], atol=1e-12)
    np.testing.assert_allclose(gain[:, 0], [1 / 2.2, -1 / 2.2], atol=1e-14)
    # Equal joint torques are entirely balanced by the ideal constraint.
    np.testing.assert_allclose(gain @ np.ones(2), 0, atol=1e-14)


def test_high_drift_norm_can_leave_the_whole_task_direction_controlled() -> None:
    """Large motion in x says nothing about controlled y in an orthogonal task."""
    drift, control = np.array([1000.0, 0.0]), np.array([0.0, 1.0])
    assert np.linalg.norm(drift) / np.linalg.norm(control) == 1000
    task = np.array([0.0, 1.0])
    assert task @ drift == 0
    assert task @ control == 1


@pytest.mark.parametrize("initial_rate", [0.0, 20.0, 50.0])
def test_short_rotor_torque_changes_angle_independently_of_initial_speed(
    initial_rate: float,
) -> None:
    """An exact ZOH solution checks the finite-horizon torque illustration."""
    a = np.array([[0.0, 1.0], [0.0, 0.0]])
    b = np.array([[0.0], [10.0]])  # I=0.1 kg m^2, input in N m.
    phi, gamma = zoh_matrices(a, b, 0.04)
    baseline = phi @ np.array([0.0, initial_rate])
    driven = baseline + gamma[:, 0]
    np.testing.assert_allclose(driven - baseline, [0.008, 0.4], atol=1e-14)


def test_stable_mode_can_weight_a_late_input_more_than_an_early_input() -> None:
    """Numerical integration independently checks the damped endpoint kernel."""
    early = quad(lambda time: np.exp(-10 * (1 - time)), 0.0, 0.1)[0]
    late = quad(lambda time: np.exp(-10 * (1 - time)), 0.9, 1.0)[0]
    assert late / early == pytest.approx(np.exp(9))


def test_event_shift_is_separate_from_fixed_time_displacement() -> None:
    """A transverse ballistic crossing has a closed-form perturbed event time."""
    position, velocity, target = 0.2, 2.0, 1.0
    step, delta_position, delta_velocity = 1e-6, 0.3, -0.2
    event = (target - position) / velocity
    plus = (target - position - step * delta_position) / (velocity + step * delta_velocity)
    minus = (target - position + step * delta_position) / (velocity - step * delta_velocity)
    fixed_time_delta = delta_position + event * delta_velocity
    assert (plus - minus) / (2 * step) == pytest.approx(-fixed_time_delta / velocity)
    # Position at the actual event is fixed, despite nonzero fixed-time variation.
    assert fixed_time_delta != 0
    assert fixed_time_delta + velocity * (-fixed_time_delta / velocity) == 0


def test_harmonic_mode_has_zero_elastic_force_at_maximum_velocity() -> None:
    """Integrate the oscillator instead of presuming aligned force/rate maxima."""
    frequency, amplitude = 10.0, 0.02
    quarter = np.pi / (2 * frequency)
    solution = solve_ivp(
        lambda _time, state: [state[1], -(frequency**2) * state[0]],
        (0, quarter),
        [amplitude, 0],
        rtol=1e-11,
        atol=1e-13,
    )
    assert solution.success
    displacement, velocity = solution.y[:, -1]
    assert displacement == pytest.approx(0, abs=1e-12)
    assert velocity == pytest.approx(-frequency * amplitude, abs=1e-11)
    assert -(frequency**2) * displacement == pytest.approx(0, abs=1e-10)


def test_central_collision_velocity_and_energy_close() -> None:
    """Solve momentum/restitution simultaneously, then check separate energies."""
    club_mass, ball_mass, restitution, incoming = 0.2, 0.04593, 0.83, 45.0
    club, ball = np.linalg.solve(
        [[club_mass, ball_mass], [-1, 1]],
        [club_mass * incoming, restitution * incoming],
    )
    initial = club_mass * incoming**2 / 2
    fractions = np.array([club_mass * club**2 / 2, ball_mass * ball**2 / 2]) / initial
    loss = ball_mass / (club_mass + ball_mass) * (1 - restitution**2)
    assert club / incoming == pytest.approx(0.6582284, abs=1e-7)
    assert fractions.sum() + loss == pytest.approx(1)
    assert loss == pytest.approx(0.0581012, abs=1e-7)
    assert fractions[1] == pytest.approx(0.5086342, abs=1e-7)


def test_stationary_ideal_contact_transmits_momentum_without_power() -> None:
    """A supported rotating body can have a nonzero external ground moment."""
    ground_force = np.array([0.0, 0.0, 800.0])
    contact_from_com = np.array([0.2, 0.0, -1.0])
    contact_velocity = np.zeros(3)
    assert ground_force @ contact_velocity == 0
    np.testing.assert_allclose(np.cross(contact_from_com, ground_force), [0, -160, 0])


@pytest.mark.parametrize("coupling", [-0.4, 0.4])
def test_proximal_input_has_no_universal_distal_acceleration_sign(coupling: float) -> None:
    """Both physically positive inertias admit opposite coupling signs."""
    mass = np.array([[2.0, coupling], [coupling, 1.0]])
    assert np.linalg.eigvalsh(mass).min() > 0
    acceleration = np.linalg.solve(mass, [1.0, 0.0])
    assert acceleration[1] == pytest.approx(-coupling / (2 - coupling**2))


def test_spring_storage_stiffness_trend_depends_on_loading_condition() -> None:
    """Integrate loading work under fixed-displacement and fixed-force endpoints."""
    stiffnesses = [100.0, 200.0]
    fixed_displacement = [quad(lambda x, k=k: k * x, 0, 0.1)[0] for k in stiffnesses]
    fixed_force = [quad(lambda x, k=k: k * x, 0, 10 / k)[0] for k in stiffnesses]
    assert fixed_displacement == pytest.approx([0.5, 1.0])
    assert fixed_force == pytest.approx([0.5, 0.25])
