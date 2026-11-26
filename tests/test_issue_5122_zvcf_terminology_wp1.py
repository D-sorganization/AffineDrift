"""WP-1 of Epic #5911 (resolves #5122): ZVCF is control-only; gravity-only is named apart.

Canonical convention (NOTATION.md ``term-zvcf``): ZVCF = M(q)^{-1} tau, the control
operand.  Shaft elastic preload belongs to drift, never to ZVCF.  The gravity-only
static acceleration -M(q)^{-1} g(q) is a separate named quantity.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ZTCF_ARTICLE = REPO_ROOT / "articles" / "zero-torque-counterfactual.qmd"
CH04 = (
    REPO_ROOT
    / "articles"
    / "proximal_distal_energy_transfer"
    / "chapters"
    / "_ch04_counterfactuals.qmd"
)
CH01 = (
    REPO_ROOT
    / "articles"
    / "proximal_distal_energy_transfer"
    / "chapters"
    / "_ch01_introduction.qmd"
)
CH11 = (
    REPO_ROOT
    / "articles"
    / "proximal_distal_companion"
    / "chapters"
    / "ch11_counterfactual_scissors.qmd"
)
TAXONOMY_ID = "tbl-counterfactual-taxonomy"
TAXONOMY_LINK = "/articles/proximal-distal-a-journey-through-the-swing.html#" + TAXONOMY_ID


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return re.sub(r"\s+", " ", _read(path))


def test_taxonomy_table_has_stable_anchor_and_zvcf_rows() -> None:
    text = _read(CH11)
    assert "{#" + TAXONOMY_ID + "}" in text
    flat = _flat(CH11)
    assert "ZVCF" in flat and "ZTCF" in flat
    assert "Gravity-only" in flat


@pytest.mark.parametrize("path", [ZTCF_ARTICLE, CH04], ids=lambda p: p.name)
def test_both_sources_link_taxonomy_table(path: Path) -> None:
    assert TAXONOMY_LINK in _read(path)


def test_ch04_zvcf_equation_is_control_only() -> None:
    text = _read(CH04)
    m = re.search(r"ddot q_\{\\mathrm\{ZVCF\}\}(.*?)\{#eq-zvcf\}", text, re.S)
    assert m, "eq-zvcf must remain defined"
    body = m.group(1)
    assert r"M(q)^{-1}" in body and r"\tau" in body
    assert "g(q)" not in body and "b(q" not in body


def test_ch04_gravity_only_has_its_own_name_and_equation() -> None:
    text = _read(CH04)
    assert "{#eq-gravity-only}" in text
    flat = _flat(CH04).lower()
    assert "gravity-only static acceleration" in flat
    assert "It is not the pure control contribution" not in flat
    assert "not called zvcf" in flat


def test_ch04_excludes_preload_from_zvcf() -> None:
    flat = _flat(CH04).lower()
    assert "preload" in flat
    assert "drift" in flat


def test_ztcf_article_excludes_preload_and_separates_gravity() -> None:
    flat = _flat(ZTCF_ARTICLE)
    assert "elastic preload" in flat
    assert "velocities and gravity are turned off" not in flat
    assert "gravity-only static acceleration" in flat.lower()


def test_ch01_zvcf_definition_matches_canon() -> None:
    flat = _flat(CH01)
    assert "both generalized velocity and the declared applied control" not in flat
