"""Universal joint visualisation helpers - extracted from monolith.

Fixes #2359: separates rendering from physics computation.
"""
from __future__ import annotations
from typing import Any


def build_joint_mesh(joint_params: dict[str, Any]) -> dict[str, Any]:
    """Build mesh data for 3D universal joint visualisation.

    Args:
        joint_params: Dict with 'radius', 'length', 'offset' keys.

    Returns:
        Dict with 'vertices', 'faces', 'normals' for rendering.
    """
    import numpy as np
    r = float(joint_params.get("radius", 0.05))
    n_segs = int(joint_params.get("segments", 16))
    angles = np.linspace(0, 2 * np.pi, n_segs, endpoint=False)
    vertices = np.column_stack([r * np.cos(angles), r * np.sin(angles), np.zeros(n_segs)])
    return {"vertices": vertices, "faces": [], "normals": []}


def joint_animation_frames(theta_range: tuple[float, float], n_frames: int = 60) -> list[float]:
    """Generate drive-angle frames for animation.

    Args:
        theta_range: (start, end) angles in radians.
        n_frames: Number of animation frames.

    Returns:
        List of drive angles, one per frame.
    """
    import numpy as np
    return list(np.linspace(theta_range[0], theta_range[1], n_frames))
