"""Golf club models and launch condition computation.

Provides club type classification, individual club specifications,
launch condition generation, and a club bag for automatic club selection
based on distance and terrain.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np

from src.core.constants import GRAVITY_M_S2
from src.core.contracts import check_non_negative, check_positive, require
from src.golf_simulation.ball_flight import BallFlightState
from src.golf_simulation.terrain import TerrainType

logger = logging.getLogger(__name__)


class ClubType(Enum):
    """Golf club classification."""

    DRIVER = "driver"
    THREE_WOOD = "3_wood"
    FIVE_WOOD = "5_wood"
    THREE_IRON = "3_iron"
    FOUR_IRON = "4_iron"
    FIVE_IRON = "5_iron"
    SIX_IRON = "6_iron"
    SEVEN_IRON = "7_iron"
    EIGHT_IRON = "8_iron"
    NINE_IRON = "9_iron"
    PW = "pw"
    GW = "gw"
    SW = "sw"
    LW = "lw"
    PUTTER = "putter"


@dataclass(frozen=True)
class GolfClub:
    """Specification for a single golf club.

    Attributes:
        club_type: Classification of the club.
        name: Human-readable name.
        loft_degrees: Loft angle in degrees.
        length_meters: Shaft length in meters.
        mass_kg: Club head mass in kg.
        typical_speed_ms: Typical ball speed off the clubface in m/s.
        typical_spin_rpm: Typical backspin in revolutions per minute.
        typical_launch_deg: Typical launch angle in degrees.
    """

    club_type: ClubType
    name: str
    loft_degrees: float
    length_meters: float
    mass_kg: float
    typical_speed_ms: float
    typical_spin_rpm: float
    typical_launch_deg: float

    def __post_init__(self) -> None:
        """Validate club specifications."""
        check_positive(self.loft_degrees, "loft_degrees")
        check_positive(self.length_meters, "length_meters")
        check_positive(self.mass_kg, "mass_kg")
        check_positive(self.typical_speed_ms, "typical_speed_ms")
        check_non_negative(self.typical_spin_rpm, "typical_spin_rpm")
        check_non_negative(self.typical_launch_deg, "typical_launch_deg")

    @property
    def typical_spin_rad_s(self) -> float:
        """Typical backspin converted to rad/s."""
        return float(self.typical_spin_rpm * 2.0 * np.pi / 60.0)

    @property
    def typical_launch_rad(self) -> float:
        """Typical launch angle converted to radians."""
        return float(np.radians(self.typical_launch_deg))

    @property
    def typical_distance_yards(self) -> float:
        """Estimated carry distance in yards based on a ballistic approximation.

        Uses a simplified range formula with a correction factor for drag.
        """
        v = self.typical_speed_ms
        angle = self.typical_launch_rad
        # Simplified range estimate: R = v^2 * sin(2*theta) / g * drag_factor
        drag_factor = 0.55  # Empirical correction for drag
        range_m = v**2 * np.sin(2.0 * angle) / GRAVITY_M_S2 * drag_factor
        return float(range_m * 1.09361)  # meters to yards


@dataclass(frozen=True)
class LaunchConditions:
    """Launch conditions for a golf shot.

    Attributes:
        ball_speed: Ball speed off the clubface in m/s.
        launch_angle: Launch angle above horizontal in radians.
        launch_direction: Horizontal launch direction in radians (0 = straight).
        backspin: Backspin rate in rad/s.
        sidespin: Sidespin rate in rad/s (positive = right curve).
    """

    ball_speed: float
    launch_angle: float
    launch_direction: float
    backspin: float
    sidespin: float

    def __post_init__(self) -> None:
        """Validate launch conditions."""
        check_positive(self.ball_speed, "ball_speed")

    def to_ball_flight_state(self) -> BallFlightState:
        """Convert launch conditions to a BallFlightState at the origin.

        Returns:
            BallFlightState with position at origin, velocity from launch
            parameters, and spin from backspin/sidespin.
        """
        # Decompose ball speed into velocity components
        horizontal_speed = self.ball_speed * np.cos(self.launch_angle)
        vertical_speed = self.ball_speed * np.sin(self.launch_angle)

        vx = horizontal_speed * np.cos(self.launch_direction)
        vy = horizontal_speed * np.sin(self.launch_direction)
        vz = vertical_speed

        # Spin: backspin is rotation about the horizontal axis perpendicular
        # to the launch direction; sidespin is rotation about the vertical axis.
        # In the body frame: backspin -> wy (pitch-back), sidespin -> wz (yaw)
        wx = 0.0
        wy = -self.backspin  # Negative because backspin opposes forward motion
        wz = self.sidespin

        return BallFlightState(
            position=np.array([0.0, 0.0, 0.0]),
            velocity=np.array([vx, vy, vz]),
            spin=np.array([wx, wy, wz]),
        )


# ── Standard Club Set ─────────────────────────────────────────────────────────

STANDARD_CLUBS: list[GolfClub] = [
    GolfClub(ClubType.DRIVER, "Driver", 10.5, 1.143, 0.200, 73.0, 2700.0, 10.5),
    GolfClub(ClubType.THREE_WOOD, "3 Wood", 15.0, 1.092, 0.210, 67.0, 3500.0, 11.0),
    GolfClub(ClubType.FIVE_WOOD, "5 Wood", 18.0, 1.067, 0.215, 64.0, 4000.0, 12.0),
    GolfClub(ClubType.THREE_IRON, "3 Iron", 21.0, 1.003, 0.235, 60.0, 4300.0, 12.5),
    GolfClub(ClubType.FOUR_IRON, "4 Iron", 24.0, 0.991, 0.240, 58.0, 4800.0, 13.0),
    GolfClub(ClubType.FIVE_IRON, "5 Iron", 27.0, 0.978, 0.245, 56.0, 5300.0, 14.0),
    GolfClub(ClubType.SIX_IRON, "6 Iron", 30.0, 0.965, 0.250, 53.0, 6100.0, 15.0),
    GolfClub(ClubType.SEVEN_IRON, "7 Iron", 34.0, 0.940, 0.260, 51.0, 7000.0, 16.0),
    GolfClub(ClubType.EIGHT_IRON, "8 Iron", 38.0, 0.927, 0.265, 48.0, 7500.0, 18.0),
    GolfClub(ClubType.NINE_IRON, "9 Iron", 42.0, 0.914, 0.270, 45.0, 8000.0, 21.0),
    GolfClub(ClubType.PW, "Pitching Wedge", 46.0, 0.902, 0.280, 42.0, 8500.0, 24.0),
    GolfClub(ClubType.GW, "Gap Wedge", 50.0, 0.895, 0.285, 38.0, 9000.0, 27.0),
    GolfClub(ClubType.SW, "Sand Wedge", 56.0, 0.889, 0.290, 33.0, 9500.0, 30.0),
    GolfClub(ClubType.LW, "Lob Wedge", 60.0, 0.883, 0.295, 28.0, 10000.0, 33.0),
    GolfClub(ClubType.PUTTER, "Putter", 3.0, 0.864, 0.340, 5.0, 200.0, 1.5),
]


class ClubBag:
    """A golfer's bag of clubs with automatic club selection.

    Provides club selection based on distance-to-pin and terrain type.
    """

    def __init__(self, clubs: list[GolfClub] | None = None) -> None:
        """Initialize club bag.

        Args:
            clubs: List of clubs to carry. Defaults to STANDARD_CLUBS.
        """
        self.clubs = clubs if clubs is not None else list(STANDARD_CLUBS)
        require(len(self.clubs) > 0, "club bag must contain at least one club")
        self._club_map: dict[ClubType, GolfClub] = {c.club_type: c for c in self.clubs}

    def get_club(self, club_type: ClubType) -> GolfClub:
        """Retrieve a specific club by type.

        Args:
            club_type: The type of club to retrieve.

        Returns:
            The matching GolfClub.

        Raises:
            KeyError: If the club type is not in the bag.
        """
        require(club_type in self._club_map, f"club type {club_type} not in bag")
        return self._club_map[club_type]

    def select_club(self, distance_yards: float, terrain: TerrainType) -> GolfClub:
        """Select the best club for the given distance and terrain.

        Chooses the club whose typical distance most closely matches the
        target distance, with adjustments for terrain conditions.

        Args:
            distance_yards: Distance to the target in yards.
            terrain: Current terrain type.

        Returns:
            The best-matching GolfClub.
        """
        check_positive(distance_yards, "distance_yards")

        # On the green, always putt
        if terrain == TerrainType.GREEN:
            if ClubType.PUTTER in self._club_map:
                return self._club_map[ClubType.PUTTER]

        # Filter out putter for non-green shots
        candidates = [c for c in self.clubs if c.club_type != ClubType.PUTTER]
        if not candidates:
            return self.clubs[0]

        # From rough/bunker, avoid long clubs (driver, woods)
        if terrain in (TerrainType.ROUGH, TerrainType.DEEP_ROUGH, TerrainType.BUNKER):
            non_long = [
                c
                for c in candidates
                if c.club_type not in (ClubType.DRIVER, ClubType.THREE_WOOD, ClubType.FIVE_WOOD)
            ]
            if non_long:
                candidates = non_long

        # Select club with typical distance closest to target
        best_club = min(
            candidates,
            key=lambda c: abs(c.typical_distance_yards - distance_yards),
        )

        logger.debug(
            "Selected %s for %.0f yards from %s (typical: %.0f yards)",
            best_club.name,
            distance_yards,
            terrain.value,
            best_club.typical_distance_yards,
        )

        return best_club
