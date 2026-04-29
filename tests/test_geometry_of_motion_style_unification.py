"""Guardrails for shared Tangent-Space Methods LaTeX style integration."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT = Path(__file__).resolve().parents[1]
STYLE_FILE = ROOT / "articles" / "The_Geometry_of_Motion" / "geometry_of_motion.sty"
VOLUME_MAIN_FILES = (
    ROOT / "articles" / "The_Geometry_of_Motion" / "Volume_0" / "main.tex",
    ROOT / "articles" / "The_Geometry_of_Motion" / "Volume_I" / "main.tex",
    ROOT / "articles" / "The_Geometry_of_Motion" / "Volume_II" / "main.tex",
    ROOT / "articles" / "The_Geometry_of_Motion" / "Volume_III" / "main.tex",
    ROOT / "articles" / "The_Geometry_of_Motion" / "Volume_IV" / "main.tex",
    ROOT / "articles" / "The_Geometry_of_Motion" / "Volume_V" / "main.tex",
)


def test_shared_style_file_exists_with_core_primitives() -> None:
    """Shared style should provide color, theorem, and listing primitives."""
    text = STYLE_FILE.read_text(encoding="utf-8")
    assert r"\ProvidesPackage{geometry_of_motion}" in text
    assert "chapblue" in text
    assert r"\gomapplylistingstyle" in text
    assert r"\gomdeclaretheorems" in text
    assert r"\RequirePackage[most]{tcolorbox}" not in text
    assert r"\RequirePackage{tcolorbox}" in text
    assert r"\providecommand{\dd}" in text


def test_all_volumes_import_shared_style_package() -> None:
    """All geometry volumes should import the shared style package."""
    for main_file in VOLUME_MAIN_FILES:
        text = main_file.read_text(encoding="utf-8")
        assert r"\usepackage{../geometry_of_motion}" in text
        assert r"\gomapplylistingstyle" in text
