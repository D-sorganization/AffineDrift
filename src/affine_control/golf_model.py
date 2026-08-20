"""Three-link planar golf model with a flexible shaft, built from kinetic energy.

Volume I chapter 8 printed a mass matrix that did not follow from the formulas
three equations above it, whose assembled blocks were not positive definite, and
explained the resulting indefinite Schur complement as a "kinematic
singularity". That explanation is wrong physics: for a system of positive masses
the mass matrix is positive definite everywhere, singular configuration or not.
A singular *Jacobian* makes a task-space inertia blow up; it never makes a
joint-space inertia indefinite.

So the model is built here from Jacobians rather than from transcribed closed
forms, which removes the transcription step entirely and makes positive
definiteness a property the tests can assert over the whole workspace.

Coordinates: ``q = (q1, q2, q3)`` are relative joint angles (shoulder, elbow,
wrist); ``eta`` are the amplitudes of the first two shaft bending modes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

__all__ = ["GolfModel", "SEGMENTS"]

type Array = NDArray[np.float64]

# Standard gravity, named with its units so the magnitude cannot be mistaken for
# a dimensionless factor.
GRAVITY_M_S2 = 9.81

# Clamped-free Euler-Bernoulli eigenvalues, beta_k * L.
_BETA_L = (1.8751040687, 4.6940911330)


@dataclass(frozen=True)
class GolfModel:
    """Segment and shaft parameters for the chapter 8 worked example."""

    # Segment 3 is the club. An earlier revision of chapter 8 gave its length as
    # 0.40 m, labelled "club length" -- forearm scale. A driver is about 1.15 m,
    # and the difference is not cosmetic: at the chapter's own joint rates the
    # short club yields a clubhead speed of 12.2 m/s (27 mph), and reaching a
    # real 45 m/s with that geometry would require a wrist rate near 92 rad/s,
    # roughly 880 rpm. The mass follows: a driver is about 0.31 kg and a hand
    # about 0.5 kg, so 0.81 kg for the lumped club-plus-hand segment rather than
    # the 2 kg previously stated.
    masses: tuple[float, float, float] = (10.0, 5.0, 0.81)
    lengths: tuple[float, float, float] = (0.30, 0.35, 1.15)
    # Segments 1 and 2 lump torso and forearm contributions, so their inertias
    # exceed the bare uniform-rod value. Segment 3 uses the rod value for its
    # stated mass and length.
    inertias: tuple[float, float, float] = (0.25, 0.08, 0.089)
    shaft_mass: float = 0.3
    modal_frequencies: tuple[float, float] = (40.0, 120.0)
    com_fractions: tuple[float, float, float] = field(default=(0.5, 0.5, 0.5))

    def com_offsets(self) -> tuple[float, float, float]:
        """Distance from each proximal joint to that link's centre of mass."""
        a, b, c = self.com_fractions
        return (self.lengths[0] * a, self.lengths[1] * b, self.lengths[2] * c)

    # -- kinematics --------------------------------------------------------

    def link_angles(self, q: Array) -> Array:
        """Absolute link angles; a serial chain accumulates its joint angles."""
        return np.cumsum(np.asarray(q, dtype=float))

    def com_jacobian(self, q: Array, index: int) -> Array:
        """``d(p_com_i)/dq``, shape ``(2, 3)``."""
        angles = self.link_angles(q)
        offsets = self.com_offsets()
        jac = np.zeros((2, 3))
        for joint in range(index + 1):
            dx = dy = 0.0
            for link in range(joint, index + 1):
                reach = offsets[link] if link == index else self.lengths[link]
                dx -= reach * np.sin(angles[link])
                dy += reach * np.cos(angles[link])
            jac[0, joint] = dx
            jac[1, joint] = dy
        return jac

    @staticmethod
    def angular_jacobian(index: int) -> Array:
        """``d(theta_i)/dq`` -- ones up to and including joint ``index``."""
        row = np.zeros(3)
        row[: index + 1] = 1.0
        return row

    # -- inertia -----------------------------------------------------------

    def rigid_mass_matrix(self, q: Array) -> Array:
        """``M_qq = sum_i (m_i Jv_i' Jv_i + I_i Jw_i Jw_i')``.

        A sum of positive-semidefinite terms whose angular parts already span
        the joint space, so the result is positive definite for any
        configuration. That is the property chapter 8's printed matrix violated.
        """
        total = np.zeros((3, 3))
        for index, (mass, inertia) in enumerate(zip(self.masses, self.inertias, strict=True)):
            jv = self.com_jacobian(q, index)
            jw = self.angular_jacobian(index)
            total += mass * (jv.T @ jv) + inertia * np.outer(jw, jw)
        return 0.5 * (total + total.T)

    def mode_shape(self, mode: int, s: Array) -> Array:
        """Clamped-free bending mode, scaled so the tip deflection is one."""
        length = self.lengths[2]
        beta_l = _BETA_L[mode]
        beta = beta_l / length
        sigma = (np.cosh(beta_l) + np.cos(beta_l)) / (np.sinh(beta_l) + np.sin(beta_l))
        shape = np.cosh(beta * s) - np.cos(beta * s)
        shape -= sigma * (np.sinh(beta * s) - np.sin(beta * s))
        return shape / 2.0

    def shaft_blocks(self, q: Array, samples: int = 4001) -> tuple[Array, Array]:
        """Return ``(M_qeta, M_etaeta)`` by integrating along the shaft.

        A material point at arclength ``s`` gains transverse velocity both from
        joint rotation -- with moment arm ``r_i(s)`` -- and from bending. The
        cross block integrates ``rho phi_k r_i``; the modal block integrates
        ``rho phi_j phi_k``, and is diagonal because the modes are orthogonal.
        """
        length = self.lengths[2]
        s = np.linspace(0.0, length, samples)
        density = self.shaft_mass / length
        shapes = np.stack([self.mode_shape(k, s) for k in range(2)])

        _, q2, q3 = np.asarray(q, dtype=float)
        arms = np.stack(
            [
                s + self.lengths[1] * np.cos(q3) + self.lengths[0] * np.cos(q2 + q3),
                s + self.lengths[1] * np.cos(q3),
                s,
            ]
        )

        coupling = np.array(
            [[density * np.trapezoid(shapes[k] * arms[i], s) for k in range(2)] for i in range(3)]
        )
        modal = np.array(
            [[density * np.trapezoid(shapes[j] * shapes[k], s) for k in range(2)] for j in range(2)]
        )
        return coupling, 0.5 * (modal + modal.T)

    def full_mass_matrix(self, q: Array, samples: int = 4001) -> Array:
        """The assembled 5x5 mass matrix over ``(q, eta)``."""
        m_qq = self.rigid_mass_matrix(q)
        m_qeta, m_etaeta = self.shaft_blocks(q, samples)
        return np.block([[m_qq, m_qeta], [m_qeta.T, m_etaeta]])

    def schur_complement(self, q: Array, samples: int = 4001) -> Array:
        """``M_qq - M_qeta M_etaeta^-1 M_etaq``, the articulated-body inertia.

        Positive definite whenever the full matrix is, since ``M_etaeta`` is.
        An indefinite result means the blocks are not a valid mass matrix -- it
        is never a statement about the configuration.
        """
        m_qq = self.rigid_mass_matrix(q)
        m_qeta, m_etaeta = self.shaft_blocks(q, samples)
        reduced = m_qq - m_qeta @ np.linalg.solve(m_etaeta, m_qeta.T)
        return 0.5 * (reduced + reduced.T)

    def effective_mobility(self, q: Array, samples: int = 4001) -> Array:
        """``H_qq``, the inverse of the articulated-body inertia."""
        return np.linalg.inv(self.schur_complement(q, samples))

    def potential_energy(self, q: Array, gravity: float = GRAVITY_M_S2) -> float:
        """Gravitational potential of the three rigid segments."""
        angles = self.link_angles(q)
        offsets = self.com_offsets()
        height = 0.0
        total = 0.0
        for index, mass in enumerate(self.masses):
            reach = offsets[index]
            com_height = height + reach * np.sin(angles[index])
            total += mass * gravity * com_height
            height += self.lengths[index] * np.sin(angles[index])
        return float(total)

    def gravity_torque(self, q: Array, gravity: float = GRAVITY_M_S2, step: float = 1e-6) -> Array:
        """``dV/dq``, the gravitational term as it enters ``M qddot + C qdot + g = tau``."""
        q = np.asarray(q, dtype=float)
        out = np.zeros(3)
        for index in range(3):
            forward, backward = q.copy(), q.copy()
            forward[index] += step
            backward[index] -= step
            high = self.potential_energy(forward, gravity)
            low = self.potential_energy(backward, gravity)
            out[index] = (high - low) / (2.0 * step)
        return out

    def coriolis(self, q: Array, qd: Array) -> Array:
        """Christoffel Coriolis matrix of the rigid block."""
        from src.affine_control.dynamics import christoffel_coriolis

        return christoffel_coriolis(self.rigid_mass_matrix, q, qd)

    def drift_acceleration(self, q: Array, qd: Array, gravity: float = GRAVITY_M_S2) -> Array:
        """``qddot`` with zero applied torque -- the pointwise ZTCF acceleration.

        Uses the articulated-body inertia, so shaft inertia is accounted for
        rather than ignored.
        """
        bias = self.coriolis(q, qd) @ np.asarray(qd, dtype=float) + self.gravity_torque(q, gravity)
        return -np.linalg.solve(self.schur_complement(q), bias)

    def clubhead_speed(self, q: Array, qd: Array) -> float:
        """Speed of the club tip, i.e. the distal end of link three."""
        angles = self.link_angles(q)
        qd = np.asarray(qd, dtype=float)
        velocity = np.zeros(2)
        for link in range(3):
            rate = float(np.sum(qd[: link + 1]))
            reach = self.lengths[link]
            velocity += rate * reach * np.array([-np.sin(angles[link]), np.cos(angles[link])])
        return float(np.linalg.norm(velocity))

    def ztcf_trajectory(
        self, q0: Array, qd0: Array, duration: float, steps: int
    ) -> list[tuple[float, Array, Array, float]]:
        """Integrate the zero-torque counterfactual: ``u = 0`` from a given state.

        Returns ``(t, q, qdot, clubhead_speed)`` sampled at each step. Fixed-step
        RK4; the drift field is smooth here so adaptive stepping buys nothing.
        """
        q = np.asarray(q0, dtype=float).copy()
        qd = np.asarray(qd0, dtype=float).copy()
        dt = duration / steps

        def derivative(state: Array) -> Array:
            """State derivative of the unforced system, ``[qdot, qddot]``."""
            pos, vel = state[:3], state[3:]
            return np.concatenate([vel, self.drift_acceleration(pos, vel)])

        state = np.concatenate([q, qd])
        out: list[tuple[float, Array, Array, float]] = [
            (0.0, state[:3].copy(), state[3:].copy(), self.clubhead_speed(state[:3], state[3:]))
        ]
        for index in range(steps):
            k1 = derivative(state)
            k2 = derivative(state + 0.5 * dt * k1)
            k3 = derivative(state + 0.5 * dt * k2)
            k4 = derivative(state + dt * k3)
            state = state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            out.append(
                (
                    (index + 1) * dt,
                    state[:3].copy(),
                    state[3:].copy(),
                    self.clubhead_speed(state[:3], state[3:]),
                )
            )
        return out

    def modal_stiffness(self, samples: int = 4001) -> Array:
        """``K_etaeta = M_etaeta diag(omega^2)``, consistent with the modal masses."""
        _, modal = self.shaft_blocks(np.zeros(3), samples)
        stiffness: Array = modal @ np.diag(np.square(self.modal_frequencies))
        return stiffness


SEGMENTS = GolfModel()
