"""Tests for deployment workflow integrity.

Verifies that critical checks and dependencies are properly configured
in the GitHub Actions deployment workflow.
"""

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT_DIR = Path(__file__).parent.parent
WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "deploy-website.yml"
CI_WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "ci-standard.yml"
REQUIREMENTS_PATH = ROOT_DIR / "requirements.txt"
LATEX_RELEASE_WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "latex-release-volumes.yml"
ANTI_PHANTOM_WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "anti-phantom-merge.yml"
LOCAL_ONLY_GUARD_WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "local-only-runner-guard.yml"


def test_deploy_workflow_integrity() -> None:
    """Ensure critical checks are present in the deployment workflow."""
    assert WORKFLOW_PATH.exists(), "Deployment workflow file missing"

    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        content = f.read()

    # Check for Pre-build checks (accept python3 or python invocation)
    link_check_present = "src.tools.check_links" in content
    assert link_check_present, "Pre-build link check must run as module to resolve imports"

    # Check for Post-build checks (accept python3 or python invocation)
    health_check_present = "src.tools.check_site_health --fail-on broken" in content
    assert health_check_present, "Post-build site health check missing"

    # Check for Verification
    assert "Verify Deployment" in content, "Deployment verification step missing"
    assert "curl" in content, "Curl verification missing"
    assert "PYTHONPATH: ." in content, "Deploy workflow must set PYTHONPATH for script imports"
    assert "frontend asset" in content.lower(), "Deploy workflow should verify frontend asset sync"
    assert (
        "quarto-actions/render" in content
    ), "Deploy workflow must render the site before post-build checks"


def test_deploy_workflow_gates_local_and_live_every_page_evidence() -> None:
    """Pages may deploy only after the manifest matrix passes locally and live."""
    content = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "scripts/public_site_manifest.py" in content
    assert content.count("scripts/verify-public-site.js") >= 2
    assert "public-site-manifest.json" in content
    assert "source_revision" in content and "GITHUB_SHA" in content
    assert "npx playwright install" in content
    assert "public-site-verification" in content
    assert "upload-artifact" in content


def test_live_manifest_poll_retries_transient_non_json_responses() -> None:
    """Pages propagation may briefly return HTML without aborting the retry loop."""
    content = WORKFLOW_PATH.read_text(encoding="utf-8")
    live_poll = content.split("Verify Deployment Manifest and Every Public Page", maxsplit=1)[1]

    assert "if SOURCE_REVISION=$(python3" in live_poll
    assert "2>/dev/null); then" in live_poll


def test_ci_and_deploy_use_the_locally_qualified_quarto_version() -> None:
    """CI and Pages render with the same qualified Quarto release as local QA."""
    for workflow in (WORKFLOW_PATH, CI_WORKFLOW_PATH):
        content = workflow.read_text(encoding="utf-8")
        assert 'version: "1.8.26"' in content
        assert 'version: "1.6.39"' not in content


def test_deploy_runner_picker_does_not_depend_on_org_api_token() -> None:
    """Deploy routing should not fail when an org runner-listing token is stale."""
    assert WORKFLOW_PATH.exists(), "Deployment workflow file missing"
    content = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "RUNNER_CHECK_TOKEN" not in content
    assert "/actions/runners" not in content
    # The picker must emit a static label rather than interrogating the org
    # runners API, so that a stale token cannot break deployment. Which label it
    # picks is a policy question that depends on repository visibility -- this
    # repo is public, so it routes to free hosted runners -- and is checked by
    # the local-only runner guard, not here.
    assert re.search(
        r"^\s*echo \"runner=[A-Za-z0-9_.-]+\"", content, re.MULTILINE
    ), "Deploy workflow must assign a static runner label"


def test_local_only_guard_does_not_run_on_main_pushes() -> None:
    """Standalone hosted-runner canary should not mark normal main pushes red."""
    assert LOCAL_ONLY_GUARD_WORKFLOW_PATH.exists(), "Local-only guard workflow file missing"
    content = LOCAL_ONLY_GUARD_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "\n  push:" not in content
    assert "\n  workflow_dispatch:" in content
    assert "\n  pull_request:" in content


def test_local_only_guard_embedded_python_has_no_actions_expression_tokens() -> None:
    """Embedded Python must not be interpolated as an Actions expression."""
    content = LOCAL_ONLY_GUARD_WORKFLOW_PATH.read_text(encoding="utf-8")
    _, embedded_python = content.split("        run: |", maxsplit=1)

    assert "${{" not in embedded_python


def test_ci_workflow_builds_site_for_e2e_and_audits_dependencies() -> None:
    """Ensure PR CI builds generated docs and audits Python dependencies."""
    assert CI_WORKFLOW_PATH.exists(), "CI workflow file missing"

    content = CI_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "pip-audit" in content, "CI workflow should audit Python dependencies"
    assert (
        "pip-audit -r requirements.txt || true" not in content
    ), "CI dependency audit must not be fail-open"
    assert "--cov=src" in content, "CI coverage should target the full src tree"
    assert "--cov=src/tools" not in content, "CI coverage scope must not exclude core packages"
    assert "Build site for E2E" in content, "E2E lane should build the site before testing"
    assert (
        "quarto render" in content or "quarto-actions/render" in content
    ), "E2E lane must render docs artifacts"
    assert (
        "scripts/sync_frontend_assets.py" in content
    ), "E2E lane should use the shared frontend sync path"
    assert (
        "Skipping e2e smoke tests" not in content
    ), "E2E lane should not silently skip smoke tests by default"


def test_requirements_integrity() -> None:
    """Ensure build dependencies are present."""
    assert REQUIREMENTS_PATH.exists()

    with open(REQUIREMENTS_PATH, encoding="utf-8") as f:
        reqs = f.read()

    bs4_present = "beautifulsoup4" in reqs
    assert bs4_present, "beautifulsoup4 missing from requirements (needed for health check)"
    assert "pytest==9." in reqs, "pytest should be pinned to a modern 9.x release"


def test_check_scripts_exist() -> None:
    """Ensure the check scripts actually exist."""
    assert (ROOT_DIR / "src" / "tools" / "check_links.py").exists()
    assert (ROOT_DIR / "src" / "tools" / "check_site_health.py").exists()


def test_ci_workflow_runs_content_lint_tests() -> None:
    """CI should run content-lint checks explicitly after the default test pass."""
    assert CI_WORKFLOW_PATH.exists(), "CI workflow file missing"
    content = CI_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "Run Content Lint Tests" in content
    assert "pytest --override-ini addopts=" in content
    assert "-m content_lint" in content


def test_anti_phantom_guard_uses_gh_jq_not_runner_jq() -> None:
    """The anti-phantom guard must not depend on jq being installed on local runners."""
    assert ANTI_PHANTOM_WORKFLOW_PATH.exists(), "Anti-phantom workflow file missing"
    content = ANTI_PHANTOM_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert " | jq " not in content
    assert "--jq .changedFiles" in content


@pytest.mark.skipif(
    not LATEX_RELEASE_WORKFLOW_PATH.exists(),
    reason="latex-release-volumes.yml not yet created",
)
def test_latex_release_workflow_integrity() -> None:
    """Ensure textbook release workflow compiles and uploads Vol I/II PDFs."""
    content = LATEX_RELEASE_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "Volume_I" in content
    assert "Volume_II" in content
    assert "gh release upload" in content
