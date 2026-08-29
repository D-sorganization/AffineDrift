"""Fail-closed execution contract for registered ZTCF interventions."""

from __future__ import annotations

from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.affine_control.golf_model import GolfModel

__all__ = [
    "UnsupportedZTCFEngineError",
    "ZTCFIntervention",
    "ZTCFUnavailableError",
    "execute_ztcf_intervention",
]


class ContractModel(BaseModel):
    """Base model that rejects undeclared intervention fields."""

    model_config = ConfigDict(extra="forbid")


class ModelParameters(ContractModel):
    """Parameters needed to reproduce the supported planar model."""

    masses: tuple[float, float, float]
    lengths: tuple[float, float, float]
    inertias: tuple[float, float, float]
    shaft_mass: float = Field(gt=0.0)
    modal_frequencies: tuple[float, float]
    com_fractions: tuple[float, float, float]


class ModelAuthority(ContractModel):
    """Immutable identity of the model and execution engine."""

    id: str
    version: str
    source_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    engine: str
    engine_version: str
    parameters: ModelParameters


class InitialState(ContractModel):
    """Branch state with explicit coordinates, frame, and units."""

    coordinates: tuple[str, str, str, str, str, str]
    frame: str = Field(min_length=1)
    position_units: Literal["rad"]
    velocity_units: Literal["rad/s"]
    q: tuple[float, float, float]
    qd: tuple[float, float, float]


class ZeroedInput(ContractModel):
    """The exact model input channel removed by the intervention."""

    name: str = Field(min_length=1)
    physical_level: Literal["applied_generalized_torque"]
    channels: tuple[str, str, str]
    units: Literal["N*m"]
    values: tuple[float, float, float]

    @model_validator(mode="after")
    def validate_zero_values(self) -> ZeroedInput:
        """A zero-input intervention may not carry a nonzero input value."""
        if any(value != 0.0 for value in self.values):
            raise ValueError("zeroed input values must be exactly zero")
        return self


class RetainedEnvironment(ContractModel):
    """Controls, constraints, contacts, loads, and internal state held fixed."""

    controls: list[str]
    constraints: list[str]
    contact: str
    loads: list[str]
    internal_states: list[str]
    parameters: str


class IntegrationContract(ContractModel):
    """Finite rollout horizon and numerical method."""

    start_time: float
    end_time: float
    time_units: Literal["s"]
    solver: Literal["fixed-step RK4"]
    solver_version: str
    steps: int = Field(gt=0)
    absolute_tolerance: float = Field(gt=0.0)

    @model_validator(mode="after")
    def validate_horizon(self) -> IntegrationContract:
        """Require a positive, finite intervention horizon."""
        if not np.isfinite(self.start_time) or not np.isfinite(self.end_time):
            raise ValueError("integration horizon must be finite")
        if self.end_time <= self.start_time:
            raise ValueError("integration end_time must exceed start_time")
        return self


class TerminalState(ContractModel):
    """Registered terminal result of a supported intervention."""

    time: float
    q: tuple[float, float, float]
    qd: tuple[float, float, float]
    clubhead_speed: float
    frame: str
    position_units: Literal["rad"]
    velocity_units: Literal["rad/s"]
    speed_units: Literal["m/s"]


class InterpretationContract(ContractModel):
    """Boundaries between numerical output and stronger interpretations."""

    simulated_trajectory_difference: str
    contribution_measure: str
    causal_estimand: str
    physiological_interpretation: str
    non_identifiability: list[str] = Field(min_length=1)


class ParityContract(ContractModel):
    """Cross-engine parity status without implied unsupported engines."""

    status: Literal["not_claimed", "verified"]
    engines: list[str] = Field(min_length=1)
    tolerance: float | None
    note: str

    @model_validator(mode="after")
    def validate_verified_parity(self) -> ParityContract:
        """Require two engines and a tolerance before parity may be verified."""
        if self.status == "verified" and (len(self.engines) < 2 or self.tolerance is None):
            raise ValueError("verified parity requires at least two engines and a tolerance")
        return self


class FailureState(ContractModel):
    """Machine-readable reason an intervention cannot produce a result."""

    code: Literal[
        "invalid_contract",
        "engine_unavailable",
        "engine_unsupported",
        "numerical_failure",
    ]
    message: str = Field(min_length=1)


