"""Tests for deployment workflow integrity.

Verifies that critical checks and dependencies are properly configured
in the GitHub Actions deployment workflow.
"""

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "deploy-website.yml"
REQUIREMENTS_PATH = ROOT_DIR / "requirements.txt"
LATEX_RELEASE_WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "latex-release-volumes.yml"


def test_deploy_workflow_integrity() -> None:
    """Ensure critical checks are present in the deployment workflow."""
    assert WORKFLOW_PATH.exists(), "Deployment workflow file missing"

    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        content = f.read()

    # Check for Pre-build checks
    assert "python -m src.tools.check_links" in content, (
        "Pre-build link check must run as module to resolve imports"
    )

    # Check for Post-build checks
    assert "python -m src.tools.check_site_health --fail-on broken" in content, (
        "Post-build site health check must run as module to resolve imports"
    )

    # Check for Verification
    assert "Verify Deployment" in content, "Deployment verification step missing"
    assert "curl" in content, "Curl verification missing"
    assert "PYTHONPATH: ." in content, "Deploy workflow must set PYTHONPATH for script imports"


def test_requirements_integrity() -> None:
    """Ensure build dependencies are present."""
    assert REQUIREMENTS_PATH.exists()

    with open(REQUIREMENTS_PATH, encoding="utf-8") as f:
        reqs = f.read()

    assert "beautifulsoup4" in reqs, (
        "beautifulsoup4 missing from requirements (needed for health check)"
    )


def test_check_scripts_exist() -> None:
    """Ensure the check scripts actually exist."""
    assert (ROOT_DIR / "src" / "tools" / "check_links.py").exists()
    assert (ROOT_DIR / "src" / "tools" / "check_site_health.py").exists()


def test_latex_release_workflow_integrity() -> None:
    """Ensure textbook release workflow compiles and uploads Vol I/II PDFs."""
    assert LATEX_RELEASE_WORKFLOW_PATH.exists(), "LaTeX release workflow file missing"
    content = LATEX_RELEASE_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "Volume_I" in content
    assert "Volume_II" in content
    assert "gh release upload" in content
