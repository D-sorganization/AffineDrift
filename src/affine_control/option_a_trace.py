"""Verified consumer of the vendored UpstreamDrift Option A reference trace (#5209).

AffineDrift is an immutable consumer: the trace bytes are vendored under ``data/`` with a
provenance record, and nothing here imports UpstreamDrift. Loading fails closed unless the
file digest, the recomputed payload digest and the recorded provenance all agree.
"""

from __future__ import annotations

import hashlib
import io
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

type Array = NDArray[np.float64]

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "humanoid_robotics" / "option_a"
TRACE_PATH = DATA_DIR / "reference_trace_v1.npz"
PROVENANCE_PATH = DATA_DIR / "reference_provenance.json"
PROVENANCE_SCHEMA_VERSION = "affinedrift.option_a.trace_provenance/v1"
TRACE_SCHEMA_VERSION = "humanoid_option_a.trace/v1"
STATE_DIM = 4
INPUT_DIM = 2
# Order matters: it is the concatenation order of the upstream canonical payload digest.
_PAYLOAD_ARRAYS = (
    "x_k",
    "u_k",
    "A_k",
    "B_k",
    "trial_index",
    "outcome_label",
    "baseline_flag_time_s",
    "control_effort",
)
_PROVENANCE_KEYS = (
    "schema_version",
    "source_repository",
    "source_commit",
    "trace_schema_version",
    "failure_definition_id",
    "npz_sha256",
    "payload_sha256",
    "recovery_threshold_rad",
    "tracking_error_baseline_rad",
)


class TraceProvenanceError(ValueError):
    """Raised when the vendored trace does not match its recorded provenance."""


@dataclass(frozen=True)
class OptionATrace:
    """Per-trial view of the verified trace: arrays are indexed ``[trial, step, ...]``."""

    x: Array
    u: Array
    a: Array
    b: Array
    outcome_label: tuple[str, ...]
    baseline_flag_time_s: Array
    control_effort: Array
    perturbation_metadata: tuple[Mapping[str, float], ...]
    timestep_s: float
    torque_limit_nm: float
    recovery_threshold_rad: float
    tracking_error_baseline_rad: float
    payload_sha256: str

    def onset_step(self, trial: int) -> int:
        """Return the step at which the fixture applied the trial's velocity impulse."""
        fraction = float(self.perturbation_metadata[trial]["onset_fraction"])
        return int(round(fraction * (self.x.shape[1] - 1)))


def _sha256(data: bytes) -> str:
    """Return the lowercase SHA-256 hex digest of the given byte string."""
    return hashlib.sha256(data).hexdigest()


def _payload_sha256(bundle: Mapping[str, Any], metadata: list[Any]) -> str:
    """Recompute the upstream canonical payload digest (``trace_contract.payload_sha256``)."""
    header = {
        "schema_version": str(bundle["schema_version"]),
        "failure_definition_id": str(bundle["failure_definition_id"]),
        "seed": int(bundle["seed"]),
        "mujoco_version": str(bundle["mujoco_version"]),
        "timestep_s": float(bundle["timestep_s"]),
        "torque_limit_nm": float(bundle["torque_limit_nm"]),
        "perturbation_metadata": metadata,
    }
    parts = [json.dumps(header, sort_keys=True, separators=(",", ":")).encode("utf-8")]
    for key in _PAYLOAD_ARRAYS:
        parts.extend((key.encode("ascii"), np.asarray(bundle[key]).tobytes(order="C")))
    return _sha256(b"".join(parts))


def _read_provenance(path: Path) -> dict[str, Any]:
    """Load and validate the JSON provenance record beside the vendored trace."""
    record = json.loads(path.read_text(encoding="utf-8"))
    missing = [key for key in _PROVENANCE_KEYS if key not in record]
    if missing or record["schema_version"] != PROVENANCE_SCHEMA_VERSION:
        raise TraceProvenanceError(f"provenance record is incomplete or unsupported: {missing}")
    return dict(record)


def _check_digests(raw: bytes, record: Mapping[str, Any]) -> None:
    """Ensure the on-disk NPZ bytes match the ``npz_sha256`` field in provenance."""
    if _sha256(raw) != record["npz_sha256"]:
        raise TraceProvenanceError("trace file sha256 differs from the recorded provenance")


def _per_trial(array: Array, trials: int) -> Array:
    """Reshape a flat trace array into ``[trial, step, ...]``."""
    return np.asarray(array, dtype=np.float64).reshape(trials, -1, *array.shape[1:])


def _to_trace(bundle: Mapping[str, Any], record: Mapping[str, Any]) -> OptionATrace:
    """Build an ``OptionATrace`` after schema, grouping, and finiteness checks."""
    if str(bundle["schema_version"]) != TRACE_SCHEMA_VERSION:
        raise TraceProvenanceError("unsupported trace schema")
    index = np.asarray(bundle["trial_index"])
    trials = int(index.max()) + 1
    if not np.array_equal(index, np.repeat(np.arange(trials), index.size // trials)):
        raise TraceProvenanceError("trial_index must group equal-length trials contiguously")
    arrays = {key: _per_trial(bundle[key], trials) for key in ("x_k", "u_k", "A_k", "B_k")}
    if not all(np.isfinite(value).all() for value in arrays.values()):
        raise TraceProvenanceError("trace arrays contain non-finite values")
    if arrays["x_k"].shape[2] != STATE_DIM or arrays["u_k"].shape[2] != INPUT_DIM:
        raise TraceProvenanceError("unexpected state or input dimension")
    return OptionATrace(
        x=arrays["x_k"],
        u=arrays["u_k"],
        a=arrays["A_k"],
        b=arrays["B_k"],
        outcome_label=tuple(str(label) for label in bundle["outcome_label"]),
        baseline_flag_time_s=np.asarray(bundle["baseline_flag_time_s"], dtype=np.float64),
        control_effort=np.asarray(bundle["control_effort"], dtype=np.float64),
        perturbation_metadata=tuple(json.loads(str(bundle["perturbation_metadata_json"]))),
        timestep_s=float(bundle["timestep_s"]),
        torque_limit_nm=float(bundle["torque_limit_nm"]),
        recovery_threshold_rad=float(record["recovery_threshold_rad"]),
        tracking_error_baseline_rad=float(record["tracking_error_baseline_rad"]),
        payload_sha256=str(record["payload_sha256"]),
    )


def load_verified_trace(
    trace_path: Path = TRACE_PATH, provenance_path: Path = PROVENANCE_PATH
) -> OptionATrace:
    """Return the trace after verifying the file digest and the recomputed payload digest.

    Preconditions: both files exist. Postcondition: the returned arrays are finite, grouped
    per trial, and the upstream payload digest was recomputed rather than trusted.
    """
    record = _read_provenance(provenance_path)
    raw = trace_path.read_bytes()
    _check_digests(raw, record)
    with np.load(io.BytesIO(raw), allow_pickle=False) as handle:
        bundle = {key: handle[key] for key in handle.files}
    metadata = json.loads(str(bundle["perturbation_metadata_json"]))
    recomputed = _payload_sha256(bundle, metadata)
    if not (recomputed == record["payload_sha256"] == str(bundle["payload_sha256"])):
        raise TraceProvenanceError("recomputed payload digest differs from the provenance record")
    return _to_trace(bundle, record)
