"""Tests for deployment workflow integrity.

Verifies that critical checks and dependencies are properly configured
in the GitHub Actions deployment workflow.
"""

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "deploy-website.yml"
REQUIREMENTS_PATH = ROOT_DIR / "requirements.txt"


def test_deploy_workflow_integrity() -> None:
    """Ensure critical checks are present in the deployment workflow."""
    assert WORKFLOW_PATH.exists(), "Deployment workflow file missing"

    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        content = f.read()

    # Check for Pre-build checks
    assert (
        "python -m src.tools.check_links" in content
    ), "Pre-build link check must run as module to resolve imports"

    # Check for Post-build checks
    assert (
        "python -m src.tools.check_site_health --fail-on broken" in content
    ), "Post-build site health check must run as module to resolve imports"

    # Check for Verification
    assert "Verify Deployment" in content, "Deployment verification step missing"
    assert "curl" in content, "Curl verification missing"


def test_requirements_integrity() -> None:
    """Ensure build dependencies are present."""
    assert REQUIREMENTS_PATH.exists()

    with open(REQUIREMENTS_PATH, encoding="utf-8") as f:
        reqs = f.read()

    assert (
        "beautifulsoup4" in reqs
    ), "beautifulsoup4 missing from requirements (needed for health check)"


def test_check_scripts_exist() -> None:
    """Ensure the check scripts actually exist."""
    assert (ROOT_DIR / "src" / "tools" / "check_links.py").exists()
    assert (ROOT_DIR / "src" / "tools" / "check_site_health.py").exists()
