"""Reproducible, explicitly scoped models for the state-space textbook chapter."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import expm

type Array = NDArray[np.float64]


def motor_matrices() -> tuple[Array, Array]:
    """Return the chapter's ideal DC motor in state order (current, angle, rate).

    Input is winding voltage; there is no applied load torque. SI units give
    numerically equal ideal torque and back-EMF constants. These are illustrative
    parameters, not identified hardware or muscle properties.
    """
    inductance, resistance = 0.01, 1.0
    torque_constant, emf_constant = 0.02, 0.02
    inertia, damping = 0.001, 0.001
    a = np.array(
        [
            [-resistance / inductance, 0.0, -emf_constant / inductance],
            [0.0, 0.0, 1.0],
            [torque_constant / inertia, 0.0, -damping / inertia],
        ]
    )
    b = np.array([[1.0 / inductance], [0.0], [0.0]])
    return a, b


@dataclass(frozen=True)
class TankParameters:
    """Equal-area open tanks with bidirectional head-driven flow, in SI units.

    Both outlets are at zero height. The transfer and outlet coefficients have
    units m^(5/2)/s; area has units m^2. The rate is defined for nonnegative
    heights and inflow. Numerical stages outside that physical domain are errors,
    rather than silently clipped states.
    """

    area: float = 0.1
    transfer: float = 0.05
    outflow: float = 0.03

    def __post_init__(self) -> None:
        """Reject nonphysical geometry or flow coefficients."""
        parameters = np.array([self.area, self.transfer, self.outflow])
        if not np.all(np.isfinite(parameters)) or np.any(parameters <= 0):
            raise ValueError("Tank parameters must be finite and positive")

    def rate(self, heights: Array, inflow: float) -> Array:
        """Compute volume-conserving height rates; positive transfer is tank 1 to 2."""
        h = np.asarray(heights, dtype=float)
        if h.shape != (2,) or not np.all(np.isfinite(h)) or np.any(h < 0):
            raise ValueError("Heights must be a finite nonnegative two-vector")
        if not np.isfinite(inflow) or inflow < 0:
            raise ValueError("Inflow must be finite and nonnegative")
        difference = h[0] - h[1]
        between = self.transfer * np.sign(difference) * np.sqrt(abs(difference))
        outlet = self.outflow * np.sqrt(h[1])
        return np.array([inflow - between, between - outlet]) / self.area


def zoh_matrices(a: Array, b: Array, period: float) -> tuple[Array, Array]:
    """Exact LTI zero-order hold using a block exponential, including singular A.

    A and B must be finite real matrices of compatible nonempty dimensions.
    Zero period returns identity/zero. This discretizes an open-loop plant;
    a sampled feedback law must be closed around the resulting matrices.
    """
    if np.iscomplexobj(a) or np.iscomplexobj(b):
        raise ValueError("Matrices must be real")
    dynamics, inputs = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if dynamics.ndim != 2 or dynamics.shape[0] == 0:
        raise ValueError("A must be a nonempty square matrix")
    n = dynamics.shape[0]
    if dynamics.shape != (n, n):
        raise ValueError("A must be square")
    if inputs.ndim != 2 or inputs.shape[0] != n or inputs.shape[1] == 0:
        raise ValueError("B must have compatible nonempty dimensions")
    if not np.all(np.isfinite(dynamics)) or not np.all(np.isfinite(inputs)):
        raise ValueError("Matrices must be finite")
    if not np.isfinite(period) or period < 0:
        raise ValueError("Period must be finite and nonnegative")
    block = np.zeros((n + inputs.shape[1], n + inputs.shape[1]))
    block[:n, :n], block[:n, n:] = dynamics, inputs
    propagated = np.asarray(expm(period * block), dtype=float)
    return propagated[:n, :n], propagated[:n, n:]
