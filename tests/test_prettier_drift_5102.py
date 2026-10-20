"""Prettier drift contracts for #5102.

Running ``pre-commit run prettier --all-files`` must not rewrite
``validation-environment.json`` or attested companion snapshot manifests.
``technical-review.md`` stays sha256-pinned and intentionally drifted (not in
``.prettierignore``); owners re-attest or reformat it separately.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]

VALIDATION_ENV = ROOT / "reports/shot-pattern-publication/validation-environment.json"
COMPANION_MANIFEST = (
    ROOT
    / "data/companion/snapshots/27b6eeadbbd970bebb8926a3c83aeaea1f6ee4da-a1c9a799ecceb4e8/manifest.json"
)
TECHNICAL_REVIEW = ROOT / "reports/shot-pattern-publication/technical-review.md"
TECHNICAL_REVIEW_REL = "reports/shot-pattern-publication/technical-review.md"
PRETTIER_IGNORE = ROOT / ".prettierignore"
INVENTORY = ROOT / "data/trust/claim_audit_inventory.json"

pytestmark = pytest.mark.skipif(shutil.which("npx") is None, reason="npx required for prettier")


def _prettier_package() -> str:
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    for repository in config["repos"]:
        repo_url = str(repository.get("repo", ""))
        if "mirrors-prettier" in repo_url:
            rev = str(repository["rev"])
            return f"prettier@{rev.lstrip('v')}" if rev.startswith("v") else f"prettier@{rev}"
    raise AssertionError("mirrors-prettier entry missing from .pre-commit-config.yaml")


def _run_prettier(*args: str) -> subprocess.CompletedProcess[str]:
    npx = shutil.which("npx")
    assert npx is not None
    return subprocess.run(
        [npx, _prettier_package(), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inventory_pin(relative: str) -> str:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    pins: set[str] = set()
    for route in inventory["routes"]:
        review = route.get("review") or {}
        evidence = review.get("evidence_sha256") or {}
        if relative in evidence:
            pins.add(str(evidence[relative]))
        for finding in route.get("findings") or []:
            finding_evidence = finding.get("evidence_sha256") or {}
            if relative in finding_evidence:
                pins.add(str(finding_evidence[relative]))
    assert len(pins) == 1, f"expected one inventory pin for {relative}, got {pins}"
    return pins.pop()


def _prettierignore_entries() -> list[str]:
    entries: list[str] = []
    for line in PRETTIER_IGNORE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        entries.append(stripped)
    return entries


def test_validation_environment_json_is_prettier_stable() -> None:
    result = _run_prettier("--check", str(VALIDATION_ENV.relative_to(ROOT)))
    assert result.returncode == 0, result.stdout + result.stderr


def test_companion_snapshot_manifest_is_prettier_ignored() -> None:
    assert any(
        entry.rstrip("/") == "data/companion/snapshots" or entry == "data/companion/snapshots/"
        for entry in _prettierignore_entries()
    ), ".prettierignore must ignore attested companion snapshot trees"
    before = COMPANION_MANIFEST.read_bytes()
    result = _run_prettier("--write", str(COMPANION_MANIFEST.relative_to(ROOT)))
    assert result.returncode == 0, result.stdout + result.stderr
    assert COMPANION_MANIFEST.read_bytes() == before


def test_technical_review_is_not_prettierignored_and_stays_attested() -> None:
    assert TECHNICAL_REVIEW_REL not in _prettierignore_entries()
    assert not any(
        TECHNICAL_REVIEW_REL.startswith(entry.rstrip("/") + "/")
        for entry in _prettierignore_entries()
        if entry.endswith("/")
    )
    pinned = _inventory_pin(TECHNICAL_REVIEW_REL)
    assert _file_sha256(TECHNICAL_REVIEW) == pinned
    drift = _run_prettier("--check", TECHNICAL_REVIEW_REL)
    assert drift.returncode != 0, "pinned review must remain intentionally prettier-drifted"
