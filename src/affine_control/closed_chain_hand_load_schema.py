"""Versioned schema for two-handed closed-chain ZTCF and ZVCF hand loads.

Separate from the serial planar model in ``ztcf_contract.py``. Missing quantities
are ``UNAVAILABLE``. ``opposing_force_cancellation`` is ``||f_L|| + ||f_R|| - ||F||``.
Couple policies are ``axial-only`` (primary) and ``bounded``.
"""

from __future__ import annotations

import math
from typing import Annotated, Literal, TypeGuard

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

DOCUMENT_SCHEMA_VERSION = "affinedrift.closed-chain-hand-load/v1"
MANIFEST_SCHEMA_VERSION = "upstreamdrift.closed-chain-hand-load-manifest/v1"
UNAVAILABLE: Literal["UNAVAILABLE"] = "UNAVAILABLE"
VECTOR_WIDTH = 3

type Vec3 = tuple[float, float, float]
type Quantity = Vec3 | Literal["UNAVAILABLE"]
type Scalar = float | Literal["UNAVAILABLE"]
type CouplePolicy = Literal["axial-only", "bounded"]
type AllocationStatus = Literal["allocation-only", "forward-replayed"]


class ClosedChainHandLoadError(ValueError):
    """A closed-chain hand-load document or manifest failed its contract."""


def _finite(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError("must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("must be a finite number")
    return number


def _scalar(value: object) -> Scalar:
    if value == UNAVAILABLE:
        return UNAVAILABLE
    return _finite(value)


def _quantity(value: object) -> Quantity:
    if value == UNAVAILABLE:
        return UNAVAILABLE
    if not isinstance(value, list) or len(value) != VECTOR_WIDTH:
        raise ValueError(f"must be a {VECTOR_WIDTH}-vector or {UNAVAILABLE}")
    return (_finite(value[0]), _finite(value[1]), _finite(value[2]))


Finite = Annotated[float, BeforeValidator(_finite)]
ScalarField = Annotated[Scalar, BeforeValidator(_scalar)]
QuantityField = Annotated[Quantity, BeforeValidator(_quantity)]
GitSha = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class _Model(BaseModel):
    """Reject undeclared fields and coerce only through the declared validators."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, populate_by_name=True)


class Wrench(_Model):
    """Midhands force in newtons and couple in newton-metres."""

    force_n: QuantityField = Field(alias="force_N")
    couple_nm: QuantityField = Field(alias="couple_Nm")


class HandSample(_Model):
    """One candidate's forces, couples, alpha, cancellation, status, and feasibility."""

    f_l_n: QuantityField = Field(alias="f_L_N")
    f_r_n: QuantityField = Field(alias="f_R_N")
    m_l_nm: QuantityField = Field(alias="m_L_Nm")
    m_r_nm: QuantityField = Field(alias="m_R_Nm")
    alpha: ScalarField
    opposing_force_cancellation: ScalarField
    status: AllocationStatus
    infeasible: bool


class Midhands(_Model):
    """Total, ZTCF, and ZVCF wrenches. ZVCF is Total minus ZTCF."""

    total: Wrench
    ztcf: Wrench
    zvcf: Wrench


class Frame(_Model):
    """Grip positions, midhands wrenches, and both hand-load candidates at one time."""

    time_s: Finite
    swing_phase: str = Field(min_length=1)
    p_l_m: QuantityField = Field(alias="p_L_m")
    p_r_m: QuantityField = Field(alias="p_R_m")
    midhands: Midhands
    baseline: HandSample
    min_squared_force: HandSample

    @property
    def total(self) -> Wrench:
        """Midhands total wrench."""
        return self.midhands.total

    @property
    def ztcf(self) -> Wrench:
        """Midhands ZTCF wrench."""
        return self.midhands.ztcf

    @property
    def zvcf(self) -> Wrench:
        """Midhands ZVCF wrench."""
        return self.midhands.zvcf


class Provenance(_Model):
    """Git revision and SHA-256 hashes of model, subject, match, tensor, and settings."""

    git_sha: GitSha
    model_sha256: Sha256
    subject_sha256: Sha256
    match_sha256: Sha256
    tensor_sha256: Sha256
    settings_sha256: Sha256


class SquaredForce(_Model):
    """Time-weighted squared-force objective for each candidate."""

    baseline: ScalarField
    min_squared_force: ScalarField


class ClosedChainHandLoadRecord(_Model):
    """One v1 closed-chain hand-load export. ``example_data`` marks a synthetic example."""

    schema_version: Literal["affinedrift.closed-chain-hand-load/v1"]
    example_data: bool
    couple_policy: CouplePolicy
    superposition_tolerance: Finite = Field(gt=0)
    j_f: SquaredForce
    frames: list[Frame] = Field(min_length=1)
    provenance: Provenance


class UpstreamManifest(_Model):
    """SHA-256 pins from an UpstreamDrift ``manifest.json``."""

    schema_version: Literal["upstreamdrift.closed-chain-hand-load-manifest/v1"]
    provenance: Provenance


def to_document(record: ClosedChainHandLoadRecord) -> dict[str, object]:
    """Serialize a record to the v1 JSON object shape."""
    dumped = record.model_dump(by_alias=True, mode="json")
    return dict(dumped.items())


def _is_number_vector(value: Quantity) -> TypeGuard[Vec3]:
    return isinstance(value, tuple)


def _residual_limit(component: float, tolerance: float) -> float:
    return tolerance + tolerance * abs(component)


def _channel_error(
    name: str, total: Quantity, ztcf: Quantity, zvcf: Quantity, tolerance: float
) -> str | None:
    if total == UNAVAILABLE and ztcf == UNAVAILABLE and zvcf == UNAVAILABLE:
        return None
    if not (_is_number_vector(total) and _is_number_vector(ztcf) and _is_number_vector(zvcf)):
        return f"{name} mixes UNAVAILABLE with numeric wrench components"
    for index in range(VECTOR_WIDTH):
        residual = abs((ztcf[index] + zvcf[index]) - total[index])
        if residual > _residual_limit(total[index], tolerance):
            return f"{name} violates ZTCF + ZVCF = Total"
    return None


def superposition_error(frame: Frame, tolerance: float) -> str | None:
    """Return why ZTCF + ZVCF misses Total, or None when the frame is admissible."""
    channels = (
        ("force_N", frame.total.force_n, frame.ztcf.force_n, frame.zvcf.force_n),
        ("couple_Nm", frame.total.couple_nm, frame.ztcf.couple_nm, frame.zvcf.couple_nm),
    )
    for name, total, ztcf, zvcf in channels:
        message = _channel_error(name, total, ztcf, zvcf, tolerance)
        if message is not None:
            return message
    return None
