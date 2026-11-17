"""Wave 1.2 (#5588): ZVCF must match NOTATION.md control-operand definition site-wide."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.tools.zvcf_notation_guard import (
    LEGACY_ZVCF_PATTERNS,
    iter_zvcf_guarded_sources,
    scan_legacy_zvcf_definitions,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CLAIM_REGISTRY = REPO_ROOT / "data" / "trust" / "claim_registry.json"


def test_legacy_patterns_are_non_empty() -> None:
    assert LEGACY_ZVCF_PATTERNS


def test_claim_ad_zvcf_001_describes_control_operand_not_holding_torque() -> None:
    registry = json.loads(CLAIM_REGISTRY.read_text(encoding="utf-8"))
    claim = next(
        c for page in registry["pages"] for c in page["claims"] if c["claim_id"] == "ad-zvcf-001"
    )
    blob = " ".join(
        [
            claim["accessible_summary"]["text"],
            claim["technical_claim"]["text"],
            claim["title"],
        ]
    ).lower()
    assert "hold a position still" not in blob
    assert "holding torque" not in blob or "not" in blob
    assert "m(q)^{-1}" in blob.replace(" ", "") or "m^{-1}" in blob or "control" in blob


@pytest.mark.parametrize("path", list(iter_zvcf_guarded_sources(REPO_ROOT)), ids=lambda p: p.name)
def test_source_has_no_legacy_zvcf_definition(path: Path) -> None:
    findings = scan_legacy_zvcf_definitions(REPO_ROOT, paths=(path,))
    assert not findings, findings


def test_repo_has_no_legacy_zvcf_definitions_in_guarded_corpus() -> None:
    findings = scan_legacy_zvcf_definitions(REPO_ROOT)
    assert not findings, "\n".join(
        f"{f['file']}:{f['line']}: matched {f['pattern']}" for f in findings[:20]
    )
