"""Regression tests for technology articles manifesto notation, Bosch bib, and hub blurb (#5616)."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_manifesto_notation_table_disambiguates_gravity_and_input_map() -> None:
    """Manifesto notation table must reserve uppercase G(x) for input and use g(q) for gravity."""
    text = (REPO_ROOT / "articles" / "drifter-manifesto.qmd").read_text(encoding="utf-8")
    assert "| $g(q)$ | Gravitational torque vector |" in text
    assert "| $G(q)$ |" not in text
    assert "| $G(x)$ | Input vector fields defining linear influence of torque inputs |" in text
    assert "| $f(x)$ | Drift vector field (zero-input drift) |" in text


def test_geometry_of_motion_bosch_bib_defects_fixed() -> None:
    """Geometry of Motion Bosch additions must not duplicate Scholz1999 or misdate Bizzi 1991."""
    bib_path = (
        REPO_ROOT
        / "articles"
        / "bosch_integration"
        / "bib_entries"
        / "geometry_of_motion_additions.bib"
    )
    text = bib_path.read_text(encoding="utf-8")
    assert "Sch{\\o}ner" not in text
    assert "@article{Scholz1999," not in text
    assert "@article{ScholzSchoner1999," in text
    assert 'Sch\\"{o}ner' in text or 'Sch{\\"o}ner' in text
    assert "number={3}," in text
    assert "@article{Bizzi1992," not in text
    bizzi_match = re.search(r"@article\{Bizzi1991,.*?\n\}", text, flags=re.DOTALL)
    assert bizzi_match is not None
    assert "year = {1991}," in bizzi_match.group(0)


def test_golf_physics_bosch_bib_defects_fixed() -> None:
    """Golf Physics Bosch additions must spell Schoner with umlaut and date Bizzi 1991."""
    bib_path = (
        REPO_ROOT / "articles" / "bosch_integration" / "bib_entries" / "golf_physics_additions.bib"
    )
    text = bib_path.read_text(encoding="utf-8")
    assert "Sch{\\o}ner" not in text
    assert "@article{Scholz1999," in text
    assert 'Scholz, John P. and Sch{\\"o}ner, Gregor' in text
    assert "@article{Bizzi1992," not in text
    bizzi_match = re.search(r"@article\{Bizzi1991,.*?\n\}", text, flags=re.DOTALL)
    assert bizzi_match is not None
    assert "year = {1991}," in bizzi_match.group(0)


def test_technology_hub_club_fitting_blurb_drops_swing_weights() -> None:
    """Hub blurb must not promise swing-weight coverage absent from technology-club-fitting.qmd."""
    hub_text = (REPO_ROOT / "pages" / "technology.qmd").read_text(encoding="utf-8")
    match = re.search(
        r"### \[Club Fitting Simulation and Parameter Identification\][^\n]*\n\n([^\n]+)",
        hub_text,
    )
    assert match is not None
    blurb = match.group(1)
    assert "swing weight" not in blurb.lower()
    assert "Explains club model changes and shaft bend." in blurb
