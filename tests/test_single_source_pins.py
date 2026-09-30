"""Single-source contracts for the coverage floor, Quarto, and Node pins.

The coverage floor used to be stated four different ways (75 / 65 / 65 / >50)
and the Quarto version twice (Docker 1.6.39 vs CI 1.8.26). Each value now has
exactly one authority: ``pyproject.toml`` ``[tool.coverage.report] fail_under``
and the ``.quarto-version`` file. Every other surface must defer to it.

The Node major version was likewise split (Dockerfile ``NODE_MAJOR=20`` vs CI
``node-version: "22"``, #4601). ``.nvmrc`` is now the single authority; the
Dockerfile pin and every workflow's ``node-version`` must match it.
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

NODE_VERSION_WORKFLOWS = (
    ".github/workflows/ci-standard.yml",
    ".github/workflows/cross-browser-nightly.yml",
    ".github/workflows/deploy-website.yml",
)

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
NODE_MAJOR = re.compile(r"^\d+$")


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


def test_nvmrc_is_a_single_node_major_version() -> None:
    """`.nvmrc` holds one bare Node major version and nothing else."""
    raw = _read(".nvmrc")
    assert raw.endswith("\n")
    lines = raw.splitlines()
    assert len(lines) == 1
    assert NODE_MAJOR.fullmatch(lines[0]), lines[0]


def test_dockerfile_node_pin_matches_nvmrc() -> None:
    """Docker builds must install the same Node major version as CI."""
    pinned = _read(".nvmrc").strip()
    match = re.search(r"^ARG NODE_MAJOR=(\S+)$", _read("Dockerfile"), flags=re.M)
    assert match is not None
    assert match.group(1) == pinned


def test_workflows_node_version_matches_nvmrc() -> None:
    """Every workflow's `node-version` matches the `.nvmrc` pin."""
    pinned = _read(".nvmrc").strip()
    for workflow in NODE_VERSION_WORKFLOWS:
        text = _read(workflow)
        versions = re.findall(r'node-version:\s*"(\d+)"', text)
        assert versions, workflow
        assert all(v == pinned for v in versions), (workflow, versions)


def test_claude_md_documents_the_pinned_node_version() -> None:
    """CLAUDE.md states the same Node version that `.nvmrc` pins."""
    pinned = _read(".nvmrc").strip()
    assert f"Node.js {pinned}" in _read("CLAUDE.md")
