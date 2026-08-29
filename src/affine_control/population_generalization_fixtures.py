"""Deterministic manufactured fixtures for population-generalization contracts."""

from __future__ import annotations

from .population_generalization import (
    DatasetCard,
    EvidenceOrigin,
    LockedSplit,
    Observation,
    PopulationProtocol,
    Preregistration,
    SplitAssignment,
)


def manufactured_observations() -> tuple[Observation, ...]:
    """Return nested records with one untouched manufactured site."""
    rows = (
        (
            "r1",
            "site-a",
            "p1",
            "s1",
            "driver-a",
            "t1",
            "developing",
            "F",
            "adult",
            "R",
            "short",
            8.0,
            8.0,
        ),
        (
            "r2",
            "site-a",
            "p2",
            "s2",
            "driver-a",
            "t2",
            "advanced",
            "M",
            "adult",
            "R",
            "tall",
            12.0,
            11.0,
        ),
        (
            "r3",
            "site-b",
            "p3",
            "s3",
            "driver-b",
            "t3",
            "developing",
            "F",
            "older",
            "L",
            "short",
            9.0,
            10.0,
        ),
        (
            "r4",
            "site-b",
            "p4",
            "s4",
            "driver-b",
            "t4",
            "advanced",
            "M",
            "older",
            "R",
            "tall",
            14.0,
            13.0,
        ),
        (
            "r5",
            "site-c",
            "p5",
            "s5",
            "driver-c",
            "t5",
            "developing",
            "F",
            "adult",
            "L",
            "short",
            10.0,
            10.0,
        ),
        (
            "r6",
            "site-c",
            "p6",
            "s6",
            "driver-c",
            "t6",
            "advanced",
            "M",
            "older",
            "R",
            "tall",
            15.0,
            20.0,
        ),
    )
    return tuple(Observation(*row) for row in rows)


def manufactured_split() -> LockedSplit:
    """Freeze a train/validation/site-held-out manufactured partition."""
    return LockedSplit(
        split_id="manufactured-population-split-v1",
        strategies=("participant-held-out", "session-held-out", "site-held-out"),
        assignments=(
            SplitAssignment("r1", "train"),
            SplitAssignment("r2", "train"),
            SplitAssignment("r3", "validation"),
            SplitAssignment("r4", "validation"),
            SplitAssignment("r5", "test"),
            SplitAssignment("r6", "test"),
        ),
        locked_test_set=True,
        lock_revision="manufactured-split-sha256-pending-public-report",
        tuning_partitions=("train", "validation"),
    )


def build_manufactured_protocol() -> PopulationProtocol:
    """Build the non-authorizing source-bounded protocol fixture."""
    card = DatasetCard(
        dataset_id="manufactured-population-fixture-v1",
        target_population="future consenting adult golfers under a separately approved protocol",
        sampling_frame="manufactured balanced fixture only",
        cohort_strata=("skill", "sex", "age", "handedness", "anthropometry", "equipment"),
        hierarchy=("site", "participant", "session", "equipment", "trial"),
        repeated_measure_unit="trial nested within equipment, session, participant, and site",
        missingness_plan=(
            "retain missingness reasons; predeclare complete-case and bounded sensitivity"
        ),
        exclusion_rules=(
            "exclude only preregistered acquisition failures",
            "never exclude a negative or null result because of its direction",
        ),
        privacy_plan="no direct identifiers; suppress cells below the declared minimum",
        consent_plan="future participant use requires study-specific informed consent",
        ethics_review="unavailable; independent human review is required before collection",
        license="manufactured fixture CC0; participant-data license unavailable",
        source_revision="affinedrift-4039-manufactured-v1",
        evidence_origin=EvidenceOrigin.MANUFACTURED_SYNTHETIC,
    )
    preregistration = Preregistration(
        status="template-only",
        estimand="participant-held-out prediction error in declared SI outcome units",
        predictors=("predeclared model outputs", "skill", "anthropometry", "equipment"),
        outcome="held-out scalar task outcome; manufactured units in the fixture",
        metric=(
            "mean absolute error, calibration intercept/slope, and participant-weighted interval"
        ),
        subgroup_plan="report declared strata; suppress cells below the fixed minimum",
        sensitivity_plan=(
            "missingness, exclusion, equipment, site, and analysis-choice perturbations"
        ),
        falsifiers=(
            "participant/session/site leakage",
            "calibration slope outside tolerance",
            "external-site error above the preregistered threshold",
            "unsupported subgroup or population promotion",
        ),
    )
    return PopulationProtocol(
        revision="affinedrift.population-generalization/v1",
        dataset_card=card,
        preregistration=preregistration,
        split=manufactured_split(),
        estimands=(
            "within-person explanation",
            "between-person association",
            "prediction",
            "causal inference",
        ),
        external_validation_status="unavailable",
        authority_limit=(
            "Manufactured validation mechanics provide no coaching, clinical, design, causal, "
            "or population authority."
        ),
    )
