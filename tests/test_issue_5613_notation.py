"""Notation and front-matter contracts for issue #5613 (mechanics reference articles)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_force_mobility_disambiguates_kinematic_ellipsoid_from_dynamic_mobility() -> None:
    text = (ROOT / "articles/force-mobility-matrices.qmd").read_text(encoding="utf-8")
    assert "velocity (manipulability) ellipsoid" in text
    assert "#sec-velocity-manipulability-ellipsoid" in text
    assert "purely **kinematic**" in text
    assert "H=JM^{-1}J^{\\mathsf T}" in text
    assert "multibody-drift-control-v3" in text


def test_after_one_solution_fibre_dimension_uses_n_not_row_count_m() -> None:
    text = (ROOT / "articles/after-one-solution-null-space-exploration.qmd").read_text(
        encoding="utf-8"
    )
    assert "$n$ activation coordinates" in text
    assert "n-\\operatorname{rank}A" in text
    assert re.search(r"balance written in \$m\$ activation", text) is None
    assert "c_{\\min}" in text and "c_{\\max}" in text
    assert re.search(r"minimum \$m\$ and maximum \$M\$", text) is None


def test_screw_reference_defines_reciprocal_product_before_use() -> None:
    text = (ROOT / "articles/screw-theory-reference.qmd").read_text(encoding="utf-8")
    assert "#sec-reciprocal-screws" in text
    assert "Reciprocal Screws and Constraint Couples" in text
    assert "\\mathcal F^\\top\\mathcal V" in text
    assert "\\mathcal S^\\perp" in text
    assert "\\dim\\mathcal S+\\dim\\mathcal S^\\perp=6" in text


def test_intentional_constraint_collapse_front_matter_matches_untested_hypothesis() -> None:
    text = (ROOT / "articles/intentional-constraint-collapse.qmd").read_text(encoding="utf-8")
    assert 'evidence-rung: "mathematical-identity"' in text
    assert 'evidence-rung: "qualified-simulation"' not in text
    assert "testable hypothesis" in text
    assert "not yet tested" in text.lower()
