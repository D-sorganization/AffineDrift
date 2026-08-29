"""Governed EMG channel-pair and co-contraction-proxy contracts."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

import numpy as np
from numpy.typing import NDArray

type FloatArray = NDArray[np.float64]
Side = Literal["lead", "trail"]
CciFamily = Literal["amplitude-driven"]
FormulaId = Literal["symmetric-envelope-overlap-v1"]
ComparisonScope = Literal["within-formula-relative-trends-only"]

_SIDES = ("lead", "trail")
_CCI_FAMILIES = ("amplitude-driven",)
_FORMULAS = ("symmetric-envelope-overlap-v1",)
_COMPARISON_SCOPES = ("within-formula-relative-trends-only",)


def _require_text(value: str, label: str) -> None:
    """Reject a blank EMG declaration."""
    if not value.strip():
        raise ValueError(f"{label} must be declared")


def _finite_positive(values: tuple[float, ...], label: str) -> None:
    """Require finite, positive acquisition values."""
    if not all(isfinite(value) and value > 0.0 for value in values):
        raise ValueError(f"{label} must be finite and positive")


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
class EmgPairDeclaration:
    """Governed agonist/antagonist pairing and one frozen proxy definition."""

    pair_id: str
    agonist_channel_id: str
    antagonist_channel_id: str
    side: Side
    normalization_revision: str
    cci_family: CciFamily
    formula_id: FormulaId
    comparison_scope: ComparisonScope
    sensitivity_plan: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate roles, runtime domains, formula, and comparison boundary."""
        for value, label in (
            (self.pair_id, "EMG pair_id"),
            (self.agonist_channel_id, "agonist channel ID"),
            (self.antagonist_channel_id, "antagonist channel ID"),
            (self.normalization_revision, "normalization revision"),
        ):
            _require_text(value, label)
        if self.agonist_channel_id == self.antagonist_channel_id:
            raise ValueError("agonist and antagonist channel IDs must be distinct")
        if self.side not in _SIDES:
            raise ValueError("EMG pair side must be lead or trail")
        domains_valid = (
            self.cci_family in _CCI_FAMILIES
            and self.formula_id in _FORMULAS
            and self.comparison_scope in _COMPARISON_SCOPES
        )
        if not domains_valid:
            raise ValueError("CCI family, formula, and comparison scope must be declared")
        if not self.sensitivity_plan or any(not item.strip() for item in self.sensitivity_plan):
            raise ValueError("CCI sensitivity plan must be declared")


@dataclass(frozen=True)
class EmgEnvelopePair:
    """Processed envelopes carrying exact channel-role identifiers."""

    agonist_channel_id: str
    antagonist_channel_id: str
    agonist: FloatArray
    antagonist: FloatArray


def co_contraction_proxy(
    declaration: EmgPairDeclaration,
    envelopes: EmgEnvelopePair,
) -> float:
    """Evaluate the declared amplitude-driven overlap formula within one pair."""
    declared_ids = (declaration.agonist_channel_id, declaration.antagonist_channel_id)
    observed_ids = (envelopes.agonist_channel_id, envelopes.antagonist_channel_id)
    if observed_ids != declared_ids:
        raise ValueError("envelope channel IDs must match the declared agonist/antagonist roles")
    first = np.asarray(envelopes.agonist, dtype=float)
    second = np.asarray(envelopes.antagonist, dtype=float)
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
