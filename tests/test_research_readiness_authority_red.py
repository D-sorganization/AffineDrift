"""RED contracts for readiness authority and referential integrity."""

from __future__ import annotations

import copy
from typing import cast

import pytest

from src.affine_control.research_readiness import ResearchReadinessError
from tests.research_readiness_test_support import (
    canonical_library,
    links,
    opaque_evidence,
    protocol,
    reseal,
    specification,
    validate,
)


def test_self_declared_human_approvals_cannot_advance_readiness() -> None:
    """Protocol owners cannot mint their own risk, calibration, or ethics authority."""
    library = canonical_library()
    record = protocol(library, "ad-protocol-active-impedance-001")
    evidence = cast(list[dict[str, object]], record["evidence"])
    history = cast(list[dict[str, object]], record["history"])
    kinds = (
        ("evidence-self-risk", "pilot-risk-review"),
        ("evidence-self-calibration", "calibration-plan"),
        ("evidence-self-ethics", "ethics-approval"),
    )
    evidence.extend(opaque_evidence(record, evidence_id, kind) for evidence_id, kind in kinds)
    history.extend(
        [
            {
                "from": "simulation-ready",
                "to": "pilot-ready",
                "on": "2026-08-29",
                "rationale": "Adversarial self-declaration.",
                "evidence_ids": ["evidence-self-risk", "evidence-self-calibration"],
            },
            {
                "from": "pilot-ready",
                "to": "ethics-approved",
                "on": "2026-08-29",
                "rationale": "Adversarial self-declaration.",
                "evidence_ids": ["evidence-self-ethics"],
            },
        ]
    )
    record["state"] = "ethics-approved"
    reseal(record)

    with pytest.raises(ResearchReadinessError, match="authority|independent|self-declared"):
        validate(library)


def test_top_level_evidence_origin_must_reconcile_with_declared_quantities() -> None:
    """A manufactured protocol cannot relabel its public aggregate origin as measured."""
    library = canonical_library()
    record = protocol(library, "ad-protocol-active-impedance-001")
    record["evidence_origin"] = "measured"
    reseal(record)

    with pytest.raises(ResearchReadinessError, match="evidence origin|quantity class"):
        validate(library)


@pytest.mark.parametrize("collection", ["estimands", "hypotheses", "calibrations"])
def test_scientific_specification_ids_are_unique(collection: str) -> None:
    """Repeated scientific IDs cannot create ambiguous joins."""
    library = canonical_library()
    record = protocol(library)
    records = cast(list[dict[str, object]], specification(record)[collection])
    records.append(copy.deepcopy(records[0]))
    reseal(record, scientific_change=True)

    with pytest.raises(ResearchReadinessError, match=f"duplicate.*{collection}"):
        validate(library)


def test_measurements_must_reference_a_declared_calibration() -> None:
    """Every measurement calibration ID must resolve inside its specification."""
    library = canonical_library()
    record = protocol(library)
    measurements = cast(list[dict[str, object]], specification(record)["measurements"])
    measurements[0]["calibration_id"] = "cal-missing"
    reseal(record, scientific_change=True)

    with pytest.raises(ResearchReadinessError, match="calibration.*cal-missing"):
        validate(library)


def test_verified_calibration_requires_matching_verified_evidence() -> None:
    """Changing a plan label cannot mint a verified calibration record."""
    library = canonical_library()
    record = protocol(library)
    calibrations = cast(list[dict[str, object]], specification(record)["calibrations"])
    calibrations[0]["status"] = "verified"
    reseal(record, scientific_change=True)

    with pytest.raises(ResearchReadinessError, match="verified calibration.*evidence"):
        validate(library)


def test_calculation_and_workflow_artifact_roles_cannot_be_swapped() -> None:
    """Exact bytes do not establish the scientific role of an artifact."""
    library = canonical_library()
    record = protocol(library, "ad-protocol-active-impedance-001")
    authority_links = links(record)
    workflows = cast(list[dict[str, object]], authority_links["workflow_artifacts"])
    authority_links["calculation_artifacts"] = [copy.deepcopy(workflows[0])]
    reseal(record)

    with pytest.raises(ResearchReadinessError, match="artifact role|calculation artifact"):
        validate(library)


def test_route_audit_links_are_unique() -> None:
    """A protocol cannot count the same reviewed route more than once."""
    library = canonical_library()
    record = protocol(library)
    route_links = cast(list[dict[str, object]], links(record)["route_audits"])
    route_links.append(copy.deepcopy(route_links[0]))
    reseal(record)

    with pytest.raises(ResearchReadinessError, match="duplicate route audit"):
        validate(library)


def test_artifacts_must_belong_to_a_declared_route_audit() -> None:
    """Artifact evidence cannot rely on an undeclared route authority."""
    library = canonical_library()
    record = protocol(library)
    other = protocol(library, "ad-protocol-hybrid-impact-001")
    links(record)["route_audits"] = copy.deepcopy(links(other)["route_audits"])
    reseal(record)

    with pytest.raises(ResearchReadinessError, match="artifact.*declared route audit"):
        validate(library)


def test_verified_validation_release_must_match_state_and_evidence() -> None:
    """A detached release reference cannot coexist with simulation-ready state."""
    library = canonical_library()
    record = protocol(library)
    links(record)["validation_release"] = {
        "status": "verified",
        "release_id": "self-declared-release",
        "record_revision": "1" * 64,
    }
    reseal(record)

    with pytest.raises(ResearchReadinessError, match="validation release.*state|release evidence"):
        validate(library)
