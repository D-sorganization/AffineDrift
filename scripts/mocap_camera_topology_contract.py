"""Fail-closed contract for markerless-mocap camera topology evaluations."""

from __future__ import annotations

from scripts.mocap_camera_registry_contract import (
    CameraRegistryError,
    require_array,
    require_object,
    require_text,
    require_unique_texts,
)

TOPOLOGY_FIELDS = {
    "id",
    "subject_id",
    "manufacturer",
    "model",
    "role",
    "camera_count",
    "qualification_state",
    "claim_ids",
    "runtime_authority",
    "procurement_authority",
    "limitations",
}
REQUIRED_TOPOLOGY_ATTRIBUTES = frozenset(
    {
        "transport",
        "synchronization",
        "power",
        "cable_distance",
        "host_controller_topology",
        "sdk_gentl",
        "aggregate_bandwidth",
        "storage_budget",
        "thermals",
        "licensing",
        "operating_systems",
        "quote_scope",
    }
)
ROLE_CONTRACTS = {
    "pilot_role": (2, "pilot_candidate_unqualified"),
    "reference_topology_role": (8, "reference_hypothesis_unqualified"),
    "distributed_challenger_role": (8, "challenger_unqualified"),
}


def _verify_claim_coverage(
    evaluation_id: str,
    subject_id: str,
    claim_ids: list[str],
    claims: dict[str, tuple[str, str]],
) -> None:
    attributes: set[str] = set()
    for claim_id in claim_ids:
        if claim_id not in claims:
            raise CameraRegistryError(
                f"topology {evaluation_id} references unknown claim id: {claim_id}"
            )
        claim_subject, attribute = claims[claim_id]
        if claim_subject != subject_id:
            raise CameraRegistryError(
                f"topology claim {claim_id} belongs to {claim_subject}, not {subject_id}"
            )
        attributes.add(attribute)
    if attributes != REQUIRED_TOPOLOGY_ATTRIBUTES:
        raise CameraRegistryError(
            f"topology {evaluation_id} attributes differ: "
            f"missing={sorted(REQUIRED_TOPOLOGY_ATTRIBUTES - attributes)}, "
            f"extra={sorted(attributes - REQUIRED_TOPOLOGY_ATTRIBUTES)}"
        )


def _verify_evaluation(
    value: object,
    index: int,
    claims: dict[str, tuple[str, str]],
) -> tuple[str, str]:
    evaluation = require_object(value, f"topology evaluation {index}", TOPOLOGY_FIELDS)
    evaluation_id = require_text(evaluation["id"], f"topology evaluation {index} id")
    subject_id = require_text(evaluation["subject_id"], f"topology {evaluation_id} subject")
    require_text(evaluation["manufacturer"], f"topology {evaluation_id} manufacturer")
    require_text(evaluation["model"], f"topology {evaluation_id} model")
    require_text(evaluation["limitations"], f"topology {evaluation_id} limitations")
    role = require_text(evaluation["role"], f"topology {evaluation_id} role")
    if role not in ROLE_CONTRACTS:
        raise CameraRegistryError(f"topology {evaluation_id} role is unsupported")
    expected_count, expected_state = ROLE_CONTRACTS[role]
    if type(evaluation["camera_count"]) is not int or evaluation["camera_count"] != expected_count:
        raise CameraRegistryError(f"topology {evaluation_id} camera count does not match its role")
    if evaluation["qualification_state"] != expected_state:
        raise CameraRegistryError(
            f"topology {evaluation_id} qualification state does not match its role"
        )
    if evaluation["runtime_authority"] != "none":
        raise CameraRegistryError(f"topology {evaluation_id} may not grant runtime authority")
    if evaluation["procurement_authority"] is not False:
        raise CameraRegistryError(f"topology {evaluation_id} may not approve procurement")
    claim_ids = require_unique_texts(evaluation["claim_ids"], f"topology {evaluation_id} claims")
    _verify_claim_coverage(evaluation_id, subject_id, claim_ids, claims)
    return evaluation_id, role


def verify_topology_evaluations(
    value: object,
    claims: dict[str, tuple[str, str]],
) -> int:
    """Validate distinct pilot, reference, and challenger topology records."""

    evaluation_ids: set[str] = set()
    roles: set[str] = set()
    for index, item in enumerate(require_array(value, "topology evaluations")):
        evaluation_id, role = _verify_evaluation(item, index, claims)
        if evaluation_id in evaluation_ids:
            raise CameraRegistryError(f"duplicate topology evaluation id: {evaluation_id}")
        if role in roles:
            raise CameraRegistryError(f"duplicate topology role: {role}")
        evaluation_ids.add(evaluation_id)
        roles.add(role)
    if roles != set(ROLE_CONTRACTS):
        raise CameraRegistryError("topology evaluations must preserve all required roles")
    return len(evaluation_ids)
