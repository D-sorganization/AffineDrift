"""Regression tests for Option A correction-authority vs baseline comparison (#5209)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from src.affine_control.option_a_comparison import (
    RESULT_PATH,
    compute_option_a_comparison,
    load_committed_comparison_result,
    run_option_a_comparison,
)
from src.affine_control.option_a_trace import (
    PROVENANCE_PATH,
    TRACE_PATH,
    TraceProvenanceError,
    load_verified_trace,
)
from src.affine_control.reachability_protocol import reject_forbidden_protocol_phrases

ROOT = Path(__file__).resolve().parents[1]
RESULTS_NOTE = ROOT / "docs/development/option-a-comparison-results-2026-11-10.md"


def test_recomputed_metrics_match_committed_result_json() -> None:
    committed = load_committed_comparison_result()
    fresh = run_option_a_comparison().to_json_dict()
    assert fresh == committed


def test_trace_digest_mismatch_is_rejected(tmp_path: Path) -> None:
    trace = tmp_path / TRACE_PATH.name
    provenance = tmp_path / PROVENANCE_PATH.name
    shutil.copy(TRACE_PATH, trace)
    shutil.copy(PROVENANCE_PATH, provenance)
    with trace.open("ab") as handle:
        handle.write(b"\x00")
    with pytest.raises(TraceProvenanceError, match="sha256"):
        load_verified_trace(trace, provenance)


def test_hypothesis_interpretation_respects_authority_boundary() -> None:
    result = run_option_a_comparison()
    for item in result.hypothesis_results:
        reject_forbidden_protocol_phrases(item.interpretation)
    assert result.hypothesis_results[0].hypothesis_id == "H-CA-LEAD"
    assert result.hypothesis_results[0].outcome in {"supported", "null", "negative", "unavailable"}


def test_results_note_declares_simulation_scope() -> None:
    text = RESULTS_NOTE.read_text(encoding="utf-8")
    required = (
        "simulation only",
        "one mujoco",
        "recovery_threshold_rad",
        "false_positive_rate",
        "Assessment Board",
    )
    lowered = text.casefold()
    for phrase in required:
        assert phrase.casefold() in lowered


def test_committed_result_binds_fixture_payload_digest() -> None:
    trace = load_verified_trace()
    payload = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    assert payload["payload_sha256"] == trace.payload_sha256


def test_compute_option_a_comparison_is_deterministic() -> None:
    trace = load_verified_trace()
    first = compute_option_a_comparison(trace).to_json_dict()
    second = compute_option_a_comparison(trace).to_json_dict()
    assert first == second
