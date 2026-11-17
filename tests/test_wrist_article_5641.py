"""Regression checks for wrist-universal-joint editorial fixes (#5641)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/wrist-universal-joint.qmd"
SIMULATOR = ROOT / "src/tools/wrist_universal_joint/grip_angle_simulator.html"


@pytest.mark.content_lint
def test_wrist_coaching_takeaway_does_not_call_constraints_purely_passive() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    assert "golfers-coaches:" in text
    assert "not purely passive" in text
    lower = text.lower()
    assert "depend on active joint torques" in lower or "active joint torques" in lower
    assert "wrist compliance" in lower


@pytest.mark.content_lint
def test_wrist_article_pins_simscape_comparison_sources() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    assert "Kinetically_Driven_Universal_Joint.slx" in text
    assert "GolfSwing3D_Kinetic.slx" in text
    assert "UpstreamDrift" in text


@pytest.mark.content_lint
def test_grip_simulator_labels_illustrative_inertia_ratio() -> None:
    html = SIMULATOR.read_text(encoding="utf-8")
    assert "0.5 * I_alpha" in html
    assert "illustrative" in html.lower()
    assert "not a measured" in html.lower() or "not measured" in html.lower()
