"""Provenance gate for the vendored Option A reference trace (#5209)."""

import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from src.affine_control.option_a_trace import (
    PROVENANCE_PATH,
    TRACE_PATH,
    TraceProvenanceError,
    load_verified_trace,
)


def _copy_bundle(tmp_path: Path) -> tuple[Path, Path]:
    trace = tmp_path / TRACE_PATH.name
    provenance = tmp_path / PROVENANCE_PATH.name
    shutil.copy(TRACE_PATH, trace)
    shutil.copy(PROVENANCE_PATH, provenance)
    return trace, provenance


def test_vendored_trace_verifies_against_recorded_provenance() -> None:
    trace = load_verified_trace()

    assert trace.x.shape == (8, 350, 4)
    assert trace.u.shape == (8, 350, 2)
    assert trace.a.shape == (8, 350, 4, 4)
    assert trace.b.shape == (8, 350, 4, 2)
    assert trace.outcome_label.count("unrecoverable") == 2


def test_trace_with_altered_bytes_is_rejected(tmp_path: Path) -> None:
    trace, provenance = _copy_bundle(tmp_path)
    with trace.open("ab") as handle:
        handle.write(b"\x00")

    with pytest.raises(TraceProvenanceError, match="sha256"):
        load_verified_trace(trace, provenance)


def test_recorded_digest_mismatch_is_rejected(tmp_path: Path) -> None:
    trace, provenance = _copy_bundle(tmp_path)
    record = json.loads(provenance.read_text(encoding="utf-8"))
    record["npz_sha256"] = "0" * 64
    provenance.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(TraceProvenanceError, match="sha256"):
        load_verified_trace(trace, provenance)


def test_payload_digest_is_recomputed_not_trusted(tmp_path: Path) -> None:
    trace, provenance = _copy_bundle(tmp_path)
    record = json.loads(provenance.read_text(encoding="utf-8"))
    record["payload_sha256"] = "f" * 64
    provenance.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(TraceProvenanceError, match="payload"):
        load_verified_trace(trace, provenance)


def test_provenance_pins_upstream_commit_and_payload_digest() -> None:
    record = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))

    assert len(record["source_commit"]) == 40
    assert record["source_repository"] == "D-sorganization/UpstreamDrift"
    with np.load(TRACE_PATH, allow_pickle=False) as bundle:
        assert str(bundle["payload_sha256"]) == record["payload_sha256"]
