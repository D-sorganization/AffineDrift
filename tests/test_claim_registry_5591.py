"""Regression tests for claim registry accuracy, provenance uniqueness, and tiering (#5591)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.generate_trust_panels import (
    DEFAULT_REGISTRY,
    DEFAULT_SCHEMA,
    TrustContractError,
    validate_registry,
)
from src.affine_control.evidence_presentation.generator import (
    build_evidence_presentation_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def _load_claims_by_id() -> dict[str, dict[str, object]]:
    data = json.loads(DEFAULT_REGISTRY.read_text(encoding="utf-8"))
    by_id: dict[str, dict[str, object]] = {}
    for page in data["pages"]:
        for claim in page["claims"]:
            by_id[str(claim["claim_id"])] = claim
    return by_id


def test_ad_ztcf_001_distinguishes_four_ztcf_constructions() -> None:
    """ad-ztcf-001 must not conflate stitched ZTCF with re-integrated rollouts (#5591 F6/F13)."""
    claim = _load_claims_by_id()["ad-ztcf-001"]
    tech = str(claim["technical_claim"]["text"]).lower()  # type: ignore[index]
    summary = str(claim["accessible_summary"]["text"]).lower()  # type: ignore[index]
    title = str(claim["title"]).lower()

    assert "re-integrat" not in tech
    assert "how much of the motion is carried by" not in summary
    assert "isolates passive-release" not in title
    for term in ("pointwise", "stitched", "forward", "branched"):
        assert term in tech


def test_ad_dcr_002_states_analytical_counterexample_and_inertia_weighting() -> None:
    """ad-dcr-002 must not claim simulated late-downswing growth or kinetic-energy metric (#5591 F11)."""
    claim = _load_claims_by_id()["ad-dcr-002"]
    combined = json.dumps(claim).lower()

    assert "often grows late in the downswing" not in combined
    assert "kinetic-energy metric" not in combined
    assert "kinetic energy metric" not in combined
    assert "simulated downswing trajectory" not in combined
    assert "inertia-weighted" in combined


def test_software_provenance_hashes_are_distinct_and_match_repo_files() -> None:
    """Every registry path must digest-match on-disk bytes; distinct paths stay distinct (#5591 F7)."""
    claims = _load_claims_by_id()
    path_hashes: dict[str, set[str]] = {}
    seen_hashes: dict[str, str] = {}

    for claim in claims.values():
        for entry in claim["software_provenance"]:  # type: ignore[attr-defined]
            path = str(entry["path"])
            digest = str(entry["sha256"])
            target = ROOT / path
            assert target.is_file(), f"Missing provenance target: {path}"
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            assert actual == digest, f"SHA-256 drift for {path}: registry={digest}, file={actual}"
            path_hashes.setdefault(path, set()).add(digest)
            if digest in seen_hashes and seen_hashes[digest] != path:
                pytest.fail(
                    f"Duplicate SHA-256 {digest} shared by {seen_hashes[digest]} and {path}"
                )
            seen_hashes[digest] = path

    assert len(seen_hashes) == len(path_hashes)
    validate_registry(json.loads(DEFAULT_REGISTRY.read_text(encoding="utf-8")), DEFAULT_SCHEMA)


def test_validate_registry_rejects_stale_provenance_hash() -> None:
    """CI trust validation must fail when a file changes but the registry digest does not."""
    data = json.loads(DEFAULT_REGISTRY.read_text(encoding="utf-8"))
    entry = data["pages"][0]["claims"][0]["software_provenance"][0]
    entry["sha256"] = "0" * 64
    with pytest.raises(TrustContractError, match="software_provenance sha256"):
        validate_registry(data, DEFAULT_SCHEMA)


def test_validate_registry_rejects_duplicate_hash_across_distinct_paths() -> None:
    """Trust validator must fail closed when two different paths share one SHA-256 (#5591 F7)."""
    data = json.loads(DEFAULT_REGISTRY.read_text(encoding="utf-8"))
    claims = [claim for page in data["pages"] for claim in page["claims"]]
    target_a = claims[0]["software_provenance"][0]
    target_b = claims[1]["software_provenance"][0]
    assert target_a["path"] != target_b["path"]
    target_b["sha256"] = target_a["sha256"]

    with pytest.raises(TrustContractError, match="Duplicate software_provenance sha256"):
        validate_registry(data, DEFAULT_SCHEMA)


def test_evidence_presentation_separates_software_artifacts_and_ad_decomp_identity() -> None:
    """Companion items must not carry qualified_simulation; ad-decomp-001 is mathematical_identity."""
    _, vms = build_evidence_presentation_registry(ROOT)
    by_id = {vm.entity_id: vm for vm in vms}

    assert by_id["ad-decomp-001"].tier == "mathematical_identity"
    myosuite = by_id["engine-myosuite"]
    assert myosuite.tier == "software_artifact"
    assert "experimental" in myosuite.state_label.lower()

    chat = by_id["feature-chat-transport"]
    assert chat.tier == "software_artifact"


def test_start_here_ztcf_figure_says_forward_rollout_and_short_caption() -> None:
    """pages/start-here.qmd caption should be concise and say forward ZTCF rollout (#5591 F13)."""
    text = (ROOT / "pages/start-here.qmd").read_text(encoding="utf-8")
    assert "pointwise Zero-Torque Counterfactual (ZTCF) rollout" not in text
    assert (
        "![Drift Plus Control Vector Field Decomposition](../pics/drift-plus-control-vector-field.svg)"
        in text
    )
    assert "forward ZTCF rollout curve" in text
