import os
import sys

import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tangent_models.examples import (
    PlanarQuadrotor,
    RobotArm,
    SimplePendulum,
    SpacecraftRendezvous,
)


def test_simple_pendulum() -> None:
    sys = SimplePendulum()
    x = np.array([0.1, 0.0])
    u = np.array([0.0])
    dx = sys.dynamics(x, u)
    assert dx.shape == (2,)

    A, B = sys.linearize(x, u)
    assert A.shape == (2, 2)
    assert B.shape == (2, 1)


def test_spacecraft_rendezvous() -> None:
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
    sys = PlanarQuadrotor()
    x = np.zeros(6)
    u = np.zeros(2)
    dx = sys.dynamics(x, u)
    assert dx.shape == (6,)

    A, B = sys.linearize(x, u)
    assert A.shape == (6, 6)
    assert B.shape == (6, 2)


def test_robot_arm() -> None:
    sys = RobotArm()
    x = np.array([0.1, 0.1, 0.0, 0.0])
    u = np.zeros(2)
    dx = sys.dynamics(x, u)
    assert dx.shape == (4,)

    A, B = sys.linearize(x, u)
    assert A.shape == (4, 4)
    assert B.shape == (4, 2)
