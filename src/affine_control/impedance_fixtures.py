"""Deterministic fixtures for active impedance identification contracts."""

from __future__ import annotations

from typing import TypedDict

import numpy as np

from src.affine_control.impedance_emg import (
    CciFamily,
    ComparisonScope,
    EmgChannel,
    EmgEnvelopePair,
    EmgPairDeclaration,
    FormulaId,
    Side,
)
from src.affine_control.impedance_evidence import HumanStudyGate, ImpedanceResult
from src.affine_control.impedance_protocol import (
    PARAMETER_NAMES,
    Hypothesis,
    IdentificationModel,
    ImpedanceProtocol,
    PhaseDeclaration,
    ResponseWindow,
    SafetyEnvelope,
)
from src.affine_control.impedance_sources import primary_sources


class _SharedModelFields(TypedDict):
    """Typed keyword fields shared by endpoint and joint declarations."""

    parameter_names: tuple[str, ...]
    reflex_delay_ms: float
    solver: str
    rank_tolerance: float
    maximum_condition_number: float
    residual_metric: str


class _SharedPairFields(TypedDict):
    """Typed keyword fields shared by the two governed EMG pairs."""

    normalization_revision: str
    cci_family: CciFamily
    formula_id: FormulaId
    comparison_scope: ComparisonScope
    sensitivity_plan: tuple[str, ...]


def _safety() -> SafetyEnvelope:
    """Return a synthetic-only perturbation envelope, not device approval."""
    return SafetyEnvelope(
        device_id="simulated-torque-pulse-device/v1",
        device_revision="synthetic-feasibility-only",
        control_mode="bounded torque pulse with independent displacement and velocity stops",
        trigger_source="registered club-angle event with hardware timestamp",
        trigger_tolerance_ms=1.0,
        maximum_displacement_rad=0.02,
        maximum_velocity_rad_s=0.5,
        maximum_torque_nm=3.0,
        hardware_stop="independent torque, displacement, and velocity interlock",
        operator_stop="held-enable switch and reachable emergency stop",
        preflight_checks=(
            "unloaded range and sign check",
            "calibration and timestamp revision check",
            "dummy-load pulse and stop verification",
        ),
        stopping_rules=(
            "stop on any limit, saturation, clipping, or timestamp discontinuity",
            "stop on unexpected contact loss or phase-trigger disagreement",
            "stop before any repeat after discomfort or operator concern",
        ),
    )


def _windows() -> tuple[ResponseWindow, ...]:
    """Return operational windows that do not assign physiological identity."""
    baseline = ResponseWindow(
        "baseline",
        -80.0,
        0.0,
        ("background EMG proxy", "pre-perturbation joint torque"),
        "The window quantifies baseline signals but does not label passive or voluntary origin.",
    )
    early = ResponseWindow(
        "early-response",
        0.0,
        80.0,
        ("effective mechanical response", "model-partitioned response", "EMG response proxy"),
        "Latency plus a declared model is required; timing alone does not identify a reflex.",
    )
    late = ResponseWindow(
        "late-response",
        80.0,
        250.0,
        ("effective mechanical response", "activation proxy", "model residual"),
        "Voluntary, reflexive, passive, and task changes can overlap in this window.",
    )
    return baseline, early, late


def _phases() -> tuple[PhaseDeclaration, ...]:
    """Return two event-triggered swing-like synthetic phases."""
    return (
        PhaseDeclaration(
            "transition",
            "registered top-of-backswing angular-velocity reversal",
            35.0,
            _windows(),
        ),
        PhaseDeclaration(
            "pre-impact",
            "registered club-shaft angle crossing before synthetic impact",
            -120.0,
            _windows(),
        ),
    )


def _emg_channel(channel_id: str, muscle: str, side: Side) -> EmgChannel:
    """Return one manufactured surface-EMG declaration."""
    return EmgChannel(
        channel_id=channel_id,
        muscle_label=muscle,
        side=side,
        electrode_location="declared longitudinal belly location from placement worksheet",
        electrode_orientation="parallel to estimated fiber direction",
        interelectrode_distance_mm=20.0,
        sample_rate_hz=2000.0,
        highpass_hz=20.0,
        lowpass_hz=450.0,
        normalization_method="predeclared task reference; MVC sensitivity reported separately",
        electromechanical_delay_ms=45.0,
        delay_uncertainty_ms=15.0,
        crosstalk_check="adjacent-channel and resisted-action crosstalk screen",
        electrode_revision="manufactured-electrode-map/v1",
    )


