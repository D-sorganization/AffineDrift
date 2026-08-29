"""Deterministic analysis contracts for feedback-perturbation timing."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

Modality = Literal["mechanical", "visual", "auditory"]
TimingLayer = Literal[
    "perturbation-detection",
    "muscle-response",
    "mechanical-effect",
    "task-correction",
]
Outcome = Literal["supported", "negative", "null", "unavailable"]
EvidenceOrigin = Literal["synthetic-fixture", "measured-human", "unavailable"]
type FloatArray = NDArray[np.float64]

_MODALITIES = {"mechanical", "visual", "auditory"}
_LAYERS = {
    "perturbation-detection",
    "muscle-response",
    "mechanical-effect",
    "task-correction",
}
_OUTCOMES = {"supported", "negative", "null", "unavailable"}
_ORIGINS = {"synthetic-fixture", "measured-human", "unavailable"}


def _require_text(value: str, label: str) -> None:
    """Require a nonblank text field."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonblank")


@dataclass(frozen=True)
class EvidenceProvenance:
    """Machine-readable origin that blocks synthetic-to-measured promotion."""

    origin: EvidenceOrigin
    record_id: str
    revision: str
    synthetic: bool

    def __post_init__(self) -> None:
        """Validate origin, identity, revision, and synthetic status."""
        _require_text(self.record_id, "evidence record ID")
        _require_text(self.revision, "evidence revision")
        if self.origin not in _ORIGINS:
            raise ValueError("evidence origin is not supported")
        if (self.origin == "synthetic-fixture") != self.synthetic:
            raise ValueError("synthetic evidence must retain its synthetic marker")
        if self.origin == "unavailable" and self.synthetic:
            raise ValueError("unavailable evidence cannot be marked synthetic")

    @classmethod
    def unavailable(cls, record_id: str) -> EvidenceProvenance:
        """Create an unavailable provenance record with no synthetic marker."""
        return cls("unavailable", record_id, "unavailable", False)


@dataclass(frozen=True)
class LayerObservation:
    """One detected layer latency without a claim of unique pathway identity."""

    modality: Modality
    layer: TimingLayer
    latency_ms: float
    provenance: EvidenceProvenance

    def __post_init__(self) -> None:
        """Validate the declared modality, layer, and latency."""
        if self.modality not in _MODALITIES or self.layer not in _LAYERS:
            raise ValueError("observation modality or timing layer is not supported")
        if not math.isfinite(self.latency_ms) or self.latency_ms < 0.0:
            raise ValueError("observation latency must be finite and nonnegative")


@dataclass(frozen=True)
class OnsetEstimate:
    """First persistent threshold crossing on a calibrated time axis."""

    sample_index: int
    latency_ms: float


@dataclass(frozen=True)
class IntervalDecision:
    """One uncertainty-aware outcome with immutable evidence origin."""

    outcome: Outcome
    estimate: float | None
    lower: float | None
    upper: float | None
    minimum_effect: float
    provenance: EvidenceProvenance

    def __post_init__(self) -> None:
        """Validate interval completeness, provenance, and outcome consistency."""
        if (
            self.outcome not in _OUTCOMES
            or not math.isfinite(self.minimum_effect)
            or self.minimum_effect <= 0.0
        ):
            raise ValueError("decision outcome or minimum effect is invalid")
        values = (self.estimate, self.lower, self.upper)
        if self.outcome == "unavailable":
            if (
                any(value is not None for value in values)
                or self.provenance.origin != "unavailable"
            ):
                raise ValueError("unavailable decisions cannot contain numeric evidence")
            return
        if any(value is None or not math.isfinite(value) for value in values):
            raise ValueError("available decisions require finite estimate and interval")
        estimate = self.estimate
        lower = self.lower
        upper = self.upper
        if estimate is None or lower is None or upper is None:
            raise ValueError("available decisions require a complete interval")
        if not lower <= estimate <= upper or self.provenance.origin == "unavailable":
            raise ValueError("decision interval or evidence origin is inconsistent")
        if self.outcome != _classify_complete_interval(lower, upper, self.minimum_effect):
            raise ValueError("decision outcome contradicts its uncertainty bounds")


def _classify_complete_interval(lower: float, upper: float, minimum_effect: float) -> Outcome:
    """Classify one already-validated interval without duplicating decision rules."""
    if lower > minimum_effect or upper < -minimum_effect:
        return "supported"
    if lower >= -minimum_effect and upper <= minimum_effect:
        return "negative"
    return "null"


def detect_first_crossing(
    times_ms: FloatArray,
    signal: FloatArray,
    *,
    threshold: float,
    persistence_samples: int,
) -> OnsetEstimate:
    """Detect the first persistent absolute threshold crossing."""
    times = np.asarray(times_ms, dtype=float)
    values = np.asarray(signal, dtype=float)
    if times.ndim != 1 or values.ndim != 1 or times.shape != values.shape or times.size == 0:
        raise ValueError("time and signal must be aligned nonempty vectors")
    if not np.all(np.isfinite(times)) or not np.all(np.isfinite(values)):
        raise ValueError("time and signal must be finite")
    if np.any(np.diff(times) <= 0.0):
        raise ValueError("time must be strictly increasing")
    if not math.isfinite(threshold) or threshold <= 0.0 or persistence_samples < 1:
        raise ValueError("threshold and persistence must be positive")
    if persistence_samples > values.size:
        raise ValueError("persistence cannot exceed trace length")
    crossings = (np.abs(values) >= threshold).astype(int)
    persistent = np.convolve(crossings, np.ones(persistence_samples, dtype=int), mode="valid")
    candidates = np.flatnonzero(persistent == persistence_samples)
    if candidates.size == 0:
        raise ValueError("no persistent crossing was detected")
    index = int(candidates[0])
    return OnsetEstimate(index, float(times[index]))


def holm_step_down(p_values: tuple[float, ...], *, family_alpha: float) -> tuple[bool, ...]:
    """Return Holm step-down rejection decisions in original hypothesis order."""
    if not p_values or not 0.0 < family_alpha <= 0.05:
        raise ValueError("a nonempty p-value family and valid alpha are required")
    if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in p_values):
        raise ValueError("p-values must be finite and lie in [0, 1]")
    ordered = sorted(enumerate(p_values), key=lambda item: item[1])
    decisions = [False] * len(p_values)
    for rank, (original_index, value) in enumerate(ordered):
        threshold = family_alpha / (len(p_values) - rank)
        if value > threshold:
            break
        decisions[original_index] = True
    return tuple(decisions)


def classify_interval(
    lower: float | None,
    upper: float | None,
    minimum_effect: float,
    provenance: EvidenceProvenance,
) -> IntervalDecision:
    """Classify an interval as supported, negative, null, or unavailable."""
    if not math.isfinite(minimum_effect) or minimum_effect <= 0.0:
        raise ValueError("minimum effect must be positive and finite")
    if lower is None or upper is None:
        if lower is not None or upper is not None:
            raise ValueError("interval bounds must be jointly available")
        return IntervalDecision("unavailable", None, None, None, minimum_effect, provenance)
    if not math.isfinite(lower) or not math.isfinite(upper) or lower > upper:
        raise ValueError("interval bounds must be finite and ordered")
    estimate = 0.5 * (lower + upper)
    outcome = _classify_complete_interval(lower, upper, minimum_effect)
    return IntervalDecision(outcome, estimate, lower, upper, minimum_effect, provenance)
