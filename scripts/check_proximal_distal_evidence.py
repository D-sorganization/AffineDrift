#!/usr/bin/env python3
"""Validate the pinned proximal-distal publication evidence without recomputing it."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import re
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

REPOSITORY = "D-sorganization/UpstreamDrift"
PENDING_STATE = "awaiting_upstream_merge"
PINNED_STATE = "pinned"
PUBLISHED_STATUS = "published"
WITHHELD_STATUS = "withheld_pending_pin"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
REQUIRED_QUANTITIES = {
    "force",
    "force_along_hand_path",
    "impulse",
    "power",
    "work",
    "joint_attribution",
}
REQUIRED_MODEL_TIERS = {
    "double_pendulum": "exact_planar_double_pendulum",
    "one_arm": "one_arm_three_link_point_mass",
    "two_arm": "two_arm_floating_club_closed_loop",
}
REQUIRED_COMPONENTS = {"total", "drift", "control", "zvcf"}
REQUIRED_CLOSURE_FIELDS = {
    "force_max_abs",
    "couple_max_abs",
    "power_max_abs",
    "work_max_abs",
}
MAX_CLOSURE_ERROR = 1e-8
TWO_HAND_MODE_CONVENTION = "common=right+left; differential=(right-left)/2"
PREVIEW_NUMERIC_FIELDS = {
    "time_constant_s",
    "best_preview_s",
    "reactive_rmse_nm",
    "preview_rmse_nm",
    "improvement_percent",
    "pointwise_ztcf_minimum_nm",
    "base_at_ztcf_minimum_nm",
    "control_residual_at_ztcf_minimum_nm",
}
PREVIEW_CLAIM_BOUNDARIES = {
    "human_preactivation": "not_established",
    "clubhead_speed_outcome": "not_evaluated",
    "muscle_activation": "not_modeled",
}


def load_manifest(path: Path) -> dict[str, Any]:
    """Load a JSON evidence manifest.

    Preconditions:
        ``path`` identifies a readable UTF-8 JSON file.
    Postconditions:
        The return value is a JSON object.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"evidence manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid evidence manifest JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("evidence manifest must be a JSON object")
    return payload


def _require_mapping(value: object, field: str, errors: list[str]) -> dict[str, Any]:
    """Return a mapping value or append a field-specific violation."""
    if isinstance(value, dict):
        return value
    errors.append(f"{field} must be an object")
    return {}


def _require_list(value: object, field: str, errors: list[str]) -> list[Any]:
    """Return a list value or append a field-specific violation."""
    if isinstance(value, list):
        return value
    errors.append(f"{field} must be a list")
    return []


