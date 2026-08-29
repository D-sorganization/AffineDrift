"""Fail-closed contracts for active impedance identification.

The module validates declarations and deterministic regression matrices. It
does not control a perturbation device, estimate muscle force, partition neural
strategy, or authorize participant collection.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from src.affine_control.impedance_evidence import HumanStudyGate

type FloatArray = NDArray[np.float64]
SourceType = Literal["primary-literature", "measurement-standard"]
WindowType = Literal["baseline", "early-response", "late-response"]
Side = Literal["lead", "trail"]
OutputQuantity = Literal["endpoint-wrench", "joint-torque"]
AdverseOutcome = Literal["negative", "null", "unavailable"]

PARAMETER_NAMES = ("inertia", "damping", "stiffness", "reflex_gain", "voluntary_basis")
WINDOW_TYPES = ("baseline", "early-response", "late-response")
_SOURCE_TYPES = ("primary-literature", "measurement-standard")
_SIDES = ("lead", "trail")
_OUTPUT_QUANTITIES = ("endpoint-wrench", "joint-torque")
_ADVERSE_OUTCOMES = ("negative", "null", "unavailable")


def _require_text(value: str, label: str) -> None:
    """Reject a blank declaration."""
    if not value.strip():
        raise ValueError(f"{label} must be declared")


def _require_texts(values: tuple[str, ...], label: str) -> None:
    """Reject an empty tuple or blank member."""
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must be declared")


def _finite_positive(values: tuple[float, ...], label: str) -> None:
    """Require finite, strictly positive numerical limits."""
    if not all(isfinite(value) and value > 0.0 for value in values):
        raise ValueError(f"{label} must be finite and positive")


@dataclass(frozen=True)
class EvidenceSource:
    """One primary or measurement-standard source and its authority limit."""

    source_id: str
    source_type: SourceType
    citation: str
    supports: str
    limitation: str

    def __post_init__(self) -> None:
        """Require complete source provenance and a valid runtime domain."""
        if self.source_type not in _SOURCE_TYPES:
            raise ValueError("source type must be primary-literature or measurement-standard")
        for value, label in (
            (self.source_id, "source_id"),
            (self.citation, "citation"),
            (self.supports, "source support"),
            (self.limitation, "source limitation"),
        ):
            _require_text(value, label)


@dataclass(frozen=True)
class SafetyEnvelope:
    """Declared perturbation device, trigger, limits, and stop controls."""

    device_id: str
    device_revision: str
    control_mode: str
    trigger_source: str
    trigger_tolerance_ms: float
    maximum_displacement_rad: float
    maximum_velocity_rad_s: float
    maximum_torque_nm: float
    hardware_stop: str
    operator_stop: str
    preflight_checks: tuple[str, ...]
    stopping_rules: tuple[str, ...]

    def __post_init__(self) -> None:
        """Reject an incomplete or nonpositive safety declaration."""
        for value, label in (
            (self.device_id, "device_id"),
            (self.device_revision, "device revision"),
            (self.control_mode, "control mode"),
            (self.trigger_source, "trigger source"),
            (self.hardware_stop, "hardware stop"),
            (self.operator_stop, "operator stop"),
        ):
            _require_text(value, label)
        _finite_positive(
            (
                self.trigger_tolerance_ms,
                self.maximum_displacement_rad,
                self.maximum_velocity_rad_s,
                self.maximum_torque_nm,
            ),
            "safety limits",
        )
        _require_texts(self.preflight_checks, "preflight checks")
        _require_texts(self.stopping_rules, "stopping rules")


@dataclass(frozen=True)
class ResponseWindow:
    """Operational time window that does not itself identify physiology."""

    window_type: WindowType
    start_ms: float
    end_ms: float
    reportable_quantities: tuple[str, ...]
    interpretation_limit: str

    def __post_init__(self) -> None:
        """Require a valid runtime label and finite ordered bounds."""
        if self.window_type not in WINDOW_TYPES:
            raise ValueError("response window type is not declared")
        if not all(isfinite(value) for value in (self.start_ms, self.end_ms)):
            raise ValueError("response-window bounds must be finite")
        if self.start_ms >= self.end_ms:
            raise ValueError("response-window start must precede its end")
        _require_texts(self.reportable_quantities, "reportable quantities")
        _require_text(self.interpretation_limit, "window interpretation limit")


@dataclass(frozen=True)
class PhaseDeclaration:
    """One event-triggered phase with an ordered operational window set."""

    phase_id: str
    event_trigger: str
    perturbation_offset_ms: float
    windows: tuple[ResponseWindow, ...]

    def __post_init__(self) -> None:
        """Require baseline, early, and late windows without overlap."""
        _require_text(self.phase_id, "phase_id")
        _require_text(self.event_trigger, "event trigger")
        if not isfinite(self.perturbation_offset_ms):
            raise ValueError("perturbation offset must be finite")
        if tuple(window.window_type for window in self.windows) != WINDOW_TYPES:
            raise ValueError("each phase must declare baseline, early, and late windows")
        pairs = zip(self.windows, self.windows[1:], strict=False)
        if any(earlier.end_ms > later.start_ms for earlier, later in pairs):
            raise ValueError("response windows must be ordered and nonoverlapping")


@dataclass(frozen=True)
class EmgChannel:
    """One revisioned EMG channel and its processing uncertainty."""

    channel_id: str
    muscle_label: str
    side: Side
    electrode_location: str
    electrode_orientation: str
    interelectrode_distance_mm: float
    sample_rate_hz: float
    highpass_hz: float
    lowpass_hz: float
    normalization_method: str
    electromechanical_delay_ms: float
    delay_uncertainty_ms: float
    crosstalk_check: str
    electrode_revision: str

    def __post_init__(self) -> None:
        """Reject ambiguous placement, filtering, or latency declarations."""
        if self.side not in _SIDES:
            raise ValueError("EMG side must be lead or trail")
        for value, label in (
            (self.channel_id, "EMG channel_id"),
            (self.muscle_label, "muscle label"),
            (self.electrode_location, "electrode location"),
            (self.electrode_orientation, "electrode orientation"),
            (self.normalization_method, "normalization method"),
            (self.crosstalk_check, "crosstalk check"),
            (self.electrode_revision, "electrode revision"),
        ):
            _require_text(value, label)
        _finite_positive(
            (
                self.interelectrode_distance_mm,
                self.sample_rate_hz,
                self.highpass_hz,
                self.lowpass_hz,
                self.electromechanical_delay_ms,
                self.delay_uncertainty_ms,
            ),
            "EMG acquisition limits",
        )
        if self.highpass_hz >= self.lowpass_hz:
            raise ValueError("EMG high-pass frequency must be below the low-pass frequency")
        if self.sample_rate_hz <= 2.0 * self.lowpass_hz:
            raise ValueError("EMG sample rate must exceed the declared Nyquist limit")


@dataclass(frozen=True)
class IdentificationModel:
    """One model-conditioned endpoint or joint impedance declaration."""

    model_id: str
    output_quantity: OutputQuantity
    coordinate_frame: str
    perturbation_unit: str
    response_unit: str
    parameter_names: tuple[str, ...]
    reflex_delay_ms: float
    jacobian_assumption: str
    solver: str
    rank_tolerance: float
    maximum_condition_number: float
    residual_metric: str

    def __post_init__(self) -> None:
        """Require fixed coordinates, parameters, delays, and numerical gates."""
        if self.output_quantity not in _OUTPUT_QUANTITIES:
            raise ValueError("output quantity must be endpoint-wrench or joint-torque")
        for value, label in (
            (self.model_id, "model_id"),
            (self.coordinate_frame, "coordinate frame"),
            (self.perturbation_unit, "perturbation unit"),
            (self.response_unit, "response unit"),
            (self.jacobian_assumption, "Jacobian assumption"),
            (self.solver, "solver"),
            (self.residual_metric, "residual metric"),
        ):
            _require_text(value, label)
        if self.parameter_names != PARAMETER_NAMES:
            raise ValueError("model parameters must follow the frozen identification order")
        _finite_positive(
            (self.reflex_delay_ms, self.rank_tolerance, self.maximum_condition_number),
            "identification limits",
        )


@dataclass(frozen=True)
class Hypothesis:
    """Predeclared metric, decision rule, falsifier, and adverse outcome."""

    hypothesis_id: str
    quantity: str
    metric: str
    decision_rule: str
    falsifier: str
    outcome_if_not_supported: AdverseOutcome

    def __post_init__(self) -> None:
        """Require a valid adverse domain and complete testable declaration."""
        if self.outcome_if_not_supported not in _ADVERSE_OUTCOMES:
            raise ValueError("adverse outcome must be negative, null, or unavailable")
        for value, label in (
            (self.hypothesis_id, "hypothesis_id"),
            (self.quantity, "hypothesis quantity"),
            (self.metric, "hypothesis metric"),
            (self.decision_rule, "decision rule"),
            (self.falsifier, "falsifier"),
        ):
            _require_text(value, label)


@dataclass(frozen=True)
class ImpedanceProtocol:
    """Complete source, safety, signal, model, and governance contract."""

    protocol_id: str
    sources: tuple[EvidenceSource, ...]
    safety: SafetyEnvelope
    phases: tuple[PhaseDeclaration, ...]
    emg_channels: tuple[EmgChannel, ...]
    models: tuple[IdentificationModel, ...]
    hypotheses: tuple[Hypothesis, ...]
    uncertainty_method: str
    reliability_metric: str
    human_gate: HumanStudyGate

    def __post_init__(self) -> None:
        """Fail closed on duplicate records or incompatible model outputs."""
        _require_text(self.protocol_id, "protocol_id")
        _require_text(self.uncertainty_method, "uncertainty method")
        _require_text(self.reliability_metric, "reliability metric")
        collections = (
            (tuple(source.source_id for source in self.sources), "source IDs"),
            (tuple(phase.phase_id for phase in self.phases), "phase IDs"),
            (tuple(channel.channel_id for channel in self.emg_channels), "EMG channel IDs"),
            (tuple(model.model_id for model in self.models), "model IDs"),
            (tuple(item.hypothesis_id for item in self.hypotheses), "hypothesis IDs"),
        )
        for values, label in collections:
            if not values or len(set(values)) != len(values):
                raise ValueError(f"{label} must be nonempty and unique")
        if {model.output_quantity for model in self.models} != set(_OUTPUT_QUANTITIES):
            raise ValueError("exactly one endpoint and joint identification model are required")


@dataclass(frozen=True)
class IdentifiabilityReport:
    """Rank, nullity, conditioning, and qualification of a design matrix."""

    observations: int
    parameters: int
    rank: int
    nullity: int
    condition_number: float
    identifiable: bool


@dataclass(frozen=True)
class ImpedanceFit:
    """Exact synthetic fit with an explicit model-conditioned evidence tier."""

    estimates: tuple[float, ...]
    residual_rms: float
    output_quantity: OutputQuantity
    evidence_tier: Literal["model-partitioned"] = "model-partitioned"


def assess_identifiability(
    design: FloatArray,
    maximum_condition_number: float,
) -> IdentifiabilityReport:
    """Assess structural rank and numerical conditioning of a design matrix."""
    matrix = np.asarray(design, dtype=float)
    if matrix.ndim != 2 or matrix.size == 0 or not np.all(np.isfinite(matrix)):
        raise ValueError("design matrix must be finite, nonempty, and two-dimensional")
    _finite_positive((maximum_condition_number,), "maximum condition number")
    observations, parameters = matrix.shape
    rank = int(np.linalg.matrix_rank(matrix))
    condition = float(np.linalg.cond(matrix))
    qualified = rank == parameters and condition <= maximum_condition_number
    return IdentifiabilityReport(
        observations,
        parameters,
        rank,
        parameters - rank,
        condition,
        qualified,
    )


def fit_impedance(
    model: IdentificationModel,
    design: FloatArray,
    response: FloatArray,
) -> ImpedanceFit:
    """Fit a qualified synthetic linear model or fail closed."""
    matrix = np.asarray(design, dtype=float)
    output = np.asarray(response, dtype=float)
    if output.ndim != 1 or not np.all(np.isfinite(output)):
        raise ValueError("response must be a finite vector")
    expected_shape = (output.size, len(model.parameter_names))
    if matrix.shape != expected_shape:
        raise ValueError("design and response must align with the declared parameters")
    report = assess_identifiability(matrix, model.maximum_condition_number)
    if not report.identifiable:
        raise ValueError("design is not identifiable under the declared conditioning gate")
    estimates, _, _, _ = np.linalg.lstsq(matrix, output, rcond=model.rank_tolerance)
    residual = output - matrix @ estimates
    residual_rms = float(np.sqrt(np.mean(np.square(residual))))
    return ImpedanceFit(
        tuple(float(value) for value in estimates),
        residual_rms,
        model.output_quantity,
    )


def co_contraction_proxy(agonist: FloatArray, antagonist: FloatArray) -> float:
    """Return a symmetric EMG-envelope overlap proxy in [0, 1]."""
    first = np.asarray(agonist, dtype=float)
    second = np.asarray(antagonist, dtype=float)
    if first.ndim != 1 or first.shape != second.shape or first.size == 0:
        raise ValueError("EMG proxy inputs must be nonempty aligned vectors")
    if not np.all(np.isfinite(first)) or not np.all(np.isfinite(second)):
        raise ValueError("EMG proxy inputs must be finite")
    if np.any(first < 0.0) or np.any(second < 0.0):
        raise ValueError("EMG proxy inputs must be nonnegative envelopes")
    denominator = first + second
    samples = np.divide(
        2.0 * np.minimum(first, second),
        denominator,
        out=np.zeros_like(denominator),
        where=denominator > 0.0,
    )
    return float(np.mean(samples))
