"""Regression guard for DCR, DIR, and chart-dependence terminology (#5592)."""

from __future__ import annotations

import re
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]

GUARDED_SOURCES = (
    ROOT / "NOTATION.md",
    ROOT / "pages/validation-roadmap.qmd",
    ROOT / "pages/Golf_Control_Theory.qmd",
    ROOT / "articles/upstreamdrift-educational-integration.qmd",
    ROOT / "articles/The_Geometry_of_Motion/quarto/ch07_counterfactuals.qmd",
    ROOT / "articles/The_Geometry_of_Motion/quarto/ch08_applications.qmd",
    ROOT / "articles/The_Geometry_of_Motion/Volume_I/chapters/ch08_applications.tex",
    ROOT / "articles/The_Physics_of_Golf/quarto/ch05_affine_structure.qmd",
    ROOT / "articles/The_Physics_of_Golf/quarto/ch06_zero_torque_counterfactual.qmd",
)

RETIRED_PATTERNS: tuple[tuple[str, str], ...] = (
    (
        r"dimensionless drift-control ratio can be defined",
        "realized-input ratio mislabeled as DCR",
    ),
    (
        r"proportion of clubhead acceleration attributable to passive",
        "DCR read as attribution share",
    ),
    (
        r"kinetic-energy-metric Riemannian norms.*chart-invariant",
        "false chart-invariance for drift under M-norm",
    ),
    (
        r"makes the drift.*chart-invariant",
        "drift claimed chart-invariant",
    ),
)

_COMPILED = tuple((re.compile(pat, re.IGNORECASE | re.DOTALL), label) for pat, label in RETIRED_PATTERNS)


def test_guarded_sources_avoid_retired_dcr_wording() -> None:
    """Key publication sources must not resurrect retired DCR or invariance claims (#5592)."""
    failures: list[str] = []
    for path in GUARDED_SOURCES:
        text = path.read_text(encoding="utf-8")
        for pattern, label in _COMPILED:
            if pattern.search(text):
                failures.append(f"{path.relative_to(ROOT)}: {label}")
    assert not failures, "Retired DCR wording found:\n" + "\n".join(failures)


def test_validation_roadmap_states_drift_block_is_chart_dependent() -> None:
    """Validation roadmap must not promise chart-invariant drift acceleration (#5592 F3)."""
    text = (ROOT / "pages/validation-roadmap.qmd").read_text(encoding="utf-8")
    assert "drift block $a_d$ remains chart-dependent" in text
    assert "does not make the drift term coordinate-invariant" in (
        ROOT / "NOTATION.md"
    ).read_text(encoding="utf-8")


def test_planar_polar_counterexample_has_nonzero_drift_m_norm() -> None:
    """Free particle in polar coordinates: M-weighted drift norm is nonzero at rest (#5592 F3)."""
    m, radius, r_dot, theta_dot = sp.symbols("m r r_dot theta_dot", positive=True)
    m_mat = sp.diag(m, m * radius**2)
    drift_acc = sp.Matrix([radius * theta_dot**2, -2 * r_dot * theta_dot / radius])
    m_norm_sq = (drift_acc.T * m_mat * drift_acc)[0]
    value = sp.simplify(m_norm_sq.subs({m: 1, radius: 1, r_dot: 1, theta_dot: 2}))
    assert value == 32


def test_tex_and_quarto_ch08_both_name_dir_not_dcr_for_realized_input() -> None:
    """GoM ch08 tex and Quarto mirrors must agree on DIR vs DCR (#5592 F3 gom-d)."""
    for relative in (
        "articles/The_Geometry_of_Motion/quarto/ch08_applications.qmd",
        "articles/The_Geometry_of_Motion/Volume_I/chapters/ch08_applications.tex",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "realized drift-to-input ratio" in text or "realized drift-to-input ratio (DIR)" in text
        assert "dimensionless drift-control ratio can be defined" not in text
        assert re.search(r"DIR_\{W_a\}|\\mathrm\{DIR\}_\{W_a\}", text)
