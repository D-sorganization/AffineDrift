"""Manufactured fixtures for the bounded model-ladder protocol."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from src.affine_control.model_ladder_protocol import (
    COMPARISON_CATEGORIES,
    LEVEL_IDS,
    ComparisonObservation,
    LevelId,
    ModelLadderProtocol,
    TaskAssessment,
    build_model_ladder_protocol,
)


@dataclass(frozen=True)
class FixtureState:
    """Exact synthetic coordinate vector for one model level."""

    level_id: LevelId
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        """Require finite fixture values."""
        if self.level_id not in LEVEL_IDS or not self.values:
            raise ValueError("fixture state must name a declared level and values")
        if not all(isfinite(value) for value in self.values):
            raise ValueError("fixture values must be finite")


@dataclass(frozen=True)
class ParityFixture:
    """Manufactured shared-state fixture for adjacent projection parity."""

    fixture_id: str
    intervention: str
    states: tuple[FixtureState, ...]

    def __post_init__(self) -> None:
        """Require named fixture semantics and at least one state."""
        if not self.fixture_id.strip():
            raise ValueError("fixture_id must be declared")
        if not self.intervention.strip():
            raise ValueError("fixture intervention must be declared")
        if not self.states:
            raise ValueError("fixture states must be declared")


@dataclass(frozen=True)
class ConvergenceSample:
    """One manufactured flexible-shaft modal convergence sample."""

    mode_count: int
    impact_speed_error: float
    unit: str = "m/s"


def manufactured_parity_fixture() -> ParityFixture:
    """Return a fixture in which every added-physics coordinate is zero."""
    protocol = build_model_ladder_protocol()
    shared = (0.25, -3.0)
    states = tuple(
        FixtureState(level.level_id, shared + (0.0,) * (len(level.coordinates) - len(shared)))
        for level in protocol.levels
    )
    return ParityFixture(
        fixture_id="adjacent-zero-added-physics/v1",
        intervention="set each child-only coordinate to zero",
        states=states,
    )


def adjacent_projection_residuals(
    protocol: ModelLadderProtocol,
    fixture: ParityFixture,
) -> dict[str, float]:
    """Compute maximum coordinate residual for each adjacent projection."""
    state_ids = tuple(state.level_id for state in fixture.states)
    if len(set(state_ids)) != len(state_ids):
        raise ValueError("duplicate fixture state for the same model level")
    expected_ids = tuple(level.level_id for level in protocol.levels)
    if set(state_ids) != set(expected_ids) or len(state_ids) != len(expected_ids):
        raise ValueError("fixture must contain exactly one state per protocol level")
    level_lengths = {level.level_id: len(level.coordinates) for level in protocol.levels}
    for state in fixture.states:
        if len(state.values) != level_lengths[state.level_id]:
            raise ValueError("fixture state vector length must match declared coordinates")
    states = {state.level_id: state for state in fixture.states}
    residuals: dict[str, float] = {}
    for child in protocol.levels[1:]:
        if child.parent_id is None:
            raise ValueError("non-root level is missing its parent")
        child_values = states[child.level_id].values
        parent_values = states[child.parent_id].values
        projected = tuple(child_values[index] for index in child.projection_to_parent)
        if len(projected) != len(parent_values):
            raise ValueError("fixture state does not align with its projection")
        residuals[f"{child.level_id}->{child.parent_id}"] = max(
            abs(child_value - parent_value)
            for child_value, parent_value in zip(projected, parent_values, strict=True)
        )
    return residuals


def manufactured_convergence_fixture() -> tuple[ConvergenceSample, ...]:
    """Return an exact geometric modal-error sequence for regression tests."""
    return tuple(
        ConvergenceSample(mode_count, 0.08 * 0.25**index)
        for index, mode_count in enumerate((1, 2, 4, 8))
    )


def manufactured_comparison_observations() -> tuple[ComparisonObservation, ...]:
    """Return deterministic task-specific observations across every level."""
    metric_units = {
        "conserved-quantity-residuals": ("absolute energy residual", "J"),
        "kinematics": ("club path error", "rad"),
        "generalized-loads": ("generalized load error", "N m"),
        "club-face-and-path": ("face-orientation error", "rad"),
        "impact-state": ("impact speed error", "m/s"),
        "conditioning": ("scaled Jacobian condition number", "1"),
        "parameter-sensitivity": ("normalized local sensitivity", "1"),
    }
    observations: list[ComparisonObservation] = []
    for level_index, level_id in enumerate(LEVEL_IDS):
        scale = float(level_index + 1)
        for category in COMPARISON_CATEGORIES:
            if category == "runtime":
                observations.append(
                    ComparisonObservation(
                        level_id,
                        category,
                        "wall-clock runtime in a frozen benchmark environment",
                        "s",
                        None,
                        None,
                        "unavailable",
                        "unavailable",
                    )
                )
                continue
            metric_name, unit = metric_units[category]
            estimate = scale * 0.01
            observations.append(
                ComparisonObservation(
                    level_id,
                    category,
                    metric_name,
                    unit,
                    estimate,
                    (estimate * 0.9, estimate * 1.1),
                    "modeled",
                    "supported",
                )
            )
    return tuple(observations)


def manufactured_task_assessments() -> tuple[TaskAssessment, ...]:
    """Return exact sufficiency, negative, null, and unavailable outcomes."""
    required_rank = {
        "planar-path": 0,
        "three-dimensional-face": 1,
        "bilateral-load-share": 2,
        "shaft-deflection-at-impact": 3,
    }
    rows: list[TaskAssessment] = []
    for task_id, minimum_rank in required_rank.items():
        for level_rank, level_id in enumerate(LEVEL_IDS):
            sufficient = level_rank >= minimum_rank
            estimate = 0.01 if sufficient else 0.08
            rows.append(
                TaskAssessment(
                    task_id=task_id,
                    level_id=level_id,
                    metric_name=f"{task_id} task error",
                    unit="task-specific normalized error",
                    estimate=estimate,
                    uncertainty_interval=(estimate - 0.005, estimate + 0.005),
                    tolerance=0.02,
                    evidence_status="modeled",
                    outcome="supported" if sufficient else "negative",
                    sufficient=sufficient,
                    interpretation=(
                        "Manufactured fixture only; transport to people is not evaluated."
                    ),
                )
            )
    rows.extend(_participant_transfer_rows())
    return tuple(rows)


def _participant_transfer_rows() -> tuple[TaskAssessment, ...]:
    """Preserve a null result and unavailable participant-level transport."""
    rows: list[TaskAssessment] = []
    for index, level_id in enumerate(LEVEL_IDS):
        if index == 0:
            rows.append(
                TaskAssessment(
                    "participant-transfer",
                    level_id,
                    "held-out participant prediction improvement",
                    "normalized error difference",
                    0.0,
                    (-0.1, 0.1),
                    0.02,
                    "modeled",
                    "null",
                    False,
                    "The synthetic fixture provides no participant-transfer evidence.",
                )
            )
        else:
            rows.append(
                TaskAssessment(
                    "participant-transfer",
                    level_id,
                    "held-out participant prediction improvement",
                    "normalized error difference",
                    None,
                    None,
                    0.02,
                    "unavailable",
                    "unavailable",
                    None,
                    "No governed participant data are available.",
                )
            )
    return tuple(rows)
