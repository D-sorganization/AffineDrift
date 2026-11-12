"""Issue #5430: ZVCF names the control component; ZTCF names drift (Dieter 2026-11-03)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

NOTATION = REPO_ROOT / "NOTATION.md"
QUICK_REF = REPO_ROOT / "pages" / "notation-quick-reference.qmd"
ZERO_VEL = REPO_ROOT / "_includes" / "mechanics-zero-velocity.qmd"
TAXONOMY = REPO_ROOT / "_includes" / "mechanics-force-taxonomy.qmd"
ALGORITHM = REPO_ROOT / "_includes" / "mechanics-counterfactual-algorithm.qmd"

SCOPED_SOURCES = (NOTATION, QUICK_REF, ZERO_VEL, TAXONOMY, ALGORITHM)


@pytest.mark.parametrize("path", SCOPED_SOURCES, ids=lambda p: p.name)
def test_scoped_sources_exist(path: Path) -> None:
    assert path.is_file()


def test_notation_defines_zvcf_as_control_component() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    section = text[text.index("### ") : text.index("### DCR")]
    assert "ZVCF" in section and "control" in section.lower()
    assert r"M(q)^{-1}" in section or r"M^{-1}" in section
    assert "tau" in section or r"\tau" in section
    assert "ZTCF" in section and "drift" in section.lower()
    assert "gravity" in section.lower()
    assert "fixed" in section.lower() or "same-state" in section.lower()
    assert r"a_{\mathrm{ZVCF}}(q,z;p)=-M(q)^{-1}h(q,0" not in text


def test_notation_superposition_counts_gravity_once() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "ZTCF" in text and "ZVCF" in text
    window = text[text.index("### Pointwise") : text.index("### DCR")]
    assert "+" in window
    assert "integrated" in window.lower() or "integrat" in window.lower()


def test_mechanics_zero_velocity_include_uses_zvcf_for_control() -> None:
    text = ZERO_VEL.read_text(encoding="utf-8")
    assert "ZVCF" in text
    assert "control" in text.lower()
    assert r"a_{\mathrm{ZVCF}}=-M(z)^{-1}h_0(z)" not in text
    assert "zero-velocity baseline" in text.lower() or "configuration baseline" in text.lower()


def test_mechanics_force_taxonomy_same_state_additive_split() -> None:
    text = TAXONOMY.read_text(encoding="utf-8")
    assert "ZTCF" in text and "ZVCF" in text
    assert "drift" in text.lower() and "control" in text.lower()
    assert r"\tau_{\mathrm{ZVCF}}:=-h_0(z)" not in text
    assert "double" not in text.lower() or "twice" in text.lower() or "same state" in text.lower()


def test_mechanics_counterfactual_algorithm_checks_drift_plus_control() -> None:
    text = ALGORITHM.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "zvcf" in lowered and "control" in lowered
    assert "drift" in lowered
    assert "configuration_drift = -bias_load(z, zero_velocity)" not in text
    assert "drift" in text and "control" in text


def test_notation_quick_reference_card_labels_zvcf_control() -> None:
    text = QUICK_REF.read_text(encoding="utf-8")
    assert "ZTCF" in text and "ZVCF" in text
    assert "drift" in text.lower()
    assert "control" in text.lower()


def test_terminology_gate_passes_on_repo() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "check_terminology.py"),
            "--baseline",
            str(REPO_ROOT / "config" / "terminology-baseline.json"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.integration
def test_notation_pages_render() -> None:
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for notation page render check")
    result = subprocess.run(
        [
            quarto,
            "render",
            "pages/notation.qmd",
            "pages/notation-quick-reference.qmd",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
    )
    assert result.returncode == 0, f"quarto render failed:\n{result.stderr}\n{result.stdout}"
