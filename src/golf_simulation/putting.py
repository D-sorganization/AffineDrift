"""Putting green simulation with surface contours and roll physics.

Models the green surface as a 2D elevation field, then simulates ball roll
including friction (calibrated to Stimpmeter reading), gravity-driven break
from surface slope, and hole-capture detection.
"""

from __future__ import annotations

import logging
import math

from src.core.constants import GRAVITY_M_S2
from src.core.contracts import check_positive, check_range, require

logger = logging.getLogger(__name__)


class GreenSurface:
    """Putting green surface with elevation contours.

    The green is modeled as a rectangular region with elevation defined
    by control points. Slope (gradient) is computed via finite differences.

    Attributes:
        width: Green width in meters (x direction).
        height: Green height in meters (y direction).
        stimp: Stimpmeter reading (higher = faster green, typical 8-14).
    """

    def __init__(
        self,
        width: float,
        height: float,
        stimp: float,
        control_points: list[tuple[float, float, float]] | None = None,
    ) -> None:
        """Initialize green surface.

        Args:
            width: Width of the green in meters.
            height: Height (depth) of the green in meters.
            stimp: Stimpmeter reading (4-16 range).
            control_points: List of (x, y, elevation) tuples defining
                the surface. If None, creates a flat green at elevation 0.
        """
        check_positive(width, "width")
        check_positive(height, "height")
        check_range(stimp, 4.0, 16.0, "stimp")

        self.width = width
        self.height = height
        self.stimp = stimp

        if control_points is not None:
            require(len(control_points) > 0, "control_points must not be empty")
            self._control_points = list(control_points)
        else:
            # Flat green: four corners at elevation 0
            self._control_points = [
                (0.0, 0.0, 0.0),
                (width, 0.0, 0.0),
                (0.0, height, 0.0),
                (width, height, 0.0),
            ]

    def evaluate_elevation(self, x: float, y: float) -> float:
        """Compute the green surface elevation at (x, y).

        Uses inverse-distance-weighted interpolation from control points.

        Args:
            x: X position in meters.
            y: Y position in meters.

        Returns:
            Elevation in meters.
        """
        if len(self._control_points) == 0:
            return 0.0

        total_weight = 0.0
        weighted_elev = 0.0

        for cx, cy, cz in self._control_points:
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist < 1e-10:
                return cz
            w = 1.0 / (dist * dist)
            total_weight += w
            weighted_elev += w * cz

        if total_weight < 1e-10:
            return 0.0

        return weighted_elev / total_weight

    def evaluate_slope(self, x: float, y: float) -> tuple[float, float]:
        """Compute the surface gradient (dz/dx, dz/dy) at (x, y).

        Uses central finite differences on the elevation function.

        Args:
            x: X position in meters.
            y: Y position in meters.

        Returns:
            Tuple of (dz/dx, dz/dy) slope components.
        """
        h = 0.001  # finite difference step in meters

        dzdx = (self.evaluate_elevation(x + h, y) - self.evaluate_elevation(x - h, y)) / (2.0 * h)
        dzdy = (self.evaluate_elevation(x, y + h) - self.evaluate_elevation(x, y - h)) / (2.0 * h)

        return (dzdx, dzdy)

    def is_on_green(self, x: float, y: float) -> bool:
        """Check whether a position is within the green boundaries.

        Args:
            x: X position in meters.
            y: Y position in meters.

        Returns:
            True if the position is on the green.
        """
        return 0.0 <= x <= self.width and 0.0 <= y <= self.height

    @staticmethod
    def create_flat_green(
        width: float = 30.0,
        height: float = 30.0,
        stimp: float = 11.0,
    ) -> GreenSurface:
        """Create a flat (level) green surface.

        Args:
            width: Green width in meters.
            height: Green height in meters.
            stimp: Stimpmeter reading.

        Returns:
            A flat GreenSurface.
        """
        return GreenSurface(width=width, height=height, stimp=stimp, control_points=None)

    @staticmethod
    def create_sloped_green(
        width: float = 30.0,
        height: float = 30.0,
        stimp: float = 11.0,
        slope_x: float = 0.0,
        slope_y: float = 0.0,
    ) -> GreenSurface:
        """Create a green with a uniform planar slope.

        The elevation at (x, y) = slope_x * x + slope_y * y.

        Args:
            width: Green width in meters.
            height: Green height in meters.
            stimp: Stimpmeter reading.
            slope_x: Slope in the x direction (rise/run).
            slope_y: Slope in the y direction (rise/run).

        Returns:
            A uniformly sloped GreenSurface.
        """
        # Create control points at the four corners with elevations from the slope
        control_points = [
            (0.0, 0.0, 0.0),
            (width, 0.0, slope_x * width),
            (0.0, height, slope_y * height),
            (width, height, slope_x * width + slope_y * height),
        ]
        return GreenSurface(
            width=width,
            height=height,
            stimp=stimp,
            control_points=control_points,
        )


