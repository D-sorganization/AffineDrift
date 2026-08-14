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
    assert source["commit"] in source["timing_viability_url"]
    assert source["commit"] in source["typed_slack_url"]
    assert audit == {
        "completion_status": "complete",
        "candidate_count": 962,
        "reviewed_candidate_count": 962,
        "unadjudicated_candidate_count": 0,
        "registered_claim_count": 252,
        "release_claim_count": 24,
    }
    assert release["pdf_pages"] == 212
    assert release["qualified_artifact_count"] == 428
    assert SHA256.fullmatch(release["claim_registry_sha256"])
    assert SHA256.fullmatch(release["pdf_sha256"])
    assert boundaries["universal_human_or_coaching_strategy"] == "not_supported"
    assert boundaries["bilateral_human_grip_wrench_validation"].startswith("unexecuted")
    assert payload["source_agenda_readiness"] == {
        "critical_point_count": 9,
        "answered_or_partly_answered": 8,
        "unresolved_or_definition_gated": 1,
        "model_plan_registered_for_all": True,
        "human_plan_registered_for_all": True,
        "human_execution_blocked": True,
    }
    timing = payload["timing_viability"]
    assert timing["paired_case_count"] == 60
    assert timing["trajectory_count"] == 120
    assert timing["primary_clock_viable_fraction"] == 0.8
    assert timing["primary_state_triggered_viable_fraction"] == 0.2
    assert timing["sustained_recovery_case_count"] == 0
    assert timing["human_timing_or_coaching_inference"] == "unsupported"
    assert SHA256.fullmatch(timing["json_sha256"])
    assert SHA256.fullmatch(timing["npz_sha256"])
    typed_slack = payload["typed_slack"]
    assert typed_slack["class_count"] == 5
    assert typed_slack["global_slack_benefit"] == "unsupported"
    assert typed_slack["single_channel_class_identification"] == "not_established"
    assert typed_slack["human_intentionality"] == "untested"
    assert SHA256.fullmatch(typed_slack["json_sha256"])
    assert SHA256.fullmatch(typed_slack["npz_sha256"])
    assert SHA256.fullmatch(typed_slack["figure_sha256"])


def test_article_exposes_the_complete_audit_without_promoting_it() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    normalized_article = " ".join(article.split())
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert "Complete Claim Audit" in article
    assert payload["source"]["commit"] in article
    assert "962 of 962" in article
    assert "zero unadjudicated" in article
    assert "does not validate a universal human or coaching strategy" in article
    assert "manual NotebookLM reauthentication" in article
    assert "nine independently tracked points" in article
    assert "Casting remains unresolved as one universal construct" in normalized_article
    assert "One transmitted-output channel therefore does not identify" in article
    assert "larger state-triggered timing region" in normalized_article
    assert "no sustained half-error recovery" in normalized_article
