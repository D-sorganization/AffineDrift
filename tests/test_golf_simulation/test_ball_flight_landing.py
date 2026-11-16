"""Landing-point accuracy of ``BallFlightDynamics.simulate``.

Expected values come from the closed-form vacuum projectile solution:
time of flight ``T = (vz + sqrt(vz^2 + 2 g z0)) / g`` and range ``vx * T``.
Air density is set to a negligible value so aerodynamic forces vanish.
"""

import math

import numpy as np
import pytest

from src.golf_simulation.ball_flight import BallFlightDynamics, BallFlightState


def _vacuum_ball() -> BallFlightDynamics:
    return BallFlightDynamics(rho=1e-12, spin_decay_rate=0.0)


@pytest.mark.parametrize("dt", [0.001, 0.05, 0.2])
def test_landing_range_matches_closed_form_for_any_step(dt: float) -> None:
    ball = _vacuum_ball()
    g = ball.gravity
    state = BallFlightState(np.zeros(3), np.array([30.0, 0.0, 20.0]), np.zeros(3))
    final = ball.simulate(state, dt=dt)[-1]
    expected_range = 30.0 * (2.0 * 20.0 / g)
    assert final.position[2] == 0.0
    assert final.position[0] == pytest.approx(expected_range, abs=1e-6)


def test_landing_from_height_matches_closed_form() -> None:
    ball = _vacuum_ball()
    g = ball.gravity
    z0, vz = 1.5, 4.0
    state = BallFlightState(np.array([0.0, 0.0, z0]), np.array([10.0, 2.0, vz]), np.zeros(3))
    final = ball.simulate(state, dt=0.1)[-1]
    flight_time = (vz + math.sqrt(vz**2 + 2.0 * g * z0)) / g
    assert final.position[0] == pytest.approx(10.0 * flight_time, abs=1e-6)
    assert final.position[1] == pytest.approx(2.0 * flight_time, abs=1e-6)


def test_ball_landing_within_first_step_never_goes_underground() -> None:
    ball = _vacuum_ball()
    g = ball.gravity
    z0, vz = 0.01, -5.0
    state = BallFlightState(np.array([0.0, 0.0, z0]), np.array([10.0, 0.0, vz]), np.zeros(3))
    trajectory = ball.simulate(state, dt=0.01)
    assert min(s.position[2] for s in trajectory) >= 0.0
    flight_time = (vz + math.sqrt(vz**2 + 2.0 * g * z0)) / g
    assert trajectory[-1].position[0] == pytest.approx(10.0 * flight_time, abs=1e-6)
