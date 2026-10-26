"""Rank counting for "Slack Take-Up as a Witness" (#5136).

Toy C counts which grasp-kernel directions a slack channel could see at best, using the grasp map
``G`` and kernel basis ``K`` of the record.
"""

from __future__ import annotations

import numpy as np

from src.tools.slack_takeup_witness import Array

RANK_TOLERANCE = 1e-9  # relative to the largest singular value
GRIP_HALF_SEPARATION = 0.06  # m, manufactured; matches the independent check in PR #5140
SPLIT_NAMES = ("axial squeeze", "shear y", "shear z", "twist couple", "bending y", "bending z")


def _rank(matrix: Array) -> int:
    """Numerical rank with the module's relative tolerance."""
    values = np.linalg.svd(matrix, compute_uv=False)
    return int(np.sum(values > RANK_TOLERANCE * max(values.max(initial=0.0), 1e-300)))


def grasp_matrices(half_separation: float = GRIP_HALF_SEPARATION) -> tuple[Array, Array]:
    """Grasp map ``G`` (6x12) and kernel basis ``K`` (12x6) for hands at ``-d`` and ``+d``."""
    d = np.array([half_separation, 0.0, 0.0])
    skew = np.array([[0.0, -d[2], d[1]], [d[2], 0.0, -d[0]], [-d[1], d[0], 0.0]])
    eye, zero = np.eye(3), np.zeros((3, 3))
    grasp = np.block([[eye, zero, eye, zero], [-skew, eye, skew, eye]])
    kernel = np.block([[-eye, zero], [-skew, -eye], [eye, zero], [-skew, eye]])
    return grasp, kernel


GRASP_CHANNELS = {
    "no slack observed": (),
    "force-axis slack, both hands": (0, 1, 2, 6, 7, 8),
    "couple-axis slack, both hands": (3, 4, 5, 9, 10, 11),
    "twist-axis slack only": (3, 9),
    "every axis except axial force": (1, 2, 3, 4, 5, 7, 8, 9, 10, 11),
    "every axis, both hands": tuple(range(12)),
}


def grasp_visibility() -> list[dict[str, object]]:
    """Exact rank of each slack channel restricted to the six-dimensional grasp kernel."""
    grasp, kernel = grasp_matrices()
    if _rank(grasp @ kernel) != 0 or _rank(kernel) != 6:
        raise ValueError("K must be a basis of the grasp-map kernel")
    table = []
    for name, rows in GRASP_CHANNELS.items():
        seen = kernel[list(rows)] if rows else np.zeros((0, 6))
        rank = _rank(seen) if rows else 0
        norms = np.linalg.norm(seen, axis=0) if rows else np.zeros(6)
        hidden = [SPLIT_NAMES[i] for i in range(6) if norms[i] == 0.0]
        seen_norms = norms[norms > 0]
        spread = float(seen_norms.max() / seen_norms.min()) if seen_norms.size else 0.0
        table.append(
            {
                "channel": name,
                "rank": rank,
                "nullity": 6 - rank,
                "hidden": hidden,
                "column_norms": [float(value) for value in norms],
                "norm_spread": spread,
            }
        )
    return table
