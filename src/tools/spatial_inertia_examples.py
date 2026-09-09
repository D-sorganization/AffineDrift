"""Frame-consistent inertia examples for Geometry Volume 0 Chapter 8.

Reuse the shared angular-first motion convention and prepared tree contract.
These routines model rigid bodies and fixed-base, one-DOF tree joints; contacts,
closed loops, armature and flexible bodies require additional equations.
"""

import numpy as np
from numpy.typing import NDArray

from src.tools.articulated_body_examples import PreparedTree
from src.tools.screw_examples import adjoint

type Array = NDArray[np.float64]


def reexpress_inertia(transform_ab: Array, inertia_b: Array) -> Array:
    """Re-express I_B in A using T_AB, which maps point coordinates B to A.

    Args:
        transform_ab: Proper rigid homogeneous transform, shape (4, 4).
        inertia_b: Spatial inertia about and expressed in B, shape (6, 6).

    Returns:
        I_A = Ad(T_AB)^(-T) I_B Ad(T_AB)^(-1).

    Physical inertia is a precondition; this checks finite shape and the rigid
    transform but deliberately permits ideal point/line-mass singular inertias.
    """
    inertia = np.asarray(inertia_b, dtype=float)
    if inertia.shape != (6, 6) or not np.isfinite(inertia).all():
        raise ValueError("inertia must be a finite 6 by 6 matrix")
    change = adjoint(transform_ab)
    left = np.linalg.solve(change.T, inertia)
    return np.asarray(np.linalg.solve(change.T, left.T).T, dtype=float)


def composite_inertias(tree: PreparedTree) -> Array:
    """Assemble each subtree's locked inertia in its root body's frame.

    ``tree.transform[i]`` maps parent motion to child motion. The pullback is
    therefore X.T @ I_child @ X. Input inertias are preserved. The recursion
    requires the parent's index to precede the child's, as PreparedTree checks.
    """
    composite = tree.inertia.copy()
    for body in reversed(range(len(tree.parents))):
        parent = tree.parents[body]
        if parent >= 0:
            change = tree.transform[body]
            composite[parent] += change.T @ composite[body] @ change
    return composite


def joint_mass_matrix(tree: PreparedTree) -> Array:
    """Compute the joint inertia by composite assembly and ancestor projection.

    Return a symmetric N by N matrix for the prepared fixed-base tree, using
    constant local one-DOF joint subspaces and no reflected rotor inertia.
    Ancestor propagation is O(N^2) in a serial chain; dense output storage is
    O(N^2) even when a branched tree has many structurally zero entries.
    """
    composite = composite_inertias(tree)
    count = len(tree.parents)
    mass = np.zeros((count, count))
    for body in range(count):
        momentum = composite[body] @ tree.subspace[body]
        mass[body, body] = tree.subspace[body] @ momentum
        ancestor = body
        while tree.parents[ancestor] >= 0:
            momentum = tree.transform[ancestor].T @ momentum
            ancestor = tree.parents[ancestor]
            mass[body, ancestor] = tree.subspace[ancestor] @ momentum
            mass[ancestor, body] = mass[body, ancestor]
    return mass
