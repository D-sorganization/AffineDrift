"""Drift/input split of the planar double pendulum for the WEB-06.3 sandbox (#4533).

The model is the point-mass double pendulum of
:func:`src.affine_control.dynamics.double_pendulum_mass_matrix`: absolute link
angles measured from the downward vertical, a point mass ``m1`` at the middle of
link 1 and a point mass ``m2`` at the middle of link 2. Its equation of motion
``M(q) qdd + C(q, qd) qd + dV/dq = tau`` is control-affine,

    qdd = f(x) + G(x) tau,   f = -M^-1 (C qd + dV/dq),   G = M^-1,

and this module exposes exactly that split, at one state and along a trajectory.
``js/drift-control-sandbox.js`` mirrors every function here; the parity
fixture ``tests/fixtures/widgets/drift-control-sandbox.parity.json`` keeps the
two in agreement.

The split is a **same-state** decomposition. Along a driven trajectory the
drift is evaluated at states the input helped to reach, so the drift samples
are not the zero-torque trajectory; that counterfactual has to be integrated
separately from the initial condition (theory Part 1, "Structural
Consequences").
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import partial

import numpy as np
from numpy.typing import ArrayLike, NDArray

from src.affine_control.dynamics import (
    double_pendulum_coriolis,
    double_pendulum_mass_matrix,
    planar_double_pendulum_trajectory,
)
from src.core.constants import GRAVITY_M_S2

type Array = NDArray[np.float64]

__all__ = [
    "DoublePendulumParams",
    "SandboxSample",
    "affine_split",
    "generalized_torque",
    "grad_potential",
    "potential",
    "simulate",
    "tip_acceleration_split",
    "tip_position",
]


@dataclass(frozen=True)
class DoublePendulumParams:
    """Masses (kg), link lengths (m) and gravity (m/s^2); all finite and positive."""

    m1: float
    m2: float
    l1: float
    l2: float
    gravity: float = GRAVITY_M_S2

    def __post_init__(self) -> None:
        """Reject non-finite or non-positive parameters (fail closed)."""
        for name in ("m1", "m2", "l1", "l2", "gravity"):
            value = getattr(self, name)
            if not (math.isfinite(value) and value > 0.0):
                raise ValueError(f"{name} must be finite and positive, got {value!r}")

    def mass_matrix(self, q: Array) -> Array:
        """``M(q)`` from :func:`double_pendulum_mass_matrix` with these parameters."""
        return double_pendulum_mass_matrix(q, self.m1, self.m2, self.l1, self.l2)


@dataclass(frozen=True)
class SandboxSample:
    """One trajectory sample with the same-state split of its joint acceleration."""

    t: float
    q: Array
    qd: Array
    drift_qdd: Array
    input_qdd: Array


def potential(q: Array, params: DoublePendulumParams) -> float:
    """Gravitational potential ``V = -g [(m1/2 + m2) l1 cos q1 + m2 (l2/2) cos q2]``."""
    p = params
    upper = (0.5 * p.m1 + p.m2) * p.l1 * math.cos(q[0])
    return -p.gravity * (upper + 0.5 * p.m2 * p.l2 * math.cos(q[1]))


def grad_potential(q: Array, params: DoublePendulumParams) -> Array:
    """``dV/dq`` for :func:`potential`, consistent with the mass matrix's mass layout."""
    p = params
    return np.array(
        [
            p.gravity * (0.5 * p.m1 + p.m2) * p.l1 * math.sin(q[0]),
            p.gravity * 0.5 * p.m2 * p.l2 * math.sin(q[1]),
        ]
    )


def generalized_torque(shoulder: float, wrist: float) -> Array:
    """Generalized force ``B u`` for a shoulder torque and a wrist torque.

    With absolute angles the wrist torque acts between link 1 and link 2, so it
    enters as ``(-wrist, wrist)``; ``B`` is constant, which keeps the model
    control-affine. Postcondition: ``B u . qd = shoulder q1d + wrist (q2d - q1d)``.
    """
    return np.array([shoulder - wrist, wrist], dtype=float)


