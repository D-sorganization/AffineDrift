"""Content contracts for AffineDrift #5610 (PDE energy ledger, closure, evidence strength)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
