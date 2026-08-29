"""Deterministic manufactured declarations for hybrid impact research."""

from __future__ import annotations

from src.affine_control.impact_contact_protocol import (
    ContactParameters,
    EventPolicy,
    EvidenceSource,
    FixtureLedgerRecord,
    FrameConvention,
    HumanStudyGate,
    ImpactProtocol,
    ImpactState,
    ParameterUncertainty,
)

BALL_MASS_KG = 0.04593
BALL_RADIUS_M = 0.02135
SOLID_SPHERE_INERTIA_KG_M2 = 0.4 * BALL_MASS_KG * BALL_RADIUS_M**2


def _sources() -> tuple[EvidenceSource, ...]:
    """Return the bounded primary-source register in protocol order."""
    return (
        EvidenceSource(
            "penner2003physics",
            "review",
            "Penner (2003), doi:10.1088/0034-4885/66/2/202",
            "Golf impact and flight physics context.",
            "Does not validate this reduced state, parameter set, or outcome interval.",
        ),
        EvidenceSource(
            "cross2014impact",
            "primary-literature",
            "Cross (1999), doi:10.1119/1.19354",
            "Impulse, restitution, friction, and implement--ball collision mechanics.",
            "Bat/racket analysis is not a golf-specific fixture qualification.",
        ),
        EvidenceSource(
            "roberts2001contacttime",
            "measurement-method",
            "Roberts, Jones, and Rothberg (2001), doi:10.1046/j.1460-2687.2001.00084.x",
            "Golf club--ball contact-time measurement and speed/ball dependence.",
            "Does not establish this solver law, timing uncertainty, or perceptual authority.",
        ),
        EvidenceSource(
            "petersen2009clubface",
            "primary-literature",
            "Petersen and McPhee (2009), doi:10.1007/s12283-009-0030-7",
            "Golf clubface/ball finite-element impact-model precedent.",
            "Does not promote this reduced compliant law to a design model.",
        ),
        EvidenceSource(
            "mackenzie2018shaftimpact",
            "primary-literature",
            "MacKenzie (2018), doi:10.3390/proceedings2060245",
            "Evidence that shaft coupling can alter modeled launch outcomes.",
            "Does not supply a universal shaft correction or validate free-body impact.",
        ),
        EvidenceSource(
            "kong2024saltation",
            "review",
            "Kong et al. (2024), doi:10.1109/JPROC.2024.3440211",
            "Hybrid guard/reset sensitivity and event-time-aware uncertainty transport.",
            "Does not validate this golf guard, reset, or first-order range.",
        ),
    )


def _frame() -> FrameConvention:
    """Return the frozen planar clubface contact frame."""
    return FrameConvention(
        frame_id="clubface-contact-planar-v1",
        origin="nominal first contact point on the undeformed clubface",
        normal_axis="+x clubface normal from club toward ball",
        tangent_axis="+y face tangent",
        angular_axis="+z right-hand rule",
        length_unit="m",
        time_unit="s",
        angle_unit="rad",
        force_unit="N",
        mass_unit="kg",
    )


def _parameters() -> ContactParameters:
    """Return one plausible-but-unqualified manufactured parameter set."""
    return ContactParameters(
        club_mass_kg=0.200,
        ball_mass_kg=BALL_MASS_KG,
        ball_radius_m=BALL_RADIUS_M,
        ball_inertia_kg_m2=SOLID_SPHERE_INERTIA_KG_M2,
        restitution=0.78,
        friction=0.25,
        contact_stiffness_n_m_exp=30_000_000.0,
        contact_damping_s_m=0.015,
        contact_exponent=1.5,
        solver_step_s=2.0e-6,
        maximum_contact_time_s=0.003,
        maximum_contact_steps=2_000,
    )


def _event_policy() -> EventPolicy:
    """Return the guarded sampling and ambiguity policy."""
    return EventPolicy(
        guard="signed clubface-to-ball gap crosses zero from positive to nonpositive",
        crossing_direction="closing only",
        interpolation="bracketed linear timestamp interpolation",
        sample_rate_hz=200_000.0,
        timing_uncertainty_s=50.0e-6,
        synchronization_uncertainty_s=10.0e-6,
        grazing_speed_threshold_m_s=0.05,
        multiple_contact_policy="fail-closed",
    )


def build_protocol() -> ImpactProtocol:
    """Build the immutable manufactured protocol declaration."""
    parameters = _parameters()
    return ImpactProtocol(
        revision="affinedrift.hybrid-impact-contact/v1",
        sources=_sources(),
        model_ids=("rigid-impulse", "compliant-contact", "hybrid-event"),
        frame=_frame(),
        parameters=parameters,
        event_policy=_event_policy(),
        uncertainty=ParameterUncertainty(
            restitution=(0.74, 0.82),
            friction=(0.15, 0.35),
            face_normal_angle_deg=(-1.0, 1.0),
            event_time_s=(-50.0e-6, 50.0e-6),
        ),
        human_gate=HumanStudyGate(
            status="unavailable",
            missing_authorities=(
                "ethics and consent approval",
                "licensed calibrated impact measurements",
                "preregistered held-out analysis",
                "independent equipment and safety qualification",
            ),
        ),
        hypotheses=(
            "Declared models differ on finite contact time and output sensitivity.",
            "Timing, restitution, friction, and face-frame uncertainty widen outcomes.",
            "Grazing and multiple-contact events are unavailable to the single-contact map.",
        ),
        authority_limit=(
            "Synthetic and analytic feasibility only; no model is universally correct and no "
            "result has coaching, clinical, causal, population, or equipment-design authority."
        ),
    )


def centered_impact_state() -> ImpactState:
    """Return a centered normal manufactured driver-like state."""
    return ImpactState(
        state_id="synthetic-centered-normal-v1",
        club_velocity_m_s=(44.0, 0.0),
        ball_velocity_m_s=(0.0, 0.0),
        ball_spin_rad_s=0.0,
        contact_count=1,
        evidence_origin="synthetic-fixture",
    )


def oblique_impact_state() -> ImpactState:
    """Return a manufactured oblique state for friction/spin sensitivity."""
    return ImpactState(
        state_id="synthetic-oblique-v1",
        club_velocity_m_s=(44.0, 2.0),
        ball_velocity_m_s=(0.0, 0.0),
        ball_spin_rad_s=0.0,
        contact_count=1,
        evidence_origin="synthetic-fixture",
    )


def build_fixture_ledger() -> tuple[FixtureLedgerRecord, ...]:
    """Retain supported, adverse, ambiguous, and unavailable outcomes."""
    return (
        FixtureLedgerRecord(
            "impact-supported-centered",
            "supported",
            "synthetic-fixture",
            "The paired rigid reset satisfies its declared momentum and restitution equations.",
            "A manufactured equation check is not physical validation.",
        ),
        FixtureLedgerRecord(
            "impact-negative-grazing",
            "negative",
            "synthetic-fixture",
            "The event-conditioned map rejects the declared grazing case.",
            "Rejection does not characterize real grazing contact.",
        ),
        FixtureLedgerRecord(
            "impact-null-universal-model",
            "null",
            "synthetic-fixture",
            "No universally preferred model is identified across outcomes.",
            "Outcome equivalence in a fixture does not imply physical equivalence.",
        ),
        FixtureLedgerRecord(
            "impact-unavailable-human",
            "unavailable",
            "unavailable",
            "No human or equipment conclusion is available.",
            "Software checks cannot replace governance, calibration, or held-out evidence.",
        ),
    )
