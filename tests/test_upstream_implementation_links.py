"""Contracts for UpstreamDrift implementation bridge ledger (#5601)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import check_upstream_implementation_links as bridge

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "data/companion/upstream_implementation_links.json"


@pytest.mark.unit
def test_ledger_loads_with_expected_schema() -> None:
    document = bridge.load_ledger(LEDGER)
    assert document["schema_version"] == bridge.SCHEMA
    assert len(document["bridges"]) >= 6


@pytest.mark.unit
def test_repository_bridges_pass_verification() -> None:
    document = bridge.load_ledger(LEDGER)
    findings = bridge.verify_document(document, REPO_ROOT)
    assert findings == [], "\n".join(findings)


@pytest.mark.unit
def test_checker_cli_reports_success() -> None:
    assert bridge.main(["--root", str(REPO_ROOT), "--ledger", str(LEDGER)]) == 0


@pytest.mark.unit
def test_missing_include_is_reported(tmp_path: Path) -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    ledger["bridges"] = [ledger["bridges"][0]]
    ledger["bridges"][0]["include"] = "articles/_includes/upstream-implementation/missing.qmd"
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps(ledger), encoding="utf-8")
    document = bridge.load_ledger(path)
    findings = bridge.verify_document(document, REPO_ROOT)
    assert any("missing include" in line for line in findings)
