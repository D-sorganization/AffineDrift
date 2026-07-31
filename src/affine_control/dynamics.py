"""Reference implementation of the dynamics identities used across the textbooks.

Every function here corresponds to a formula that appears in *The Geometry of
Motion*, and the accompanying tests assert the properties the text claims. The
point is that worked-example numbers should be generated from checked code
rather than typed by hand.

The 2026-07-31 content review found each of the following in the published text,
which is why each has a test rather than only an implementation:

* the spatial equation of motion with its bias term **subtracted**, so every
  gyroscopic and centrifugal wrench came out backwards;
* the spatial-inertia parallel-axis term **subtracted**, producing a worked
  example with a negative moment of inertia that the text defended as valid;
* the ``Mdot - 2C`` skew-symmetry property asserted without its Christoffel
  hypothesis, and a double pendulum whose own matrices violated it;
* constrained dynamics written with the constraint force lumped into the drift,
  which makes the drift depend on the input and invalidates the Zero-Torque
  Counterfactual on any system with closed loops or ground contact.

Conventions follow Featherstone and Lynch & Park: spatial **motion** vectors are
angular-first, ``V = (omega, v)``; spatial **force** vectors are moment-first,
``F = (n, f)``. Mixing that with the opposite ordering silently transposes every
6-vector and every adjoint, so it is asserted in the tests.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

__all__ = [
    "christoffel_coriolis",
    "constrained_affine_fields",
    "double_pendulum_coriolis",
    "double_pendulum_mass_matrix",
    "force_cross",
    "motion_cross",
    "skew",
    "spatial_inertia",
    "spatial_newton_euler",
]

# Declared with the `type` keyword rather than a bare assignment. The pre-push
# mypy hook runs with --ignore-missing-imports and without numpy stubs, so
# NDArray resolves to Any there; given a plain assignment mypy reads `Array` as an
# ordinary variable and rejects every use of it as "not valid as a type".
type Array = NDArray[np.float64]


def skew(vector: Array) -> Array:
    """Return the 3x3 skew-symmetric matrix ``[v]`` with ``[v] w == cross(v, w)``."""
    v = np.asarray(vector, dtype=float).reshape(3)
    return np.array(
        [[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]],
        dtype=float,
    )


def spatial_inertia(mass: float, com: Array, inertia_com: Array) -> Array:
    """Build the 6x6 spatial inertia about the frame origin, angular-first.

    The parallel-axis term **adds** to the rotational inertia::

        I_O = [[ I_c + m [c][c]^T , m [c]   ],
               [ m [c]^T          , m 1     ]]

    ``[c][c]^T = |c|^2 I - c c^T`` is positive semi-definite, so the top-left
    block grows with the offset. Writing it with a minus sign yields a matrix
    that is not positive definite -- physically impossible for an inertia, and
    the error the review found in the published worked example.

    Args:
        mass: Body mass, strictly positive.
        com: Centre of mass expressed in the frame whose origin the inertia is
            taken about.
        inertia_com: 3x3 rotational inertia about the centre of mass.

    Returns:
        The 6x6 spatial inertia, symmetric positive definite.
    """
    if mass <= 0.0:
        raise ValueError(f"mass must be positive, got {mass}")
    c = skew(com)
    inertia_com = np.asarray(inertia_com, dtype=float).reshape(3, 3)
    upper_left = inertia_com + mass * (c @ c.T)
    return np.block(
        [
            [upper_left, mass * c],
            [mass * c.T, mass * np.eye(3)],
        ]
    )


def motion_cross(velocity: Array) -> Array:
    """Return ``[V x]``, the 6x6 operator acting on spatial motion vectors."""
    v = np.asarray(velocity, dtype=float).reshape(6)
    omega, linear = v[:3], v[3:]
    return np.block(
        [
            [skew(omega), np.zeros((3, 3))],
            [skew(linear), skew(omega)],
        ]
    )


def force_cross(velocity: Array) -> Array:
    """Return ``[V x]*``, the operator acting on spatial force vectors.

    Defined as the negative transpose of the motion cross product, which is what
    makes the pairing ``F . V`` a power.
    """
    return -motion_cross(velocity).T


def spatial_newton_euler(inertia: Array, velocity: Array, acceleration: Array) -> Array:
    """Spatial equation of motion: ``F = I Vdot + [V x]* (I V)``.

    The bias term is **added**. Checked in the tests against classical
    Newton-Euler, which is not in dispute.

    A subtlety worth stating, because getting it wrong makes both signs look
    incorrect: a spatial acceleration is not a classical acceleration. The
    classical acceleration of the body-fixed point currently at the origin is
    ``a_O + omega x v_O``.
    """
    inertia = np.asarray(inertia, dtype=float).reshape(6, 6)
    v = np.asarray(velocity, dtype=float).reshape(6)
    a = np.asarray(acceleration, dtype=float).reshape(6)
    wrench: Array = inertia @ a + force_cross(v) @ (inertia @ v)
    return wrench


def double_pendulum_mass_matrix(q: Array, m1: float, m2: float, l1: float, l2: float) -> Array:
    """Mass matrix of the ch11 planar double pendulum (point-mass rods).

    Derived from the kinetic energy

        T = 1/2 [ (m1/4 + m2) l1^2 q1d^2 + (m2 l2^2 / 4) q2d^2
                  + m2 l1 l2 cos(q1 - q2) q1d q2d ].

    Note the off-diagonal entry is **half** the coefficient of the cross term,
    because that term appears twice in ``qd^T M qd``. Forgetting the factor of a
    half is the error the review found in the published matrix.
    """
    q1, q2 = float(q[0]), float(q[1])
    off = 0.5 * m2 * l1 * l2 * np.cos(q1 - q2)
    return np.array(
        [
            [(m1 / 4.0 + m2) * l1**2, off],
            [off, m2 * l2**2 / 4.0],
        ]
    )


def christoffel_coriolis(
    mass_matrix: Callable[[Array], Array],
    q: Array,
    qd: Array,
    step: float = 1e-6,
) -> Array:
    """Coriolis matrix from the Christoffel symbols of an arbitrary ``M(q)``.

    ``C_kj = sum_i 1/2 (dM_kj/dq_i + dM_ki/dq_j - dM_ij/dq_k) qd_i``, with the
    partial derivatives taken by central differences so that only ``M`` itself
    has to be supplied.

    This exists to check a *published* Coriolis matrix against the mass matrix
    printed beside it, without re-deriving either by hand. A sign slip in one
    off-diagonal entry leaves the matrix looking plausible while destroying the
    skew-symmetry of ``Mdot - 2C``, and therefore energy conservation -- which is
    exactly the defect the 2026-07-31 review found in Volume I chapter 7.
    """
    q = np.asarray(q, dtype=float)
    qd = np.asarray(qd, dtype=float)
    n = q.size
    grad = np.zeros((n, n, n))
    for k in range(n):
        forward, backward = q.copy(), q.copy()
        forward[k] += step
        backward[k] -= step
        grad[k] = (mass_matrix(forward) - mass_matrix(backward)) / (2.0 * step)

    coriolis = np.zeros((n, n))
    for k in range(n):
        for j in range(n):
            coriolis[k, j] = 0.5 * sum(
                (grad[i, k, j] + grad[j, k, i] - grad[k, i, j]) * qd[i] for i in range(n)
            )
    return coriolis


def double_pendulum_coriolis(q: Array, qd: Array, m2: float, l1: float, l2: float) -> Array:
    """Christoffel Coriolis matrix for :func:`double_pendulum_mass_matrix`.

    The Christoffel construction is what makes ``Mdot - 2C`` skew-symmetric. Any
    other factorisation with the same ``C qd`` gives identical equations of
    motion but generally loses that property, so control designs that rely on
    skew-symmetry require this specific form.
    """
    q1, q2 = float(q[0]), float(q[1])
    d1, d2 = float(qd[0]), float(qd[1])
    k = 0.5 * m2 * l1 * l2 * np.sin(q1 - q2)
    return np.array([[0.0, k * d2], [-k * d1, 0.0]])


def constrained_affine_fields(
    mass_matrix: Array,
    bias: Array,
    input_matrix: Array,
    constraint_jacobian: Array,
    constraint_bias: Array,
) -> tuple[Array, Array]:
    """Drift and input fields of a constrained system, in control-affine form.

    Solving ``M qdd = B u + Jc^T lam - h`` together with the acceleration
    constraint ``Jc qdd + Jcdot qd = 0`` gives a multiplier that is *affine in
    the input*::

        lam = -Lam [ Jc M^-1 (B u - h) + Jcdot qd ],   Lam = (Jc M^-1 Jc^T)^-1

    so the constraint force cannot simply be lumped into the drift: doing so
    makes the drift depend on ``u`` and destroys ``df/du = 0``, the property the
    Zero-Torque Counterfactual is built on. Eliminating ``lam`` instead yields::

        f   = -P M^-1 h - M^-1 Jc^T Lam Jcdot qd
        g   =  P M^-1 B,     P = I - M^-1 Jc^T Lam Jc

    where ``P`` is the dynamically consistent projector onto constraint-admissible
    directions. Because ``Jc P M^-1 = 0``, accelerations built from these fields
    satisfy the constraint by construction.

    Args:
        mass_matrix: Symmetric positive definite ``M(q)``.
        bias: ``h = C(q, qd) qd + grad V(q)``.
        input_matrix: ``B(q)``, mapping inputs to generalised forces.
        constraint_jacobian: ``Jc(q)``, assumed full row rank.
        constraint_bias: ``Jcdot(q, qd) qd``.

    Returns:
        ``(f, g)`` with ``qdd = f + g @ u``.
    """
    mass_matrix = np.asarray(mass_matrix, dtype=float)
    n = mass_matrix.shape[0]
    minv = np.linalg.inv(mass_matrix)
    jac = np.atleast_2d(np.asarray(constraint_jacobian, dtype=float))

    schur = jac @ minv @ jac.T
    if np.linalg.matrix_rank(schur) < schur.shape[0]:
        raise np.linalg.LinAlgError(
            "constraint Jacobian is rank deficient; Jc M^-1 Jc^T is singular"
        )
    lam_gain = np.linalg.inv(schur)
    projector = np.eye(n) - minv @ jac.T @ lam_gain @ jac

    drift = -projector @ minv @ np.asarray(
        bias, dtype=float
    ) - minv @ jac.T @ lam_gain @ np.asarray(constraint_bias, dtype=float)
    input_field = projector @ minv @ np.asarray(input_matrix, dtype=float)
    return drift, input_field
