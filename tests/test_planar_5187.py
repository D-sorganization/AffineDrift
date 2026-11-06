"""Smoke tests for planar triple-pendulum #5187 pipeline ( AffineDrift #5187)."""

from __future__ import annotations

import numpy as np

from src.affine_control.planar_5187 import Planar5187Config, run_planar_5187_pipeline


def test_planar_5187_pipeline_runs_and_finishes() -> None:
    cfg = Planar5187Config(dt_s=0.01, monte_carlo_samples=4)
    result = run_planar_5187_pipeline(cfg)
    assert np.isfinite(result.mc["rho_monte_carlo"])
    assert result.mc["n_samples"] == 4
    assert result.mc["sigma_max_phi_event"] > 0.0
