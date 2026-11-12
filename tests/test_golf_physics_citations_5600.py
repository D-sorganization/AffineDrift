"""Regression tests for Physics of Golf citation fixes (issue #5600)."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BIB = REPO / "articles" / "The_Physics_of_Golf" / "golf_physics.bib"
QUARTO = REPO / "articles" / "The_Physics_of_Golf" / "quarto"


def _bib_block(key: str) -> str:
    text = BIB.read_text(encoding="utf-8")
    match = re.search(rf"@\w+\{{{re.escape(key)},.*?\n\}}\n", text, re.DOTALL)
    assert match is not None, f"Missing bib entry {key!r}"
    return match.group(0)


def _quarto_text(name: str) -> str:
    return (QUARTO / name).read_text(encoding="utf-8")


def test_jorgensen_book_is_second_edition_springer_1999() -> None:
    block = _bib_block("Jorgensen1994")
    assert "edition = {2nd}" in block
    assert "publisher = {Springer-Verlag}" in block or "publisher = {Springer}" in block
    assert "year = {1999}" in block


def test_misleading_bib_keys_renamed() -> None:
    text = BIB.read_text(encoding="utf-8")
    obsolete = (
        "haykowsky2003resistance",
        "bo2004pelvic",
        "Sprigings2005",
        "hommel2009theory",
    )
    for key in obsolete:
        assert f"{{{key}," not in text, f"Obsolete key still defined: {key}"


def test_renamed_bib_keys_exist() -> None:
    for key in (
        "Haykowsky1996SAH",
        "Bo2005PelvicFloor",
        "SprigingsNeal2000",
        "Hommel2001TEC",
        "GomiKawato1996",
        "Feldman1986",
    ):
        _bib_block(key)


def test_ch28_impact_inputs_source_citations() -> None:
    ch28 = _quarto_text("ch28_impact_collision.qmd")
    assert "glossaryUSGAEquipment" in ch28 or "club_design_cg" in ch28
    assert "Cochran1968" in ch28 or "Penner2003" in ch28
    assert "illustrative $e=0.83$" not in ch28


def test_ch25_ucm_literature_cited() -> None:
    ch25 = _quarto_text("ch25_motor_learning.qmd")
    assert "Scholz1999" in ch25
    assert "uncontrolled-manifold" in ch25.lower() or "uncontrolled manifold" in ch25.lower()


def test_ch27_equilibrium_point_hypothesis_named() -> None:
    ch27 = _quarto_text("ch27_passive_distributed_control.qmd")
    assert "equilibrium-point" in ch27.lower() or "equilibrium point" in ch27.lower()
    assert "Feldman1986" in ch27
    assert "GomiKawato1996" in ch27
