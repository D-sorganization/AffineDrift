"""Contracts for the hybrid impact/contact research program (#4038)."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from src.affine_control.impact_contact_fixtures import (
    build_fixture_ledger,
    build_protocol,
    centered_impact_state,
    oblique_impact_state,
)
from src.affine_control.impact_contact_models import (
    ContactCaseError,
    ContactSolverError,
    compare_contact_models,
    solve_compliant_contact,
    solve_hybrid_event,
    solve_rigid_impulse,
)
from src.affine_control.impact_contact_protocol import (
    ContactParameters,
    EventPolicy,
    FrameConvention,
    ImpactState,
)
from src.affine_control.impact_contact_uncertainty import propagate_outcome_interval


def test_protocol_freezes_sources_models_frames_and_authority() -> None:
    protocol = build_protocol()

    assert protocol.revision == "affinedrift.hybrid-impact-contact/v1"
    assert tuple(source.source_id for source in protocol.sources) == (
        "penner2003physics",
        "cross2014impact",
        "roberts2001contacttime",
        "petersen2009clubface",
        "mcnally2018shaftimpact",
        "kong2024saltation",
    )
    assert protocol.model_ids == ("rigid-impulse", "compliant-contact", "hybrid-event")
    assert protocol.frame.normal_axis == "+x clubface normal from club toward ball"
    assert protocol.frame.tangent_axis == "+y face tangent"
    assert protocol.frame.angular_axis == "+z right-hand rule"
    assert protocol.human_gate.status == "unavailable"
    assert "coaching" in protocol.authority_limit
    assert "universally correct" in protocol.authority_limit


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("normal_axis", "", "normal axis"),
        ("length_unit", "cm", "SI units"),
        ("angular_axis", "+y face tangent", "axes must be distinct"),
    ),
)
def test_frame_convention_fails_closed(field: str, value: str, message: str) -> None:
    frame = build_protocol().frame

    with pytest.raises(ValueError, match=message):
        FrameConvention(**{**frame.__dict__, field: value})


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("club_velocity_m_s", (np.nan, 0.0), "finite"),
        ("ball_spin_rad_s", np.inf, "finite"),
        ("contact_count", -1, "nonnegative integer"),
    ),
)
def test_impact_state_rejects_invalid_measurements(field: str, value: object, message: str) -> None:
    state = centered_impact_state()

    with pytest.raises(ValueError, match=message):
        ImpactState(**{**state.__dict__, field: value})


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("restitution", 1.01, "restitution"),
        ("friction", -0.1, "friction"),
        ("ball_inertia_kg_m2", 0.0, "positive"),
        ("solver_step_s", 0.0, "positive"),
        ("contact_exponent", 0.9, "at least one"),
    ),
)
def test_contact_parameters_reject_invalid_domains(field: str, value: float, message: str) -> None:
    parameters = build_protocol().parameters

    with pytest.raises(ValueError, match=message):
        ContactParameters(**{**parameters.__dict__, field: value})


def test_event_policy_rejects_unqualified_sampling_and_multiple_contact() -> None:
    policy = build_protocol().event_policy

    with pytest.raises(ValueError, match="sample rate"):
        EventPolicy(**{**policy.__dict__, "sample_rate_hz": 0.0})
    with pytest.raises(ValueError, match="fail-closed"):
        EventPolicy(**{**policy.__dict__, "multiple_contact_policy": "sequential"})


def test_rigid_impulse_preserves_linear_momentum_and_restitution_contract() -> None:
    protocol = build_protocol()
    state = centered_impact_state()

    outcome = solve_rigid_impulse(state, protocol.parameters, protocol.event_policy)
    momentum_before = (
        protocol.parameters.club_mass_kg * state.club_velocity_m_s[0]
        + protocol.parameters.ball_mass_kg * state.ball_velocity_m_s[0]
    )
    momentum_after = (
        protocol.parameters.club_mass_kg * outcome.club_velocity_m_s[0]
        + protocol.parameters.ball_mass_kg * outcome.ball_velocity_m_s[0]
    )
    closing_before = state.club_velocity_m_s[0] - state.ball_velocity_m_s[0]
    separating_after = outcome.ball_velocity_m_s[0] - outcome.club_velocity_m_s[0]

    assert momentum_after == pytest.approx(momentum_before, abs=1e-12)
    assert separating_after == pytest.approx(
        protocol.parameters.restitution * closing_before, rel=1e-12
    )
    assert outcome.energy_after_j <= outcome.energy_before_j + 1e-12
    assert outcome.normal_impulse_n_s > 0.0
    assert outcome.contact_time_s == 0.0


def test_oblique_rigid_impulse_caps_friction_and_updates_spin_with_declared_sign() -> None:
    protocol = build_protocol()
    outcome = solve_rigid_impulse(
        oblique_impact_state(), protocol.parameters, protocol.event_policy
    )

    friction_limit = protocol.parameters.friction * outcome.normal_impulse_n_s
    assert abs(outcome.tangential_impulse_n_s) <= friction_limit + 1e-12
    assert outcome.ball_spin_rad_s < 0.0
    assert outcome.slip_after_m_s <= outcome.slip_before_m_s


@pytest.mark.parametrize(
    ("state", "status"),
    (
        (replace(centered_impact_state(), club_velocity_m_s=(1e-8, 0.0)), "grazing"),
        (replace(centered_impact_state(), contact_count=2), "multiple-contact"),
        (replace(centered_impact_state(), club_velocity_m_s=(-1.0, 0.0)), "separating"),
    ),
)
def test_contact_cases_fail_closed(state: ImpactState, status: str) -> None:
    protocol = build_protocol()

    with pytest.raises(ContactCaseError, match=status):
        solve_rigid_impulse(state, protocol.parameters, protocol.event_policy)


def test_compliant_contact_has_finite_duration_balance_and_step_convergence() -> None:
    protocol = build_protocol()
    state = centered_impact_state()
    coarse = solve_compliant_contact(state, protocol.parameters, protocol.event_policy)
    medium = solve_compliant_contact(
        state,
        replace(protocol.parameters, solver_step_s=protocol.parameters.solver_step_s / 2.0),
        protocol.event_policy,
    )
    fine = solve_compliant_contact(
        state,
        replace(protocol.parameters, solver_step_s=protocol.parameters.solver_step_s / 4.0),
        protocol.event_policy,
    )

    assert 0.0 < coarse.contact_time_s < protocol.parameters.maximum_contact_time_s
    assert coarse.peak_force_n > 0.0
    assert coarse.momentum_residual_kg_m_s < 1e-10
    coarse_error = abs(coarse.ball_velocity_m_s[0] - fine.ball_velocity_m_s[0])
    medium_error = abs(medium.ball_velocity_m_s[0] - fine.ball_velocity_m_s[0])
    assert medium_error < coarse_error


def test_compliant_solver_failure_is_explicit_not_a_partial_result() -> None:
    protocol = build_protocol()
    impossible = replace(protocol.parameters, maximum_contact_steps=1)

    with pytest.raises(ContactSolverError, match="did not reach separation"):
        solve_compliant_contact(centered_impact_state(), impossible, protocol.event_policy)


def test_hybrid_event_propagates_event_time_and_matches_nominal_rigid_reset() -> None:
    protocol = build_protocol()
    state = centered_impact_state()
    rigid = solve_rigid_impulse(state, protocol.parameters, protocol.event_policy)
    nominal = solve_hybrid_event(
        state,
        protocol.parameters,
        protocol.event_policy,
        event_time_offset_s=0.0,
        club_acceleration_m_s2=(120.0, 0.0),
        ball_acceleration_m_s2=(0.0, 0.0),
    )
    late = solve_hybrid_event(
        state,
        protocol.parameters,
        protocol.event_policy,
        event_time_offset_s=protocol.event_policy.timing_uncertainty_s,
        club_acceleration_m_s2=(120.0, 0.0),
        ball_acceleration_m_s2=(0.0, 0.0),
    )

    assert nominal.ball_velocity_m_s == pytest.approx(rigid.ball_velocity_m_s)
    assert late.ball_velocity_m_s[0] > nominal.ball_velocity_m_s[0]
    assert late.event_time_offset_s == protocol.event_policy.timing_uncertainty_s


def test_uncertainty_interval_contains_nominal_and_reports_every_input() -> None:
    protocol = build_protocol()
    result = propagate_outcome_interval(protocol, oblique_impact_state())

    assert (
        result.ball_speed_m_s.minimum
        <= result.nominal_ball_speed_m_s
        <= result.ball_speed_m_s.maximum
    )
    assert (
        result.launch_angle_deg.minimum
        <= result.nominal_launch_angle_deg
        <= result.launch_angle_deg.maximum
    )
    assert (
        result.ball_spin_rad_s.minimum
        <= result.nominal_ball_spin_rad_s
        <= result.ball_spin_rad_s.maximum
    )
    assert result.ball_speed_m_s.width > 0.0
    assert result.varied_inputs == (
        "event time",
        "restitution",
        "friction",
        "face-normal angle",
    )
    assert result.sample_count == 81


def test_model_comparison_reports_differences_without_universal_ranking() -> None:
    protocol = build_protocol()
    comparison = compare_contact_models(centered_impact_state(), protocol)

    assert tuple(outcome.model_id for outcome in comparison.outcomes) == protocol.model_ids
    assert comparison.preferred_model is None
    assert comparison.comparison_limit.startswith("Outcome-specific")
    assert comparison.compliant_convergence_error_m_s >= 0.0


def test_fixture_ledger_retains_adverse_and_unavailable_results() -> None:
    ledger = build_fixture_ledger()

    assert tuple(record.status for record in ledger) == (
        "supported",
        "negative",
        "null",
        "unavailable",
    )
    assert all(record.evidence_origin == "synthetic-fixture" for record in ledger[:3])
    assert ledger[-1].evidence_origin == "unavailable"
    assert all("participant" not in record.authorized_claim.lower() for record in ledger)