def affine_split(
    q: ArrayLike, qd: ArrayLike, torque: ArrayLike, params: DoublePendulumParams
) -> tuple[Array, Array]:
    """Return ``(f_qdd, G tau)``: the drift and input joint accelerations at one state.

    Postcondition: ``M (f_qdd + G tau) + C qd + dV/dq = tau``. The drift term does
    not depend on ``torque``; the input term is linear in it.
    """
    q = np.asarray(q, dtype=float)
    qd = np.asarray(qd, dtype=float)
    mass = params.mass_matrix(q)
    bias = double_pendulum_coriolis(q, qd, params.m2, params.l1, params.l2) @ qd + grad_potential(
        q, params
    )
    drift = np.linalg.solve(mass, -bias)
    input_qdd = np.linalg.solve(mass, np.asarray(torque, dtype=float))
    return drift, input_qdd


def tip_position(q: Array, params: DoublePendulumParams) -> Array:
    """Cartesian position of the end of link 2; ``y`` points up, the pivot is the origin."""
    return np.array(
        [
            params.l1 * math.sin(q[0]) + params.l2 * math.sin(q[1]),
            -params.l1 * math.cos(q[0]) - params.l2 * math.cos(q[1]),
        ]
    )


def tip_acceleration_split(
    q: ArrayLike,
    qd: ArrayLike,
    drift_qdd: ArrayLike,
    input_qdd: ArrayLike,
    params: DoublePendulumParams,
) -> tuple[Array, Array]:
    """Split the tip acceleration ``J qdd + Jdot qd`` into drift and input parts.

    ``Jdot qd`` depends only on the state, so it belongs to the drift (theory
    Part 1: the kinematic term "remains in the same-state baseline").
    """
    q = np.asarray(q, dtype=float)
    qd = np.asarray(qd, dtype=float)
    l1, l2 = params.l1, params.l2
    c1, s1, c2, s2 = math.cos(q[0]), math.sin(q[0]), math.cos(q[1]), math.sin(q[1])
    jacobian = np.array([[l1 * c1, l2 * c2], [l1 * s1, l2 * s2]])
    jdot_qd = np.array(
        [
            -l1 * s1 * qd[0] ** 2 - l2 * s2 * qd[1] ** 2,
            l1 * c1 * qd[0] ** 2 + l2 * c2 * qd[1] ** 2,
        ]
    )
    return jacobian @ np.asarray(drift_qdd, dtype=float) + jdot_qd, jacobian @ np.asarray(
        input_qdd, dtype=float
    )


def simulate(
    params: DoublePendulumParams,
    q0: ArrayLike,
    qd0: ArrayLike,
    torque: ArrayLike,
    horizon: float,
    steps: int,
) -> list[SandboxSample]:
    """Integrate with :func:`planar_double_pendulum_trajectory` under constant torque.

    Each sample carries :func:`affine_split` at its own state. Preconditions:
    ``horizon > 0`` and ``steps >= 1``.
    """
    if not (math.isfinite(horizon) and horizon > 0.0):
        raise ValueError("horizon must be finite and positive")
    if steps < 1:
        raise ValueError("steps must be at least 1")
    torque = np.asarray(torque, dtype=float)
    trajectory = planar_double_pendulum_trajectory(
        params.mass_matrix,
        partial(grad_potential, params=params),
        np.asarray(q0, dtype=float),
        np.asarray(qd0, dtype=float),
        torque,
        horizon,
        steps,
    )
    samples = []
    for t, q, qd in trajectory:
        drift, input_qdd = affine_split(q, qd, torque, params)
        samples.append(SandboxSample(t=t, q=q, qd=qd, drift_qdd=drift, input_qdd=input_qdd))
    return samples
