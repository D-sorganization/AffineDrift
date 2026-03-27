"""Full round-of-golf simulator integrating all components.

Orchestrates ball flight, putting, club selection, and terrain management
to simulate a complete round of golf on a given course.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass

import numpy as np

from src.golf_simulation.ball_flight import BallFlightDynamics, BallFlightState
from src.golf_simulation.clubs import ClubBag, ClubType, GolfClub, LaunchConditions
from src.golf_simulation.course import METERS_TO_YARDS, GolfCourse, GolfHole
from src.golf_simulation.putting import GreenSurface, PuttingSimulator
from src.golf_simulation.terrain import TerrainType

logger = logging.getLogger(__name__)

# Maximum strokes before conceding a hole
MAX_STROKES_PER_HOLE = 10


@dataclass
class ShotResult:
    """Result of a single golf shot.

    Attributes:
        club: Club used for the shot.
        start_position: Starting (x, y, z) in meters.
        end_position: Ending (x, y, z) in meters.
        trajectory: List of (x, y, z) positions along the shot path.
        terrain_at_rest: Terrain type where the ball came to rest.
        distance_yards: Distance covered in yards.
        is_penalty: Whether the shot incurred a penalty stroke.
    """

    club: GolfClub
    start_position: tuple[float, float, float]
    end_position: tuple[float, float, float]
    trajectory: list[tuple[float, float, float]]
    terrain_at_rest: TerrainType
    distance_yards: float
    is_penalty: bool


@dataclass
class HoleResult:
    """Result of playing a single hole.

    Attributes:
        hole: The hole definition.
        shots: List of shot results for this hole.
        score: Total strokes taken (including penalties).
        par: Par for the hole.
        relative_to_par: Score minus par (negative = under par).
    """

    hole: GolfHole
    shots: list[ShotResult]
    score: int
    par: int
    relative_to_par: int


@dataclass
class RoundResult:
    """Result of a full round of golf.

    Attributes:
        course: The course played.
        hole_results: Results for each hole.
    """

    course: GolfCourse
    hole_results: list[HoleResult]

    @property
    def total_score(self) -> int:
        """Total strokes for the round."""
        return sum(hr.score for hr in self.hole_results)

    @property
    def total_par(self) -> int:
        """Total par for the holes played."""
        return sum(hr.par for hr in self.hole_results)

    @property
    def relative_to_par(self) -> int:
        """Total score relative to par (negative = under par)."""
        return self.total_score - self.total_par

    @property
    def total_shots(self) -> int:
        """Total number of shots taken (same as total_score)."""
        return self.total_score


class RoundSimulator:
    """Simulates a full round of golf on a given course.

    Integrates ball flight dynamics, putting simulation, and club selection
    to play through each hole from tee to cup.
    """

    def __init__(
        self,
        course: GolfCourse,
        club_bag: ClubBag | None = None,
        ball_flight: BallFlightDynamics | None = None,
        rng_seed: int | None = None,
    ) -> None:
        """Initialize the round simulator.

        Args:
            course: The golf course to play.
            club_bag: Club bag to use. Defaults to standard set.
            ball_flight: Ball flight dynamics model. Defaults to standard params.
            rng_seed: Random seed for shot dispersion (None = non-deterministic).
        """
        self.course = course
        self.club_bag = club_bag if club_bag is not None else ClubBag()
        self.ball_flight = ball_flight if ball_flight is not None else BallFlightDynamics()
        self.rng = np.random.default_rng(rng_seed)

    def simulate_round(self) -> RoundResult:
        """Simulate a complete round of golf.

        Returns:
            RoundResult with results for every hole on the course.
        """
        hole_results: list[HoleResult] = []

        for hole in self.course.holes:
            result = self.simulate_hole(hole)
            hole_results.append(result)
            logger.info(
                "Hole %d (par %d): score %d (%+d)",
                hole.number,
                hole.par,
                result.score,
                result.relative_to_par,
            )

        round_result = RoundResult(course=self.course, hole_results=hole_results)
        logger.info(
            "Round complete on %s: %d (%+d)",
            self.course.name,
            round_result.total_score,
            round_result.relative_to_par,
        )
        return round_result

    def simulate_hole(self, hole: GolfHole) -> HoleResult:
        """Simulate playing a single hole from tee to cup.

        Args:
            hole: The hole to play.

        Returns:
            HoleResult with all shots and final score.
        """
        position = hole.tee_position
        shots: list[ShotResult] = []
        stroke_count = 0

        while stroke_count < MAX_STROKES_PER_HOLE:
            terrain = hole.get_terrain(position[0], position[1])
            dist_to_pin = hole.distance_to_pin(position[0], position[1])
            dist_to_pin_yards = dist_to_pin * METERS_TO_YARDS

            # Check if we're on the green
            if terrain == TerrainType.GREEN and dist_to_pin_yards < 80:
                shot = self._simulate_putt(position, hole)
            else:
                club = self._select_shot_type(position, hole)
                shot = self._simulate_shot(position, hole, club)

            shots.append(shot)
            stroke_count += 1

            if shot.is_penalty:
                stroke_count += 1  # Penalty stroke

            position = shot.end_position

            # Check if holed
            dist_remaining = hole.distance_to_pin(position[0], position[1])
            if dist_remaining < 0.054:  # Within hole radius
                logger.debug("Hole %d completed in %d strokes", hole.number, stroke_count)
                break

        return HoleResult(
            hole=hole,
            shots=shots,
            score=stroke_count,
            par=hole.par,
            relative_to_par=stroke_count - hole.par,
        )

    def _select_shot_type(
        self,
        position: tuple[float, float, float],
        hole: GolfHole,
    ) -> GolfClub:
        """Select the appropriate club based on distance and terrain.

        Args:
            position: Current ball position (x, y, z) in meters.
            hole: The current hole being played.

        Returns:
            The selected GolfClub.
        """
        dist_to_pin = hole.distance_to_pin(position[0], position[1])
        dist_yards = dist_to_pin * METERS_TO_YARDS
        terrain = hole.get_terrain(position[0], position[1])

        return self.club_bag.select_club(max(dist_yards, 1.0), terrain)

    def _simulate_shot(
        self,
        position: tuple[float, float, float],
        hole: GolfHole,
        club: GolfClub,
    ) -> ShotResult:
        """Simulate a full shot (tee shot, approach, chip, etc.).

        Adds realistic dispersion to launch conditions and simulates
        ball flight. Handles penalty situations (water, OB).

        Args:
            position: Starting position (x, y, z) in meters.
            hole: The current hole.
            club: The club to use.

        Returns:
            ShotResult with trajectory and landing info.
        """
        # Generate launch conditions with dispersion
        speed_variation = 1.0 + self.rng.normal(0.0, 0.02)
        ball_speed = club.typical_speed_ms * max(speed_variation, 0.5)

        direction_error = self.rng.normal(0.0, np.radians(2.0))

        # Aim toward the pin
        dx = hole.pin_position[0] - position[0]
        dy = hole.pin_position[1] - position[1]
        aim_direction = math.atan2(dy, dx)

        launch = LaunchConditions(
            ball_speed=ball_speed,
            launch_angle=club.typical_launch_rad,
            launch_direction=aim_direction + direction_error,
            backspin=club.typical_spin_rad_s,
            sidespin=self.rng.normal(0.0, 10.0),
        )

        # Convert to ball flight state and simulate
        initial = launch.to_ball_flight_state()

        # Offset initial position
        offset_initial = BallFlightState(
            position=np.array(position, dtype=float),
            velocity=initial.velocity,
            spin=initial.spin,
        )

        trajectory_states = self.ball_flight.simulate(offset_initial, dt=0.01, max_time=15.0)

        # Extract trajectory points
        traj_points: list[tuple[float, float, float]] = [
            (float(s.position[0]), float(s.position[1]), float(s.position[2]))
            for s in trajectory_states
        ]

        # Landing position
        final_state = trajectory_states[-1]
        end_pos = (
            float(final_state.position[0]),
            float(final_state.position[1]),
            float(final_state.position[2]),
        )

        # Determine terrain at landing
        terrain_at_rest = hole.get_terrain(end_pos[0], end_pos[1])

        # Distance covered
        dx_shot = end_pos[0] - position[0]
        dy_shot = end_pos[1] - position[1]
        distance_m = math.sqrt(dx_shot**2 + dy_shot**2)
        distance_yards = distance_m * METERS_TO_YARDS

        # Handle penalty situations
        is_penalty = terrain_at_rest in (TerrainType.WATER, TerrainType.OUT_OF_BOUNDS)
        if is_penalty:
            logger.debug(
                "Penalty: ball in %s at (%.1f, %.1f)",
                terrain_at_rest.value,
                end_pos[0],
                end_pos[1],
            )
            # Drop ball near where it entered the hazard, back on fairway
            # Move 80% of the way to the landing point
            drop_fraction = 0.8
            drop_x = position[0] + drop_fraction * dx_shot
            drop_y = position[1] + drop_fraction * dy_shot
            end_pos = (drop_x, drop_y, 0.0)
            terrain_at_rest = hole.get_terrain(drop_x, drop_y)

        return ShotResult(
            club=club,
            start_position=position,
            end_position=end_pos,
            trajectory=traj_points,
            terrain_at_rest=terrain_at_rest,
            distance_yards=distance_yards,
            is_penalty=is_penalty,
        )

    def _simulate_putt(
        self,
        position: tuple[float, float, float],
        hole: GolfHole,
    ) -> ShotResult:
        """Simulate a putt on the green.

        Args:
            position: Starting position (x, y, z) in meters.
            hole: The current hole.

        Returns:
            ShotResult for the putt.
        """
        putter = self.club_bag.get_club(ClubType.PUTTER)

        # Compute direction and speed for putt
        dx = hole.pin_position[0] - position[0]
        dy = hole.pin_position[1] - position[1]
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 1e-6:
            # Already at the hole
            return ShotResult(
                club=putter,
                start_position=position,
                end_position=hole.pin_position,
                trajectory=[position, hole.pin_position],
                terrain_at_rest=TerrainType.GREEN,
                distance_yards=0.0,
                is_penalty=False,
            )

        # Simple green surface for putting simulation
        green = GreenSurface.create_flat_green(
            width=hole.green_radius * 3.0,
            height=hole.green_radius * 3.0,
            stimp=11.0,
        )
        putt_sim = PuttingSimulator(surface=green)

        # Aim direction with slight error
        direction_error = self.rng.normal(0.0, np.radians(1.0))
        aim_angle = math.atan2(dy, dx) + direction_error

        # Putt speed: roughly proportional to distance, with stimp correction
        # Empirical: speed ~ sqrt(2 * deceleration * distance) * 1.1 (overshoot)
        deceleration = 1.285 / green.stimp
        target_speed = math.sqrt(2.0 * deceleration * dist) * 1.1
        speed_variation = 1.0 + self.rng.normal(0.0, 0.05)
        putt_speed = target_speed * max(speed_variation, 0.3)

        vx = putt_speed * math.cos(aim_angle)
        vy = putt_speed * math.sin(aim_angle)

        # Simulate the putt
        putt_trajectory = putt_sim.simulate(position[0], position[1], vx, vy)

        # Check if holed at each point along the trajectory
        final_x, final_y = putt_trajectory[-1]

        for px, py in putt_trajectory:
            # Approximate velocity at this point (difference from next point)
            idx = putt_trajectory.index((px, py))
            if idx < len(putt_trajectory) - 1:
                nx, ny = putt_trajectory[idx + 1]
                cvx = (nx - px) / putt_sim.dt
                cvy = (ny - py) / putt_sim.dt
            else:
                cvx, cvy = 0.0, 0.0

            if putt_sim.is_holed(
                px,
                py,
                cvx,
                cvy,
                hole.pin_position[0],
                hole.pin_position[1],
            ):
                final_x, final_y = hole.pin_position[0], hole.pin_position[1]
                break

        end_pos = (final_x, final_y, 0.0)
        traj_3d: list[tuple[float, float, float]] = [(px, py, 0.0) for px, py in putt_trajectory]

        putt_dist_m = math.sqrt((final_x - position[0]) ** 2 + (final_y - position[1]) ** 2)

        return ShotResult(
            club=putter,
            start_position=position,
            end_position=end_pos,
            trajectory=traj_3d,
            terrain_at_rest=TerrainType.GREEN,
            distance_yards=putt_dist_m * METERS_TO_YARDS,
            is_penalty=False,
        )
