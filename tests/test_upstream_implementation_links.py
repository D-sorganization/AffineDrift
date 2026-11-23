"""Contracts for UpstreamDrift implementation bridge ledger (#5601)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import check_upstream_implementation_links as bridge_cli
from src.tools import upstream_implementation_bridge as bridge

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "data/companion/upstream_implementation_links.json"


@pytest.mark.unit
def test_ledger_loads_with_expected_schema() -> None:
    document = bridge.load_ledger(LEDGER)
    assert document["schema_version"] == bridge.SCHEMA
    assert len(document["bridges"]) >= 14


@pytest.mark.unit
def test_ledger_lists_pog_ch27_and_ch31_ztcf_bridges() -> None:
    document = bridge.load_ledger(LEDGER)
    ids = {entry["id"] for entry in document["bridges"]}
    assert {"pog-ch27-ztcf", "pog-ch31-ztcf"}.issubset(ids)


@pytest.mark.unit
def test_repository_bridges_pass_verification() -> None:
    document = bridge.load_ledger(LEDGER)
    findings = bridge.verify_document(document, REPO_ROOT)
    assert findings == [], "\n".join(findings)


@pytest.mark.unit
def test_checker_cli_reports_success() -> None:
    assert (
        bridge_cli.main(["--root", str(REPO_ROOT), "--ledger", str(LEDGER), "--skip-remote"]) == 0
    )


@pytest.mark.unit
def test_missing_remote_path_is_reported() -> None:
    document = bridge.load_ledger(LEDGER)

    def boom(_commit: str, _path: str) -> None:
        raise FileNotFoundError("missing")

    findings = bridge.verify_remote_paths(document, fetch_path=boom)
    assert findings
    assert any("missing remote path" in line for line in findings)


@pytest.mark.integration
def test_ledger_remote_paths_exist_at_pin() -> None:
    document = bridge.load_ledger(LEDGER)
    findings = bridge.verify_remote_paths(document)
    assert findings == [], "\n".join(findings)


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
