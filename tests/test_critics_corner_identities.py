"""Independent integrations for the internal critique's manufactured examples."""

import math

import numpy as np
import pytest
from scipy.integrate import solve_ivp


@pytest.mark.parametrize("growth", [-2.0, 0.0, 2.0])
def test_nonlinear_input_response_and_interaction(growth: float) -> None:
    """Integrate four inputs to distinguish prediction error from interaction."""
    duration, amplitude = 1.0, 0.1
    endpoints = []
    for multiplier in (0.0, 1.0, 2.0, 3.0):
        command = multiplier * amplitude
        solution = solve_ivp(
            lambda time, state, command=command: growth * state + command**2,
            (0.0, duration),
            [0.0],
            rtol=1e-11,
            atol=1e-13,
        )
        assert solution.success
        endpoints.append(solution.y[0, -1])
    transport = duration if growth == 0 else math.expm1(growth * duration) / growth
    assert endpoints[1] == pytest.approx(amplitude**2 * transport, rel=1e-10)
    interaction = endpoints[3] - endpoints[2] - endpoints[1] + endpoints[0]
    assert interaction == pytest.approx(4 * amplitude**2 * transport, rel=1e-10)
    if growth == 2.0:
        assert endpoints[1] > 3 * amplitude**2 * duration


@pytest.mark.parametrize("relative_tolerance", [1e-9, 1e-12])
def test_scaled_pendulum_bound(relative_tolerance: float) -> None:
    """Verify the claimed bound against both scaled and physical equations."""
    gravity_over_length, amplitude, duration = 10.0, 0.1, 1.0
    frequency = math.sqrt(gravity_over_length)
    scaled_time = frequency * duration
    options = {"rtol": relative_tolerance, "atol": relative_tolerance / 100}
    scaled = solve_ivp(
        lambda time, state: [state[1], -math.sin(state[0])],
        (0.0, scaled_time),
        [amplitude, 0.0],
        **options,
    )
    physical = solve_ivp(
        lambda time, state: [state[1], -gravity_over_length * math.sin(state[0])],
        (0.0, duration),
        [amplitude, 0.0],
        **options,
    )
    assert scaled.success and physical.success
    np.testing.assert_allclose(
        physical.y[:, -1] / [1.0, frequency], scaled.y[:, -1], atol=2e-10, rtol=0
    )
    energy = scaled.y[1] ** 2 / 2 + 1 - np.cos(scaled.y[0])
    np.testing.assert_allclose(energy, 1 - math.cos(amplitude), atol=2e-11, rtol=0)
    linear = amplitude * np.array([math.cos(scaled_time), -math.sin(scaled_time)])
    error = np.linalg.norm(scaled.y[:, -1] - linear)
    bound = amplitude**3 * scaled_time / 6
    assert 0 < error < bound
    assert bound == pytest.approx(0.00052704627669473, rel=1e-12)


def _hybrid_endpoint(initial: float) -> float:
    """Locate the crossing numerically before integrating the second mode."""

    def guard(time: float, state: np.ndarray) -> float:
        return float(state[0])

    before = solve_ivp(
        lambda time, state: [1.0],
        (0.0, 2.0),
        [initial],
        events=guard,
        rtol=1e-12,
        atol=1e-14,
    )
    assert before.success and len(before.t_events[0]) == 1
    after = solve_ivp(
        lambda time, state: [3.0],
        (before.t_events[0][0], 2.0),
        before.y_events[0][0],
        rtol=1e-12,
        atol=1e-14,
    )
    assert after.success
    return float(after.y[0, -1])


def test_identity_reset_still_changes_endpoint_sensitivity() -> None:
    """Event-time relocation, absent in the reset Jacobian, triples sensitivity."""
    step = 1e-5
    assert _hybrid_endpoint(-1.0) == pytest.approx(3.0, abs=1e-12)
    derivative = (_hybrid_endpoint(-1.0 + step) - _hybrid_endpoint(-1.0 - step)) / (2 * step)
    assert derivative == pytest.approx(3.0, abs=1e-9)
    assert derivative != pytest.approx(1.0)