class ZTCFIntervention(ContractModel):
    """Normative record for one model-conditioned ZTCF intervention."""

    schema_version: Literal["affinedrift.ztcf-intervention/v1"]
    intervention_id: str = Field(min_length=1)
    status: Literal["available", "unavailable"]
    construction: Literal["forward"]
    model: ModelAuthority
    state: InitialState
    zeroed_input: ZeroedInput
    retained: RetainedEnvironment
    integration: IntegrationContract
    expected: TerminalState | None
    interpretation: InterpretationContract
    parity: ParityContract
    failure: FailureState | None
    preconditions: list[str] = Field(min_length=1)
    postconditions: list[str] = Field(min_length=1)
    failure_states: list[FailureState] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_availability(self) -> ZTCFIntervention:
        """Prevent unavailable records from carrying publishable results."""
        if self.status == "available" and self.expected is None:
            raise ValueError("available intervention requires an expected result")
        if self.status == "available" and self.failure is not None:
            raise ValueError("available intervention cannot carry a failure")
        if self.status == "unavailable" and self.failure is None:
            raise ValueError("unavailable intervention requires a failure")
        if self.status == "unavailable" and self.expected is not None:
            raise ValueError("unavailable intervention cannot carry an expected result")
        return self


class ZTCFUnavailableError(RuntimeError):
    """Raised when a registered intervention has no available result."""


class UnsupportedZTCFEngineError(RuntimeError):
    """Raised when no executable adapter exists for the declared engine."""


def _build_supported_model(authority: ModelAuthority) -> GolfModel:
    """Construct the only locally supported ZTCF model adapter."""
    supported = (
        "affinedrift.planar-golf",
        "1.0",
        "affinedrift-python",
        "GolfModel.ztcf_trajectory/v1",
    )
    declared = (
        authority.id,
        authority.version,
        authority.engine,
        authority.engine_version,
    )
    if declared != supported:
        raise UnsupportedZTCFEngineError(
            f"engine-unsupported intervention: {authority.engine}/{authority.engine_version}"
        )
    parameters = authority.parameters
    return GolfModel(
        masses=parameters.masses,
        lengths=parameters.lengths,
        inertias=parameters.inertias,
        shaft_mass=parameters.shaft_mass,
        modal_frequencies=parameters.modal_frequencies,
        com_fractions=parameters.com_fractions,
    )


def _validate_supported_protocol(intervention: ZTCFIntervention) -> None:
    """Reject protocol claims that the registered adapter does not implement."""
    expected_coordinates = ("q1", "q2", "q3", "qd1", "qd2", "qd3")
    if intervention.state.coordinates != expected_coordinates:
        raise UnsupportedZTCFEngineError("engine-unsupported coordinate convention")
    if intervention.integration.solver_version != "GolfModel.ztcf_trajectory/v1":
        raise UnsupportedZTCFEngineError("engine-unsupported solver version")
    if intervention.retained.controls:
        raise UnsupportedZTCFEngineError("engine-unsupported retained controls")
    if intervention.retained.contact != "none":
        raise UnsupportedZTCFEngineError("engine-unsupported contact protocol")
    if intervention.retained.loads != ["uniform gravity at 9.81 m/s^2"]:
        raise UnsupportedZTCFEngineError("engine-unsupported load protocol")


def execute_ztcf_intervention(intervention: ZTCFIntervention) -> TerminalState:
    """Replay a supported intervention or fail closed without substituting engines."""
    if intervention.status == "unavailable":
        failure = intervention.failure
        if failure is None:
            raise ZTCFUnavailableError("invalid_contract: unavailable record lacks failure")
        raise ZTCFUnavailableError(f"{failure.code}: {failure.message}")
    _validate_supported_protocol(intervention)
    model = _build_supported_model(intervention.model)
    integration = intervention.integration
    duration = integration.end_time - integration.start_time
    trajectory = model.ztcf_trajectory(
        np.asarray(intervention.state.q),
        np.asarray(intervention.state.qd),
        duration,
        integration.steps,
    )
    time, q, qd, speed = trajectory[-1]
    if not np.all(np.isfinite(np.concatenate((q, qd, [time, speed])))):
        raise ZTCFUnavailableError("numerical_failure: terminal state is non-finite")
    return TerminalState(
        time=integration.start_time + time,
        q=(float(q[0]), float(q[1]), float(q[2])),
        qd=(float(qd[0]), float(qd[1]), float(qd[2])),
        clubhead_speed=float(speed),
        frame=intervention.state.frame,
        position_units=intervention.state.position_units,
        velocity_units=intervention.state.velocity_units,
        speed_units="m/s",
    )