def _validate_common(
    manifest: dict[str, Any], errors: list[str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate fields shared by pending and pinned states."""
    if manifest.get("schema_version") != "1.0.0":
        errors.append("schema_version must equal 1.0.0")
    source = _require_mapping(manifest.get("source"), "source", errors)
    evidence = _require_mapping(manifest.get("evidence"), "evidence", errors)
    if source.get("repository") != REPOSITORY:
        errors.append(f"source.repository must equal {REPOSITORY}")
    issue_url = source.get("issue_url")
    if not isinstance(issue_url, str) or not issue_url.endswith("/issues/8470"):
        errors.append("source.issue_url must identify UpstreamDrift issue 8470")
    _require_list(manifest.get("pin_procedure"), "pin_procedure", errors)
    _require_list(manifest.get("release_blockers"), "release_blockers", errors)
    return source, evidence


def _validate_pending(
    manifest: dict[str, Any], source: dict[str, Any], evidence: dict[str, Any], errors: list[str]
) -> None:
    """Ensure a placeholder cannot carry evidence or look publishable."""
    if source.get("commit") is not None:
        errors.append("pending source.commit must be null")
    if manifest.get("artifacts") not in ([], None):
        errors.append("pending manifest must not contain claim artifacts")
    if manifest.get("regeneration_commands") not in ([], None):
        errors.append("pending manifest must not contain regeneration commands")
    if evidence.get("status") != WITHHELD_STATUS:
        errors.append(f"pending evidence.status must equal {WITHHELD_STATUS}")
    if evidence.get("model_tiers") not in ([], None):
        errors.append("pending manifest must not contain model-tier results")
    if evidence.get("quantities") not in ([], None):
        errors.append("pending manifest must not contain published quantities")
    blockers = manifest.get("release_blockers")
    if not isinstance(blockers, list) or not blockers:
        errors.append("pending manifest must declare at least one release blocker")


def _artifact_errors(artifacts: list[Any], root: Path) -> list[str]:
    """Return integrity errors for pinned artifact records."""
    errors: list[str] = []
    for index, record_value in enumerate(artifacts):
        record = _require_mapping(record_value, f"artifacts[{index}]", errors)
        relative = record.get("path")
        digest = record.get("sha256")
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
            errors.append(f"artifacts[{index}].path must be a non-empty relative path")
            continue
        if not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
            errors.append(f"artifacts[{index}].sha256 must be 64 lowercase hexadecimal characters")
            continue
        root_resolved = root.resolve()
        path = (root / relative).resolve()
        try:
            path.relative_to(root_resolved)
        except ValueError:
            errors.append(f"artifact escapes the declared root: {relative}")
            continue
        if not path.is_file():
            errors.append(f"artifact is missing: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"SHA-256 mismatch for artifact: {relative}")
    return errors


def _is_finite_number(value: object) -> bool:
    """Return whether ``value`` is a finite real number but not a boolean."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _validate_component_values(value: object, field: str, errors: list[str]) -> None:
    """Validate a total/drift/control/ZVCF scalar component record."""
    components = _require_mapping(value, field, errors)
    missing = sorted(REQUIRED_COMPONENTS - set(components))
    if missing:
        errors.append(f"{field} missing components: {', '.join(missing)}")
    for name in REQUIRED_COMPONENTS & set(components):
        if not _is_finite_number(components[name]):
            errors.append(f"{field}.{name} must be finite")


def _validate_model_results(evidence: dict[str, Any]) -> list[str]:
    """Validate the compact three-tier numerical evidence contract."""
    errors: list[str] = []
    results = _require_mapping(evidence.get("results"), "evidence.results", errors)
    missing = sorted(set(REQUIRED_MODEL_TIERS) - set(results))
    if missing:
        errors.append(f"evidence.results missing model results: {', '.join(missing)}")

    for name, expected_tier in REQUIRED_MODEL_TIERS.items():
        if name not in results:
            continue
        field = f"evidence.results.{name}"
        record = _require_mapping(results[name], field, errors)
        if record.get("model_tier") != expected_tier:
            errors.append(f"{field}.model_tier must equal {expected_tier}")
        for text_field in ("trajectory_kind", "integration_interpretation"):
            value = record.get(text_field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field}.{text_field} must be a non-empty string")

        estimand_field = f"{field}.primary_estimand"
        estimand = _require_mapping(record.get("primary_estimand"), estimand_field, errors)
        path_length = estimand.get("path_length_m")
        if not _is_finite_number(path_length) or float(path_length) <= 0.0:
            errors.append(f"{estimand_field}.path_length_m must be finite and positive")
        for text_field in ("reference_point", "force_direction"):
            value = estimand.get(text_field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{estimand_field}.{text_field} must be a non-empty string")
        _validate_component_values(
            estimand.get("force_work_j"), f"{estimand_field}.force_work_j", errors
        )
        _validate_component_values(
            estimand.get("mean_force_n"), f"{estimand_field}.mean_force_n", errors
        )

        closure_field = f"{field}.closure"
        closure = _require_mapping(record.get("closure"), closure_field, errors)
        for closure_name in REQUIRED_CLOSURE_FIELDS:
            value = closure.get(closure_name)
            if not _is_finite_number(value) or abs(float(value)) > MAX_CLOSURE_ERROR:
                errors.append(
                    f"{closure_field}.{closure_name} must be finite and no greater than "
                    f"{MAX_CLOSURE_ERROR:g} in magnitude"
                )

        if (
            name == "two_arm"
            and record.get("common_differential_convention") != TWO_HAND_MODE_CONVENTION
        ):
            errors.append(
                f"{field}.common_differential_convention must equal {TWO_HAND_MODE_CONVENTION}"
            )
    return errors


def _validate_bounded_preview(evidence: dict[str, Any]) -> list[str]:
    """Validate the bounded signal hypothesis without promoting it to physiology."""
    errors: list[str] = []
    field = "evidence.bounded_preview_hypothesis"
    hypothesis = _require_mapping(evidence.get("bounded_preview_hypothesis"), field, errors)
    if hypothesis.get("study_type") != "model_only_delayed_actuator_preview_hypothesis":
        errors.append(f"{field}.study_type must remain model-only")
    for name in PREVIEW_NUMERIC_FIELDS:
        if not _is_finite_number(hypothesis.get(name)):
            errors.append(f"{field}.{name} must be finite")
    for name in ("time_constant_s", "reactive_rmse_nm", "preview_rmse_nm"):
        value = hypothesis.get(name)
        if _is_finite_number(value) and float(value) <= 0.0:
            errors.append(f"{field}.{name} must be positive")
    preview = hypothesis.get("best_preview_s")
    if _is_finite_number(preview) and float(preview) < 0.0:
        errors.append(f"{field}.best_preview_s must be nonnegative")
    improvement = hypothesis.get("improvement_percent")
    if _is_finite_number(improvement) and not 0.0 <= float(improvement) <= 100.0:
        errors.append(f"{field}.improvement_percent must be between 0 and 100")
    for name, required in PREVIEW_CLAIM_BOUNDARIES.items():
        if hypothesis.get(name) != required:
            errors.append(f"{field}.{name} must equal {required}")
    return errors


def _validate_pinned(
    manifest: dict[str, Any], source: dict[str, Any], evidence: dict[str, Any], root: Path
) -> list[str]:
    """Validate exact-commit provenance and the compact publication contract."""
    errors: list[str] = []
    commit = source.get("commit")
    if not isinstance(commit, str) or SHA40.fullmatch(commit) is None:
        errors.append("pinned source.commit must be a 40-character lowercase hexadecimal SHA")
    commands = _require_list(manifest.get("regeneration_commands"), "regeneration_commands", errors)
    if not commands or not all(isinstance(command, str) and command for command in commands):
        errors.append("pinned manifest must contain regeneration commands")
    artifacts = _require_list(manifest.get("artifacts"), "artifacts", errors)
    if not artifacts:
        errors.append("pinned manifest must contain at least one artifact")
    errors.extend(_artifact_errors(artifacts, root))
    if evidence.get("status") != PUBLISHED_STATUS:
        errors.append(f"pinned evidence.status must equal {PUBLISHED_STATUS}")
    tiers = evidence.get("model_tiers")
    if not isinstance(tiers, list) or not tiers:
        errors.append("pinned evidence must declare model_tiers")
    elif set(tiers) != set(REQUIRED_MODEL_TIERS.values()):
        errors.append("pinned evidence must declare exactly the three required model tiers")
    quantities = evidence.get("quantities")
    present = set(quantities) if isinstance(quantities, list) else set()
    missing = sorted(REQUIRED_QUANTITIES - present)
    if missing:
        errors.append(f"pinned evidence missing required quantities: {', '.join(missing)}")
    errors.extend(_validate_model_results(evidence))
    errors.extend(_validate_bounded_preview(evidence))
    if manifest.get("release_blockers") != []:
        errors.append("pinned manifest must have no release blockers")
    return errors


def validate_manifest(manifest: dict[str, Any], artifact_root: Path) -> list[str]:
    """Return every contract violation without contacting another repository."""
    errors: list[str] = []
    source, evidence = _validate_common(manifest, errors)
    state = manifest.get("publication_state")
    if state == PENDING_STATE:
        _validate_pending(manifest, source, evidence, errors)
    elif state == PINNED_STATE:
        errors.extend(_validate_pinned(manifest, source, evidence, artifact_root))
    else:
        errors.append(f"publication_state must equal {PENDING_STATE} or {PINNED_STATE}")
    return errors


def publication_ready(manifest: dict[str, Any]) -> bool:
    """Return whether the manifest explicitly represents pinned evidence."""
    return (
        manifest.get("publication_state") == PINNED_STATE
        and isinstance(manifest.get("evidence"), dict)
        and manifest["evidence"].get("status") == PUBLISHED_STATUS
    )


def main() -> int:
    """Validate the repository manifest, optionally requiring a completed pin."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/proximal_distal_energy_transfer/hand_path_attribution_snapshot.json"),
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=Path("."),
        help="root for repository-relative artifact paths (default: current directory)",
    )
    parser.add_argument("--require-pinned", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        manifest = load_manifest(args.manifest)
    except ValueError as exc:
        LOGGER.error("%s", exc)
        return 1
    errors = validate_manifest(manifest, args.artifact_root)
    if errors:
        for error in errors:
            LOGGER.error("%s", error)
        return 1
    if args.require_pinned and not publication_ready(manifest):
        LOGGER.error("evidence is structurally valid but remains withheld pending an exact pin")
        return 1
    if publication_ready(manifest):
        LOGGER.info("proximal-distal evidence is pinned and publishable")
    else:
        LOGGER.warning("proximal-distal evidence is withheld pending an exact upstream pin")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
