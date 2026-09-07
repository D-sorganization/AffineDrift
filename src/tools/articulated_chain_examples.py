"""Physically specified cylindrical links for the articulated-body worked example."""

import numpy as np
from numpy.typing import NDArray

from src.affine_control.dynamics import skew, spatial_inertia
from src.tools.articulated_body_examples import PreparedTree

type Array = NDArray[np.float64]


def _chain_parameters(lengths: Array, masses: Array, angles: Array, radius: float) -> None:
    """Require a nonempty chain with positive SI dimensions and finite angles."""
    if lengths.ndim != 1 or lengths.size == 0 or masses.shape != lengths.shape:
        raise ValueError("lengths and masses must be nonempty matching vectors")
    if angles.shape != lengths.shape or not np.isfinite(angles).all():
        raise ValueError("angles must match the chain and be finite")
    if any(not np.isfinite(value).all() or np.any(value <= 0) for value in (lengths, masses)):
        raise ValueError("lengths and masses must be positive and finite")
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError("radius must be positive and finite")


def cylinder_chain(lengths: Array, masses: Array, angles: Array, radius: float) -> PreparedTree:
    """Build a planar chain of uniform solid cylinders rotating about parallel z axes.

    Args:
        lengths: Link lengths in metres, measured along each local x axis.
        masses: Link masses in kilograms.
        angles: Relative right-handed joint angles in radians.
        radius: Common cylinder radius in metres.

    Returns:
        A fixed-base tree whose body frames originate at the proximal joints.
        COM offsets are half the link lengths. This is a teaching mechanism,
        not a fitted anatomical or flexible golf-club model.
    """
    lengths, masses, angles = (
        np.asarray(value, dtype=float) for value in (lengths, masses, angles)
    )
    _chain_parameters(lengths, masses, angles, radius)
    count = len(lengths)
    transforms, inertias = np.zeros((count, 6, 6)), np.zeros((count, 6, 6))
    subspaces = np.zeros((count, 6))
    subspaces[:, 2] = 1
    for body in range(count):
        cosine, sine = np.cos(angles[body]), np.sin(angles[body])
        rotation = np.array([[cosine, sine, 0], [-sine, cosine, 0], [0, 0, 1]])
        offset = np.array([0 if body == 0 else lengths[body - 1], 0, 0])
        transforms[body] = np.block(
            [[rotation, np.zeros((3, 3))], [-rotation @ skew(offset), rotation]]
        )
        axial = masses[body] * radius**2 / 2
        transverse = masses[body] * (lengths[body] ** 2 + 3 * radius**2) / 12
        inertias[body] = spatial_inertia(
            masses[body],
            np.array([lengths[body] / 2, 0, 0]),
            np.diag([axial, transverse, transverse]),
        )
    return PreparedTree(tuple(range(-1, count - 1)), transforms, subspaces, inertias)
