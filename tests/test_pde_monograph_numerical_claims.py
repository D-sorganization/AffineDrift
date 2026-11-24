"""Tests that pinned artifacts reproduce the monograph's stated numerical claims."""

from __future__ import annotations

import pytest

from scripts.pde_monograph_numerical_claims import (
    compute_h4_held_out_contrast,
    count_e1_torque_programs,
    load_integrator_closure,
    load_uncertainty_integrator_closure,
)


def test_e1_program_row_and_distinct_counts() -> None:
    counts = count_e1_torque_programs()
    assert counts.program_rows == 92
    assert counts.distinct_programs == 88


def test_h4_held_out_q10_and_paired_deltas_match_archived_study() -> None:
    contrast = compute_h4_held_out_contrast()
    assert contrast.held_out_samples == 6
    assert contrast.early_restrain_q10_m_s == pytest.approx(4.705878716075947, rel=0, abs=1e-9)
    assert contrast.late_drive_q10_m_s == pytest.approx(4.417288308696056, rel=0, abs=1e-9)
    assert contrast.paired_speed_delta_min_m_s == pytest.approx(0.2502, abs=0.001)
    assert contrast.paired_speed_delta_median_m_s == pytest.approx(0.3185, abs=0.001)
    assert contrast.paired_speed_delta_max_m_s == pytest.approx(0.3720, abs=0.001)


def test_integrator_work_energy_residual_is_about_3_77_percent() -> None:
    closure = load_integrator_closure()
    assert closure.step_s == pytest.approx(0.004)
    assert closure.maximum_normalized_work_energy_residual == pytest.approx(0.0377, abs=0.0001)


def test_uncertainty_control_records_constraint_residuals_only() -> None:
    constraint = load_uncertainty_integrator_closure()
    assert "maximum_position_constraint_m" in constraint
    assert "maximum_contact_power_residual_w" in constraint
    assert constraint["maximum_position_constraint_m"] < 1e-9
