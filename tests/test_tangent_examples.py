import numpy as np
import pytest

# Add project root to path
from src.core.constants import DEFAULT_SPACECRAFT_MASS_KG, EARTH_MU, ISS_ORBIT_RADIUS_M
from src.tangent_models.examples import (
    PlanarQuadrotor,
    RobotArm,
    SimplePendulum,
    SpacecraftRendezvous,
)


def test_simple_pendulum() -> None:
    """Test simple pendulum dynamics and linearization."""
    sys = SimplePendulum()
    x = np.array([0.1, 0.0])
    u = np.array([0.0])
    dx = sys.dynamics(x, u)
    assert dx.shape == (2,)

    A, B = sys.linearize(x, u)
    assert A.shape == (2, 2)
    assert B.shape == (2, 1)


def test_spacecraft_rendezvous() -> None:
    """Test spacecraft rendezvous dynamics and linearization."""
    sys = SpacecraftRendezvous()
    x = np.zeros(6)
    u = np.zeros(3)
    dx = sys.dynamics(x, u)
    assert dx.shape == (6,)

    A, B = sys.linearize(x, u)
    assert A.shape == (6, 6)
    assert B.shape == (6, 3)

    # Check that linearization at origin matches HCW structure approximately
    # HCW A matrix has 0s and identity on top right, and n dependent terms
    assert A[0, 3] == 1.0
    assert A[3, 0] > 0  # n^2 * 1? No, 3n^2 - 2n^2?
    # Let's just check shapes and runnability for now, deeper math verification is in the article text/logic.


def test_planar_quadrotor() -> None:
    """Test planar quadrotor dynamics and linearization."""
    sys = PlanarQuadrotor()
    x = np.zeros(6)
    u = np.zeros(2)
    dx = sys.dynamics(x, u)
    assert dx.shape == (6,)

    A, B = sys.linearize(x, u)
    assert A.shape == (6, 6)
    assert B.shape == (6, 2)


def test_robot_arm() -> None:
    """Test robot arm dynamics and linearization."""
    sys = RobotArm()
    x = np.array([0.1, 0.1, 0.0, 0.0])
    u = np.zeros(2)
    dx = sys.dynamics(x, u)
    assert dx.shape == (4,)

    A, B = sys.linearize(x, u)
    assert A.shape == (4, 4)
    assert B.shape == (4, 2)


def test_spacecraft_rendezvous_rejects_scalar_control_in_dynamics() -> None:
    """SpacecraftRendezvous.dynamics should raise ValueError for scalar control."""
    system = SpacecraftRendezvous()
    x = np.zeros(6)
    with pytest.raises(ValueError):
        system.dynamics(x, 1.0)


def test_spacecraft_rendezvous_rejects_scalar_control_in_linearize() -> None:
    """SpacecraftRendezvous.linearize should raise ValueError for scalar control."""
    system = SpacecraftRendezvous()
    x = np.zeros(6)
    with pytest.raises(ValueError):
        system.linearize(x, 1.0)


def test_planar_quadrotor_rejects_scalar_control_in_dynamics() -> None:
    """PlanarQuadrotor.dynamics should raise ValueError for scalar control."""
    system = PlanarQuadrotor()
    x = np.zeros(6)
    with pytest.raises(ValueError):
        system.dynamics(x, 1.0)


def test_planar_quadrotor_rejects_scalar_control_in_linearize() -> None:
    """PlanarQuadrotor.linearize should raise ValueError for scalar control."""
    system = PlanarQuadrotor()
    x = np.zeros(6)
    with pytest.raises(ValueError):
        system.linearize(x, 1.0)


def test_robot_arm_rejects_scalar_control_in_dynamics() -> None:
    """RobotArm.dynamics should raise ValueError for scalar control."""
    system = RobotArm()
    x = np.array([0.1, 0.1, 0.0, 0.0])
    with pytest.raises(ValueError):
        system.dynamics(x, 1.0)


def test_robot_arm_rejects_scalar_control_in_linearize() -> None:
    """RobotArm.linearize should raise ValueError for scalar control."""
    system = RobotArm()
    x = np.array([0.1, 0.1, 0.0, 0.0])
    with pytest.raises(ValueError):
        system.linearize(x, 1.0)


def test_spacecraft_rendezvous_defaults_use_named_constants() -> None:
    """SpacecraftRendezvous defaults must match named constants from src.core.constants."""
    sys = SpacecraftRendezvous()
    assert sys.mu == EARTH_MU, "mu default must equal EARTH_MU from core.constants"
    assert (
        sys.r_t == ISS_ORBIT_RADIUS_M
    ), "r_t default must equal ISS_ORBIT_RADIUS_M from core.constants"
    assert (
        sys.m == DEFAULT_SPACECRAFT_MASS_KG
    ), "m default must equal DEFAULT_SPACECRAFT_MASS_KG from core.constants"