def _models() -> tuple[IdentificationModel, ...]:
    """Return distinct endpoint and joint model declarations."""
    shared: _SharedModelFields = {
        "parameter_names": PARAMETER_NAMES,
        "reflex_delay_ms": 45.0,
        "solver": "scaled linear least squares with preregistered rank tolerance",
        "rank_tolerance": 1.0e-12,
        "maximum_condition_number": 1.0e5,
        "residual_metric": "phase-held-out root-mean-square response error",
    }
    endpoint = IdentificationModel(
        model_id="endpoint-effective-impedance/v1",
        output_quantity="endpoint-wrench",
        coordinate_frame="club-grip-center Cartesian wrench frame",
        perturbation_unit="m,rad",
        response_unit="N,Nm",
        jacobian_assumption=(
            "registered full-rank Jacobian with geometric stiffness retained as a separate term"
        ),
        **shared,
    )
    joint = IdentificationModel(
        model_id="joint-effective-impedance/v1",
        output_quantity="joint-torque",
        coordinate_frame="declared generalized joint coordinates and positive torque signs",
        perturbation_unit="rad",
        response_unit="Nm",
        jacobian_assumption=(
            "joint-space fit is primary; no endpoint equivalence without the declared Jacobian"
        ),
        **shared,
    )
    return endpoint, joint


def _emg_pairs() -> tuple[EmgPairDeclaration, ...]:
    """Return exact same-side channel pairings and proxy definitions."""
    shared: _SharedPairFields = {
        "normalization_revision": "task-reference/v1 with MVC sensitivity",
        "cci_family": "amplitude-driven",
        "formula_id": "symmetric-envelope-overlap-v1",
        "comparison_scope": "within-formula-relative-trends-only",
        "sensitivity_plan": (
            "normalization method",
            "electrode placement and crosstalk",
            "muscle-pair selection",
            "electromechanical delay",
        ),
    }
    lead = EmgPairDeclaration(
        pair_id="lead-flexor-extensor/v1",
        agonist_channel_id="lead-flexor/v1",
        antagonist_channel_id="lead-extensor/v1",
        side="lead",
        **shared,
    )
    trail = EmgPairDeclaration(
        pair_id="trail-flexor-extensor/v1",
        agonist_channel_id="trail-flexor/v1",
        antagonist_channel_id="trail-extensor/v1",
        side="trail",
        **shared,
    )
    return lead, trail


def _hypotheses() -> tuple[Hypothesis, ...]:
    """Return predeclared feasibility, recovery, and human-transfer hypotheses."""
    return (
        Hypothesis(
            "H1-excitation-rank",
            "phase-specific effective impedance parameter vector",
            "design rank, nullity, condition number, and held-out residual",
            "full column rank and condition below the frozen threshold",
            "rank loss, excessive condition number, or held-out residual above tolerance",
            "negative",
        ),
        Hypothesis(
            "H2-partition-sensitivity",
            "model-partitioned intrinsic, reflex, passive, and voluntary bases",
            "complete sensitivity interval over delay and basis alternatives",
            "report a component only when its interval remains inside tolerance",
            "basis confounding or interval crossing the declared tolerance",
            "null",
        ),
        Hypothesis(
            "H3-human-transport",
            "participant-held-out reliability and prediction",
            "held-out error and preregistered reliability coefficient",
            "evaluate only after every governance and safety gate is satisfied",
            "any missing approval, calibration, stop, reliability, or held-out record",
            "unavailable",
        ),
    )


def manufactured_protocol() -> ImpedanceProtocol:
    """Return the source-bounded synthetic preregistration."""
    channels = (
        _emg_channel("lead-flexor/v1", "lead-side flexor proxy", "lead"),
        _emg_channel("lead-extensor/v1", "lead-side extensor proxy", "lead"),
        _emg_channel("trail-flexor/v1", "trail-side flexor proxy", "trail"),
        _emg_channel("trail-extensor/v1", "trail-side extensor proxy", "trail"),
    )
    return ImpedanceProtocol(
        protocol_id="affinedrift.active-impedance/v1",
        sources=primary_sources(),
        safety=_safety(),
        phases=_phases(),
        emg_channels=channels,
        emg_pairs=_emg_pairs(),
        models=_models(),
        hypotheses=_hypotheses(),
        uncertainty_method=(
            "complete intervals over perturbation amplitude/bandwidth, reflex delay, passive "
            "basis, electrode placement, normalization, and event-timing alternatives"
        ),
        reliability_metric=(
            "phase-stratified repeatability coefficient and held-out prediction error"
        ),
        human_gate=manufactured_human_gate(),
    )


