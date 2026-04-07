"""Double pendulum dynamics and physics for RL funnel benchmarking."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.integrate import solve_ivp

from src.core.constants import GRAVITY_M_S2
from src.core.contracts.definitions import require
from src.core.contracts.validators import check_finite_array, check_positive

logger = logging.getLogger(__name__)

# Double pendulum physical parameters (2-DoF golf swing proxy)
PENDULUM_M1 = 1.0  # kg, mass of upper link
PENDULUM_M2 = 1.0  # kg, mass of lower link
PENDULUM_L1 = 0.5  # m, length of upper link
PENDULUM_L2 = 0.5  # m, length of lower link

# Default control saturation limits for the double-pendulum benchmark (N*m).
DEFAULT_CONTROL_SATURATION = 50.0
CONTROL_SATURATION_DEFAULT: tuple[float, float] = (-50.0, 50.0)


def validate_state_vector(x: npt.NDArray[Any], name: str) -> None:
    """Validate that the state vector is finite."""
    check_finite_array(x, name)


def double_pendulum_mass_matrix(th1: float, th2: float) -> npt.NDArray[Any]:
    """Compute the 2x2 mass (inertia) matrix for a double pendulum.

    M = [[( m1 + m2 ) * L1^2,        m2 * L1 * L2 * cos(th1-th2)],
         [m2 * L1 * L2 * cos(th1-th2),  m2 * L2^2               ]]
    """
    c12 = np.cos(th1 - th2)
    M = np.array(
        [
            [
                (PENDULUM_M1 + PENDULUM_M2) * PENDULUM_L1**2,
                PENDULUM_M2 * PENDULUM_L1 * PENDULUM_L2 * c12,
            ],
            [
                PENDULUM_M2 * PENDULUM_L1 * PENDULUM_L2 * c12,
                PENDULUM_M2 * PENDULUM_L2**2,
            ],
        ]
    )
    return M


def double_pendulum_drift(
    t: float, x: npt.NDArray[Any], g: float = GRAVITY_M_S2
) -> npt.NDArray[Any]:
    """Passive dynamics of a double pendulum (drift term f(x,0)).

    State: x = [theta1, theta2, dtheta1, dtheta2]
    Parameters: m1=m2=1kg, L1=L2=0.5m
    """
    require(
        isinstance(x, np.ndarray) and x.shape == (4,),
        "x must be a numpy array of shape (4,)",
        x,
    )
    check_finite_array(x, "x")
    check_positive(g, "g")

    # m1, m2, L1, L2 unused
    th1, th2, dth1, dth2 = x
    s12 = np.sin(th1 - th2)
    M = double_pendulum_mass_matrix(th1, th2)
    rhs = np.array(
        [
            -PENDULUM_M2 * PENDULUM_L1 * PENDULUM_L2 * dth2**2 * s12
            - (PENDULUM_M1 + PENDULUM_M2) * g * PENDULUM_L1 * np.sin(th1),
            PENDULUM_M2 * PENDULUM_L1 * PENDULUM_L2 * dth1**2 * s12
            - PENDULUM_M2 * g * PENDULUM_L2 * np.sin(th2),
        ]
    )
    ddth = np.linalg.solve(M, rhs)
    return np.array([dth1, dth2, ddth[0], ddth[1]])


def double_pendulum_B(x: npt.NDArray[Any]) -> npt.NDArray[Any]:
    """Control input matrix g(x): torques applied at both joints."""
    require(
        isinstance(x, np.ndarray) and x.shape == (4,),
        "x must be a numpy array of shape (4,)",
        x,
    )
    check_finite_array(x, "x")

    # m1, m2, L1, L2 unused
    th1, th2, _, _ = x
    M_inv = np.linalg.inv(double_pendulum_mass_matrix(th1, th2))
    B_full = np.zeros((4, 2))
    B_full[2:, :] = M_inv  # torques affect angular accelerations
    return B_full


def generate_reference_trajectory(
    t_span: tuple[float, float],
    dt: float = 0.01,
    x0: npt.NDArray[Any] | None = None,
) -> tuple[npt.NDArray[Any], npt.NDArray[Any]]:
    """Generate reference trajectory via passive simulation from backswing position."""
    require(
        len(t_span) == 2 and t_span[1] > t_span[0],
        "t_span must be (t0, tf) with tf > t0",
        t_span,
    )
    check_positive(dt, "dt")
    if x0 is not None:
        require(
            isinstance(x0, np.ndarray) and x0.shape == (4,),
            "x0 must be a numpy array of shape (4,)",
            x0,
        )
        check_finite_array(x0, "x0")

    if x0 is None:
        x0 = np.array([np.pi / 2, np.pi / 4, 0.0, 0.0])
    validate_state_vector(x0, "x0")

    sol = solve_ivp(
        double_pendulum_drift,
        t_span,
        x0,
        max_step=dt,
        dense_output=True,
    )
    t_ref = np.arange(t_span[0], t_span[1], dt)
    x_ref = sol.sol(t_ref)
    return t_ref, x_ref
