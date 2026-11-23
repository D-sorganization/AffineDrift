"""Regression guards for the corrected proximal-distal monograph prose (#5610).

``test_pde_monograph_numerical_claims`` pins the numbers. These tests pin the
*wording* the #5610 acceptance criteria depend on, so a later edit cannot
silently restore the mis-signed energy ledger, the unqualified closure claim, or
an over-strong verdict. Each check is a whitespace-normalised substring match.
"""

from __future__ import annotations

import re
from pathlib import Path

ARTICLES = Path(__file__).resolve().parents[1] / "articles"
CHAPTERS = ARTICLES / "proximal_distal_energy_transfer" / "chapters"
WRAPPER = ARTICLES / "proximal-distal-energy-transfer.qmd"


def _text(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


def _chapter(name: str) -> str:
    return _text(CHAPTERS / name)


def test_energy_ledger_defines_es_and_signs_the_shaft_term() -> None:
    ch07c = _chapter("_ch07c_transmission_robustness.qmd")
    assert r"E_S \equiv T_S" in ch07c
    assert r"W_{\mathrm{release}} \equiv -\Delta U_{\mathrm{shaft}}" in ch07c
    assert "shaft_energy_release_j" in ch07c
    # The double-counted form (+Delta U_shaft and W_g inside a mechanical balance)
    # must not return.
    assert r"\underbrace{\Delta U_{\mathrm{shaft}}}_{W_{\mathrm{elastic}}}" not in ch07c


def test_closure_claim_is_restated_against_the_integrator_residual() -> None:
    ch07c = _chapter("_ch07c_transmission_robustness.qmd")
    assert "worst normalized work--energy residual of 3.77%" in ch07c
    assert "not a machine-precision closure claim" in ch07c


def test_h4_verdict_is_stated_at_the_strength_six_samples_support() -> None:
    ch06d = _chapter("_ch06d_uncertainty_control.qmd")
    assert "$n=6$, paired by seed" in ch06d
    assert "these six paired cases only" in ch06d
    assert "not a validated population lower" in ch06d


def test_program_count_distinguishes_rows_from_distinct_schedules() -> None:
    assert "88 distinct schedules" in _chapter("_ch06_methods.qmd")


def test_conclusions_report_the_modal_shaft_study_and_six_falsifiers() -> None:
    ch09 = _chapter("_ch09_conclusions.qmd")
    assert "registered 5% deflection screen fails" in ch09
    assert "six prediction-specific falsifiers (EXP-H1--EXP-H6)" in ch09


def test_uncertainty_ucm_index_is_flagged_as_not_comparable() -> None:
    ch07c = _chapter("_ch07c_transmission_robustness.qmd")
    assert "0.0264 per degree of freedom" in ch07c
    assert "not directly comparable to published uncontrolled-manifold indices" in ch07c


def test_wrapper_discloses_the_energy_matched_family_that_weakens_the_result() -> None:
    wrapper = _text(WRAPPER)
    assert "A third family matches total kinetic energy" in wrapper
    assert r"$R^2 \approx 0.005$" in wrapper
    assert "undercuts monotonic proximal-speed narratives" in wrapper


def test_coriolis_work_is_not_presented_as_an_energy_change() -> None:
    ch03ba = _chapter("_ch03ba_coordinate_force_sources.qmd")
    assert r"Neither sum alone is $\Delta K$" in ch03ba


def test_ch05b_does_not_claim_speed_outcomes_it_does_not_report() -> None:
    ch05b = _chapter("_ch05b_forward_two_hand.qmd")
    assert "does not report clubhead-speed or tangential-acceleration traces" in ch05b


def test_ztcf_contact_power_discrepancy_stays_disclosed() -> None:
    assert "maximum ZTCF discrepancy is 72.8 W" in _chapter("_ch05_two_hand_wrench.qmd")
