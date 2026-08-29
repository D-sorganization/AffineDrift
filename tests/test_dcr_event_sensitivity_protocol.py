"""Contracts for bounded DCR, reachability, and event-sensitivity validation."""

from math import e, exp, isfinite
from pathlib import Path

import pytest

from src.affine_control.reachability import (
    ContactEventCase,
    CorrectionRequest,
    LinearScalarSystem,
    PlanarRankDeficientSystem,
    bounded_optimal_correction,
    contact_event_control_sensitivity,
    instantaneous_scalar_dcr,
    parameter_reachability_envelope,
    rank_deficient_reachable_box,
    scalar_linear_reachable_interval,
    solve_contact_event,
)
from src.affine_control.reachability_protocol import (
    AnalysisDeclaration,
    CoordinateDeclaration,
    CrossValidationSample,
    EventDeclaration,
    Hypothesis,
    HypothesisResult,
    InputDeclaration,
    ModelDeclaration,
    ReachabilityProtocol,
    SolverDeclaration,
    StateDeclaration,
    TaskMetricDeclaration,
    UncertaintyDeclaration,
    assess_incremental_prediction,
    preserve_hypothesis_results,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTICLE = REPO_ROOT / "articles" / "controllability-drift-ratio.qmd"


def _declared_protocol() -> ReachabilityProtocol:
    coordinates = CoordinateDeclaration(
        names=("path_angle", "path_rate"),
        units=("rad", "rad/s"),
        scaling=(1.0, 0.1),
        norm="weighted_l2",
    )
    state = StateDeclaration(values=(0.2, 8.0), coordinates=coordinates)
    inputs = InputDeclaration(
        names=("path_torque",),
        bounds=((-40.0, 40.0),),
        units=("N m",),
    )
    model = ModelDeclaration(
        model_id="synthetic-planar-event-fixture",
        revision="v1",
        state=state,
        inputs=inputs,
    )
    event = EventDeclaration(
        guard="path_angle = 0",
        direction="descending",
        reset="no reset in synthetic fixture",
        timing="first future crossing",
    )
    task_metric = TaskMetricDeclaration(
        name="absolute event-angle correction error",
        unit="rad",
        tolerance=0.01,
        evaluation="at the declared event",
    )
    uncertainty = UncertaintyDeclaration(
        model="deterministic bounded parameter envelope",
        parameters="declared drift-gradient set",
        evidence_status="assumed",
    )
    analysis = AnalysisDeclaration(
        horizon=0.2, event=event, task_metric=task_metric, uncertainty=uncertainty
    )
    solver = SolverDeclaration(name="analytic-plus-fixed-step", revision="v1", tolerance=1e-10)
    return ReachabilityProtocol(
        protocol_id="affinedrift.dcr-event-validation/v1",
        model=model,
        analysis=analysis,
        solver=solver,
    )


def test_protocol_declares_every_quantity_needed_for_interpretation() -> None:
    protocol = _declared_protocol()

    assert protocol.model.state.coordinates.names == ("path_angle", "path_rate")
    assert protocol.model.inputs.bounds == ((-40.0, 40.0),)
    assert protocol.model.state.coordinates.scaling == (1.0, 0.1)
    assert protocol.model.state.coordinates.norm == "weighted_l2"
    assert protocol.analysis.horizon == pytest.approx(0.2)
    assert protocol.analysis.event.direction == "descending"
    assert protocol.analysis.event.timing == "first future crossing"
    assert protocol.analysis.task_metric.tolerance == pytest.approx(0.01)
    assert protocol.analysis.task_metric.evaluation == "at the declared event"
    assert protocol.analysis.uncertainty.evidence_status == "assumed"
    assert "parameter envelope" in protocol.analysis.uncertainty.model
    assert protocol.solver.tolerance == pytest.approx(1e-10)


@pytest.mark.parametrize(
    "factory",
    (
        lambda: CoordinateDeclaration((), (), (), "weighted_l2"),
        lambda: CoordinateDeclaration(("x",), ("m",), (0.0,), "weighted_l2"),
        lambda: CoordinateDeclaration(("x",), ("m",), (1.0,), "undeclared"),
        lambda: InputDeclaration(("u",), ((1.0, -1.0),), ("N",)),
        lambda: EventDeclaration("", "descending", "none", "first crossing"),
        lambda: TaskMetricDeclaration("error", "rad", -1.0, "at event"),
        lambda: UncertaintyDeclaration("bounded", "a", "undeclared"),
        lambda: SolverDeclaration("solver", "v1", 0.0),
    ),
)
def test_protocol_fails_closed_when_a_required_declaration_is_invalid(factory: object) -> None:
    with pytest.raises(ValueError):
        assert callable(factory)
        factory()


def test_state_dependent_drift_breaks_any_dcr_to_reachable_width_mapping() -> None:
    additive = LinearScalarSystem(1.0, 0.0, 1.0, 1.0)
    state_dependent = LinearScalarSystem(1.0, 1.0, 0.0, 1.0)

    additive_interval = scalar_linear_reachable_interval(additive, horizon=1.0)
    state_dependent_interval = scalar_linear_reachable_interval(state_dependent, horizon=1.0)

    assert instantaneous_scalar_dcr(additive) == pytest.approx(1.0)
    assert instantaneous_scalar_dcr(state_dependent) == pytest.approx(1.0)
    assert additive_interval == pytest.approx((1.0, 3.0))
    assert state_dependent_interval == pytest.approx((1.0, 2.0 * e - 1.0))
    assert additive_interval[1] - additive_interval[0] == pytest.approx(2.0)
    assert state_dependent_interval[1] - state_dependent_interval[0] == pytest.approx(
        2.0 * (e - 1.0)
    )


def test_rank_deficient_input_preserves_an_uncontrolled_direction() -> None:
    system = PlanarRankDeficientSystem(
        initial_state=(0.0, 0.0),
        drift=(0.0, 10.0),
        control_bound=1.0,
        horizon=1.0,
    )

    reachable = rank_deficient_reachable_box(system)

    assert reachable.lower == pytest.approx((-1.0, 10.0))
    assert reachable.upper == pytest.approx((1.0, 10.0))
    assert reachable.controllability_rank == 1
    assert reachable.volume == pytest.approx(0.0)


def test_saturation_preserves_the_unmet_task_residual() -> None:
    result = bounded_optimal_correction(
        CorrectionRequest(required_delta=2.0, control_gain=1.0, input_bound=0.5)
    )

    assert result.control == pytest.approx(0.5)
    assert result.achieved_delta == pytest.approx(0.5)
    assert result.residual == pytest.approx(1.5)
    assert result.saturated is True


def test_event_sensitivity_changes_with_state_at_the_same_dcr() -> None:
    slower = ContactEventCase(1.0, -1.0, -9.0, 1.0)
    faster = ContactEventCase(1.0, -3.0, -9.0, 1.0)

    slower_event = solve_contact_event(slower)
    faster_event = solve_contact_event(faster)
    slower_sensitivity = contact_event_control_sensitivity(slower, perturbation=1e-5)
    faster_sensitivity = contact_event_control_sensitivity(faster, perturbation=1e-5)

    assert slower_event.time == pytest.approx((1.0 - 17.0**0.5) / -8.0)
    assert slower_event.velocity == pytest.approx(-(17.0**0.5))
    assert faster_event.time == pytest.approx(0.25)
    assert faster_event.velocity == pytest.approx(-5.0)
    assert slower_sensitivity == pytest.approx(1.0 / 17.0**0.5, rel=1e-6)
    assert faster_sensitivity == pytest.approx(0.2, rel=1e-6)
    assert slower_sensitivity != pytest.approx(faster_sensitivity)


def test_parameter_perturbations_publish_a_deterministic_uncertainty_envelope() -> None:
    systems = tuple(LinearScalarSystem(1.0, gradient, 0.0, 1.0) for gradient in (0.8, 1.0, 1.2))

    envelope = parameter_reachability_envelope(systems, horizon=1.0)

    expected_min_width = 2.0 * (exp(0.8) - 1.0) / 0.8
    expected_max_width = 2.0 * (exp(1.2) - 1.0) / 1.2
    assert envelope.center_interval == pytest.approx((exp(0.8), exp(1.2)))
    assert envelope.width_interval == pytest.approx((expected_min_width, expected_max_width))


def test_cross_validation_reports_no_incremental_dcr_value_when_baseline_is_exact() -> None:
    samples = tuple(
        CrossValidationSample(
            state=float(index),
            speed=float((index % 3) - 1),
            control_authority=float(1 + (index % 2)),
            dcr=float((index * 5) % 7),
            task_error=2.0 * index + 3.0 * ((index % 3) - 1) - (1 + (index % 2)),
        )
        for index in range(8)
    )

    result = assess_incremental_prediction(samples, minimum_rmse_improvement=0.01)

    assert result.baseline_rmse < 1e-10
    assert result.augmented_rmse < 1e-10
    assert result.outcome == "null"
    assert all(isfinite(value) for value in result.augmented_error_interval)


def test_hypothesis_ledger_preserves_association_prediction_and_theorem_results() -> None:
    hypotheses = (
        Hypothesis("H-A", "association", "Test adjusted association.", "interval excludes zero"),
        Hypothesis("H-P", "prediction", "Test held-out prediction.", "RMSE improves by 0.01"),
        Hypothesis("H-T", "theorem", "Test scalar sufficiency.", "all counterexamples fail"),
    )
    results = (
        HypothesisResult("H-A", "null", 0.0, (-0.1, 0.1), "No adjusted association."),
        HypothesisResult("H-P", "negative", -0.2, (-0.3, -0.1), "Held-out error worsened."),
        HypothesisResult(
            "H-T", "negative", None, None, "Analytic counterexamples refute sufficiency."
        ),
    )

    ledger = preserve_hypothesis_results(hypotheses, results)

    assert tuple(result.outcome for result in ledger) == ("null", "negative", "negative")


@pytest.mark.parametrize(
    "interpretation",
    (
        "DCR proves an elite strategy.",
        "This is a coaching prescription.",
        "The result causes lower errors in all golfers.",
        "This establishes clinical authority.",
    ),
)
def test_hypothesis_results_reject_coaching_causal_and_population_overreach(
    interpretation: str,
) -> None:
    with pytest.raises(ValueError, match="authority boundary"):
        HypothesisResult("H-P", "supported", 0.2, (0.1, 0.3), interpretation)


@pytest.mark.content_lint
def test_public_protocol_declares_scope_hypotheses_and_negative_result_policy() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    required = (
        "Bounded DCR Validation Protocol",
        "State and coordinates",
        "Input set and bounds",
        "Scaling and norm",
        "Finite horizon",
        "Event definition",
        "Task metric",
        "Uncertainty model",
        "Solver and tolerance",
        "constant additive drift",
        "state-dependent drift",
        "rank-deficient input map",
        "saturation",
        "contact and event timing",
        "model and parameter perturbations",
        "Association hypothesis",
        "Prediction hypothesis",
        "Theorem-level hypothesis",
        "leave-one-out cross-validation",
        "baseline state, speed, and control authority",
        "Null and negative results remain in the ledger",
        "not coaching, clinical, design, causal, or population authority",
    )
    for statement in required:
        assert statement in article

    forbidden = (
        "DCR predicts correction authority in golfers",
        "proves an elite strategy",
        "validated coaching prescription",
        "causes lower impact error",
    )
    for statement in forbidden:
        assert statement not in article
