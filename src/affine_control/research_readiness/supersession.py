"""Supersession graph and exact-successor evidence validation."""

from __future__ import annotations

from typing import cast

from .errors import ResearchReadinessError


def _successor_map(records: list[dict[str, object]]) -> dict[str, str]:
    by_id = {str(record["protocol_id"]): record for record in records}
    successors: dict[str, str] = {}
    for record in records:
        successor = record.get("successor_protocol_id")
        state = str(record["state"])
        if state == "superseded" and successor is None:
            raise ResearchReadinessError("A superseded protocol requires an existing successor")
        if state != "superseded" and successor is not None:
            raise ResearchReadinessError("A non-superseded protocol cannot declare a successor")
        if successor is None:
            continue
        source = str(record["protocol_id"])
        target = str(successor)
        if target == source or target not in by_id:
            raise ResearchReadinessError(f"Invalid successor protocol ID: {target}")
        successors[source] = target
    return successors


def _reject_cycles(successors: dict[str, str]) -> None:
    for source in successors:
        visited = {source}
        target = successors[source]
        while target in successors:
            if target in visited:
                raise ResearchReadinessError("Supersession cycle is forbidden")
            visited.add(target)
            target = successors[target]


def _validate_successor_pin(
    record: dict[str, object], target: str, target_revision: object
) -> None:
    history = cast(list[dict[str, object]], record["history"])
    evidence = {
        str(item["evidence_id"]): item for item in cast(list[dict[str, object]], record["evidence"])
    }
    event = history[-1]
    linked = [evidence[str(value)] for value in cast(list[object], event["evidence_ids"])]
    exact = any(
        item.get("kind") == "supersession-record"
        and item.get("status") == "verified"
        and item.get("availability") in {"public", "private"}
        and item.get("related_protocol_id") == target
        and item.get("related_record_revision") == target_revision
        for item in linked
    )
    if not exact:
        source = record["protocol_id"]
        raise ResearchReadinessError(
            f"Supersession record for {source} does not pin successor {target} revision"
        )


def validate_supersession(records: list[dict[str, object]]) -> None:
    """Require an acyclic successor graph with exact revision-pinned evidence."""
    by_id = {str(record["protocol_id"]): record for record in records}
    successors = _successor_map(records)
    _reject_cycles(successors)
    for source, target in successors.items():
        _validate_successor_pin(by_id[source], target, by_id[target]["record_revision"])
