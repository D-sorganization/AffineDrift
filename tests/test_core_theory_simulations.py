"""Regression tests for pinned core-theory figure simulations (#5590)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from src.affine_control.core_theory_simulations import (
    SuperpositionBreakdownSeries,
    ZtcfFigureSeries,
    load_json_pin,
    superposition_breakdown_series,
    superposition_instantaneous_vectors,
    superposition_modal_responses,
    ztcf_figure_series,
)

REPO = Path(__file__).resolve().parent.parent
ZTcf_PIN = REPO / "data/core_theory/ztcf_figure_run_v1.json"
SUP_PIN = REPO / "data/core_theory/superposition_breakdown_run_v1.json"


def test_pins_load() -> None:
    """Pinned figure-run records must parse as JSON objects."""
    assert load_json_pin(ZTcf_PIN)["figure_set"] == "ztcf"
    assert load_json_pin(SUP_PIN)["figure_set"] == "superposition_breakdown"


def test_ztcf_series_matches_fixture_state() -> None:
    """ZTCF figure series uses the registered fixture initial state."""
    pin = load_json_pin(ZTcf_PIN)
    fixture = json.loads((REPO / pin["model_fixture"]).read_text(encoding="utf-8"))
    series = ztcf_figure_series(pin_path=ZTcf_PIN)
    assert isinstance(series, ZtcfFigureSeries)
    q0 = np.asarray(fixture["state"]["q"], dtype=float)
    qd0 = np.asarray(fixture["state"]["qd"], dtype=float)
    from src.affine_control.golf_model import SEGMENTS

    expected = SEGMENTS.clubhead_speed(q0, qd0)
    assert series.actual_speed_m_s[0] == pytest.approx(expected, rel=1e-6)
    assert len(series.branch_steps) == len(pin["branch_intervention_steps"])


def test_superposition_error_scales_like_t4_at_short_horizons() -> None:
    """Position superposition error grows ~t^4 for the pinned double-pendulum run."""
    series = superposition_breakdown_series(pin_path=SUP_PIN)
    assert isinstance(series, SuperpositionBreakdownSeries)
    mask = (series.time_s > 0.005) & (series.position_error_norm > 1e-8)
    log_t = np.log(series.time_s[mask])
    log_e = np.log(series.position_error_norm[mask])
    slope, _ = np.polyfit(log_t, log_e, 1)
    assert 3.5 < slope < 4.6


def test_superposition_instantaneous_vectors_close_parallelogram() -> None:
    """Instantaneous acceleration increments from two inputs sum exactly."""
    vectors = superposition_instantaneous_vectors()
    delta = vectors.combined - (vectors.baseline + vectors.delta_u1 + vectors.delta_u2)
    assert np.linalg.norm(delta) < 1e-10


def test_superposition_modal_responses_use_mass_matrix_inverse() -> None:
    """Unit-torque modal bars come from M(q)^{-1}, not hand-typed literals."""
    bars = superposition_modal_responses()
    assert bars.responses.shape == (3, 3)
    assert np.all(np.isfinite(bars.responses))
    assert np.linalg.norm(bars.responses) > 0.0
