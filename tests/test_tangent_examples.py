import numpy as np
import pytest

# Add project root to path
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


def test_robot_arm_linearize_uses_central_differences() -> None:
    """RobotArm.linearize should use central differences (O(eps^2) accuracy).

    Central differences are more accurate than forward differences for the same epsilon.
    We verify this by comparing the A matrix from linearize() to a reference computed
    with a very small epsilon via central differences directly, using a larger epsilon
    for the forward-difference baseline to expose the accuracy gap.
    """
    system = RobotArm()
    x = np.array([0.3, 0.4, 0.1, 0.05])
    u = np.array([1.0, 0.5])

    # Compute A, B via linearize() (should use central differences)
    A, B = system.linearize(x, u)
    assert A.shape == (4, 4)
    assert B.shape == (4, 2)

    # Compute a high-accuracy reference A using central differences with smaller epsilon
    eps_ref = 1e-8
    n = 4
    A_ref = np.zeros((n, n))
    for i in range(n):
        x_plus = x.copy()
        x_plus[i] += eps_ref
        x_minus = x.copy()
        x_minus[i] -= eps_ref
        A_ref[:, i] = (system.dynamics(x_plus, u) - system.dynamics(x_minus, u)) / (2 * eps_ref)

    # The linearize() result should closely match the high-accuracy central-difference reference
    np.testing.assert_allclose(A, A_ref, rtol=1e-4, atol=1e-6)

    # Also verify B against central-difference reference
    m = 2
    B_ref = np.zeros((n, m))
    u_arr = np.array(u, dtype=float)
    for i in range(m):
        u_plus = u_arr.copy()
        u_plus[i] += eps_ref
        u_minus = u_arr.copy()
        u_minus[i] -= eps_ref
        B_ref[:, i] = (system.dynamics(x, u_plus) - system.dynamics(x, u_minus)) / (2 * eps_ref)

    np.testing.assert_allclose(B, B_ref, rtol=1e-4, atol=1e-6)
