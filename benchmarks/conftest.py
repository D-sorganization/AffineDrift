"""Fixtures for AffineDrift performance benchmarks.

Provides reusable benchmark data and configured objects so each benchmark
test can focus purely on the hot path under measurement.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

from src.affine_control.swing_types import SwingOptimizationConfig
from src.golf_simulation.ball_flight import BallFlightDynamics, BallFlightState
from src.golf_simulation.putting import GreenSurface, PuttingSimulator


# ---------------------------------------------------------------------------
# Shared dynamics helpers
# ---------------------------------------------------------------------------


def double_integrator_dynamics(
    x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
) -> np.ndarray[Any, Any]:
    """Simple double-integrator dynamics for a single joint: [dq, ddq] = [q_dot, u]."""
    n = len(x) // 2
    dq = x[n:]
    ddq = u
    return np.concatenate([dq, ddq])


def pendulum_dynamics(
    x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
) -> np.ndarray[Any, Any]:
    """Single-link pendulum with unit length and gravity = 9.81.

    State: [theta, omega], Control: [torque]
    """
    g = 9.81
    theta, omega = x[0], x[1]
    dtheta = omega
    domega = -g * np.sin(theta) + u[0]
    return np.array([dtheta, domega])


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ball_flight_dynamics() -> BallFlightDynamics:
    """Standard golf ball flight dynamics model."""
    return BallFlightDynamics()


@pytest.fixture
def driver_initial_state() -> BallFlightState:
    """Typical driver launch state (60 m/s, 12-deg launch, 3000 rpm backspin)."""
    speed = 60.0  # m/s
    launch_angle = np.radians(12.0)
    vx = speed * np.cos(launch_angle)
    vz = speed * np.sin(launch_angle)
    spin_rad_s = 3000.0 * (2.0 * np.pi / 60.0)  # RPM -> rad/s
    return BallFlightState(
        position=np.array([0.0, 0.0, 0.01]),
        velocity=np.array([vx, 0.0, vz]),
        spin=np.array([0.0, -spin_rad_s, 0.0]),
    )


@pytest.fixture
def wedge_initial_state() -> BallFlightState:
    """Typical wedge shot state (35 m/s, 30-deg launch, 8000 rpm backspin)."""
    speed = 35.0
    launch_angle = np.radians(30.0)
    vx = speed * np.cos(launch_angle)
    vz = speed * np.sin(launch_angle)
    spin_rad_s = 8000.0 * (2.0 * np.pi / 60.0)
    return BallFlightState(
        position=np.array([0.0, 0.0, 0.01]),
        velocity=np.array([vx, 0.0, vz]),
        spin=np.array([0.0, -spin_rad_s, 0.0]),
    )


@pytest.fixture
def flat_green_simulator() -> PuttingSimulator:
    """Flat, medium-speed green for putting benchmarks."""
    green = GreenSurface.create_flat_green(width=20.0, height=20.0, stimp=11.0)
    return PuttingSimulator(surface=green)


@pytest.fixture
def contoured_green_simulator() -> PuttingSimulator:
    """Contoured green surface with several elevation control points."""
    control_points = [
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 0.05),
        (20.0, 0.0, 0.10),
        (0.0, 10.0, 0.02),
        (10.0, 10.0, 0.08),
        (20.0, 10.0, 0.15),
        (0.0, 20.0, 0.05),
        (10.0, 20.0, 0.12),
        (20.0, 20.0, 0.20),
    ]
    green = GreenSurface(width=20.0, height=20.0, stimp=11.0, control_points=control_points)
    return PuttingSimulator(surface=green)


@pytest.fixture
def ilqr_solver() -> Any:
    """iLQR solver instance."""
    from src.core.optimizers.ilqr_solver import ILQRSolver

    return ILQRSolver()


@pytest.fixture
def swing_optimizer_config_3j() -> SwingOptimizationConfig:
    """Swing optimizer config for a 3-joint model (benchmark-safe horizon)."""
    return SwingOptimizationConfig(
        n_joints=3,
        horizon_steps=20,
        dt=0.01,
        max_iterations=3,
        allow_mock_solver=True,
    )


@pytest.fixture
def double_integrator_fn() -> Callable[[Any, Any], Any]:
    """Return the double-integrator dynamics function."""
    return double_integrator_dynamics


@pytest.fixture
def pendulum_dynamics_fn() -> Callable[[Any, Any], Any]:
    """Return the pendulum dynamics function."""
    return pendulum_dynamics
