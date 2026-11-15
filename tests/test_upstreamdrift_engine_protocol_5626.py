"""Engine-protocol disambiguation for UpstreamDrift counterfactual method names (#5626 G1)."""

from __future__ import annotations

from pathlib import Path

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
