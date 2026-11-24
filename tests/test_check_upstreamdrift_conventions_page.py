"""Tests for scripts/check_upstreamdrift_conventions_page.py (#5619)."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from scripts.check_upstreamdrift_conventions_page import (
    check_page,
    check_upstream_doc,
    load_contract,
    main,
    run_check,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "data/upstreamdrift/canonical_v2_page_contract.json"
PAGE = REPO_ROOT / "pages/upstreamdrift-conventions.qmd"


def test_contract_loads_with_expected_schema() -> None:
    contract = load_contract(CONTRACT)
    assert contract.upstream_commit == "c8814a1b9d120ce382ee1de9a6583bb5ef569a15"
    assert contract.page_path == Path("pages/upstreamdrift-conventions.qmd")
    assert len(contract.upstream_required) >= 4
    assert len(contract.page_required) >= 4


def test_check_page_reports_missing_substring() -> None:
    contract = load_contract(CONTRACT)
    errors = check_page("c8814a1b9d120ce382ee1de9a6583bb5ef569a15\n", contract)
    assert len(errors) >= 3


def test_check_upstream_doc_reports_missing_anchor() -> None:
    contract = load_contract(CONTRACT)
    errors = check_upstream_doc("g = [0, 0, -9.80665]\n", contract)
    assert errors


def test_live_repo_page_satisfies_page_contract() -> None:
    contract = load_contract(CONTRACT)
    page_text = PAGE.read_text(encoding="utf-8")
    assert not check_page(page_text, contract)


@mock.patch("scripts.check_upstreamdrift_conventions_page.fetch_canonical_v2")
def test_run_check_merges_upstream_and_page_errors(mock_fetch: mock.Mock) -> None:
    contract = load_contract(CONTRACT)
    mock_fetch.return_value = "g = [0, 0, -9.80665]\n"
    errors = run_check(CONTRACT, REPO_ROOT)
    assert any("upstream" in e for e in errors)
    assert not check_page(PAGE.read_text(encoding="utf-8"), contract)


@pytest.mark.requires_network
def test_main_returns_zero_on_current_repo() -> None:
    """Integration: live fetch of canonical-v2.md at the pin."""
    assert main([]) == 0
