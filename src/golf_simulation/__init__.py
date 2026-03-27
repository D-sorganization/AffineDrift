"""Golf simulation environment for AffineDrift.

Provides course modeling, ball flight dynamics, putting simulation,
club models, and full round simulation integrated with the AffineDrift
forward dynamics framework.
"""

from src.golf_simulation.ball_flight import BallFlightDynamics, BallFlightState
from src.golf_simulation.clubs import ClubBag, ClubType, GolfClub, LaunchConditions
from src.golf_simulation.course import GolfCourse, GolfHole, TerrainType
from src.golf_simulation.putting import GreenSurface, PuttingSimulator
from src.golf_simulation.round_simulator import RoundResult, RoundSimulator, ShotResult

__all__ = [
    "BallFlightDynamics",
    "BallFlightState",
    "ClubBag",
    "ClubType",
    "GolfClub",
    "GolfCourse",
    "GolfHole",
    "GreenSurface",
    "LaunchConditions",
    "PuttingSimulator",
    "RoundResult",
    "RoundSimulator",
    "ShotResult",
    "TerrainType",
]
