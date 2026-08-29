"""Deterministic fixtures for the bilateral hand-wrench protocol."""

from __future__ import annotations

import numpy as np

from src.affine_control.hand_wrench_evidence import HumanTierGate, LoadResult
from src.affine_control.hand_wrench_protocol import (
    AnalysisContract,
    BandwidthSample,
    Hand,
    Hypothesis,
    Preregistration,
    SensorCalibration,
    SourceRecord,
    WrenchTransform,
)


def manufactured_sensor(hand: Hand) -> SensorCalibration:
    """Return one exact full-rank six-axis cross-talk declaration."""
    matrix = np.eye(6)
    matrix[0, 1] = 0.01
    matrix[2, 4] = -0.008
    matrix[5, 3] = 0.006
    return SensorCalibration(
        sensor_id=f"{hand}-grip-six-axis/v1",
        hand=hand,
        output_frame=f"{hand}-sensor-frame",
        calibration_matrix=tuple(tuple(float(value) for value in row) for row in matrix),
        sample_rate_hz=2000.0,
        bandwidth_hz=300.0,
        maximum_passband_gain_error=0.03,
        maximum_condition_number=1.1,
        traceability="manufactured deadweight and applied-moment fixture; not device calibration",
        revision="manufactured-cross-talk/v1",
    )


def manufactured_frames() -> tuple[WrenchTransform, WrenchTransform]:
    """Return lead and trail sensor frames registered to one club frame."""
    identity = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    lead = WrenchTransform(
        "lead-sensor-frame",
        "club-grip-center-frame",
        identity,
        (-0.1, 0.0, 0.0),
    )
    trail = WrenchTransform(
        "trail-sensor-frame",
        "club-grip-center-frame",
        identity,
        (0.1, 0.0, 0.0),
    )
    return lead, trail


def manufactured_preregistration() -> Preregistration:
    """Return the source-bounded preregistration without human authority."""
    sources = (
        SourceRecord(
            "koike-2016",
            "primary-literature",
            "Koike (2016), Measurement of Individual Hand Forces Exerted on a Golf Club Grip",
            "instrumented-grip measurement precedent",
            "conference report is not this device calibration or a governed data deposit",
        ),
        SourceRecord(
            "choi-park-2020",
            "primary-literature",
            "Choi and Park (2020), Sensors 20(13):3672, doi:10.3390/s20133672",
            "measured internal grip force used in upper-limb kinetics",
            "does not validate this protocol, device, cohort, or bilateral six-axis accuracy",
        ),
        SourceRecord(
            "upstream-identifiability-2026",
            "immutable-executable",
            "UpstreamDrift 85cce4d3 bilateral-wrench structural-identifiability study",
            "rank-five point-force and rank-six/nullity-six full-wrench maps",
            "synthetic structural result; no practical or human validation",
        ),
        SourceRecord(
            "upstream-sensor-qualification-2026",
            "immutable-executable",
            "UpstreamDrift 85cce4d3 trajectory-level point-force sensor qualification",
            "cross-talk, noise, contact migration, and allocation-error controls",
            "synthetic point-force fixture; not physical-device calibration",
        ),
    )
    analysis = AnalysisContract(
        analysis_window="predeclared transition-to-impact window with event-aligned endpoints",
        synchronization_tolerance_s=0.0005,
        inertial_compensation="subtract registered club, sensor, and fixture inertial wrench",
        contact_assumptions=(
            "each sensor reports the complete wrench transmitted through its grip section",
            "distributed pressure and changing centers of pressure remain sensitivity inputs",
        ),
        exclusion_rules=(
            "exclude saturation, clipping, timestamp discontinuity, or calibration expiry",
            "retain failed, negative, null, and unavailable trials in the disposition ledger",
        ),
        uncertainty_method=(
            "calibration, synchronization, contact, shaft, and grip perturbation envelope"
        ),
        participant_split="participant-held-out",
        shaft_sensitivity="repeat over predeclared shaft mass, inertia, and compliance bounds",
        grip_sensitivity="repeat over predeclared grip compliance and contact-center bounds",
    )
    hypotheses = (
        Hypothesis(
            "H1-total-does-not-allocate",
            "bilateral wrench allocation",
            "observation-map rank and nullity",
            "total sensing remains rank six with nullity six",
            "a declared full-wrench total map uniquely recovers all twelve hand components",
            "negative",
        ),
        Hypothesis(
            "H2-calibration-recovery",
            "bilateral calibrated wrench",
            "componentwise recovery error with uncertainty",
            "complete interval remains inside the preregistered tolerance",
            "either hand exceeds tolerance or required passband evidence is missing",
            "null",
        ),
        Hypothesis(
            "H3-human-transport",
            "participant-held-out bilateral trajectory",
            "held-out prediction and coverage error",
            "evaluate only after every human governance gate is satisfied",
            "governed participant data or approval records are absent",
            "unavailable",
        ),
    )
    return Preregistration(
        protocol_id="affinedrift.bilateral-hand-wrench/v1",
        sources=sources,
        sensors=(manufactured_sensor("lead"), manufactured_sensor("trail")),
        frames=manufactured_frames(),
        analysis=analysis,
        hypotheses=hypotheses,
    )


def manufactured_wrench_pair() -> tuple[np.ndarray, np.ndarray]:
    """Return exact lead and trail six-axis sensor wrenches."""
    lead = np.array([12.0, -5.0, 30.0, 0.5, 1.2, -0.4])
    trail = np.array([-2.0, 8.0, 20.0, -0.7, 0.2, 0.3])
    return lead, trail


def manufactured_calibration_case() -> tuple[SensorCalibration, np.ndarray, np.ndarray]:
    """Return an exact applied-wrench and cross-talk-corrupted raw signal."""
    calibration = manufactured_sensor("lead")
    applied = np.array([100.0, -50.0, 250.0, 4.0, -8.0, 3.0])
    raw = calibration.matrix @ applied
    return calibration, applied, raw


def manufactured_bandwidth_samples() -> tuple[BandwidthSample, ...]:
    """Return complete passband samples through the declared boundary."""
    return (
        BandwidthSample(0.0, 1.0),
        BandwidthSample(50.0, 1.002),
        BandwidthSample(150.0, 0.995),
        BandwidthSample(300.0, 0.98),
    )


def manufactured_benchtop_results() -> tuple[LoadResult, ...]:
    """Return all evidence tiers and adverse dispositions without suppression."""
    return (
        LoadResult(
            "total club wrench closure error",
            "total-measured",
            0.004,
            (0.002, 0.008),
            "normalized wrench error",
            "supported",
            ("shaft inertia", "grip reference point"),
            "Manufactured benchtop total-wrench closure only.",
        ),
        LoadResult(
            "bilateral allocation recovery error",
            "bilateral-measured",
            0.025,
            (0.015, 0.041),
            "normalized wrench error",
            "negative",
            ("shaft compliance", "grip cross-talk"),
            "The declared adverse perturbation exceeds its synthetic tolerance.",
        ),
        LoadResult(
            "regularized bilateral allocation advantage",
            "model-estimated",
            0.0,
            (-0.08, 0.08),
            "normalized error difference",
            "null",
            ("shaft stiffness", "grip compliance"),
            "The model-selected allocation has no advantage in this fixture.",
        ),
        LoadResult(
            "individual biological actuator force",
            "unavailable",
            None,
            None,
            "N",
            "unavailable",
            (),
            "No observation map identifies this quantity.",
        ),
    )


def manufactured_human_gate() -> HumanTierGate:
    """Return the deliberately unavailable participant tier."""
    return HumanTierGate(None, None, None, None, False)
