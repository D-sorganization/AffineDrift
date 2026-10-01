"""Tests verifying Quarto equation numbering and cross-references (issue #4580).

Ensures that:
1. MathJax loader sets `tags: 'none'` to avoid conflict with Quarto numbering.
2. No content files contain raw LaTeX equation labels (`\\label{eq:...}`).
3. No raw LaTeX `\\begin{equation}` or `\\begin{align}` environments remain in `.qmd` sources.
4. Equation cross-references follow Quarto syntax (`@eq-...`) rather than raw LaTeX (`\\ref{eq:...}`, `\\eqref{eq:...}`).
5. Target converted articles contain standard Quarto `{#eq-...}` labels.
6. All `@eq-...` cross-references in `.qmd` files resolve to defined labels.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

EQUATION_LABEL_DEF_PATTERN = re.compile(r"\{#(eq-[A-Za-z0-9_:-]+)\}")
EQUATION_REF_PATTERN = re.compile(r"@((?:eq-[A-Za-z0-9_:-]+))")
RAW_EQ_LABEL_PATTERN = re.compile(r"\\label\{eq:")
RAW_EQ_ENV_PATTERN = re.compile(r"\\begin\{(?:equation|align)\*?\}")
RAW_EQ_REF_PATTERN = re.compile(r"\\(?:eq)?ref\{eq:")


def _iter_qmd_files() -> list[Path]:
    """Return all .qmd files in the repository."""
    return sorted(REPO_ROOT.rglob("*.qmd"))


def test_mathjax_loader_equation_tags_disabled() -> None:
    """MathJax loader must disable native TeX tagging to avoid double numbering."""
    loader_path = REPO_ROOT / "_includes" / "mathjax-loader.html"
    assert loader_path.is_file(), f"MathJax loader not found at {loader_path}"
    content = loader_path.read_text(encoding="utf-8")

    assert "tags: 'none'" in content, "Expected tags: 'none' in MathJax config"
    assert "tags: 'ams'" not in content, "tags: 'ams' should be replaced with 'none'"


def test_no_raw_latex_equation_labels_in_qmd() -> None:
    """No .qmd files should use raw \\label{eq:...}."""
    violations: dict[str, list[int]] = {}
    for qmd in _iter_qmd_files():
        lines = qmd.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            if RAW_EQ_LABEL_PATTERN.search(line):
                rel_path = str(qmd.relative_to(REPO_ROOT))
                violations.setdefault(rel_path, []).append(idx)

    assert not violations, f"Raw \\label{{eq:...}} found in files: {violations}"


def test_no_raw_latex_equation_environments_in_qmd() -> None:
    """No .qmd files should use raw \\begin{equation} or \\begin{align}."""
    violations: dict[str, list[int]] = {}
    for qmd in _iter_qmd_files():
        lines = qmd.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            if RAW_EQ_ENV_PATTERN.search(line):
                rel_path = str(qmd.relative_to(REPO_ROOT))
                violations.setdefault(rel_path, []).append(idx)

    assert (
        not violations
    ), f"Raw \\begin{{equation}} or \\begin{{align}} found in files: {violations}"


def test_no_raw_latex_equation_references_in_qmd() -> None:
    """Equation cross-references must follow Quarto syntax (@eq-...), not LaTeX \\ref{eq:...}."""
    violations: dict[str, list[int]] = {}
    for qmd in _iter_qmd_files():
        lines = qmd.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            if RAW_EQ_REF_PATTERN.search(line):
                rel_path = str(qmd.relative_to(REPO_ROOT))
                violations.setdefault(rel_path, []).append(idx)

    assert not violations, f"Raw LaTeX equation references found in files: {violations}"


def test_target_files_have_quarto_equation_labels() -> None:
    """Target converted files must contain canonical Quarto {#eq-...} labels."""
    expected_labels: dict[str, list[str]] = {
        "articles/The_Geometry_of_Motion/quarto/ch03b_induced_acceleration_biomechanics.qmd": [
            "eq-ch3b-eom",
            "eq-ch3b-forward",
            "eq-ch3b-biomech_convention",
            "eq-ch3b-iaa_decomp",
        ],
        "articles/The_Geometry_of_Motion/quarto/ch05_optimal_control.qmd": [
            "eq-ch5:traj-opt",
            "eq-ch5:bellman",
            "eq-ch5:lagrangian",
            "eq-ch5:kkt-u",
            "eq-ch5:costate-update",
            "eq-ch5:cost-expansion",
            "eq-ch5:perturbation",
            "eq-ch5:Qx",
            "eq-ch5:Qxx",
            "eq-ch5:Quu",
            "eq-ch5:Qxu",
            "eq-ch5:feedback-affine",
            "eq-ch5:gain-def",
            "eq-ch5:S-def",
            "eq-ch5:riccati-full",
            "eq-ch5:riccati-alt",
            "eq-ch5:quad-convergence",
            "eq-ch5:pendulum-dynamics",
            "eq-ch5:pendulum-first-order",
            "eq-ch5:hjb",
            "eq-ch5:DRE",
        ],
        "articles/The_Geometry_of_Motion/quarto/ch09_parallel_mechanisms_constrained_dynamics.qmd": [
            "eq-ch9:tangent-constraint",
            "eq-ch9:accel-constraint",
            "eq-ch9:orthogonal-complement",
            "eq-ch9:euler-lagrange-constrained",
            "eq-ch9:christoffel",
            "eq-ch9:multiplier",
            "eq-ch9:drift",
            "eq-ch9:input-field",
            "eq-ch9:general-control",
            "eq-ch9:optimal-null-space",
            "eq-ch9:passivity",
            "eq-ch9:mechanical-connection",
            "eq-ch9:berry-phase-formula",
        ],
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd": [
            "eq-pend_unactuated",
            "eq-unactuated_dynamics",
        ],
    }

    for rel_path, labels in expected_labels.items():
        file_path = REPO_ROOT / rel_path
        assert file_path.is_file(), f"Expected file not found: {rel_path}"
        text = file_path.read_text(encoding="utf-8")
        found_labels = set(EQUATION_LABEL_DEF_PATTERN.findall(text))
        for expected in labels:
            assert expected in found_labels, f"Missing expected label '{expected}' in {rel_path}"


def test_all_equation_cross_references_resolve() -> None:
    """All @eq-... cross-references across .qmd files must resolve to existing labels."""
    defined_labels: set[str] = set()
    for qmd in _iter_qmd_files():
        text = qmd.read_text(encoding="utf-8")
        defined_labels.update(EQUATION_LABEL_DEF_PATTERN.findall(text))

    unresolved: list[tuple[str, str]] = []
    for qmd in _iter_qmd_files():
        text = qmd.read_text(encoding="utf-8")
        for match in EQUATION_REF_PATTERN.findall(text):
            clean_ref = match.rstrip(":.,;!?")
            if clean_ref not in defined_labels:
                unresolved.append((str(qmd.relative_to(REPO_ROOT)), clean_ref))

    assert not unresolved, f"Unresolved equation cross-references found: {unresolved}"
