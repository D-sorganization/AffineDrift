"""Fail-closed contracts for multimodal feedback-perturbation experiments."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

EvidenceScope = Literal["general-upper-limb", "golf-specific"]
SourceType = Literal["primary-experiment"]
Modality = Literal["mechanical", "visual", "auditory"]
TimingLayer = Literal[
    "perturbation-detection",
    "muscle-response",
    "mechanical-effect",
    "task-correction",
]
Expectation = Literal["unexpected", "cued-direction-unknown", "fully-predictable"]
Hierarchy = Literal["primary", "secondary", "exploratory"]

_EVIDENCE_SCOPES = {"general-upper-limb", "golf-specific"}
_SOURCE_TYPES = {"primary-experiment"}
_MODALITIES = {"mechanical", "visual", "auditory"}
_LAYERS = {
    "perturbation-detection",
    "muscle-response",
    "mechanical-effect",
    "task-correction",
}
_EXPECTATIONS = {"unexpected", "cued-direction-unknown", "fully-predictable"}
_HIERARCHIES = {"primary", "secondary", "exploratory"}


def _require_text(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonblank")


def _require_finite(value: float, label: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")


def _require_unique(values: tuple[str, ...], label: str) -> None:
    if not values or len(set(values)) != len(values):
        raise ValueError(f"{label} must be nonempty and unique")


@dataclass(frozen=True)
class EvidenceSource:
    """One primary experiment with an explicit transport boundary."""

    source_id: str
    citation_key: str
    doi: str
    evidence_scope: EvidenceScope
    modality: Modality
    source_type: SourceType
    supports: str
    does_not_authorize: str

    def __post_init__(self) -> None:
        for value, label in (
            (self.source_id, "source ID"),
            (self.citation_key, "citation key"),
            (self.supports, "supported scope"),
            (self.does_not_authorize, "authority boundary"),
        ):
            _require_text(value, label)
        if not self.doi.startswith("10."):
            raise ValueError("DOI must use a registered 10. prefix")
        if self.evidence_scope not in _EVIDENCE_SCOPES:
            raise ValueError("evidence scope must be general-upper-limb or golf-specific")
        if self.modality not in _MODALITIES:
            raise ValueError("source modality is not supported")
        if self.source_type not in _SOURCE_TYPES:
            raise ValueError("source type must be primary-experiment")


@dataclass(frozen=True)
class PhaseDeclaration:
    """One event-bounded phase on the registered motion clock."""

    phase_id: str
    start_event: str
    end_event: str

    def __post_init__(self) -> None:
        _require_text(self.phase_id, "phase ID")
        _require_text(self.start_event, "phase start event")
        _require_text(self.end_event, "phase end event")
        if self.start_event == self.end_event:
            raise ValueError("phase events must be distinct")


@dataclass(frozen=True)
class ShamDeclaration:
    """One blinded control that omits the active perturbation component."""

    sham_id: str
    modality: Modality
    matched_features: str
    omitted_active_component: str
    blinded_code: str

    def __post_init__(self) -> None:
        for value, label in (
            (self.sham_id, "sham ID"),
            (self.matched_features, "matched sham features"),
            (self.omitted_active_component, "omitted sham component"),
            (self.blinded_code, "blinded sham code"),
        ):
            _require_text(value, label)
        if self.modality not in _MODALITIES:
            raise ValueError("sham modality is not supported")


@dataclass(frozen=True)
class SignalChannel:
    """One calibrated signal on the shared acquisition clock."""

    channel_id: str
    signal_type: Literal["command", "kinematic", "kinetic", "emg", "task"]
    units: str
    sample_rate_hz: float
    frame: str
    calibration_revision: str

    def __post_init__(self) -> None:
        for value, label in (
            (self.channel_id, "channel ID"),
            (self.units, "channel units"),
            (self.frame, "channel frame"),
            (self.calibration_revision, "channel calibration revision"),
        ):
            _require_text(value, label)
        if self.signal_type not in {"command", "kinematic", "kinetic", "emg", "task"}:
            raise ValueError("signal type is not supported")
        _require_finite(self.sample_rate_hz, "sample rate")
        if self.sample_rate_hz <= 0.0:
            raise ValueError("sample rate must be positive")


@dataclass(frozen=True)
class PerturbationDeclaration:
    """One phase-specific perturbation with a paired sham and stopping rule."""

    perturbation_id: str
    modality: Modality
    phase_id: str
    onset_event: str
    direction: str
    magnitude: float
    units: str
    duration_ms: float
    expectation: Expectation
    sham_id: str
    calibration_revision: str
    safety_stop: str

    def __post_init__(self) -> None:
        for value, label in (
            (self.perturbation_id, "perturbation ID"),
            (self.phase_id, "perturbation phase"),
            (self.onset_event, "perturbation onset event"),
            (self.direction, "perturbation direction"),
            (self.units, "perturbation units"),
            (self.sham_id, "perturbation sham ID"),
            (self.calibration_revision, "perturbation calibration revision"),
            (self.safety_stop, "perturbation safety stop"),
        ):
            _require_text(value, label)
        if self.modality not in _MODALITIES:
            raise ValueError("perturbation modality is not supported")
        if self.expectation not in _EXPECTATIONS:
            raise ValueError("expectation domain is not supported")
        _require_finite(self.magnitude, "perturbation magnitude")
        _require_finite(self.duration_ms, "perturbation duration")
        if self.magnitude <= 0.0 or self.duration_ms <= 0.0:
            raise ValueError("perturbation magnitude and duration must be positive")


@dataclass(frozen=True)
class ResponseWindow:
    """One operational analysis window, not a universal physiological constant."""

    window_id: str
    modality: Modality
    layer: TimingLayer
    start_ms: float
    end_ms: float
    onset_method: str
    metric: str

    def __post_init__(self) -> None:
        _require_text(self.window_id, "window ID")
        _require_text(self.onset_method, "window onset method")
        _require_text(self.metric, "window metric")
        if self.modality not in _MODALITIES or self.layer not in _LAYERS:
            raise ValueError("window modality or timing layer is not supported")
        _require_finite(self.start_ms, "window start")
        _require_finite(self.end_ms, "window end")
        if self.start_ms < 0.0 or self.end_ms <= self.start_ms:
            raise ValueError("response windows must have nonnegative increasing bounds")


@dataclass(frozen=True)
class SynchronizationContract:
    """Shared-clock and physical-onset calibration requirements."""

    clock_source: str
    calibration_record_id: str
    timestamp_resolution_ms: float
    maximum_channel_skew_ms: float
    onset_uncertainty_ms: float
    required_channel_ids: tuple[str, ...]
    photodiode_required: bool
    microphone_loopback_required: bool
    force_onset_required: bool

    def __post_init__(self) -> None:
        _require_text(self.clock_source, "clock source")
        _require_text(self.calibration_record_id, "synchronization calibration record")
        _require_unique(self.required_channel_ids, "synchronization channel IDs")
        for value, label in (
            (self.timestamp_resolution_ms, "timestamp resolution"),
            (self.maximum_channel_skew_ms, "maximum channel skew"),
            (self.onset_uncertainty_ms, "onset uncertainty"),
        ):
            _require_finite(value, label)
        if self.timestamp_resolution_ms <= 0.0:
            raise ValueError("timestamp resolution must be positive")
        if self.maximum_channel_skew_ms < 0.0 or self.onset_uncertainty_ms < 0.0:
            raise ValueError("timing uncertainties must be nonnegative")
        if not all(
            (self.photodiode_required, self.microphone_loopback_required, self.force_onset_required)
        ):
            raise ValueError("visual, auditory, and mechanical physical-onset checks are required")


@dataclass(frozen=True)
class Hypothesis:
    """One preregistered contrast in an explicit testing hierarchy."""

    hypothesis_id: str
    hierarchy: Hierarchy
    modality: Modality
    phase_id: str
    window_id: str
    metric: str
    contrast: str
    family_id: str
    decision_rule: str
    falsifier: str

    def __post_init__(self) -> None:
        for value, label in (
            (self.hypothesis_id, "hypothesis ID"),
            (self.phase_id, "hypothesis phase"),
            (self.window_id, "hypothesis window"),
            (self.metric, "hypothesis metric"),
            (self.contrast, "hypothesis contrast"),
            (self.family_id, "hypothesis family"),
            (self.decision_rule, "hypothesis decision rule"),
            (self.falsifier, "hypothesis falsifier"),
        ):
            _require_text(value, label)
        if self.hierarchy not in _HIERARCHIES or self.modality not in _MODALITIES:
            raise ValueError("hypothesis hierarchy or modality is not supported")


@dataclass(frozen=True)
class PowerPlan:
    """Preregistered effect and variance inputs without invented recruitment authority."""

    family_id: str
    family_alpha: float
    target_power: float
    minimum_effect: float
    effect_units: str
    variance_source: str
    calculation_revision: str
    multiplicity_method: Literal["holm-step-down"]
    participant_count: None = None

    def __post_init__(self) -> None:
        for value, label in (
            (self.family_id, "power family ID"),
            (self.effect_units, "minimum-effect units"),
            (self.variance_source, "variance source"),
            (self.calculation_revision, "power calculation revision"),
        ):
            _require_text(value, label)
        if not 0.0 < self.family_alpha <= 0.05 or not 0.0 < self.target_power < 1.0:
            raise ValueError("alpha and target power must lie in their declared domains")
        if not math.isfinite(self.minimum_effect) or self.minimum_effect <= 0.0:
            raise ValueError("minimum effect must be positive and finite")
        if self.multiplicity_method != "holm-step-down" or self.participant_count is not None:
            raise ValueError(
                "power plan must retain Holm control and unavailable participant count"
            )


@dataclass(frozen=True)
class HumanStudyBoundary:
    """Checked-in state that cannot authorize participant work."""

    status: Literal["unavailable"]
    participant_data_present: Literal[False]
    authorizes_participant_collection: Literal[False]

    def __post_init__(self) -> None:
        if (
            self.status != "unavailable"
            or self.participant_data_present is not False
            or self.authorizes_participant_collection is not False
        ):
            raise ValueError("software state must remain unavailable and non-authorizing")


def _protocol_ids(protocol: NeuralTimingProtocol) -> None:
    collections = (
        (tuple(item.source_id for item in protocol.sources), "source IDs"),
        (tuple(item.phase_id for item in protocol.phases), "phase IDs"),
        (tuple(item.sham_id for item in protocol.shams), "sham IDs"),
        (tuple(item.channel_id for item in protocol.channels), "channel IDs"),
        (tuple(item.perturbation_id for item in protocol.perturbations), "perturbation IDs"),
        (tuple(item.window_id for item in protocol.windows), "window IDs"),
        (tuple(item.hypothesis_id for item in protocol.hypotheses), "hypothesis IDs"),
        (tuple(item.family_id for item in protocol.power_plans), "power family IDs"),
    )
    for values, label in collections:
        _require_unique(values, label)


def _protocol_modalities(protocol: NeuralTimingProtocol) -> None:
    if {source.evidence_scope for source in protocol.sources} != _EVIDENCE_SCOPES:
        raise ValueError("sources must separate general upper-limb and golf-specific evidence")
    if {item.modality for item in protocol.perturbations} != _MODALITIES:
        raise ValueError("mechanical, visual, and auditory perturbations are required")
    pairs = [(item.modality, item.layer) for item in protocol.windows]
    expected = {(modality, layer) for modality in _MODALITIES for layer in _LAYERS}
    if set(pairs) != expected or len(pairs) != len(expected):
        raise ValueError("exactly one window is required for every modality and timing layer")


def _protocol_references(protocol: NeuralTimingProtocol) -> None:
    phases = {item.phase_id for item in protocol.phases}
    shams = {item.sham_id: item for item in protocol.shams}
    windows = {item.window_id: item for item in protocol.windows}
    families = {item.family_id for item in protocol.power_plans}
    channels = {item.channel_id for item in protocol.channels}
    if set(protocol.synchronization.required_channel_ids) != channels:
        raise ValueError("synchronization must cover every declared channel exactly")
    for perturbation in protocol.perturbations:
        if perturbation.phase_id not in phases or perturbation.sham_id not in shams:
            raise ValueError("perturbations must reference registered phases and shams")
        if shams[perturbation.sham_id].modality != perturbation.modality:
            raise ValueError("each perturbation and sham must use the same modality")
    for hypothesis in protocol.hypotheses:
        if hypothesis.phase_id not in phases or hypothesis.window_id not in windows:
            raise ValueError("hypotheses must reference registered phases and windows")
        if (
            hypothesis.family_id not in families
            or windows[hypothesis.window_id].modality != hypothesis.modality
        ):
            raise ValueError("hypotheses must join matching windows and power families")


@dataclass(frozen=True)
class NeuralTimingProtocol:
    """Complete bounded protocol for multimodal feedback perturbations."""

    protocol_id: str
    analysis_revision: str
    sources: tuple[EvidenceSource, ...]
    phases: tuple[PhaseDeclaration, ...]
    shams: tuple[ShamDeclaration, ...]
    channels: tuple[SignalChannel, ...]
    synchronization: SynchronizationContract
    perturbations: tuple[PerturbationDeclaration, ...]
    windows: tuple[ResponseWindow, ...]
    hypotheses: tuple[Hypothesis, ...]
    power_plans: tuple[PowerPlan, ...]
    history_model: str
    uncertainty_plan: str
    human_boundary: HumanStudyBoundary

    def __post_init__(self) -> None:
        _require_text(self.protocol_id, "protocol ID")
        _require_text(self.analysis_revision, "analysis revision")
        _require_text(self.history_model, "history model")
        _require_text(self.uncertainty_plan, "uncertainty plan")
        _protocol_ids(self)
        _protocol_modalities(self)
        _protocol_references(self)
