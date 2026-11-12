"""Notation and prose contracts for issue #5614 (ball, putting, slack articles)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_slack_takeup_stiffness_prose_matches_two_independent_draws() -> None:
    text = (ROOT / "articles/slack-takeup-identifiability.qmd").read_text(encoding="utf-8")
    assert "one stiffness scale shared" not in text
    assert "independent stiffness" in text.lower() or "two independent stiffness" in text.lower()
    assert "**seven** unknowns" in text


def test_green_simulation_uses_putting_roll_slip_convention() -> None:
    text = (ROOT / "articles/green-simulation.qmd").read_text(encoding="utf-8")
    assert "signed slip $s=v-R\\omega$" in text
    assert "signed forward spin speed $s=R\\omega$" not in text
    assert "signed slip $u=v-s$" not in text
    assert "v_{\\mathrm{ff}}" in text
    assert "v_{\\mathrm{proxy}}" in text


def test_putting_roll_penner_capture_uses_distinct_symbol() -> None:
    text = (ROOT / "articles/putting-roll-models.qmd").read_text(encoding="utf-8")
    assert "v_P(b)=1.63" in text or "v_{\\mathrm P}(b)" in text
    assert re.search(r"v_c\(b\)=1\.63", text) is None


def test_appendix_uses_hyphenated_ztcf_term() -> None:
    text = (ROOT / "articles/appendix-applications.qmd").read_text(encoding="utf-8")
    assert "Zero-Torque Counterfactual" in text
    assert "Zero Torque Counterfactual" not in text


def test_slack_management_tracking_error_not_named_j() -> None:
    text = (ROOT / "articles/slack-management-linked-systems.qmd").read_text(encoding="utf-8")
    assert "**Integrated tracking error** $\\mathcal{E}$" in text or (
        "**Integrated tracking error** $E$" in text
    )
    assert "Integrated tracking error** $J$" not in text


def test_impact_reference_disambiguates_reused_symbols() -> None:
    text = (ROOT / "articles/impact-mechanics-and-ball-flight.qmd").read_text(encoding="utf-8")
    assert "I_b=\\kappa mR^2" in text
    assert "\\lambda_s" in text
    assert "\\mathbf{v}_{\\mathrm{rel}}" in text
    assert "\\mathbf{v}_{\\mathrm{cp}}" in text
    assert "horizontal launch $\\beta_h$" in text


def test_shot_pattern_has_checkable_methods_and_verified_date() -> None:
    text = (ROOT / "articles/shot-pattern-analysis.qmd").read_text(encoding="utf-8")
    assert 'date: "Date unverified"' not in text
    assert "UpstreamDrift" in text
    assert "highest-density" in text.lower() or "HDR" in text
    assert "strokes gained" in text.lower() or "strokes-gained" in text.lower()
