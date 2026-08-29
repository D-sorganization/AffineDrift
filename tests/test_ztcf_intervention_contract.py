"""Executable and publication contracts for issue #4016's ZTCF repair."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from src.affine_control.ztcf_contract import (
    UnsupportedZTCFEngineError,
    ZTCFIntervention,
    ZTCFUnavailableError,
    execute_ztcf_intervention,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "data" / "ztcf" / "ztcf_intervention_v1.schema.json"
FIXTURE_PATH = REPO_ROOT / "data" / "ztcf" / "planar_golf_forward_fixture_v1.json"
PUBLIC_SOURCES = (
    REPO_ROOT / "articles" / "zero-torque-counterfactual.qmd",
    REPO_ROOT
    / "articles"
    / "The_Physics_of_Golf"
    / "quarto"
    / "ch06_zero_torque_counterfactual.qmd",
    REPO_ROOT
    / "articles"
    / "The_Physics_of_Golf"
    / "chapters"
    / "ch06_zero_torque_counterfactual.tex",
)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_normative_schema_accepts_the_registered_golden_fixture() -> None:
    """The public machine record must satisfy the checked-in normative schema."""
    schema = _load_json(SCHEMA_PATH)
    fixture = _load_json(FIXTURE_PATH)

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(fixture)
    intervention = ZTCFIntervention.model_validate(fixture)

    assert intervention.schema_version == "affinedrift.ztcf-intervention/v1"
    assert intervention.status == "available"


def test_python_golden_fixture_replays_at_registered_tolerance() -> None:
    """Only the locally supported planar Python rollout receives a golden result."""
    intervention = ZTCFIntervention.model_validate(_load_json(FIXTURE_PATH))
    result = execute_ztcf_intervention(intervention)

    assert intervention.expected is not None
    assert result.time == pytest.approx(intervention.expected.time, abs=1e-15)
    assert result.q == pytest.approx(intervention.expected.q, abs=1e-11)
    assert result.qd == pytest.approx(intervention.expected.qd, abs=1e-11)
    assert result.clubhead_speed == pytest.approx(intervention.expected.clubhead_speed, abs=1e-11)


def test_unavailable_intervention_fails_closed() -> None:
    """An unavailable result is evidence of absence, not permission to simulate."""
    fixture = copy.deepcopy(_load_json(FIXTURE_PATH))
    fixture["status"] = "unavailable"
    fixture["expected"] = None
    fixture["failure"] = {
        "code": "engine_unavailable",
        "message": "The declared engine is not installed.",
    }
    intervention = ZTCFIntervention.model_validate(fixture)

    with pytest.raises(ZTCFUnavailableError, match="engine_unavailable"):
        execute_ztcf_intervention(intervention)


def test_engine_unsupported_intervention_fails_closed() -> None:
    """A named but unsupported engine cannot inherit the Python fixture's result."""
    fixture = copy.deepcopy(_load_json(FIXTURE_PATH))
    model = fixture["model"]
    assert isinstance(model, dict)
    model["engine"] = "simulink"
    intervention = ZTCFIntervention.model_validate(fixture)

    with pytest.raises(UnsupportedZTCFEngineError, match="simulink"):
        execute_ztcf_intervention(intervention)


def test_nonzero_intervention_cannot_claim_the_ztcf_contract() -> None:
    """The typed contract rejects a branch that does not set inputs to zero."""
    fixture = copy.deepcopy(_load_json(FIXTURE_PATH))
    zeroed_input = fixture["zeroed_input"]
    assert isinstance(zeroed_input, dict)
    zeroed_input["values"] = [0.0, 1.0, 0.0]

    with pytest.raises(ValidationError, match="exactly zero"):
        ZTCFIntervention.model_validate(fixture)


def test_unsupported_solver_version_fails_closed() -> None:
    """A record cannot silently replay under a different solver contract."""
    fixture = copy.deepcopy(_load_json(FIXTURE_PATH))
    integration = fixture["integration"]
    assert isinstance(integration, dict)
    integration["solver_version"] = "unknown-rk4"
    intervention = ZTCFIntervention.model_validate(fixture)

    with pytest.raises(UnsupportedZTCFEngineError, match="solver version"):
        execute_ztcf_intervention(intervention)


def test_public_ztcf_sources_publish_the_intervention_and_interpretation_contract() -> None:
    """Canonical and paired textbook sources must expose the same claim boundary."""
    required = (
        "affinedrift.ztcf-intervention/v1",
        "model-conditioned intervention",
        "simulated trajectory difference",
        "contribution measure",
        "causal estimand",
        "physiological interpretation",
        "non-identifiability",
        "engine-unsupported",
        "golden fixture",
    )
    forbidden = (
        "your muscles simply shut off",
        "actually controlling",
        "the only achievable path",
        "muscular effort is largely expended",
        "any divergence is purely due to the difference in applied torques",
        "the deviation tells you where active control is required",
        "how much requires active muscular control",
        "the actual skill lies in",
        "validated using MATLAB and Simulink",
        "56 kill-switch times",
    )

    for source_path in PUBLIC_SOURCES:
        source = source_path.read_text(encoding="utf-8").lower()
        for phrase in required:
            assert phrase in source, f"{source_path}: missing {phrase!r}"
        for phrase in forbidden:
            assert phrase not in source, f"{source_path}: forbidden {phrase!r}"
