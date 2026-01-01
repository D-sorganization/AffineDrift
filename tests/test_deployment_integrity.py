from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "deploy-website.yml"
REQUIREMENTS_PATH = ROOT_DIR / "requirements.txt"


def test_deploy_workflow_integrity():
    """Ensure critical checks are present in the deployment workflow."""
    assert WORKFLOW_PATH.exists(), "Deployment workflow file missing"

    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        content = f.read()

    # Check for Pre-build checks
    assert "tools/check_links.py" in content, "Pre-build link check missing from workflow"

    # Check for Post-build checks
    assert (
        "tools/check_site_health.py" in content
    ), "Post-build site health check missing from workflow"

    # Check for Verification
    assert "Verify Deployment" in content, "Deployment verification step missing"
    assert "curl" in content, "Curl verification missing"


def test_requirements_integrity():
    """Ensure build dependencies are present."""
    assert REQUIREMENTS_PATH.exists()

    with open(REQUIREMENTS_PATH, encoding="utf-8") as f:
        reqs = f.read()

    assert (
        "beautifulsoup4" in reqs
    ), "beautifulsoup4 missing from requirements (needed for health check)"


def test_check_scripts_exist():
    """Ensure the check scripts actually exist."""
    assert (ROOT_DIR / "tools" / "check_links.py").exists()
    assert (ROOT_DIR / "tools" / "check_site_health.py").exists()
