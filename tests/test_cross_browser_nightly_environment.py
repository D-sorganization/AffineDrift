"""The nightly Quarto render needs the site's Python post-render dependencies."""

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RENDER_STEP = "Build site for E2E"
SITE_ARTIFACT = "cross-browser-site"
# A cold full-site render took 44 minutes on 2026-11-01 (run 41283430615) and
# cancelled the firefox leg at its 45-minute job timeout before any test ran.
COLD_RENDER_MINUTES = 44


def _jobs() -> dict[str, Any]:
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/cross-browser-nightly.yml").read_text(encoding="utf-8")
    )
    return workflow["jobs"]


def test_cross_browser_nightly_bootstraps_python_requirements_before_render() -> None:
    steps = _jobs()["build-site"]["steps"]
    render_index = next(
        index for index, step in enumerate(steps) if step.get("name") == RENDER_STEP
    )
    python_setup_index = next(
        index
        for index, step in enumerate(steps)
        if step.get("uses", "").startswith("actions/setup-python@")
    )
    bootstrap_index = next(
        index for index, step in enumerate(steps) if step.get("name") == "Bootstrap Python venv"
    )

    assert python_setup_index < bootstrap_index < render_index
    assert steps[python_setup_index]["with"]["python-version"] == "3.12"
    assert "pip install --no-cache-dir -r requirements.txt" in steps[bootstrap_index]["run"]


def test_site_renders_once_with_room_for_a_cold_render() -> None:
    """#5301: each browser leg rendered the site itself and timed out."""
    jobs = _jobs()
    build = jobs["build-site"]
    upload = next(
        step
        for step in build["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact@")
    )

    assert build["timeout-minutes"] > COLD_RENDER_MINUTES
    assert upload["with"]["name"] == SITE_ARTIFACT
    assert upload["with"]["path"] == "_site"


def test_browser_legs_reuse_the_rendered_site_instead_of_rendering() -> None:
    e2e = _jobs()["cross-browser-e2e"]
    steps = e2e["steps"]
    download = next(
        step for step in steps if step.get("uses", "").startswith("actions/download-artifact@")
    )

    assert e2e["needs"] == "build-site"
    assert download["with"] == {"name": SITE_ARTIFACT, "path": "_site"}
    assert not any(step.get("name") == RENDER_STEP for step in steps)
    assert not any("quarto" in step.get("uses", "") for step in steps)
