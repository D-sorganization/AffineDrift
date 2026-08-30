"""Tests for Programming Companion onboarding and installation contracts (ISSUE-4024).

Verifies that all reader-facing installation, onboarding, and verification instructions
reference verified provider entrypoints without stale, unpinned, or conflicting claims.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _read_file(relative_path: str) -> str:
    target = ROOT / relative_path
    assert target.exists(), f"File {relative_path} does not exist"
    return target.read_text(encoding="utf-8")


@pytest.mark.unit
def test_educational_integration_references_verified_installation_entrypoint() -> None:
    """Educational integration guide uses the verified verification script and workflow."""
    content = _read_file("articles/upstreamdrift-educational-integration.qmd")

    # Must reference the verified CI entrypoint or governed workflow
    assert (
        "python scripts/ci/verify_installation.py" in content
        or "python -m scripts.companion_workflows execute --workflow-id installation-verification"
        in content
    )

    # Must not contain stale legacy unverified verification path
    assert "python scripts/verify_installation.py" not in content


@pytest.mark.unit
def test_engines_matrix_references_verified_installation_workflow() -> None:
    """Generated engines page references the governed installation verification workflow."""
    content = _read_file("models/programming/engines.qmd")

    assert "python scripts/ci/verify_installation.py" in content
    assert (
        "python -m scripts.companion_workflows execute --workflow-id installation-verification"
        in content
    )


@pytest.mark.unit
def test_no_pages_contain_stale_root_level_verification_commands() -> None:
    """No QMD files instruct readers to run obsolete scripts/verify_installation.py at root."""
    qmd_files = list(ROOT.glob("**/*.qmd"))
    for qmd in qmd_files:
        if ".git" in str(qmd) or "worktrees" in str(qmd):
            continue
        text = qmd.read_text(encoding="utf-8", errors="ignore")
        assert (
            "python scripts/verify_installation.py" not in text
        ), f"Found stale verification command in {qmd.relative_to(ROOT)}"


@pytest.mark.unit
def test_onboarding_helper_module_exposes_verified_entrypoints() -> None:
    """Onboarding helper exports canonical verify script and workflow IDs."""
    from src.affine_control.programming_companion.onboarding import (
        CANONICAL_VERIFY_SCRIPT,
        CANONICAL_WORKFLOW_ID,
        get_verified_onboarding_entrypoints,
    )

    assert CANONICAL_VERIFY_SCRIPT == "scripts/ci/verify_installation.py"
    assert CANONICAL_WORKFLOW_ID == "installation-verification"

    entrypoints = get_verified_onboarding_entrypoints()
    assert len(entrypoints) == 2
    assert any("verify_installation.py" in ep.command for ep in entrypoints)
    assert any("installation-verification" in ep.command for ep in entrypoints)