def _base_design() -> np.ndarray:
    """Return a deterministic, well-conditioned five-column excitation matrix."""
    time = np.linspace(0.0, 1.0, 96, endpoint=False)
    acceleration = np.sin(2.0 * np.pi * time)
    velocity = np.cos(4.0 * np.pi * time + 0.1)
    displacement = np.sin(6.0 * np.pi * time + 0.3)
    delayed_velocity = np.maximum(np.sin(10.0 * np.pi * time + 0.2), 0.0)
    voluntary_basis = np.cos(14.0 * np.pi * time + 0.4)
    return np.column_stack(
        (acceleration, velocity, displacement, delayed_velocity, voluntary_basis)
    )


def manufactured_full_rank_case(
    phase_id: str,
) -> tuple[IdentificationModel, np.ndarray, np.ndarray, tuple[float, ...]]:
    """Return one exact phase-specific joint-impedance recovery fixture."""
    truths = {
        "transition": (1.8, 5.0, 72.0, 14.0, 3.5),
        "pre-impact": (1.8, 7.5, 96.0, 9.0, -2.0),
    }
    if phase_id not in truths:
        raise ValueError("phase_id must name a declared manufactured phase")
    design = _base_design()
    truth = truths[phase_id]
    response = design @ np.asarray(truth, dtype=float)
    joint_model = _models()[1]
    return joint_model, design, response, truth


def manufactured_confounded_case() -> tuple[IdentificationModel, np.ndarray, np.ndarray]:
    """Return exact stiffness/voluntary-basis confounding with one null direction."""
    design = _base_design()
    design[:, 4] = design[:, 2]
    truth = np.asarray((1.8, 5.0, 72.0, 14.0, 3.5), dtype=float)
    return _models()[1], design, design @ truth


def manufactured_emg_pair_declaration() -> EmgPairDeclaration:
    """Return the lead-side governed pair used by the synthetic proxy fixture."""
    return _emg_pairs()[0]


def manufactured_emg_pair() -> EmgEnvelopePair:
    """Return deterministic nonnegative normalized agonist/antagonist envelopes."""
    agonist = np.asarray((0.2, 0.4, 0.7, 0.9, 0.8, 0.5, 0.3, 0.1))
    antagonist = np.asarray((0.1, 0.3, 0.5, 0.4, 0.6, 0.4, 0.2, 0.1))
    declaration = manufactured_emg_pair_declaration()
    return EmgEnvelopePair(
        declaration.agonist_channel_id,
        declaration.antagonist_channel_id,
        agonist,
        antagonist,
    )


def manufactured_results() -> tuple[ImpedanceResult, ...]:
    """Return all evidence tiers and adverse outcomes without suppression."""
    return (
        ImpedanceResult(
            "phase-specific effective joint stiffness",
            "effective-mechanical",
            96.0,
            (90.0, 103.0),
            "Nm/rad",
            "supported",
            ("passive tissue basis", "perturbation bandwidth"),
            "The synthetic mechanical response closes inside its declared interval.",
        ),
        ImpedanceResult(
            "reflex-basis recovery error",
            "model-partitioned",
            0.18,
            (0.11, 0.26),
            "normalized RMS error",
            "negative",
            ("reflex delay", "passive basis", "voluntary basis"),
            "The adverse synthetic basis exceeds its preregistered recovery tolerance.",
        ),
        ImpedanceResult(
            "agonist-antagonist envelope overlap",
            "emg-proxy",
            0.46,
            (0.28, 0.61),
            "normalized proxy",
            "null",
            ("electrode placement", "EMG normalization", "muscle-pair selection"),
            "The proxy interval supports no unique mechanical partition.",
        ),
        ImpedanceResult(
            "individual biological actuator contribution",
            "unavailable",
            None,
            None,
            "N",
            "unavailable",
            (),
            "No declared observation identifies the requested biological source.",
        ),
    )


def manufactured_human_gate() -> HumanStudyGate:
    """Return the deliberately unavailable participant tier."""
    return HumanStudyGate(None, None, None, None, None, None, None, None, None, False)
