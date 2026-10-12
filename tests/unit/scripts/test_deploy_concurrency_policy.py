"""Protect revision-bound Pages publication from newer main pushes."""

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[3]
DEPLOY = ROOT / ".github" / "workflows" / "deploy-website.yml"
WORKFLOW_LINTER = ROOT / ".github" / "workflows" / "lint-workflow-files.yml"


def test_deploy_finishes_active_revision_before_newer_main_push() -> None:
    """Keep one active revision-bound publish while newer pending pushes coalesce."""
    content = DEPLOY.read_text(encoding="utf-8")
    concurrency = content.split("\nconcurrency:\n", maxsplit=1)[1].split(
        "\npermissions:\n", maxsplit=1
    )[0]

    assert "group: ${{ github.workflow }}-${{ github.ref }}" in concurrency
    assert re.search(r"(?m)^  cancel-in-progress: false$", concurrency)
    assert not re.search(r"(?m)^  queue:", concurrency)
    assert '--source-revision "$GITHUB_SHA"' in content
    assert 'if [ "$SOURCE_REVISION" = "$GITHUB_SHA" ]; then' in content


def test_workflow_linter_recognizes_only_the_exact_pages_publisher() -> None:
    """The publishing exception must not relax ordinary workflow cancellation."""
    content = WORKFLOW_LINTER.read_text(encoding="utf-8")
    exception_block = content.split('case "$(basename "$f")" in', maxsplit=1)[1]
    exceptions = exception_block.split(";;", maxsplit=1)[0]

    assert "deploy-website.yml" in exceptions
    assert "cancel-in-progress:\\s*true" in content.split("      *)", maxsplit=1)[1]
