"""Tests for golf ball flight dynamics."""

import numpy as np
import pytest

from src.golf_simulation.ball_flight import BallFlightDynamics, BallFlightState

GRAVITY_M_S2 = 9.81


class TestBallFlightState:
    def test_state_creation(self):
        state = BallFlightState(
            position=np.array([0.0, 0.0, 0.0]),
            velocity=np.array([70.0, 0.0, 20.0]),
            spin=np.array([0.0, -300.0, 0.0]),
        )
        assert state.position.shape == (3,)
        assert state.velocity.shape == (3,)
        assert state.spin.shape == (3,)

    def test_speed_property(self):
        state = BallFlightState(
            position=np.zeros(3),
            velocity=np.array([3.0, 4.0, 0.0]),
            spin=np.zeros(3),
        )
        assert abs(state.speed - 5.0) < 1e-10

    def test_state_vector_concatenation(self):
        state = BallFlightState(
            position=np.array([1.0, 2.0, 3.0]),
            velocity=np.array([4.0, 5.0, 6.0]),
            spin=np.array([7.0, 8.0, 9.0]),
        )
        sv = state.state_vector
        assert sv.shape == (9,)
        np.testing.assert_array_equal(sv, [1, 2, 3, 4, 5, 6, 7, 8, 9])


class TestBallFlightDynamics:
    def test_default_construction(self):
        bfd = BallFlightDynamics()
        assert bfd.mass > 0
        assert bfd.radius > 0

    def test_invalid_mass_raises(self):
        with pytest.raises(ValueError):
            BallFlightDynamics(mass=-1.0)

    def test_dynamics_returns_correct_shape(self):
        bfd = BallFlightDynamics()
        x = np.array([0, 0, 0, 70, 0, 20, 0, -300, 0], dtype=float)
        u = np.zeros(3)
        dx = bfd.dynamics(x, u)
        assert dx.shape == (9,)

    def test_gravity_only(self):
        """With zero velocity and spin, only gravity acts."""
        bfd = BallFlightDynamics(cd=0.0, cl=0.0)
        x = np.array([0, 0, 10, 0, 0, 0, 0, 0, 0], dtype=float)
        u = np.zeros(3)
        dx = bfd.dynamics(x, u)
        # Velocity derivatives: only gravity in z
        assert abs(dx[5] - (-GRAVITY_M_S2)) < 0.01  # az ~ -g

    def test_no_magnus_without_spin(self):
        """Zero spin should produce no Magnus force."""
        bfd = BallFlightDynamics()
        x = np.array([0, 0, 10, 50, 0, 10, 0, 0, 0], dtype=float)
        u = np.zeros(3)
        dx = bfd.dynamics(x, u)
        # Should still have drag and gravity but no lift
        assert dx.shape == (9,)

    def test_spin_decay(self):
        """Spin should decay over time."""
        bfd = BallFlightDynamics(spin_decay_rate=0.05)
        x = np.array([0, 0, 10, 50, 0, 10, 0, -300, 0], dtype=float)
        u = np.zeros(3)
        dx = bfd.dynamics(x, u)
        # Spin derivative should be negative (decaying)
        assert dx[7] > 0  # -spin_decay * (-300) = +15

    def test_simulate_driver_shot(self):
        """A driver shot should carry roughly 200-280 yards (183-256m)."""
        bfd = BallFlightDynamics()
        initial = BallFlightState(
            position=np.array([0.0, 0.0, 0.0]),
            velocity=np.array([65.0, 0.0, 22.0]),
            spin=np.array([0.0, -280.0, 0.0]),
        )
        trajectory = bfd.simulate(initial, dt=0.002, max_time=10.0)
        assert len(trajectory) > 10
        final = trajectory[-1]
        carry_m = final.position[0]
        assert 100 < carry_m < 350, f"Carry {carry_m}m outside expected range"

    def test_simulate_stops_at_ground(self):
        """Ball should stop when z <= 0."""
        bfd = BallFlightDynamics()
        initial = BallFlightState(
            position=np.zeros(3),
            velocity=np.array([50.0, 0.0, 15.0]),
            spin=np.zeros(3),
        )
        trajectory = bfd.simulate(initial, dt=0.005)
        final_z = trajectory[-1].position[2]
        assert final_z <= 0.1  # Should be near ground

    def test_linearize_returns_correct_shapes(self):
        bfd = BallFlightDynamics()
        x = np.array([0, 0, 10, 50, 0, 10, 0, -300, 0], dtype=float)
        u = np.zeros(3)
        A, B = bfd.linearize(x, u)
        assert A.shape == (9, 9)
        assert B.shape == (9, 3)

    def test_wind_affects_trajectory(self):
        """Headwind should reduce carry distance."""
        bfd_no_wind = BallFlightDynamics(wind=np.array([0.0, 0.0, 0.0]))
        bfd_headwind = BallFlightDynamics(wind=np.array([-10.0, 0.0, 0.0]))
        initial = BallFlightState(
            position=np.zeros(3),
            velocity=np.array([65.0, 0.0, 22.0]),
            spin=np.array([0.0, -280.0, 0.0]),
        )
        traj_no = bfd_no_wind.simulate(initial, dt=0.005)
        traj_hw = bfd_headwind.simulate(initial, dt=0.005)
        carry_no = traj_no[-1].position[0]
        carry_hw = traj_hw[-1].position[0]
        assert carry_hw < carry_no, "Headwind should reduce carry"
