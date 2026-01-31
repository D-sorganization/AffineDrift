import numpy as np

from src.tangent_models.examples import (
    GRAVITY_M_S2,
    PlanarQuadrotor,
    RobotArm,
    SimplePendulum,
    SpacecraftRendezvous,
)


def test_simple_pendulum() -> None:
    """Test Simple Pendulum dynamics."""
    sys = SimplePendulum(m=1.0, L=2.0, g=GRAVITY_M_S2)
    x = np.array([np.pi / 2, 0])
    u = np.array([0.0])
    dx = sys.dynamics(x, u)
    # At horizontal, gravity pulls down
    # dtheta = 0
    # domega = -g/L * sin(pi/2) = -9.81/2 = -4.905
    assert np.isclose(dx[0], 0)
    assert np.isclose(dx[1], -4.905)


def test_spacecraft_rendezvous() -> None:
    """Test Spacecraft Rendezvous dynamics."""
    sys = SpacecraftRendezvous()
    x = np.zeros(6)
    u = np.zeros(3)
    dx = sys.dynamics(x, u)
    # At equilibrium
    assert np.allclose(dx, 0)

    # With offset
    x[0] = 100  # 100m radial offset
    dx = sys.dynamics(x, u)
    assert not np.allclose(dx, 0)

    # Test linearization shape
    A, B = sys.linearize(x, u)
    assert A.shape == (6, 6)
    assert B.shape == (6, 3)


def test_planar_quadrotor() -> None:
    """Test Planar Quadrotor dynamics."""
    sys = PlanarQuadrotor()
    x = np.zeros(6)
    # Hover thrust
    # T = mg
    # u1 + u2 = m*g
    u_hover = sys.m * sys.g / 2
    u = np.array([u_hover, u_hover])

    dx = sys.dynamics(x, u)
    # Should be zero accel (except maybe numerical noise)
    assert np.allclose(dx[3:], 0)


def test_robot_arm() -> None:
    """Test Robot Arm dynamics."""
    sys = RobotArm()
    x = np.zeros(4)
    u = np.zeros(2)

    # Just check it runs and returns correct shape
    dx = sys.dynamics(x, u)
    assert dx.shape == (4,)

    A, B = sys.linearize(x, u)
    assert A.shape == (4, 4)
    assert B.shape == (4, 2)
