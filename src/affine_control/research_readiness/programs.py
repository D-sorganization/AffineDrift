"""Bounded scientific metadata for the companion E1--E8 programs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProgramSeed:
    """Scientific metadata needed to create one manufactured protocol record."""

    issue: int
    slug: str
    title: str
    route: str
    question: str
    outcome: str
    intervention: str
    measurement: str
    unit: str
    frame: str
    participant_scope: str
    evidence_origin: str
    calculation_path: str
    workflow_path: str


PROGRAMS = (
    ProgramSeed(
        4033,
        "dcr-perturbation",
        "DCR and Finite-Horizon Reachability",
        "/articles/controllability-drift-ratio.html",
        "When does a declared DCR fail to predict bounded event-time reachability?",
        "reachable-set width and event-state sensitivity",
        "modeled bounded input perturbation",
        "projected acceleration and event state",
        "declared SI units",
        "declared model coordinates",
        "none",
        "analytical",
        "tests/test_scientific_trust_metadata.py",
        "tests/test_dcr_reachability_contract.py",
    ),
    ProgramSeed(
        4034,
        "model-ladder",
        "Planar-to-Flexible-Shaft Model Ladder",
        "/models/model-ladder.html",
        "Which declared conclusions change across planar, spatial, closed-chain, "
        "and flexible-shaft models?",
        "cross-rung discrepancy and promotion decision",
        "modeled rung promotion",
        "state, constraint, and shaft-response discrepancy",
        "declared SI units",
        "rung-specific declared frames",
        "none",
        "modeled",
        "src/affine_control/model_ladder_fixtures.py",
        "src/affine_control/model_ladder_protocol.py",
    ),
    ProgramSeed(
        4035,
        "bilateral-hand-wrench",
        "Bilateral Hand-Wrench Identification",
        "/models/bilateral-hand-wrench-validation.html",
        "Can instrumented bilateral grip measurements identify declared hand-wrench "
        "components within calibration limits?",
        "identifiability rank and wrench error",
        "planned instrumented-grip perturbation",
        "bilateral force and moment",
        "N and N m",
        "declared grip frame",
        "human",
        "manufactured-synthetic",
        "src/affine_control/hand_wrench_fixtures.py",
        "src/affine_control/hand_wrench_protocol.py",
    ),
    ProgramSeed(
        4036,
        "active-impedance",
        "Active Impedance Identification",
        "/models/active-impedance-identification.html",
        "Can declared perturbations distinguish active impedance from modeled passive response?",
        "stiffness, damping, and residual diagnostics",
        "planned mechanical perturbation",
        "displacement, force, activation, and response",
        "m, N, and normalized activation",
        "declared segment and perturbation frames",
        "human",
        "manufactured-synthetic",
        "src/affine_control/impedance_result_fixtures.py",
        "src/affine_control/impedance_protocol.py",
    ),
    ProgramSeed(
        4037,
        "neural-timing",
        "Neural Timing and Feedback Perturbation",
        "/models/neural-timing-feedback.html",
        "Which timing hypotheses remain distinguishable under declared sensory and "
        "mechanical perturbations?",
        "latency-window and response-contrast estimates",
        "planned sensory or mechanical perturbation",
        "event time, kinematics, and activation",
        "s, rad, and normalized activation",
        "declared event-aligned frames",
        "human",
        "manufactured-synthetic",
        "src/affine_control/neural_timing_fixtures.py",
        "src/affine_control/neural_timing_analysis.py",
    ),
    ProgramSeed(
        4038,
        "hybrid-impact",
        "Hybrid Impact and Event-Time Uncertainty",
        "/models/hybrid-impact-contact.html",
        "How do contact-model and event-time choices affect declared impact outcomes?",
        "impulse, event-time, and post-impact sensitivity",
        "modeled contact and timing perturbation",
        "contact state, impulse, and event time",
        "m, m/s, N s, and s",
        "declared club-ball contact frame",
        "none",
        "modeled",
        "src/affine_control/impact_contact_fixtures.py",
        "src/affine_control/impact_contact_models.py",
    ),
    ProgramSeed(
        4039,
        "population-generalization",
        "Population Generalization and Held-Out Validation",
        "/models/population-generalization.html",
        "What evidence would support transport beyond a development sample without "
        "participant, session, site, or equipment leakage?",
        "held-out error, calibration, subgroup, and transportability metrics",
        "planned group-held-out evaluation",
        "predictions, outcomes, group IDs, and calibration",
        "declared outcome units",
        "declared measurement frames",
        "human",
        "manufactured-synthetic",
        "src/affine_control/population_generalization_fixtures.py",
        "src/affine_control/population_generalization.py",
    ),
    ProgramSeed(
        4040,
        "equipment-response",
        "Equipment Individual-Response Validation",
        "/models/equipment-individual-response.html",
        "Which equipment-response differences are identifiable within custody, calibration, "
        "repeated-measures, and multiplicity limits?",
        "individual contrast, interval, repeatability, and sensitivity",
        "planned randomized equipment condition",
        "equipment state, shaft response, and impact outcome",
        "declared SI and launch-monitor units",
        "declared equipment and laboratory frames",
        "human",
        "manufactured-synthetic",
        "src/affine_control/equipment_response_fixtures.py",
        "src/affine_control/equipment_response_analysis.py",
    ),
)
