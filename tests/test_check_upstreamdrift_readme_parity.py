"""Tests for scripts/check_upstreamdrift_readme_parity.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_upstreamdrift_readme_parity import check_readme, load_contract, main


@pytest.mark.unit
def test_check_readme_flags_missing_install_step() -> None:
    errors = check_readme(
        "# Install\npip install -e .\n",
        required=("git submodule update --init --recursive vendor/ud-tools",),
        forbidden=(),
    )
    assert errors


@pytest.mark.unit
def test_main_passes_with_live_readme_at_pinned_commit() -> None:
    contract = load_contract()
    commit = contract["upstream_readme_commit"]
    assert isinstance(commit, str) and len(commit) == 40
    assert main([]) == 0


@pytest.mark.unit
def test_readme_requirements_present_in_contract() -> None:
    payload = json.loads(
        Path("data/upstreamdrift/install_readme_contract.json").read_text(encoding="utf-8")
    )
    requirements = payload["upstream_readme_requirements"]
    assert "vendor/ud-tools" in " ".join(requirements["required_substrings"])
