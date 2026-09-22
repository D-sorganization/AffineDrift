"""Independent numerical checks for the force-measurement article's examples."""

import numpy as np
import pytest
from scipy.integrate import solve_ivp


def _cop(observations: np.ndarray) -> np.ndarray:
    """Recover planar COP from force, moment and surface-height observations."""
    force_x, force_y, force_z, moment_x, moment_y, height = observations
    return np.array(
        [(height * force_x - moment_y) / force_z, (moment_x + height * force_y) / force_z]
    )


def test_central_axis_surface_intersection_differs_from_cop() -> None:
    force = np.array([100.0, -50.0, 800.0])
    cop = np.array([0.10, -0.05, 0.04])
    free_couple = np.array([0.0, 0.0, 8.0])
    moment = np.cross(cop, force) + free_couple
    closest = np.cross(force, moment) / (force @ force)
    intersection = closest + (cop[2] - closest[2]) / force[2] * force
    predicted = cop + free_couple[2] / (force @ force) * np.cross(force, [0, 0, 1])
    np.testing.assert_allclose(intersection, predicted)
    assert np.linalg.norm(intersection - cop) > 0.001
    pitch = (force @ moment) / (force @ force)
    np.testing.assert_allclose(moment - np.cross(intersection, force), pitch * force)
    np.testing.assert_allclose((intersection - cop)[:2] * 1000, [-0.61302682, -1.22605364])


def test_cop_sensitivity_matches_independent_finite_differences() -> None:
    observation = np.array([100.0, -50.0, 800.0, -38.0, -76.0, 0.04])
    force_x, force_y, force_z, _, _, height = observation
    cop_x, cop_y = _cop(observation)
    jacobian = (
        np.array([[height, 0, -cop_x, 0, -1, force_x], [0, height, -cop_y, 1, 0, force_y]])
        / force_z
    )
    steps = np.array([1e-3, 1e-3, 1e-3, 1e-4, 1e-4, 1e-6])
    perturbations = np.diag(steps)
    numerical = np.column_stack(
        [
            (_cop(observation + delta) - _cop(observation - delta)) / (2 * step)
            for delta, step in zip(perturbations, steps, strict=True)
        ]
    )
    np.testing.assert_allclose(jacobian, numerical, rtol=1e-8, atol=1e-12)


def test_correlated_channel_errors_change_cop_uncertainty() -> None:
    observation = np.array([100.0, -50.0, 800.0, -38.0, -76.0, 0.04])
    # A common gain changes all wrench components but cancels from their ratio.
    gain_direction = observation.copy()
    gain_direction[-1] = 0
    gains = np.array([-0.01, 0.0, 0.01])
    results = np.array([_cop(observation + gain * gain_direction) for gain in gains])
    np.testing.assert_allclose(results, np.tile(_cop(observation), (3, 1)))
    jacobian_x = np.array([0.04, 0, -0.1, 0, -1, 100]) / 800
    covariance = np.outer(gain_direction, gain_direction) * 0.01**2
    assert abs(jacobian_x @ covariance @ jacobian_x) < 1e-16
    assert jacobian_x @ np.diag(np.diag(covariance)) @ jacobian_x > 0


def test_identical_normal_pressure_can_hide_torsional_traction() -> None:
    positions = np.array([[-0.1, -0.1, 0], [-0.1, 0.1, 0], [0.1, -0.1, 0], [0.1, 0.1, 0]])
    normal_forces = np.tile([0.0, 0.0, 200.0], (4, 1))
    tangential = np.cross(np.tile([0.0, 0.0, 100.0], (4, 1)), positions)
    assert np.all(np.linalg.norm(tangential, axis=1) < 0.5 * normal_forces[:, 2])
    np.testing.assert_allclose(tangential.sum(axis=0), 0)
    before = np.cross(positions, normal_forces).sum(axis=0)
    after = np.cross(positions, normal_forces + tangential).sum(axis=0)
    np.testing.assert_allclose(before, 0)
    np.testing.assert_allclose(after, [0, 0, 8])


