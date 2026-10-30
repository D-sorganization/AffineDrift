"""The nightly Quarto render needs the site's Python post-render dependencies."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_cross_browser_nightly_bootstraps_python_requirements_before_render() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/cross-browser-nightly.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["cross-browser-e2e"]["steps"]
    render_index = next(
        index for index, step in enumerate(steps) if step.get("name") == "Build site for E2E"
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
