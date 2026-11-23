"""Pin Chapter 7c transmission numbers to local UpstreamDrift study snapshots (#5610)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.check_pde_ch07c_transmission_claims import verify_ch07c_transmission_claims
from scripts.pde_monograph_numerical_claims import (
    _format_scientific_latex,
    _round_display,
    load_ch07c_transmission_claims,
    load_integrator_closure,
)

CH07C = (
    Path(__file__).resolve().parents[1]
    / "articles/proximal_distal_energy_transfer/chapters/_ch07c_transmission_robustness.qmd"
)


def test_ch07c_prose_matches_pinned_transmission_snapshots() -> None:
    assert verify_ch07c_transmission_claims() == []


def test_closure_contact_power_matches_transmission_study_snapshot() -> None:
    closure = load_integrator_closure()
    assert closure.maximum_contact_power_residual_w == pytest.approx(8.526512829121202e-14)
    assert closure.maximum_normalized_work_energy_residual == pytest.approx(0.037655635794477435)
    text = CH07C.read_text(encoding="utf-8")
    latex = _format_scientific_latex(closure.maximum_contact_power_residual_w)
    assert latex.strip("$") in text


def test_ch07c_held_out_q10_values_match_claims_snapshot() -> None:
    claims = load_ch07c_transmission_claims()
    text = CH07C.read_text(encoding="utf-8")
    assert claims.held_out_perturbations == 15
    assert (
        f"{_round_display(claims.clock_q10_delivery_speed_m_s):.2f}" in text
        and f"{_round_display(claims.state_q10_delivery_speed_m_s):.2f}" in text
    )
    assert claims.synergy_index == pytest.approx(0.932, abs=0.001)
    assert f"=0.{int(round(claims.synergy_index * 1000)):03d}" in text


def test_ch07c_ucm_totals_match_local_task_map_snapshot() -> None:
    claims = load_ch07c_transmission_claims()
    text = re.sub(r"\s+", " ", CH07C.read_text(encoding="utf-8"))
    assert f"{_round_display(claims.null_variance, 4):.4f}" in text
    assert f"{_round_display(claims.task_relevant_variance, 5):.5f}" in text
