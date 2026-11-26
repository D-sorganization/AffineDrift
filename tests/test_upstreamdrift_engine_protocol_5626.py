"""Engine-protocol disambiguation for UpstreamDrift counterfactual method names (#5626 G1)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "pages" / "upstreamdrift-engine-protocol.qmd"


@pytest.mark.content_lint
def test_engine_protocol_disambiguates_compute_zvcf_from_site_zvcf() -> None:
    """Readers must not equate PhysicsEngine.compute_zvcf with AffineDrift ZVCF."""
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "## PhysicsEngine Counterfactual Names Versus AffineDrift Notation" in text
    assert "compute_control_acceleration" in text
    assert "simulation_backends" in text and "ztcf_zvcf" in text
    assert "zero-velocity baseline" in text.lower()
    assert "must not be called ZVCF on this site" in text or "do not call ZVCF" in text


@pytest.mark.parametrize("torque", [[0.0, 0.0], [0.0, 3.0]])
def test_active_constraint_need_not_change_every_control_increment(torque: list[float]) -> None:
    """An active holonomic constraint preserves constraint-tangent inputs."""
    mass = np.diag([2.0, 3.0])
    jacobian = np.array([[1.0, 0.0]])
    free = np.linalg.solve(mass, torque)
    weighted = np.linalg.solve(mass, jacobian.T)
    constrained = free - weighted @ np.linalg.solve(jacobian @ weighted, jacobian @ free)
    np.testing.assert_allclose(constrained, free)
    text = " ".join(PROTOCOL.read_text(encoding="utf-8").split())
    assert "does not force a difference for every input" in text


def test_protocol_keeps_unconstrained_control_and_full_baselines_distinct() -> None:
    """Passive forces and legacy forward baselines must not be erased in prose."""
    text = " ".join(PROTOCOL.read_text(encoding="utf-8").split())
    assert "passive forces absent from `h`" in text
    assert "only when its drift equals `-M^-1 h`" in text
    assert "not necessarily gravity-only" in text