class PuttingSimulator:
    """Simulates a putt on a green surface with friction and slope effects.

    Uses a Stimpmeter-calibrated friction model combined with gravity-driven
    acceleration from the green's surface slope.
    """

    def __init__(
        self,
        surface: GreenSurface,
        dt: float = 0.001,
        hole_radius: float = 0.054,
    ) -> None:
        """Initialize putting simulator.

        Args:
            surface: The green surface to putt on.
            dt: Simulation timestep in seconds.
            hole_radius: Radius of the hole in meters (regulation: 0.054 m / 4.25 in).
        """
        check_positive(dt, "dt")
        check_positive(hole_radius, "hole_radius")

        self.surface = surface
        self.dt = dt
        self.hole_radius = hole_radius

    def _euler_step(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        deceleration: float,
    ) -> tuple[float, float, float, float]:
        """Advance the putt state by one Euler step.

        Args:
            x: Current x position in meters.
            y: Current y position in meters.
            vx: Current x velocity in m/s.
            vy: Current y velocity in m/s.
            deceleration: Stimpmeter-calibrated friction deceleration (m/s^2).

        Returns:
            Updated (x, y, vx, vy) after one timestep.
        """
        speed = math.sqrt(vx * vx + vy * vy)
        slope_x, slope_y = self.surface.evaluate_slope(x, y)
        ax = -GRAVITY_M_S2 * slope_x - deceleration * vx / max(speed, 1e-10)
        ay = -GRAVITY_M_S2 * slope_y - deceleration * vy / max(speed, 1e-10)
        vx += ax * self.dt
        vy += ay * self.dt
        x += vx * self.dt
        y += vy * self.dt
        return x, y, vx, vy

    def simulate(
        self,
        start_x: float,
        start_y: float,
        velocity_x: float,
        velocity_y: float,
        max_time: float = 30.0,
    ) -> list[tuple[float, float]]:
        """Simulate a putt from start position with initial velocity.

        Integrates ball roll including friction and slope until the ball
        stops (speed < threshold) or max_time is exceeded.

        Args:
            start_x: Starting x position in meters.
            start_y: Starting y position in meters.
            velocity_x: Initial x velocity in m/s.
            velocity_y: Initial y velocity in m/s.
            max_time: Maximum simulation time in seconds.

        Returns:
            List of (x, y) position tuples along the ball's path.
        """
        check_positive(max_time, "max_time")

        x, y, vx, vy = start_x, start_y, velocity_x, velocity_y
        deceleration = 1.285 / self.surface.stimp
        trajectory: list[tuple[float, float]] = [(x, y)]
        t = 0.0

        while t < max_time:
            speed = math.sqrt(vx * vx + vy * vy)
            if speed < 0.005:
                logger.debug("Putt stopped at (%.3f, %.3f) after %.2f s", x, y, t)
                break
            x, y, vx, vy = self._euler_step(x, y, vx, vy, deceleration)
            t += self.dt
            trajectory.append((x, y))

        return trajectory

    def is_holed(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        pin_x: float,
        pin_y: float,
    ) -> bool:
        """Check whether the ball falls into the hole.

        The ball is holed if it is within the hole radius and moving
        slowly enough to be captured.

        Args:
            x: Ball x position in meters.
            y: Ball y position in meters.
            vx: Ball x velocity in m/s.
            vy: Ball y velocity in m/s.
            pin_x: Hole x position in meters.
            pin_y: Hole y position in meters.

        Returns:
            True if the ball is captured by the hole.
        """
        dist = math.sqrt((x - pin_x) ** 2 + (y - pin_y) ** 2)
        speed = math.sqrt(vx * vx + vy * vy)

        # Ball must be within hole radius and slow enough to drop in
        # Maximum capture speed: ~1.5 m/s (empirical)
        max_capture_speed = 1.5
        return dist <= self.hole_radius and speed < max_capture_speed
