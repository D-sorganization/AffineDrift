"""Check the shared phase-zero outline review contract before publication work."""

from pathlib import Path

import pytest

OUTLINES = Path(__file__).resolve().parents[1] / "docs/humanoid/outlines"
pytestmark = pytest.mark.integration


@pytest.mark.parametrize("slug", ["cross-engine-parity", "contact-grf-wrenches", "whole-body-mpc"])
def test_outline_has_reviewable_scope_and_gates(slug: str) -> None:
    """Each outline must expose prerequisites, dependencies, rights and review gates."""
    files = list(OUTLINES.glob(f"series-*-{slug}.md"))
    assert len(files) == 1
    text = files[0].read_text()
    for heading in (
        "Learning Goals",
        "Prerequisites",
        "Planned Articles",
        "Engines and Datasets",
        "UpstreamDrift Dependencies",
        "Common Thread",
        "Publication Gate",
    ):
        assert f"## {heading}" in text
    for gate in (
        "rights-licence-ledger.md",
        "not cleared",
        "Karl",
        "Feynman",
        "panel",
        "Fleet-Critic",
        "sign-off",
        "do-not-merge",
    ):
        assert gate in text
    assert "Lie groups" in text and "screw theory" in text
    if slug == "whole-body-mpc":
        assert "AMASS" in text and "ON-HOLD" in text
