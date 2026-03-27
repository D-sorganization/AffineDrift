"""Golf course definition and terrain management.

Provides data structures for individual holes and full courses, with
terrain classification based on distance from key landmarks. Includes
factory functions for common course layouts.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Callable
from dataclasses import dataclass, field

from src.core.contracts import check_positive, check_range, require
from src.golf_simulation.terrain import TerrainType

logger = logging.getLogger(__name__)

# Conversion factor: 1 yard = 0.9144 meters
YARDS_TO_METERS = 0.9144
METERS_TO_YARDS = 1.0 / YARDS_TO_METERS


@dataclass(frozen=True)
class GolfHole:
    """Definition of a single golf hole.

    Attributes:
        number: Hole number (1-18).
        par: Par for the hole (3, 4, or 5).
        yardage: Total distance from tee to pin in yards.
        handicap: Stroke index / handicap rating (1-18).
        tee_position: 3D coordinates of the tee box (x, y, z) in meters.
        pin_position: 3D coordinates of the pin (x, y, z) in meters.
        green_center: 3D coordinates of the green center in meters.
        green_radius: Radius of the putting green in meters.
        terrain_fn: Optional callable mapping (x, y) -> TerrainType.
    """

    number: int
    par: int
    yardage: float
    handicap: int
    tee_position: tuple[float, float, float]
    pin_position: tuple[float, float, float]
    green_center: tuple[float, float, float]
    green_radius: float
    terrain_fn: Callable[[float, float], TerrainType] | None = field(
        default=None, compare=False, hash=False
    )

    def __post_init__(self) -> None:
        """Validate hole parameters."""
        check_range(self.number, 1, 18, "hole number")
        require(self.par in (3, 4, 5), f"par must be 3, 4, or 5, got {self.par}")
        check_positive(self.yardage, "yardage")
        check_range(self.handicap, 1, 18, "handicap")
        check_positive(self.green_radius, "green_radius")

    def distance_to_pin(self, x: float, y: float) -> float:
        """Compute horizontal distance from (x, y) to the pin in meters.

        Args:
            x: Current x position in meters.
            y: Current y position in meters.

        Returns:
            Euclidean distance to pin in meters (2D, ignoring elevation).
        """
        dx = self.pin_position[0] - x
        dy = self.pin_position[1] - y
        return math.sqrt(dx * dx + dy * dy)

    def get_terrain(self, x: float, y: float) -> TerrainType:
        """Determine the terrain type at a given position.

        Uses the terrain_fn if available; otherwise falls back to a
        distance-based heuristic relative to the tee, fairway corridor,
        and green.

        Args:
            x: X position in meters.
            y: Y position in meters.

        Returns:
            The terrain type at the given position.
        """
        if self.terrain_fn is not None:
            return self.terrain_fn(x, y)

        # Distance-based heuristic
        dist_to_tee = math.sqrt((x - self.tee_position[0]) ** 2 + (y - self.tee_position[1]) ** 2)

        # On the green
        dist_to_green_center = math.sqrt(
            (x - self.green_center[0]) ** 2 + (y - self.green_center[1]) ** 2
        )
        if dist_to_green_center <= self.green_radius:
            return TerrainType.GREEN

        # Near the tee
        if dist_to_tee < 5.0:
            return TerrainType.TEE_BOX

        # Fairway corridor: within a band along the tee-to-pin line
        tee_x, tee_y = self.tee_position[0], self.tee_position[1]
        pin_x, pin_y = self.pin_position[0], self.pin_position[1]
        hole_dx = pin_x - tee_x
        hole_dy = pin_y - tee_y
        hole_length = math.sqrt(hole_dx**2 + hole_dy**2)

        if hole_length > 1e-6:
            # Project point onto tee-to-pin line
            t = ((x - tee_x) * hole_dx + (y - tee_y) * hole_dy) / (hole_length**2)
            # Perpendicular distance from the fairway center line
            proj_x = tee_x + t * hole_dx
            proj_y = tee_y + t * hole_dy
            perp_dist = math.sqrt((x - proj_x) ** 2 + (y - proj_y) ** 2)

            # Fairway width narrows near the green
            fairway_width = 25.0 if t < 0.8 else 15.0  # meters

            if 0.0 <= t <= 1.0 and perp_dist <= fairway_width:
                return TerrainType.FAIRWAY

            if 0.0 <= t <= 1.05 and perp_dist <= fairway_width + 15.0:
                return TerrainType.ROUGH

        return TerrainType.DEEP_ROUGH


class GolfCourse:
    """A complete golf course consisting of 9 or 18 holes.

    Attributes:
        name: Course name.
        holes: Ordered list of GolfHole definitions.
    """

    def __init__(self, name: str, holes: list[GolfHole]) -> None:
        """Initialize a golf course.

        Args:
            name: Name of the course.
            holes: List of hole definitions (must be 9 or 18 holes).
        """
        require(len(name) > 0, "course name must not be empty")
        require(
            len(holes) in (9, 18),
            f"course must have 9 or 18 holes, got {len(holes)}",
        )
        for hole in holes:
            require(
                hole.par in (3, 4, 5),
                f"hole {hole.number} has invalid par {hole.par}",
            )

        self.name = name
        self.holes = holes
        self._hole_map: dict[int, GolfHole] = {h.number: h for h in holes}

    @property
    def total_par(self) -> int:
        """Total par for the course."""
        return sum(h.par for h in self.holes)

    @property
    def total_yardage(self) -> float:
        """Total yardage for the course."""
        return sum(h.yardage for h in self.holes)

    @property
    def front_nine(self) -> list[GolfHole]:
        """First 9 holes of the course."""
        return [h for h in self.holes if h.number <= 9]

    @property
    def back_nine(self) -> list[GolfHole]:
        """Last 9 holes (holes 10-18). Empty for 9-hole courses."""
        return [h for h in self.holes if h.number > 9]

    def get_hole(self, number: int) -> GolfHole:
        """Get a hole by its number.

        Args:
            number: Hole number (1-18).

        Returns:
            The GolfHole with the given number.
        """
        require(number in self._hole_map, f"hole {number} not found on {self.name}")
        return self._hole_map[number]


# ── Factory Functions ─────────────────────────────────────────────────────────


def _make_hole(
    number: int,
    par: int,
    yardage: float,
    handicap: int,
    y_offset: float = 0.0,
) -> GolfHole:
    """Create a hole with positions computed from yardage.

    The hole is laid out along the x-axis with an optional y offset.
    """
    distance_m = yardage * YARDS_TO_METERS
    tee_pos = (0.0, y_offset, 0.0)
    pin_pos = (distance_m, y_offset, 0.0)
    green_center = (distance_m, y_offset, 0.0)
    green_radius = 15.0  # meters (~16 yards)

    return GolfHole(
        number=number,
        par=par,
        yardage=yardage,
        handicap=handicap,
        tee_position=tee_pos,
        pin_position=pin_pos,
        green_center=green_center,
        green_radius=green_radius,
    )


def create_par3_course(name: str = "Pine Valley Par 3") -> GolfCourse:
    """Create a 9-hole par-3 course.

    Args:
        name: Course name.

    Returns:
        A GolfCourse with 9 par-3 holes ranging from 100 to 220 yards.
    """
    yardages = [130.0, 155.0, 100.0, 185.0, 140.0, 200.0, 165.0, 220.0, 110.0]
    handicaps = [7, 3, 9, 1, 5, 2, 4, 6, 8]

    holes = [
        _make_hole(
            number=i + 1,
            par=3,
            yardage=yardages[i],
            handicap=handicaps[i],
            y_offset=i * 100.0,
        )
        for i in range(9)
    ]

    logger.info("Created par-3 course '%s' with 9 holes, par 27", name)
    return GolfCourse(name=name, holes=holes)


def create_championship_course(name: str = "AffineDrift Championship") -> GolfCourse:
    """Create an 18-hole championship course, par 72.

    Layout: four par 3s, ten par 4s, four par 5s.

    Args:
        name: Course name.

    Returns:
        A GolfCourse with 18 holes totaling par 72.
    """
    # (par, yardage) for each hole
    hole_specs: list[tuple[int, float]] = [
        (4, 415.0),  # 1
        (5, 545.0),  # 2
        (4, 390.0),  # 3
        (3, 185.0),  # 4
        (4, 440.0),  # 5
        (4, 375.0),  # 6
        (5, 530.0),  # 7
        (3, 165.0),  # 8
        (4, 460.0),  # 9
        (4, 420.0),  # 10
        (3, 195.0),  # 11
        (5, 560.0),  # 12
        (4, 385.0),  # 13
        (4, 350.0),  # 14
        (4, 430.0),  # 15
        (3, 220.0),  # 16
        (5, 570.0),  # 17
        (4, 445.0),  # 18
    ]

    handicaps = [5, 11, 9, 15, 1, 13, 7, 17, 3, 6, 16, 10, 12, 14, 2, 18, 8, 4]

    holes = [
        _make_hole(
            number=i + 1,
            par=par,
            yardage=yardage,
            handicap=handicaps[i],
            y_offset=i * 150.0,
        )
        for i, (par, yardage) in enumerate(hole_specs)
    ]

    total_par = sum(p for p, _ in hole_specs)
    logger.info(
        "Created championship course '%s' with 18 holes, par %d",
        name,
        total_par,
    )
    return GolfCourse(name=name, holes=holes)
