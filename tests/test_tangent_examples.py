"""Tests for tangent models examples."""

import numpy as np

from src.tangent_models.examples import (
    PlanarQuadrotor,
    RobotArm,
    SimplePendulum,
    SpacecraftRendezvous,
)


def test_simple_pendulum():
    """Test simple pendulum dynamics."""
    model = SimplePendulum()
    x = np.array([0.0, 0.0])
    u = 0.0
    dx = model.dynamics(x, u)
    assert dx.shape == (2,)

    A, B = model.linearize(x, u)
    assert A.shape == (2, 2)
    assert B.shape == (2, 1)


def test_spacecraft_rendezvous():
    """Test spacecraft rendezvous dynamics."""
    model = SpacecraftRendezvous()
    x = np.zeros(6)
    u = np.zeros(3)
    dx = model.dynamics(x, u)
    assert dx.shape == (6,)

    # Equilibrium check
    # At [0,0,0,0,0,0], acceleration should be zero with zero input?
    # Relative motion: if rx=0, ry=0, rz=0, vx=0, vy=0, vz=0
    # rc = rt
    # ax = n^2 rt - mu rt / rt^3 = n^2 rt - (mu/rt^3) rt = 0. Correct.
    assert np.allclose(dx, 0.0)

    A, B = model.linearize(x, u)
    assert A.shape == (6, 6)
    assert B.shape == (6, 3)


def test_planar_quadrotor():
    """Test planar quadrotor dynamics."""
    model = PlanarQuadrotor()
    x = np.zeros(6)
    # Hover thrust: T = mg
    # u1 + u2 = mg => u1 = u2 = mg/2
    u_hover = np.array([model.m * model.g / 2, model.m * model.g / 2])

    dx = model.dynamics(x, u_hover)
    # Should be zero accel
    # ax = 0
    # ay = T/m - g = g - g = 0
    # alpha = 0
    assert np.allclose(dx[3:], 0.0)

    A, B = model.linearize(x, u_hover)
    assert A.shape == (6, 6)
    assert B.shape == (6, 2)


def test_robot_arm():
    """Test robot arm dynamics."""
    model = RobotArm()
    x = np.zeros(4)
    u = np.zeros(2)

    dx = model.dynamics(x, u)
    assert dx.shape == (4,)

    A, B = model.linearize(x, u)
    assert A.shape == (4, 4)
    assert B.shape == (4, 2)
