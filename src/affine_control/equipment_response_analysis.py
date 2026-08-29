"""Fail-closed qualification and hierarchical equipment-response summaries."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import fmean, variance

from src.affine_control.equipment_response_protocol import (
    EquipmentResponseProtocol,
    ResponseObservation,
    ResultStatus,
)


@dataclass(frozen=True)
class ParticipantQualification:
    participant_id: str
    status: str
    reason: str


@dataclass(frozen=True)
class QualificationResult:
    complete: bool
    retained_observation_count: int
    unavailable_participant_ids: tuple[str, ...]
    participant_records: tuple[ParticipantQualification, ...]


@dataclass(frozen=True)
class ParticipantResponse:
    participant_id: str
    status: ResultStatus
    raw_effect: float | None
    shrunken_effect: float | None
    interval: tuple[float, float] | None
    stable_across_cycles: bool
    origin: str
    authorized_guidance: str = "unavailable"

    @property
    def interval_width(self) -> float:
        if self.interval is None:
            return 0.0
        return self.interval[1] - self.interval[0]


@dataclass(frozen=True)
class GroupResponse:
    mean_effect: float
    between_participant_variance: float
    interpretation: str


@dataclass(frozen=True)
class EquipmentResponseAnalysis:
    participants: tuple[ParticipantResponse, ...]
    group: GroupResponse
    global_recommendation: None = None


def qualify_observations(
    protocol: EquipmentResponseProtocol,
    observations: tuple[ResponseObservation, ...],
) -> QualificationResult:
    """Retain every record while making incomplete or contaminated cells unavailable."""
    ids = tuple(row.observation_id for row in observations)
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate observation ID")
    _require_complete_cells(protocol, observations)
    records = tuple(
        _qualify_participant(protocol, participant, observations)
        for participant, _ in protocol.randomization.assignments
    )
    unavailable = tuple(row.participant_id for row in records if row.status == "unavailable")
    return QualificationResult(True, len(observations), unavailable, records)


def _require_complete_cells(
    protocol: EquipmentResponseProtocol,
    observations: tuple[ResponseObservation, ...],
) -> None:
    expected = {
        (participant, cycle, condition.condition_id, trial)
        for participant, _ in protocol.randomization.assignments
        for cycle in range(1, protocol.randomization.cycles_per_participant + 1)
        for condition in protocol.conditions
        for trial in range(1, protocol.randomization.trials_per_condition_per_cycle + 1)
    }
    actual = {(row.participant_id, row.cycle, row.condition_id, row.trial) for row in observations}
    if actual != expected or len(observations) != len(expected):
        raise ValueError("observations must provide complete participant-cycle-condition cells")


def _qualify_participant(
    protocol: EquipmentResponseProtocol,
    participant_id: str,
    observations: tuple[ResponseObservation, ...],
) -> ParticipantQualification:
    rows = tuple(row for row in observations if row.participant_id == participant_id)
    if max(row.carryover_residual for row in rows) > protocol.carryover_limit:
        return ParticipantQualification(participant_id, "unavailable", "carryover limit exceeded")
    if max(row.intent_error for row in rows) > protocol.intent_error_limit:
        return ParticipantQualification(
            participant_id, "unavailable", "intent-control limit exceeded"
        )
    return ParticipantQualification(participant_id, "qualified", "all declared gates passed")


def analyze_equipment_response(
    protocol: EquipmentResponseProtocol,
    observations: tuple[ResponseObservation, ...],
) -> EquipmentResponseAnalysis:
    """Estimate within-person effects without promoting them to fitting advice."""
    qualification = qualify_observations(protocol, observations)
    unavailable = set(qualification.unavailable_participant_ids)
    raw = {
        participant: _cycle_effects(protocol, participant, observations)
        for participant, _ in protocol.randomization.assignments
        if participant not in unavailable
    }
    raw_means = {participant: fmean(values) for participant, values in raw.items()}
    group_mean = fmean(raw_means.values())
    observed_variance = variance(raw_means.values()) if len(raw_means) > 1 else 0.0
    average_sampling_variance = fmean(
        _sampling_variance(participant, raw[participant], observations) for participant in raw
    )
    between_variance = max(0.0, observed_variance - average_sampling_variance)
    results = tuple(
        _participant_result(
            protocol,
            participant,
            raw.get(participant),
            observations,
            group_mean,
            between_variance,
        )
        for participant, _ in protocol.randomization.assignments
    )
    return EquipmentResponseAnalysis(
        participants=results,
        group=GroupResponse(
            mean_effect=group_mean,
            between_participant_variance=between_variance,
            interpretation=(
                "Manufactured mixed individual effects; no population, product, "
                "or fitting inference."
            ),
        ),
    )


def _cycle_effects(
    protocol: EquipmentResponseProtocol,
    participant_id: str,
    observations: tuple[ResponseObservation, ...],
) -> tuple[float, ...]:
    baseline_id, target_id = (row.condition_id for row in protocol.conditions)
    effects: list[float] = []
    for cycle in range(1, protocol.randomization.cycles_per_participant + 1):
        baseline = fmean(
            row.outcome_value
            for row in observations
            if row.participant_id == participant_id
            and row.cycle == cycle
            and row.condition_id == baseline_id
        )
        target = fmean(
            row.outcome_value
            for row in observations
            if row.participant_id == participant_id
            and row.cycle == cycle
            and row.condition_id == target_id
        )
        effects.append(target - baseline)
    return tuple(effects)


def _sampling_variance(
    participant_id: str,
    effects: tuple[float, ...],
    observations: tuple[ResponseObservation, ...],
) -> float:
    cycle_component = variance(effects) / len(effects) if len(effects) > 1 else 0.0
    uncertainty = fmean(
        row.measurement_standard_uncertainty
        for row in observations
        if row.participant_id == participant_id
    )
    trial_count = len(tuple(row for row in observations if row.participant_id == participant_id))
    return cycle_component + 2.0 * uncertainty**2 / trial_count


def _participant_result(
    protocol: EquipmentResponseProtocol,
    participant_id: str,
    effects: tuple[float, ...] | None,
    observations: tuple[ResponseObservation, ...],
    group_mean: float,
    between_variance: float,
) -> ParticipantResponse:
    if effects is None:
        return ParticipantResponse(
            participant_id, "unavailable", None, None, None, False, "unavailable"
        )
    raw_effect = fmean(effects)
    sampling_variance = _sampling_variance(participant_id, effects, observations)
    weight = between_variance / (between_variance + sampling_variance)
    shrunken = weight * raw_effect + (1.0 - weight) * group_mean
    half_width = 1.96 * sqrt(sampling_variance)
    interval = (raw_effect - half_width, raw_effect + half_width)
    status = _classify(interval, protocol.practical_threshold)
    stable = _stable_directions(effects, protocol.practical_threshold)
    return ParticipantResponse(
        participant_id,
        status,
        raw_effect,
        shrunken,
        interval,
        stable,
        "manufactured-synthetic",
    )


def _classify(interval: tuple[float, float], threshold: float) -> ResultStatus:
    lower, upper = interval
    if lower > threshold:
        return "positive"
    if upper < -threshold:
        return "negative"
    if lower >= -threshold and upper <= threshold:
        return "null"
    return "indeterminate"


def _stable_directions(effects: tuple[float, ...], threshold: float) -> bool:
    directions = {1 if value > threshold else -1 if value < -threshold else 0 for value in effects}
    return len(directions) == 1
