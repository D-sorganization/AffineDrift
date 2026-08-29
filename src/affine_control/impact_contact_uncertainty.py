"""Deterministic uncertainty transport for the reduced hybrid impact fixture."""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
from math import atan2, cos, degrees, hypot, radians, sin

from src.affine_control.impact_contact_models import solve_hybrid_event
from src.affine_control.impact_contact_protocol import ImpactProtocol, ImpactState

_LEVELS = (0, 1, 2)


@dataclass(frozen=True)
class ClosedInterval:
    """Finite minimum/maximum summary for one declared quantity."""

    minimum: float
    maximum: float
    unit: str

    @property
    def width(self) -> float:
        """Return the closed-interval width."""
        return self.maximum - self.minimum


@dataclass(frozen=True)
class OutcomeInterval:
    """Nominal and complete Cartesian sensitivity sweep summary."""

    ball_speed_m_s: ClosedInterval
    launch_angle_deg: ClosedInterval
    ball_spin_rad_s: ClosedInterval
    nominal_ball_speed_m_s: float
    nominal_launch_angle_deg: float
    nominal_ball_spin_rad_s: float
    varied_inputs: tuple[str, ...]
    sample_count: int
    evidence_origin: str = "synthetic-fixture"


def _three_levels(bounds: tuple[float, float]) -> tuple[float, float, float]:
    """Return lower, midpoint, and upper levels for a closed interval."""
    lower, upper = bounds
    return lower, (lower + upper) / 2.0, upper


def _rotate_vector(vector: tuple[float, float], angle_deg: float) -> tuple[float, float]:
    """Express one lab-frame vector in a perturbed contact frame."""
    angle = radians(angle_deg)
    x_value, y_value = vector
    return (
        cos(angle) * x_value + sin(angle) * y_value,
        -sin(angle) * x_value + cos(angle) * y_value,
    )


def _rotate_state(state: ImpactState, angle_deg: float) -> ImpactState:
    """Rotate both measured velocities into one candidate face frame."""
    return replace(
        state,
        club_velocity_m_s=_rotate_vector(state.club_velocity_m_s, angle_deg),
        ball_velocity_m_s=_rotate_vector(state.ball_velocity_m_s, angle_deg),
    )


def _outcome_metrics(
    protocol: ImpactProtocol,
    state: ImpactState,
    restitution: float,
    friction: float,
    angle_deg: float,
    event_time_s: float,
) -> tuple[float, float, float]:
    """Evaluate one parameter corner and return three reported metrics."""
    parameters = replace(protocol.parameters, restitution=restitution, friction=friction)
    outcome = solve_hybrid_event(
        _rotate_state(state, angle_deg),
        parameters,
        protocol.event_policy,
        event_time_offset_s=event_time_s,
        club_acceleration_m_s2=_rotate_vector((120.0, 0.0), angle_deg),
        ball_acceleration_m_s2=(0.0, 0.0),
    )
    normal_velocity, tangent_velocity = outcome.ball_velocity_m_s
    speed = hypot(normal_velocity, tangent_velocity)
    angle = degrees(atan2(tangent_velocity, normal_velocity)) + angle_deg
    return speed, angle, outcome.ball_spin_rad_s


def _closed_interval(values: list[float], unit: str) -> ClosedInterval:
    """Summarize a nonempty deterministic sample set."""
    if not values:
        raise ValueError("uncertainty sweep must produce at least one value")
    return ClosedInterval(min(values), max(values), unit)


def propagate_outcome_interval(
    protocol: ImpactProtocol,
    state: ImpactState,
) -> OutcomeInterval:
    """Propagate four declared inputs through a complete 3-level grid."""
    uncertainty = protocol.uncertainty
    levels = (
        _three_levels(uncertainty.restitution),
        _three_levels(uncertainty.friction),
        _three_levels(uncertainty.face_normal_angle_deg),
        _three_levels(uncertainty.event_time_s),
    )
    metrics = [
        _outcome_metrics(protocol, state, restitution, friction, angle, event_time)
        for restitution, friction, angle, event_time in product(*levels)
    ]
    nominal = _outcome_metrics(
        protocol,
        state,
        protocol.parameters.restitution,
        protocol.parameters.friction,
        0.0,
        0.0,
    )
    speeds, angles, spins = (list(values) for values in zip(*metrics, strict=True))
    return OutcomeInterval(
        ball_speed_m_s=_closed_interval(speeds, "m/s"),
        launch_angle_deg=_closed_interval(angles, "deg"),
        ball_spin_rad_s=_closed_interval(spins, "rad/s"),
        nominal_ball_speed_m_s=nominal[0],
        nominal_launch_angle_deg=nominal[1],
        nominal_ball_spin_rad_s=nominal[2],
        varied_inputs=("event time", "restitution", "friction", "face-normal angle"),
        sample_count=len(metrics),
    )
