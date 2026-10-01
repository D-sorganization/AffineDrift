"""Single-source contracts for the coverage floor and the Quarto pin (#4126).

The coverage floor used to be stated four different ways (75 / 65 / 65 / >50)
and the Quarto version twice (Docker 1.6.39 vs CI 1.8.26). Each value now has
exactly one authority: ``pyproject.toml`` ``[tool.coverage.report] fail_under``
and the ``.quarto-version`` file. Every other surface must defer to it.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

COVERAGE_CLI_SURFACES = (
    ".github/workflows/ci-standard.yml",
    ".github/workflows/deploy-website.yml",
    "Makefile",
    "Dockerfile",
    "CLAUDE.md",
    "AGENTS.md",
    "SPEC.md",
    "CONTRIBUTING.md",
    "README.md",
)

QUARTO_SETUP_WORKFLOWS = (
    ".github/workflows/ci-standard.yml",
    ".github/workflows/deploy-website.yml",
)

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def test_pyproject_declares_exactly_one_coverage_floor() -> None:
    """The floor is a number in pyproject.toml and nowhere else."""
    config = tomllib.loads(_read("pyproject.toml"))
    floor = config["tool"]["coverage"]["report"]["fail_under"]
    assert isinstance(floor, int | float)
    assert 50 <= floor <= 100


def test_no_cli_surface_overrides_the_coverage_floor() -> None:
    """`--cov-fail-under` on any CLI would silently override pyproject."""
    offenders = [
        surface for surface in COVERAGE_CLI_SURFACES if "--cov-fail-under" in _read(surface)
    ]
    assert offenders == []


def test_quarto_version_file_is_a_single_semver_line() -> None:
    """`.quarto-version` holds one bare version and nothing else."""
    raw = _read(".quarto-version")
    assert raw.endswith("\n")
    lines = raw.splitlines()
    assert len(lines) == 1
    assert SEMVER.fullmatch(lines[0]), lines[0]


def test_dockerfile_quarto_pin_matches_quarto_version_file() -> None:
    """Docker builds must render with the same Quarto as CI."""
    pinned = _read(".quarto-version").strip()
    match = re.search(r"^ARG QUARTO_VERSION=(\S+)$", _read("Dockerfile"), flags=re.M)
    assert match is not None
    assert match.group(1) == pinned


def test_workflows_resolve_quarto_from_the_version_file() -> None:
    """Workflows read `.quarto-version` instead of hard-coding a version."""
    for workflow in QUARTO_SETUP_WORKFLOWS:
        text = _read(workflow)
        assert "quarto-dev/quarto-actions/setup@" in text, workflow
        assert ".quarto-version" in text, workflow
        hard_coded = re.findall(r"^\s*version:\s*\"?\d+\.\d+\.\d+\"?\s*$", text, flags=re.M)
        assert hard_coded == [], (workflow, hard_coded)


def test_spec_documents_the_pinned_quarto_version() -> None:
    """SPEC.md states the same Quarto version that `.quarto-version` pins."""
    pinned = _read(".quarto-version").strip()
    assert f"Quarto {pinned}" in _read("SPEC.md")


NODE_MAJOR_PATTERN = re.compile(r"^\d+$")


def test_nvmrc_file_is_a_single_integer_line() -> None:
    r""".nvmrc exists, is a single integer line matching ^\d+$, and equals 22."""
    nvmrc_path = REPO_ROOT / ".nvmrc"
    assert nvmrc_path.is_file(), ".nvmrc file must exist"
    raw = nvmrc_path.read_text(encoding="utf-8")
    assert raw.endswith("\n"), ".nvmrc must end with a newline"
    lines = raw.splitlines()
    assert len(lines) == 1, f".nvmrc must contain exactly one line, got {len(lines)}"
    version = lines[0]
    assert NODE_MAJOR_PATTERN.fullmatch(version), f".nvmrc must match ^\\d+$, got {version!r}"
    assert version == "22", f".nvmrc must equal 22, got {version!r}"


def test_dockerfile_node_major_matches_nvmrc() -> None:
    """Dockerfile's ARG NODE_MAJOR matches .nvmrc."""
    nvmrc_path = REPO_ROOT / ".nvmrc"
    assert nvmrc_path.is_file(), ".nvmrc file must exist"
    raw = nvmrc_path.read_text(encoding="utf-8")
    pinned = raw.strip()
    dockerfile_text = _read("Dockerfile")
    match = re.search(r"^ARG NODE_MAJOR=(\S+)$", dockerfile_text, flags=re.M)
    assert match is not None, "Dockerfile must define ARG NODE_MAJOR"
    node_major = match.group(1)
    assert node_major == pinned, f"Dockerfile NODE_MAJOR ({node_major}) != .nvmrc ({pinned})"


def test_workflows_specify_node_version_file_nvmrc() -> None:
    """All workflows using actions/setup-node specify node-version-file: ".nvmrc"."""
    workflow_dir = REPO_ROOT / ".github" / "workflows"
    workflow_files = sorted(workflow_dir.glob("*.yml"))
    setup_node_workflows = [
        wf for wf in workflow_files if "actions/setup-node" in wf.read_text(encoding="utf-8")
    ]
    assert (
        len(setup_node_workflows) >= 3
    ), f"Expected at least 3 setup-node workflows, found {len(setup_node_workflows)}"
    for workflow in setup_node_workflows:
        text = workflow.read_text(encoding="utf-8")
        assert (
            'node-version-file: ".nvmrc"' in text
        ), f'{workflow.name} must specify node-version-file: ".nvmrc"'
        hard_coded = re.findall(r"^\s*node-version:\s*.*$", text, flags=re.M)
        assert hard_coded == [], f"{workflow.name} hardcodes node-version: {hard_coded}"


def test_claude_documents_pinned_node_version() -> None:
    """CLAUDE.md documents Node 22 matching .nvmrc."""
    nvmrc_path = REPO_ROOT / ".nvmrc"
    assert nvmrc_path.is_file(), ".nvmrc file must exist"
    raw = nvmrc_path.read_text(encoding="utf-8")
    pinned = raw.strip()
    claude_text = _read("CLAUDE.md")
    assert (
        f"Node.js {pinned}" in claude_text
    ), f"CLAUDE.md must document Node.js {pinned} matching .nvmrc"
    assert "Node.js 20" not in claude_text, "CLAUDE.md must not reference outdated Node.js 20"
