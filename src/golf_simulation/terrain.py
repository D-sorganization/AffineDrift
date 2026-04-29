"""Terrain types and physical properties for golf course simulation.

Defines the terrain classification enum, physical properties for each terrain
type (friction, restitution, spin retention), and bounce computation for
ball-surface interactions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

from src.core.contracts import check_finite_array, check_non_negative, require

logger = logging.getLogger(__name__)


class TerrainType(Enum):
    """Classification of terrain on a golf course."""

    TEE_BOX = "tee_box"
    FAIRWAY = "fairway"
    ROUGH = "rough"
    DEEP_ROUGH = "deep_rough"
    BUNKER = "bunker"
    GREEN = "green"
    WATER = "water"
    OUT_OF_BOUNDS = "out_of_bounds"


@dataclass(frozen=True)
class TerrainProperties:
    """Physical properties of a terrain type.

    Attributes:
        friction_coefficient: Rolling/sliding friction coefficient.
        coefficient_of_restitution: Bounciness (0 = dead, 1 = perfect bounce).
        spin_retention: Fraction of spin retained after landing (0-1).
        lie_quality: Quality of lie for striking the ball (0.0 = unplayable, 1.0 = perfect).
    """

    friction_coefficient: float
    coefficient_of_restitution: float
    spin_retention: float
    lie_quality: float

    def __post_init__(self) -> None:
        """Validate terrain property ranges."""
        check_non_negative(self.friction_coefficient, "friction_coefficient")
        check_non_negative(self.coefficient_of_restitution, "coefficient_of_restitution")
        require(
            0.0 <= self.spin_retention <= 1.0,
            f"spin_retention must be in [0, 1], got {self.spin_retention}",
        )
        require(
            0.0 <= self.lie_quality <= 1.0,
            f"lie_quality must be in [0, 1], got {self.lie_quality}",
        )


TERRAIN_PROPERTIES: dict[TerrainType, TerrainProperties] = {
    TerrainType.TEE_BOX: TerrainProperties(0.08, 0.65, 0.75, 1.0),
    TerrainType.FAIRWAY: TerrainProperties(0.10, 0.60, 0.70, 1.0),
    TerrainType.ROUGH: TerrainProperties(0.20, 0.40, 0.40, 0.7),
    TerrainType.DEEP_ROUGH: TerrainProperties(0.30, 0.30, 0.30, 0.4),
    TerrainType.BUNKER: TerrainProperties(0.40, 0.20, 0.20, 0.5),
    TerrainType.GREEN: TerrainProperties(0.065, 0.50, 0.80, 1.0),
    TerrainType.WATER: TerrainProperties(1.0, 0.0, 0.0, 0.0),
    TerrainType.OUT_OF_BOUNDS: TerrainProperties(1.0, 0.0, 0.0, 0.0),
}


def _normalized_surface_normal(surface_normal: np.ndarray[Any, Any] | None) -> np.ndarray[Any, Any]:
    """Return a finite unit surface normal, defaulting to flat ground."""
    if surface_normal is None:
        return np.array([0.0, 0.0, 1.0])

    check_finite_array(surface_normal, "surface_normal")
    norm = float(np.linalg.norm(surface_normal))
    require(norm > 1e-10, "surface_normal must be non-zero")
    return surface_normal / norm


def _validate_bounce_vectors(velocity: np.ndarray[Any, Any], spin: np.ndarray[Any, Any]) -> None:
    """Validate pre-impact velocity and spin vectors."""
    check_finite_array(velocity, "velocity")
    check_finite_array(spin, "spin")
    require(len(velocity) == 3, "velocity must be a 3D vector")
    require(len(spin) == 3, "spin must be a 3D vector")


def _split_velocity(
    velocity: np.ndarray[Any, Any], surface_normal: np.ndarray[Any, Any]
) -> tuple[float, np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Split velocity into signed normal magnitude, normal vector, and tangent vector."""
    normal_magnitude = float(np.dot(velocity, surface_normal))
    normal_velocity = normal_magnitude * surface_normal
    tangential_velocity = velocity - normal_velocity
    return normal_magnitude, normal_velocity, tangential_velocity


def _apply_surface_friction(
    tangential_velocity: np.ndarray[Any, Any],
    normal_magnitude: float,
    friction_coefficient: float,
) -> np.ndarray[Any, Any]:
    """Reduce tangential velocity by impact-scaled surface friction."""
    tangential_speed = float(np.linalg.norm(tangential_velocity))
    if tangential_speed <= 1e-10:
        return tangential_velocity

    friction_decel = friction_coefficient * abs(normal_magnitude)
    reduced_speed = max(0.0, tangential_speed - friction_decel)
    return tangential_velocity * (reduced_speed / tangential_speed)


def compute_bounce(
    velocity: np.ndarray[Any, Any],
    spin: np.ndarray[Any, Any],
    terrain_props: TerrainProperties,
    surface_normal: np.ndarray[Any, Any] | None = None,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Compute post-impact velocity and spin after a ball strikes a surface."""
    _validate_bounce_vectors(velocity, spin)
    surface_normal = _normalized_surface_normal(surface_normal)
    normal_magnitude, normal_velocity, tangential_velocity = _split_velocity(
        velocity, surface_normal
    )
    post_v_normal = -terrain_props.coefficient_of_restitution * normal_velocity
    post_v_tangential = _apply_surface_friction(
        tangential_velocity,
        normal_magnitude,
        terrain_props.friction_coefficient,
    )
    post_velocity = post_v_normal + post_v_tangential
    post_spin = spin * terrain_props.spin_retention

    logger.debug(
        "Bounce: v_in=%.2f m/s, v_out=%.2f m/s, spin_retention=%.2f",
        np.linalg.norm(velocity),
        np.linalg.norm(post_velocity),
        terrain_props.spin_retention,
    )

    return post_velocity, post_spin
