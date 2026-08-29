"""Fail-closed contracts for bilateral hand-wrench identification.

The module qualifies declarations and deterministic fixtures. It does not
implement inverse dynamics, infer anatomy, or authorize human data collection.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

import numpy as np
from numpy.typing import NDArray

Hand = Literal["lead", "trail"]
FloatArray = NDArray[np.float64]

_WRENCH_SIZE = 6


def _require_text(value: str, label: str) -> None:
    """Reject a blank declaration."""
    if not value.strip():
        raise ValueError(f"{label} must be declared")


def _require_texts(values: tuple[str, ...], label: str) -> None:
    """Reject an empty or blank tuple declaration."""
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must be declared")


def _as_finite_vector(values: FloatArray, size: int, label: str) -> FloatArray:
    """Return a finite one-dimensional vector with a fixed size."""
    vector = np.asarray(values, dtype=float)
    if vector.shape != (size,) or not np.all(np.isfinite(vector)):
        raise ValueError(f"{label} must be a finite {size}-component vector")
    return vector


def _as_matrix(values: tuple[tuple[float, ...], ...], shape: tuple[int, int]) -> FloatArray:
    """Return a finite matrix with a fixed shape."""
    matrix = np.asarray(values, dtype=float)
    if matrix.shape != shape or not np.all(np.isfinite(matrix)):
        raise ValueError(f"matrix must be finite with shape {shape}")
    return matrix


@dataclass(frozen=True)
class SourceRecord:
    """One primary or immutable executable source and its authority limit."""

    source_id: str
    source_type: Literal["primary-literature", "immutable-executable"]
    citation: str
    supports: str
    limitation: str

    def __post_init__(self) -> None:
        """Require complete source provenance and scope."""
        for value, label in (
            (self.source_id, "source_id"),
            (self.citation, "citation"),
            (self.supports, "source support"),
            (self.limitation, "source limitation"),
        ):
            _require_text(value, label)


@dataclass(frozen=True)
class SensorCalibration:
    """Declared six-axis calibration and dynamic acquisition envelope."""

    sensor_id: str
    hand: Hand
    output_frame: str
    calibration_matrix: tuple[tuple[float, ...], ...]
    sample_rate_hz: float
    bandwidth_hz: float
    maximum_passband_gain_error: float
    maximum_condition_number: float
    traceability: str
    revision: str

    def __post_init__(self) -> None:
        """Reject incomplete, singular, or aliased calibration declarations."""
        for value, label in (
            (self.sensor_id, "sensor_id"),
            (self.output_frame, "output frame"),
            (self.traceability, "traceability"),
            (self.revision, "calibration revision"),
        ):
            _require_text(value, label)
        matrix = _as_matrix(self.calibration_matrix, (_WRENCH_SIZE, _WRENCH_SIZE))
        if np.linalg.matrix_rank(matrix) != _WRENCH_SIZE:
            raise ValueError("calibration matrix must have full rank")
        numeric = (
            self.sample_rate_hz,
            self.bandwidth_hz,
            self.maximum_passband_gain_error,
            self.maximum_condition_number,
        )
        if not all(isfinite(value) and value > 0.0 for value in numeric):
            raise ValueError("calibration limits must be finite and positive")
        if self.sample_rate_hz <= 2.0 * self.bandwidth_hz:
            raise ValueError("sample rate must exceed the declared Nyquist limit")
        if self.condition_number > self.maximum_condition_number:
            raise ValueError("calibration condition number exceeds the declared maximum")

    @property
    def matrix(self) -> FloatArray:
        """Return the declared calibration matrix."""
        return np.asarray(self.calibration_matrix, dtype=float)

    @property
    def matrix_rank(self) -> int:
        """Return the structural rank of the calibration matrix."""
        return int(np.linalg.matrix_rank(self.matrix))

    @property
    def condition_number(self) -> float:
        """Return the numerical two-norm condition number."""
        return float(np.linalg.cond(self.matrix))


@dataclass(frozen=True)
class BandwidthSample:
    """Measured or manufactured gain at one excitation frequency."""

    frequency_hz: float
    gain_ratio: float

    def __post_init__(self) -> None:
        """Require finite nonnegative frequency and gain."""
        if not isfinite(self.frequency_hz) or self.frequency_hz < 0.0:
            raise ValueError("frequency must be finite and nonnegative")
        if not isfinite(self.gain_ratio) or self.gain_ratio < 0.0:
            raise ValueError("gain must be finite and nonnegative")


@dataclass(frozen=True)
class WrenchTransform:
    """Rigid transform from one sensor frame to the declared club frame."""

    source_frame: str
    target_frame: str
    rotation: tuple[tuple[float, ...], ...]
    target_to_source_origin_m: tuple[float, float, float]

    def __post_init__(self) -> None:
        """Require a proper orthonormal rotation and finite lever arm."""
        _require_text(self.source_frame, "source frame")
        _require_text(self.target_frame, "target frame")
        rotation = _as_matrix(self.rotation, (3, 3))
        translation = np.asarray(self.target_to_source_origin_m, dtype=float)
        if translation.shape != (3,) or not np.all(np.isfinite(translation)):
            raise ValueError("frame translation must be a finite three-vector")
        if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1.0e-12):
            raise ValueError("frame rotation must be orthonormal")
        if not np.isclose(np.linalg.det(rotation), 1.0, atol=1.0e-12):
            raise ValueError("frame rotation must be proper")


@dataclass(frozen=True)
class AnalysisContract:
    """Frozen synchronization, compensation, contact, and split declarations."""

    analysis_window: str
    synchronization_tolerance_s: float
    inertial_compensation: str
    contact_assumptions: tuple[str, ...]
    exclusion_rules: tuple[str, ...]
    uncertainty_method: str
    participant_split: str
    shaft_sensitivity: str
    grip_sensitivity: str

    def __post_init__(self) -> None:
        """Require all acquisition and inference assumptions."""
        for value, label in (
            (self.analysis_window, "analysis window"),
            (self.inertial_compensation, "inertial compensation"),
            (self.uncertainty_method, "uncertainty method"),
            (self.participant_split, "participant split"),
            (self.shaft_sensitivity, "shaft sensitivity"),
            (self.grip_sensitivity, "grip sensitivity"),
        ):
            _require_text(value, label)
        _require_texts(self.contact_assumptions, "contact assumptions")
        _require_texts(self.exclusion_rules, "exclusion rules")
        if not isfinite(self.synchronization_tolerance_s):
            raise ValueError("synchronization tolerance must be finite")
        if self.synchronization_tolerance_s <= 0.0:
            raise ValueError("synchronization tolerance must be positive")
        if self.participant_split != "participant-held-out":
            raise ValueError("human analysis must be participant-held-out")

    def qualifies_sync_offset(self, absolute_offset_s: float) -> bool:
        """Return whether an absolute timestamp offset meets the frozen limit."""
        if not isfinite(absolute_offset_s) or absolute_offset_s < 0.0:
            raise ValueError("synchronization offset must be finite and nonnegative")
        return absolute_offset_s <= self.synchronization_tolerance_s


@dataclass(frozen=True)
class Hypothesis:
    """Predeclared hypothesis, metric, falsifier, and adverse disposition."""

    hypothesis_id: str
    quantity: str
    metric: str
    decision_rule: str
    falsifier: str
    outcome_if_not_supported: Literal["negative", "null", "unavailable"]

    def __post_init__(self) -> None:
        """Require a testable, non-promotional hypothesis."""
        for value, label in (
            (self.hypothesis_id, "hypothesis_id"),
            (self.quantity, "hypothesis quantity"),
            (self.metric, "hypothesis metric"),
            (self.decision_rule, "decision rule"),
            (self.falsifier, "falsifier"),
        ):
            _require_text(value, label)


@dataclass(frozen=True)
class Preregistration:
    """Complete source, instrumentation, analysis, and hypothesis contract."""

    protocol_id: str
    sources: tuple[SourceRecord, ...]
    sensors: tuple[SensorCalibration, ...]
    frames: tuple[WrenchTransform, ...]
    analysis: AnalysisContract
    hypotheses: tuple[Hypothesis, ...]

    def __post_init__(self) -> None:
        """Reject duplicate or incomplete preregistration records."""
        _require_text(self.protocol_id, "protocol_id")
        collections = (
            (tuple(source.source_id for source in self.sources), "source"),
            (tuple(sensor.hand for sensor in self.sensors), "sensor hand"),
            (tuple(frame.source_frame for frame in self.frames), "frame"),
            (tuple(item.hypothesis_id for item in self.hypotheses), "hypothesis"),
        )
        for values, label in collections:
            if not values or len(set(values)) != len(values):
                raise ValueError(f"{label} records must be nonempty and unique")
        if set(sensor.hand for sensor in self.sensors) != {"lead", "trail"}:
            raise ValueError("exactly one lead and one trail calibration are required")


@dataclass(frozen=True)
class IdentifiabilityReport:
    """Rank and nullity of one declared linear observation map."""

    observations: int
    unknowns: int
    rank: int
    nullity: int
    identifiable: bool


def total_wrench_map() -> FloatArray:
    """Map two six-axis hand wrenches to one total club wrench."""
    return np.hstack((np.eye(_WRENCH_SIZE), np.eye(_WRENCH_SIZE)))


def bilateral_sensor_map() -> FloatArray:
    """Return the direct observation map for two independent six-axis sensors."""
    return np.eye(2 * _WRENCH_SIZE)


def point_force_wrench_map(lead_position: FloatArray, trail_position: FloatArray) -> FloatArray:
    """Map two point forces to total force and moment about the club origin."""
    lead = _as_finite_vector(lead_position, 3, "lead position")
    trail = _as_finite_vector(trail_position, 3, "trail position")
    return np.block([[np.eye(3), np.eye(3)], [_skew(lead), _skew(trail)]])


def _skew(vector: FloatArray) -> FloatArray:
    """Return the cross-product matrix for a three-vector."""
    first, second, third = vector
    return np.array([[0.0, -third, second], [third, 0.0, -first], [-second, first, 0.0]])


def assess_identifiability(mapping: FloatArray) -> IdentifiabilityReport:
    """Report structural rank and nullity for a finite linear observation map."""
    matrix = np.asarray(mapping, dtype=float)
    if matrix.ndim != 2 or not np.all(np.isfinite(matrix)) or matrix.size == 0:
        raise ValueError("observation map must be a finite nonempty matrix")
    rank = int(np.linalg.matrix_rank(matrix))
    observations, unknowns = matrix.shape
    return IdentifiabilityReport(observations, unknowns, rank, unknowns - rank, rank == unknowns)


def compatible_bilateral_allocations(
    total_wrench: FloatArray,
) -> tuple[tuple[FloatArray, FloatArray], ...]:
    """Return two exact bilateral allocations with the same total wrench."""
    total = _as_finite_vector(total_wrench, _WRENCH_SIZE, "total wrench")
    internal = np.array([3.0, -2.0, 1.0, 0.4, -0.3, 0.2])
    return ((0.5 * total, 0.5 * total), (0.5 * total + internal, 0.5 * total - internal))


def calibrate_wrench(raw_signal: FloatArray, calibration: SensorCalibration) -> FloatArray:
    """Recover a six-axis sensor wrench within the declared calibration model."""
    raw = _as_finite_vector(raw_signal, _WRENCH_SIZE, "raw sensor signal")
    return np.linalg.solve(calibration.matrix, raw)


def qualify_bandwidth(
    calibration: SensorCalibration,
    samples: tuple[BandwidthSample, ...],
) -> bool:
    """Evaluate passband gain evidence through the declared bandwidth boundary."""
    if not samples:
        raise ValueError("bandwidth samples must be declared")
    frequencies = tuple(sample.frequency_hz for sample in samples)
    if any(later <= earlier for earlier, later in zip(frequencies, frequencies[1:], strict=False)):
        raise ValueError("bandwidth sample frequencies must be strictly increasing")
    if not np.isclose(frequencies[-1], calibration.bandwidth_hz):
        raise ValueError("samples must include the declared bandwidth boundary")
    return all(
        abs(sample.gain_ratio - 1.0) <= calibration.maximum_passband_gain_error
        for sample in samples
    )


def transform_wrench(wrench: FloatArray, transform: WrenchTransform) -> FloatArray:
    """Transport a force-moment wrench from sensor coordinates to club coordinates."""
    source = _as_finite_vector(wrench, _WRENCH_SIZE, "wrench")
    rotation = np.asarray(transform.rotation, dtype=float)
    lever = np.asarray(transform.target_to_source_origin_m, dtype=float)
    force = rotation @ source[:3]
    moment = rotation @ source[3:] + np.cross(lever, force)
    return np.concatenate((force, moment))


def inertial_compensate(
    measured_wrench: FloatArray,
    inertial_wrench: FloatArray | None,
) -> FloatArray:
    """Subtract a declared instrument/club inertial wrench from the measurement."""
    measured = _as_finite_vector(measured_wrench, _WRENCH_SIZE, "measured wrench")
    if inertial_wrench is None:
        raise ValueError("inertial wrench is required for compensation")
    inertial = _as_finite_vector(inertial_wrench, _WRENCH_SIZE, "inertial wrench")
    return measured - inertial