@pytest.mark.parametrize("transfer", [[20.0, 0.0, 0.0], [0.0, 20.0, 0.0]])
def test_bilateral_partition_is_not_fixed_by_net_wrench_and_cops(transfer: list[float]) -> None:
    positions = np.array([[-0.2, 0.0, 0.0], [0.2, 0.0, 0.0]])
    original = np.array([[0.0, 0.0, 400.0], [0.0, 0.0, 500.0]])
    delta = np.array(transfer)
    changed = original + np.array([delta, -delta])
    normal_couple_change = -np.cross(positions[0] - positions[1], delta)
    original_moment = np.cross(positions, original).sum(axis=0)
    changed_moment = np.cross(positions, changed).sum(axis=0) + normal_couple_change
    np.testing.assert_allclose(original.sum(axis=0), changed.sum(axis=0))
    np.testing.assert_allclose(original_moment, changed_moment)
    np.testing.assert_allclose(original[:, 2], changed[:, 2])
    np.testing.assert_allclose(normal_couple_change[:2], 0)
    assert np.all(np.linalg.norm(changed[:, :2], axis=1) < 0.5 * changed[:, 2])
    assert abs(normal_couple_change[2]) <= 8.0


def test_bridge_voltage_requires_ratiometric_excitation_correction() -> None:
    resistances = np.array([350.35, 349.65, 349.65, 350.35])
    excitation = np.array([2.5, 5.0, 10.0])
    ratio = resistances[1] / sum(resistances[:2]) - resistances[3] / sum(resistances[2:])
    outputs = excitation * ratio
    np.testing.assert_allclose(outputs / excitation, ratio)
    assert outputs[-1] == pytest.approx(4 * outputs[0])
    thermally_scaled = resistances * 1.02
    compensated_ratio = thermally_scaled[1] / sum(thermally_scaled[:2]) - thermally_scaled[3] / sum(
        thermally_scaled[2:]
    )
    assert compensated_ratio == pytest.approx(ratio)


@pytest.mark.parametrize("time_constant", [100.0, 1000.0])
def test_charge_amplifier_droop_and_impulse_follow_circuit_ode(time_constant: float) -> None:
    duration = 5.0
    # After a unit force step, integrate voltage and its accumulated impulse.
    result = solve_ivp(
        lambda _time, state: [-state[0] / time_constant, state[0]],
        (0, duration),
        [1.0, 0.0],
        rtol=1e-10,
        atol=1e-12,
    )
    voltage, measured_impulse = result.y[:, -1]
    assert voltage == pytest.approx(np.exp(-duration / time_constant))
    assert measured_impulse == pytest.approx(time_constant * (1 - voltage))
    assert measured_impulse < duration
    permitted_droop = 0.01
    required_constant = -duration / np.log1p(-permitted_droop)
    assert 1 - np.exp(-duration / required_constant) == pytest.approx(permitted_droop)


def test_sampling_cannot_distinguish_aliased_frequencies() -> None:
    sample_rate = 2000.0
    times = np.arange(100) / sample_rate
    high_frequency = np.cos(2 * np.pi * 1300 * times)
    low_frequency = np.cos(2 * np.pi * 700 * times)
    np.testing.assert_allclose(high_frequency, low_frequency, atol=2e-13)
    undamped_gain = 1 / (1 - 0.2**2)
    assert undamped_gain == pytest.approx(1.0416666667)


def test_sum_of_foot_peaks_is_not_peak_of_synchronized_total() -> None:
    first = np.array([1.2, 0.5, 0.3])
    second = np.array([0.3, 0.5, 1.2])
    assert max(first + second) == pytest.approx(1.5)
    assert max(first) + max(second) == pytest.approx(2.4)
    parallel = np.array([0.0, 0.0, 0.01])
    perpendicular = np.array([0.01, 0.0, 0.0])
    force = np.array([0.0, 0.0, 1000.0])
    np.testing.assert_allclose(np.cross(parallel, force), 0)
    assert np.linalg.norm(np.cross(perpendicular, force)) == pytest.approx(10.0)
