"""Tests for wheel packaging and importability (#4532).

Ensures that AffineDrift is properly packaged as an installable Python package,
that pyproject.toml defines valid PEP 621 project metadata, and that modules
can be installed and imported from an isolated directory outside repository root.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

from scripts.smoke_test_installed_wheel import find_latest_wheel, run_smoke_test

REPO_ROOT = Path(__file__).resolve().parents[1]


def _get_or_build_wheel() -> Path:
    """Return latest wheel in dist/, building one if none exists."""
    dist_dir = REPO_ROOT / "dist"
    wheels = list(dist_dir.glob("affinedrift-*.whl")) if dist_dir.exists() else []
    if not wheels:
        dist_dir.mkdir(exist_ok=True)
        subprocess.run(
            [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
    return find_latest_wheel(dist_dir)


def test_pyproject_project_metadata_is_valid() -> None:
    """pyproject.toml must declare PEP 621 project metadata and package discovery."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml must exist"

    with pyproject_path.open("rb") as f:
        config = tomllib.load(f)

    assert "project" in config, "pyproject.toml must define [project]"
    project = config["project"]
    assert project["name"] == "affinedrift"
    assert "version" in project
    assert re.match(r"^\d+\.\d+\.\d+$", project["version"])
    assert "description" in project
    assert "dependencies" in project
    assert isinstance(project["dependencies"], list)
    assert len(project["dependencies"]) > 0

    # Package discovery
    setuptools_cfg = config.get("tool", {}).get("setuptools", {})
    find_cfg = setuptools_cfg.get("packages", {}).get("find", {})
    assert find_cfg.get("where") == ["."]
    assert "src*" in find_cfg.get("include", [])


def test_pyproject_version_matches_spec() -> None:
    """Package version in pyproject.toml must match Current Version in SPEC.md."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        pyproject_version = tomllib.load(f)["project"]["version"]

    spec_path = REPO_ROOT / "SPEC.md"
    spec_text = spec_path.read_text(encoding="utf-8")
    match = re.search(r"\*\*Current Version\*\*\s*\|\s*([0-9.]+)", spec_text)
    assert match is not None, "SPEC.md must contain '**Current Version**'"
    spec_version = match.group(1).strip()

    assert (
        pyproject_version == spec_version
    ), f"pyproject.toml version ({pyproject_version}) does not match SPEC.md ({spec_version})"


def test_wheel_contains_all_models_and_py_typed() -> None:
    """The built wheel archive must contain all model packages and py.typed."""
    wheel_path = _get_or_build_wheel()
    with zipfile.ZipFile(wheel_path, "r") as zf:
        namelist = set(zf.namelist())

    required_entries = [
        "src/__init__.py",
        "src/py.typed",
        "src/core/__init__.py",
        "src/core/constants.py",
        "src/affine_control/__init__.py",
        "src/affine_control/residuals.py",
        "src/golf_simulation/__init__.py",
        "src/golf_simulation/round_simulator.py",
        "src/tangent_models/__init__.py",
        "src/tangent_models/examples.py",
    ]

    for req in required_entries:
        assert req in namelist, f"Wheel missing required entry: {req}"


def test_wheel_import_smoke_outside_repo_root() -> None:
    """Smoke test importing modules from wheel installed outside repository root."""
    wheel_path = _get_or_build_wheel()
    exit_code = run_smoke_test(wheel_path)
    assert exit_code == 0, "Smoke test for installed wheel must exit with 0"
