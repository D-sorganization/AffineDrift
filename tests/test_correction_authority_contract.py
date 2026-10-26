"""Preregistered correction-authority contract and analytical edge-case oracles."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from src.affine_control.correction_authority_contract import (
    BaselineDetectorDeclaration,
    HorizonSweepDeclaration,
    double_integrator_position_interval,
    evaluate_double_integrator_correction_authority,
    evaluate_planar_rank_deficient_authority,
    evaluate_scalar_correction_authority,
    preregistered_humanoid_correction_authority_protocol,
    validate_correction_authority_protocol,
)
from src.affine_control.reachability import (
    LinearScalarSystem,
    PlanarRankDeficientSystem,
    assert_controllability_gramian_well_conditioned,
    instantaneous_scalar_dcr,
    scalar_linear_reachable_interval,
)
from src.affine_control.reachability_protocol import (
    HypothesisResult,
    ReachabilityIllConditionedError,
    reject_forbidden_protocol_phrases,
)

ARTICLE = Path(__file__).resolve().parents[1] / "articles" / "drift-control-ratio.qmd"


@pytest.mark.parametrize(
    ("oracle", "expected_recoverable", "expected_margin"),
    (
        (
            lambda: evaluate_double_integrator_correction_authority(0.3, 0.0, 0.0, 1.0, 1.0, 0.05),
            True,
            0.2,
        ),
        (
            lambda: evaluate_planar_rank_deficient_authority(
                (0.0, -1.0),
                PlanarRankDeficientSystem((0.0, 0.0), (0.0, 2.0), 1.0, 1.0),
                0.1,
            ),
            False,
            0.0,
        ),
        (
            lambda: evaluate_scalar_correction_authority(
                0.0, LinearScalarSystem(0.0, 0.0, 0.0, 2.0), 0.5, 0.25
            ),
            True,
            0.75,
        ),
        (
            lambda: evaluate_scalar_correction_authority(
                0.0, LinearScalarSystem(0.0, 0.0, 50.0, 1.0), 1.0, 0.1
            ),
            False,
            None,
        ),
    ),
)
def test_analytical_edge_case_oracles(
    oracle: object,
    expected_recoverable: bool,
    expected_margin: float | None,
) -> None:
    assert callable(oracle)
    result = oracle()
    assert result.recoverable is expected_recoverable
    if expected_margin is not None:
        assert result.margin == pytest.approx(expected_margin)


def test_double_integrator_interval_and_zero_drift_envelope() -> None:
    assert double_integrator_position_interval(0.0, 0.0, 1.0, 1.0) == pytest.approx((-0.5, 0.5))
    system = LinearScalarSystem(0.0, 0.0, 0.0, 2.0)
    assert scalar_linear_reachable_interval(system, 0.5) == pytest.approx((-1.0, 1.0))
    assert instantaneous_scalar_dcr(LinearScalarSystem(0.0, 0.0, 50.0, 1.0)) == pytest.approx(50.0)


@pytest.mark.parametrize(
    ("input_matrix", "kappa_max", "pattern"),
    (
        (np.array([[0.0], [0.0]]), 1e8, "singular"),
        (np.array([[0.0], [1.0]]), 1.0, "kappa_max"),
    ),
)
def test_gramian_gates_fail_loud(input_matrix: np.ndarray, kappa_max: float, pattern: str) -> None:
    state_matrix = np.array([[0.0, 1.0], [0.0, 0.0]])
    with pytest.raises(ReachabilityIllConditionedError, match=pattern):
        assert_controllability_gramian_well_conditioned(
            state_matrix, input_matrix, horizon=1.0, kappa_max=kappa_max
        )


def test_preregistered_protocol_declares_required_contract_fields() -> None:
    protocol = preregistered_humanoid_correction_authority_protocol()
    validate_correction_authority_protocol(protocol)
    assert protocol.authority.horizon.sweep_max > protocol.authority.horizon.sweep_min
    assert protocol.authority.kappa_max > 0.0


@pytest.mark.parametrize(
    "field", ("failure_definition", "effort_definition", "lead_time_definition")
)
def test_contract_rejects_incomplete_protocol_fields(field: str) -> None:
    protocol = preregistered_humanoid_correction_authority_protocol()
    with pytest.raises(ValueError):
        replace(protocol.authority, **{field: ""})


def test_contract_rejects_invalid_horizon_and_baseline() -> None:
    with pytest.raises(ValueError):
        HorizonSweepDeclaration(0.0, 0.1, 0.2)
    with pytest.raises(ValueError):
        BaselineDetectorDeclaration("", 0.1)


def test_validate_rejects_protocol_without_hypotheses() -> None:
    protocol = preregistered_humanoid_correction_authority_protocol()
    with pytest.raises(ValueError, match="hypothesis"):
        validate_correction_authority_protocol(replace(protocol, hypotheses=()))


@pytest.mark.parametrize(
    "phrase",
    (
        "DCR proves an elite strategy for humanoids.",
        "This is a coaching prescription for swing recovery.",
        "The estimate causes lower errors in all golfers.",
    ),
)
def test_contract_rejects_forbidden_overclaim_phrasing(phrase: str) -> None:
    with pytest.raises(ValueError, match="authority boundary"):
        reject_forbidden_protocol_phrases(phrase)


def test_hypothesis_results_stay_numeric_free_in_dispatch_one() -> None:
    protocol = preregistered_humanoid_correction_authority_protocol()
    results = tuple(
        HypothesisResult(
            hypothesis.hypothesis_id,
            "unavailable",
            None,
            None,
            "Simulation-only preregistration.",
        )
        for hypothesis in protocol.hypotheses
    )
    assert all(result.estimate is None for result in results)


@pytest.mark.content_lint
def test_public_protocol_doc_records_simulation_only_assumptions() -> None:
    source = ARTICLE.read_text(encoding="utf-8")
    for statement in (
        "Correction-Authority Analysis Contract",
        "simulation-only",
        "κ_max",
        "effort measure",
        "baseline detector",
        "lead-time",
        "HypothesisResult",
        "no uncalibrated numbers",
    ):
        assert statement in source
