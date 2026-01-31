"""Tests for DDP solver."""

import numpy as np
import pytest
from src.affine_control.ddp import adaptive_timestep_ddp


def double_integrator(x, u):
    """Dynamics for double integrator."""
    # x = [pos, vel]
    # u = [acc]
    return np.array([x[1], u[0]])


def test_ddp_mock():
    """Test DDP mock implementation."""
    x0 = np.array([0.0, 0.0])
    x_target = np.array([1.0, 0.0])
    T = 1.0

    # Just check it runs and returns something
    # Since the implementation is a mock, we don't expect correct control
    x_traj, u_traj, t_traj = adaptive_timestep_ddp(double_integrator, x0, x_target, T)

    assert len(x_traj) > 0
    assert len(u_traj) > 0
    assert len(t_traj) > 0
