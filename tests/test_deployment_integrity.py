"""Tests for deployment workflow integrity.

Verifies that critical checks and dependencies are properly configured
in the GitHub Actions deployment workflow.
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT_DIR = Path(__file__).parent.parent
WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "deploy-website.yml"
CI_WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "ci-standard.yml"
REQUIREMENTS_PATH = ROOT_DIR / "requirements.txt"
LATEX_RELEASE_WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "latex-release-volumes.yml"


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
    assert "quarto-actions/render" in content, (
        "Deploy workflow must render the site before post-build checks"
    )


def test_ci_workflow_builds_site_for_e2e_and_audits_dependencies() -> None:
    """Ensure PR CI builds generated docs and audits Python dependencies."""
    assert CI_WORKFLOW_PATH.exists(), "CI workflow file missing"

    content = CI_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "pip-audit" in content, "CI workflow should audit Python dependencies"
    assert "pip-audit -r requirements.txt || true" not in content, (
        "CI dependency audit must not be fail-open"
    )
    assert "--cov=src" in content, "CI coverage should target the full src tree"
    assert "--cov=src/tools" not in content, "CI coverage scope must not exclude core packages"
    assert "Build site for E2E" in content, "E2E lane should build the site before testing"
    assert "quarto render" in content or "quarto-actions/render" in content, (
        "E2E lane must render docs artifacts"
    )
    assert "scripts/sync_frontend_assets.py" in content, (
        "E2E lane should use the shared frontend sync path"
    )
    assert "Skipping e2e smoke tests" not in content, (
        "E2E lane should not silently skip smoke tests by default"
    )


def test_requirements_integrity() -> None:
    """Ensure build dependencies are present."""
    assert REQUIREMENTS_PATH.exists()

    with open(REQUIREMENTS_PATH, encoding="utf-8") as f:
        reqs = f.read()

    bs4_present = "beautifulsoup4" in reqs
    assert bs4_present, "beautifulsoup4 missing from requirements (needed for health check)"
    assert "pytest==8." in reqs, "pytest should be pinned to a modern 8.x release"


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


def test_latex_release_workflow_integrity() -> None:
    """Ensure textbook release workflow compiles and uploads Vol I/II PDFs."""
    assert LATEX_RELEASE_WORKFLOW_PATH.exists(), "LaTeX release workflow file missing"
    content = LATEX_RELEASE_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "Volume_I" in content
    assert "Volume_II" in content
    assert "gh release upload" in content
