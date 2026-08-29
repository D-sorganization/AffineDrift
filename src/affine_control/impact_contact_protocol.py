"""Fail-closed declarations for hybrid club--ball impact research.

The contracts describe a reduced planar contact-coordinate experiment. They do
not qualify a golf ball, club, participant, coaching intervention, or design.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

ModelId = Literal["rigid-impulse", "compliant-contact", "hybrid-event"]
EvidenceType = Literal["primary-literature", "measurement-method", "review"]
LedgerStatus = Literal["supported", "negative", "null", "unavailable"]

MODEL_IDS: tuple[ModelId, ...] = ("rigid-impulse", "compliant-contact", "hybrid-event")
_EVIDENCE_TYPES = ("primary-literature", "measurement-method", "review")
_SI_UNITS = ("m", "s", "rad", "N", "kg")


def _require_text(value: str, label: str) -> None:
    """Require a nonblank declaration."""
    if not value.strip():
        raise ValueError(f"{label} must be declared")


def _require_texts(values: tuple[str, ...], label: str) -> None:
    """Require a nonempty tuple without blank entries."""
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must be declared")


def _require_positive(values: tuple[float, ...], label: str) -> None:
    """Require finite, strictly positive values."""
    if not all(isfinite(value) and value > 0.0 for value in values):
        raise ValueError(f"{label} must be finite and positive")


def _require_interval(bounds: tuple[float, float], nominal: float, label: str) -> None:
    """Require finite ordered bounds containing the nominal value."""
    low, high = bounds
    if not all(isfinite(value) for value in (low, nominal, high)):
        raise ValueError(f"{label} interval must be finite")
    if low > nominal or nominal > high:
        raise ValueError(f"{label} interval must contain its nominal value")


@dataclass(frozen=True)
class EvidenceSource:
    """One source and the boundary on what it can support."""

    source_id: str
    evidence_type: EvidenceType
    citation: str
    supports: str
    limitation: str

    def __post_init__(self) -> None:
        """Reject unknown evidence classes and incomplete provenance."""
        if self.evidence_type not in _EVIDENCE_TYPES:
            raise ValueError("evidence type is outside the declared domain")
        for value, label in (
            (self.source_id, "source ID"),
            (self.citation, "citation"),
            (self.supports, "source support"),
            (self.limitation, "source limitation"),
        ):
            _require_text(value, label)


@dataclass(frozen=True)
class FrameConvention:
    """Planar contact frame, handedness, origin, and unit declaration."""

    frame_id: str
    origin: str
    normal_axis: str
    tangent_axis: str
    angular_axis: str
    length_unit: str
    time_unit: str
    angle_unit: str
    force_unit: str
    mass_unit: str

    def __post_init__(self) -> None:
        """Require distinct axes and one frozen SI unit set."""
        for value, label in (
            (self.frame_id, "frame ID"),
            (self.origin, "frame origin"),
            (self.normal_axis, "normal axis"),
            (self.tangent_axis, "tangent axis"),
            (self.angular_axis, "angular axis"),
        ):
            _require_text(value, label)
        if len({self.normal_axis, self.tangent_axis, self.angular_axis}) != 3:
            raise ValueError("frame axes must be distinct")
        units = (
            self.length_unit,
            self.time_unit,
            self.angle_unit,
            self.force_unit,
            self.mass_unit,
        )
        if units != _SI_UNITS:
            raise ValueError("frame must use the frozen SI units m, s, rad, N, and kg")


@dataclass(frozen=True)
class ImpactState:
    """Measured or manufactured pre-impact state in the declared frame."""

    state_id: str
    club_velocity_m_s: tuple[float, float]
    ball_velocity_m_s: tuple[float, float]
    ball_spin_rad_s: float
    contact_count: int
    evidence_origin: str

    def __post_init__(self) -> None:
        """Require finite planar kinematics and an explicit contact count."""
        _require_text(self.state_id, "state ID")
        _require_text(self.evidence_origin, "evidence origin")
        values = (*self.club_velocity_m_s, *self.ball_velocity_m_s, self.ball_spin_rad_s)
        if len(self.club_velocity_m_s) != 2 or len(self.ball_velocity_m_s) != 2:
            raise ValueError("impact velocities must be planar two-vectors")
        if not all(isfinite(value) for value in values):
            raise ValueError("impact state values must be finite")
        if isinstance(self.contact_count, bool) or not isinstance(self.contact_count, int):
            raise ValueError("contact count must be a nonnegative integer")
        if self.contact_count < 0:
            raise ValueError("contact count must be a nonnegative integer")


@dataclass(frozen=True)
class ContactParameters:
    """Reduced planar mass, friction, compliance, and solver declaration."""

    club_mass_kg: float
    ball_mass_kg: float
    ball_radius_m: float
    ball_inertia_kg_m2: float
    restitution: float
    friction: float
    contact_stiffness_n_m_exp: float
    contact_damping_s_m: float
    contact_exponent: float
    solver_step_s: float
    maximum_contact_time_s: float
    maximum_contact_steps: int

    def __post_init__(self) -> None:
        """Reject nonphysical or numerically unbounded parameter domains."""
        _require_positive(
            (
                self.club_mass_kg,
                self.ball_mass_kg,
                self.ball_radius_m,
                self.ball_inertia_kg_m2,
                self.contact_stiffness_n_m_exp,
                self.solver_step_s,
                self.maximum_contact_time_s,
            ),
            "contact parameters",
        )
        if not isfinite(self.restitution) or not 0.0 <= self.restitution <= 1.0:
            raise ValueError("restitution must be finite and between zero and one")
        if not isfinite(self.friction) or self.friction < 0.0:
            raise ValueError("friction must be finite and nonnegative")
        if not isfinite(self.contact_damping_s_m) or self.contact_damping_s_m < 0.0:
            raise ValueError("contact damping must be finite and nonnegative")
        if not isfinite(self.contact_exponent) or self.contact_exponent < 1.0:
            raise ValueError("contact exponent must be finite and at least one")
        if (
            isinstance(self.maximum_contact_steps, bool)
            or not isinstance(self.maximum_contact_steps, int)
            or self.maximum_contact_steps < 1
        ):
            raise ValueError("maximum contact steps must be a positive integer")


@dataclass(frozen=True)
class EventPolicy:
    """Guard, sampling, interpolation, and ambiguous-contact disposition."""

    guard: str
    crossing_direction: str
    interpolation: str
    sample_rate_hz: float
    timing_uncertainty_s: float
    synchronization_uncertainty_s: float
    grazing_speed_threshold_m_s: float
    multiple_contact_policy: str

    def __post_init__(self) -> None:
        """Require bounded timing and a fail-closed ambiguous-contact policy."""
        for value, label in (
            (self.guard, "event guard"),
            (self.crossing_direction, "crossing direction"),
            (self.interpolation, "event interpolation"),
        ):
            _require_text(value, label)
        _require_positive((self.sample_rate_hz, self.grazing_speed_threshold_m_s), "sample rate")
        timing = (self.timing_uncertainty_s, self.synchronization_uncertainty_s)
        if not all(isfinite(value) and value >= 0.0 for value in timing):
            raise ValueError("timing uncertainties must be finite and nonnegative")
        if self.multiple_contact_policy != "fail-closed":
            raise ValueError("multiple-contact policy must be fail-closed")


@dataclass(frozen=True)
class ParameterUncertainty:
    """Closed uncertainty ranges used by the manufactured sensitivity sweep."""

    restitution: tuple[float, float]
    friction: tuple[float, float]
    face_normal_angle_deg: tuple[float, float]
    event_time_s: tuple[float, float]

    def validate(self, parameters: ContactParameters) -> None:
        """Require every range to include the protocol nominal value."""
        _require_interval(self.restitution, parameters.restitution, "restitution")
        _require_interval(self.friction, parameters.friction, "friction")
        _require_interval(self.face_normal_angle_deg, 0.0, "face-normal angle")
        _require_interval(self.event_time_s, 0.0, "event time")
        if self.restitution[0] < 0.0 or self.restitution[1] > 1.0:
            raise ValueError("restitution uncertainty must remain between zero and one")
        if self.friction[0] < 0.0:
            raise ValueError("friction uncertainty must remain nonnegative")


@dataclass(frozen=True)
class HumanStudyGate:
    """Human-study promotion state; unavailable is the only fixture state."""

    status: Literal["unavailable"]
    missing_authorities: tuple[str, ...]

    def __post_init__(self) -> None:
        """Keep the manufactured protocol outside participant authority."""
        if self.status != "unavailable":
            raise ValueError("human study status must remain unavailable")
        _require_texts(self.missing_authorities, "missing human authorities")


@dataclass(frozen=True)
class ImpactProtocol:
    """Complete source, model, state, uncertainty, and authority declaration."""

    revision: str
    sources: tuple[EvidenceSource, ...]
    model_ids: tuple[ModelId, ...]
    frame: FrameConvention
    parameters: ContactParameters
    event_policy: EventPolicy
    uncertainty: ParameterUncertainty
    human_gate: HumanStudyGate
    hypotheses: tuple[str, ...]
    authority_limit: str

    def __post_init__(self) -> None:
        """Require the exact comparison and a complete bounded protocol."""
        _require_text(self.revision, "protocol revision")
        unique_source_count = len({source.source_id for source in self.sources})
        if not self.sources or unique_source_count != len(self.sources):
            raise ValueError("protocol sources must be nonempty and unique")
        if self.model_ids != MODEL_IDS:
            raise ValueError("protocol must compare rigid, compliant, and hybrid models")
        self.uncertainty.validate(self.parameters)
        _require_texts(self.hypotheses, "hypotheses")
        _require_text(self.authority_limit, "authority limit")


@dataclass(frozen=True)
class FixtureLedgerRecord:
    """One retained manufactured result and its permitted statement."""

    record_id: str
    status: LedgerStatus
    evidence_origin: str
    authorized_claim: str
    limitation: str

    def __post_init__(self) -> None:
        """Require explicit outcome and provenance semantics."""
        if self.status not in ("supported", "negative", "null", "unavailable"):
            raise ValueError("fixture status is outside the declared ledger")
        for value, label in (
            (self.record_id, "record ID"),
            (self.evidence_origin, "evidence origin"),
            (self.authorized_claim, "authorized claim"),
            (self.limitation, "fixture limitation"),
        ):
            _require_text(value, label)
