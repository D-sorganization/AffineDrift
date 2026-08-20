"""Recursive Newton-Euler for a planar revolute chain, with a Lagrangian check.

Volume 0 chapter 7 works through an RNEA computation for a 3-link planar arm,
then omits the arithmetic ("detailed numerical computation omitted for brevity")
and states the answer as ``tau = [2.3, 1.1, 0.08]`` prefaced by "the output
*might* be" -- immediately followed by "These are the torques the three joint
motors must produce". A stipulated number presented as a computed one.

The partial outward pass it does show is also wrong. It gives

    V_1 x S_1 qdot_1 = (0, 0, 0.5) x (0, 0, 0.2) = (0.1, 0, 0)   (approx)

but the cross product of two parallel vectors is exactly zero, not approximately
``(0.1, 0, 0)``. The spurious term is then carried into ``Vdot_1``.

This module computes the torques by both routes the chapter names -- the
recursion it is teaching, and the Lagrangian formulation it proposes as
validation -- so the published numbers come from a computation and the
chapter's own cross-check is executed rather than asserted.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from src.affine_control.dynamics import christoffel_coriolis

__all__ = ["PlanarChain", "PlanarLink"]


type Array = NDArray[np.float64]

GRAVITY_M_S2 = 9.81


@dataclass(frozen=True)
class PlanarLink:
    """One revolute link rotating about the out-of-plane axis.

    ``com_offset`` is measured from the link's own proximal joint, along the
    link; ``inertia`` is about the link's centre of mass.
    """

    mass: float
    length: float
    com_offset: float
    inertia: float


@dataclass(frozen=True)
class PlanarChain:
    """A serial chain of planar revolute links."""

    links: tuple[PlanarLink, ...]

    @property
    def size(self) -> int:
        """Number of joints."""
        return len(self.links)

    @staticmethod
    def _cross(a: Array, b: Array) -> float:
        """Out-of-plane component of a planar cross product.

        Written out because numpy 2 removed the two-dimensional ``np.cross``.
        """
        return float(a[0] * b[1] - a[1] * b[0])

    def inverse_dynamics(
        self, q: Array, qd: Array, qdd: Array, gravity: float = GRAVITY_M_S2
    ) -> Array:
        """Joint torques by the recursive Newton-Euler algorithm.

        Gravity enters the standard way, as a fictitious base acceleration of
        ``+g`` upward, which saves carrying a separate weight term through the
        recursion.
        """
        q = np.asarray(q, dtype=float)
        qd = np.asarray(qd, dtype=float)
        qdd = np.asarray(qdd, dtype=float)
        n = self.size

        angles = np.cumsum(q)
        omega = np.cumsum(qd)
        alpha = np.cumsum(qdd)

        # -- outward pass: accelerate each joint origin, then each centre of mass
        joint_accel = np.array([0.0, gravity])
        com_accel = np.zeros((n, 2))
        for index, link in enumerate(self.links):
            direction = np.array([np.cos(angles[index]), np.sin(angles[index])])
            to_com = link.com_offset * direction
            to_next = link.length * direction
            # a = a_parent + alpha x r - omega^2 r, planar form
            perp_com = np.array([-to_com[1], to_com[0]])
            perp_next = np.array([-to_next[1], to_next[0]])
            com_accel[index] = joint_accel + alpha[index] * perp_com - omega[index] ** 2 * to_com
            joint_accel = joint_accel + alpha[index] * perp_next - omega[index] ** 2 * to_next

        # -- inward pass: accumulate force and moment from the tip back
        force = np.zeros(2)
        moment = 0.0
        torque = np.zeros(n)
        for index in reversed(range(n)):
            link = self.links[index]
            direction = np.array([np.cos(angles[index]), np.sin(angles[index])])
            to_com = link.com_offset * direction
            to_next = link.length * direction

            distal_force = force
            distal_moment = moment
            force = link.mass * com_accel[index] + distal_force
            moment = (
                link.inertia * alpha[index]
                + distal_moment
                + self._cross(to_com, link.mass * com_accel[index])
                + self._cross(to_next, distal_force)
            )
            torque[index] = moment
        return torque

    # -- independent route, for cross-checking -----------------------------

    def _com_jacobian(self, q: Array, index: int) -> Array:
        """``d(p_com_i)/dq`` for link ``index``, shape ``(2, size)``."""
        angles = np.cumsum(np.asarray(q, dtype=float))
        jac = np.zeros((2, self.size))
        for joint in range(index + 1):
            delta = np.zeros(2)
            for link in range(joint, index + 1):
                reach = self.links[link].com_offset if link == index else self.links[link].length
                delta += reach * np.array([-np.sin(angles[link]), np.cos(angles[link])])
            jac[:, joint] = delta
        return jac

    def mass_matrix(self, q: Array) -> Array:
        """``M(q)`` assembled from centre-of-mass Jacobians."""
        total = np.zeros((self.size, self.size))
        for index, link in enumerate(self.links):
            jac = self._com_jacobian(q, index)
            angular = np.zeros(self.size)
            angular[: index + 1] = 1.0
            total += link.mass * (jac.T @ jac) + link.inertia * np.outer(angular, angular)
        return 0.5 * (total + total.T)

    def potential_energy(self, q: Array, gravity: float = GRAVITY_M_S2) -> float:
        """Gravitational potential, taking ``+y`` as up."""
        angles = np.cumsum(np.asarray(q, dtype=float))
        height = 0.0
        total = 0.0
        for index, link in enumerate(self.links):
            total += link.mass * gravity * (height + link.com_offset * np.sin(angles[index]))
            height += link.length * np.sin(angles[index])
        return float(total)

    def gravity_torque(self, q: Array, gravity: float = GRAVITY_M_S2) -> Array:
        """``dV/dq`` by central differences."""
        q = np.asarray(q, dtype=float)
        out = np.zeros(self.size)
        step = 1e-6
        for index in range(self.size):
            forward, backward = q.copy(), q.copy()
            forward[index] += step
            backward[index] -= step
            high = self.potential_energy(forward, gravity)
            low = self.potential_energy(backward, gravity)
            out[index] = (high - low) / (2.0 * step)
        return out

    def inverse_dynamics_lagrangian(
        self, q: Array, qd: Array, qdd: Array, gravity: float = GRAVITY_M_S2
    ) -> Array:
        """``tau = M qddot + C qdot + dV/dq``, the route the chapter proposes as validation.

        Structurally independent of :meth:`inverse_dynamics`: it never forms a
        link-by-link recursion, and its Coriolis term comes from differentiating
        the mass matrix rather than from spatial cross products. Agreement
        between the two is therefore evidence, not a restatement.
        """
        mass = self.mass_matrix(q)
        coriolis = christoffel_coriolis(self.mass_matrix, q, qd)
        torque: Array = (
            mass @ np.asarray(qdd, dtype=float)
            + coriolis @ np.asarray(qd, dtype=float)
            + self.gravity_torque(q, gravity)
        )
        return torque
