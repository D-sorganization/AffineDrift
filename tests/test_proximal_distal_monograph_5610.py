"""Content contracts for AffineDrift #5610 (PDE energy ledger, closure, evidence strength)."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FORCE_SOURCE_ARCHIVE = ROOT / "reports/technical-review/force-work-provider-outcomes.json"
MONOGRAPH = ROOT / "articles/proximal_distal_energy_transfer"
WRAPPER = ROOT / "articles/proximal-distal-energy-transfer.qmd"

CH03BA = MONOGRAPH / "chapters/_ch03ba_coordinate_force_sources.qmd"
CH05B = MONOGRAPH / "chapters/_ch05b_forward_two_hand.qmd"
CH06D = MONOGRAPH / "chapters/_ch06d_uncertainty_control.qmd"
CH06E = MONOGRAPH / "chapters/_ch06e_experimental_protocol.qmd"
CH06_METHODS = MONOGRAPH / "chapters/_ch06_methods.qmd"
CH07C = MONOGRAPH / "chapters/_ch07c_transmission_robustness.qmd"
CH09 = MONOGRAPH / "chapters/_ch09_conclusions.qmd"


def test_ch07c_defines_kinetic_subsystem_ledger_with_shaft_release() -> None:
    """F1: E_S is T_S; W_release aligns with shaft_energy_release_j."""
    text = CH07C.read_text(encoding="utf-8")
    assert r"Take $E_S \equiv T_S$" in text or "E_S \\equiv T_S" in text
    assert "shaft_energy_release_j" in text
    assert r"W_{\mathrm{release}} \equiv -\Delta U_{\mathrm{shaft}}" in text
    assert r"\Delta T_S =" in text
    assert "3.77%" in text


def test_ch06d_separates_constraint_residuals_from_work_energy_error() -> None:
    """F2/F3: closure wording and H4 strength on n=6 held-out ensemble."""
    text = CH06D.read_text(encoding="utf-8")
    assert "materially below the reported effects" not in text
    assert "3.77%" in text
    assert "$n=6$" in text or "n=6" in text
    assert "H4 is supported" not in text
    assert "consistent" in text.lower()
    assert "paired" in text.lower()


def test_e1_program_counts_in_methods() -> None:
    """F7: 92 rows, 88 distinct torque programs."""
    text = CH06_METHODS.read_text(encoding="utf-8")
    assert "92 program rows" in text
    assert "88 distinct" in text


def test_ch03ba_states_velocity_bias_energy_neutral_identity() -> None:
    """F6 (pde-a): Coriolis and squared-speed generalized work do not change K alone."""
    text = CH03BA.read_text(encoding="utf-8")
    assert r"\tfrac12\dot{\mathbf q}^{\mathsf T}\dot{\mathbf M}\dot{\mathbf q}" in text
    assert "do not appear as separate sinks" in text
    assert r"\mathrm d K/\mathrm dt" in text
    assert "opposes the instantaneous generalized velocity on net" not in text
    assert r"\dot{\mathbf q}^{\mathsf T}(\boldsymbol\tau-\mathbf g-\mathbf d)" in text
    assert r"\boldsymbol\tau+\mathbf g" not in text
    assert r"\boldsymbol\tau+\mathbf g_{\mathrm{grav}}" not in text


def _max_coriolis_impulse_row() -> dict[str, object]:
    archive = json.loads(FORCE_SOURCE_ARCHIVE.read_text(encoding="utf-8"))
    qualified = [r for r in archive["outcomes"] if r["status"] == "qualified_impact"]
    return max(qualified, key=lambda r: r["coriolis_absolute_tangent_impulse_n_s"])


def test_ch03ba_max_impulse_work_ledger_matches_archive_sums() -> None:
    """Quoted component work and the velocity-bias pair sum match the registered archive."""
    row = _max_coriolis_impulse_row()
    text = CH03BA.read_text(encoding="utf-8")
    assert row["candidate"]["wrist_restrain_nm"] == 10
    assert row["candidate"]["onset_s"] == 0.1
    coriolis = float(row["coriolis_work_j"])
    squared = float(row["squared_speed_work_j"])
    gravity = float(row["gravity_work_j"])
    applied = float(row["applied_work_j"])
    assert coriolis == pytest.approx(-100.69, abs=0.005)
    assert squared == pytest.approx(-33.73, abs=0.005)
    assert gravity == pytest.approx(25.56, abs=0.005)
    assert applied == pytest.approx(358.20, abs=0.005)
    bias_sum = coriolis + squared
    four_sum = bias_sum + gravity + applied
    assert bias_sum == pytest.approx(-134.42, abs=0.005)
    assert four_sum == pytest.approx(249.34, abs=0.01)
    assert four_sum != pytest.approx(bias_sum, abs=1.0)
    assert "-100.69 J" in text
    assert "-33.73 J" in text
    assert "+25.56 J" in text
    assert "+358.20 J" in text
    assert "-134.42" in text
    assert "213.6" not in text
    assert "Their sum is $-134.42$" not in text


def test_ch05b_does_not_claim_unreported_distal_speed_outcomes() -> None:
    """F8 (pde-a): strategy wording stays within reported forward-couple interval."""
    text = CH05B.read_text(encoding="utf-8")
    assert "increasing distal speed" not in text
    assert "club acceleration" not in text.lower()


def test_wrapper_discloses_energy_matched_velocity_family() -> None:
    """F5 (pde-a): site wrapper mentions the adverse energy-matched contract."""
    text = WRAPPER.read_text(encoding="utf-8")
    assert "third family" in text.lower() or "energy-matched" in text.lower()
    assert "R^2" in text or "0.005" in text


def test_ch06e_protocol_registration_wording() -> None:
    """F10: preregistration scope is explicit (self-registered + JSON-linked gates)."""
    text = CH06E.read_text(encoding="utf-8")
    assert "version-pinned" in text
    assert "self-registered" in text
    assert "eight valid driver swings" in text.lower()
    assert "10% body weight" in text


def test_ch09_modal_shaft_and_six_falsifiers() -> None:
    """F6 (pde-b): conclusions acknowledge ch06bbb and six EXP falsifiers."""
    text = CH09.read_text(encoding="utf-8")
    assert "forward modal-shaft" in text.lower() or "modal-shaft coupling" in text
    assert "EXP-H1--EXP-H6" in text or "EXP-H1" in text and "EXP-H6" in text
    assert "four prediction-specific falsifiers" not in text
