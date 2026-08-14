"""Contracts for the complete canonical proximal-distal claim audit pin."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/proximal_distal_energy_transfer/complete_claim_audit_snapshot.json"
ARTICLE = ROOT / "articles/proximal-distal-energy-transfer.qmd"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def test_complete_claim_audit_snapshot_is_exact_and_fail_closed() -> None:
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    source = payload["source"]
    audit = payload["audit"]
    release = payload["release"]
    boundaries = payload["principal_boundaries"]

    assert source["repository"] == "D-sorganization/UpstreamDrift"
    assert SHA40.fullmatch(source["commit"])
    assert source["commit"] in source["registry_url"]
    assert source["commit"] in source["pdf_url"]
    assert source["commit"] in source["readiness_url"]
    assert audit == {
        "completion_status": "complete",
        "candidate_count": 956,
        "reviewed_candidate_count": 956,
        "unadjudicated_candidate_count": 0,
        "registered_claim_count": 250,
        "release_claim_count": 20,
    }
    assert release["pdf_pages"] == 210
    assert release["qualified_artifact_count"] == 418
    assert SHA256.fullmatch(release["claim_registry_sha256"])
    assert SHA256.fullmatch(release["pdf_sha256"])
    assert boundaries["universal_human_or_coaching_strategy"] == "not_supported"
    assert boundaries["bilateral_human_grip_wrench_validation"].startswith("unexecuted")
    assert payload["source_agenda_readiness"] == {
        "critical_point_count": 9,
        "answered_or_partly_answered": 5,
        "unresolved_or_definition_gated": 4,
        "model_plan_registered_for_all": True,
        "human_plan_registered_for_all": True,
        "human_execution_blocked": True,
    }


def test_article_exposes_the_complete_audit_without_promoting_it() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert "Complete Claim Audit" in article
    assert payload["source"]["commit"] in article
    assert "956 of 956" in article
    assert "zero unadjudicated" in article
    assert "does not validate a universal human or coaching strategy" in article
    assert "manual NotebookLM reauthentication" in article
    assert "nine independently tracked points" in article
    assert "typed slack remain unresolved" in article
