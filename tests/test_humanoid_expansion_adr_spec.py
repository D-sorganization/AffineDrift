"""Guard the proposed humanoid scope and its phase-zero approval boundary."""

from pathlib import Path

import pytest

ADR_DIR = Path(__file__).resolve().parents[1] / "docs/adr"
ADR_NAME = "0003-humanoid-expansion-scope-and-phase-gates.md"
pytestmark = pytest.mark.integration


def test_humanoid_expansion_adr_is_indexed_in_readme() -> None:
    assert f"]({ADR_NAME})" in (ADR_DIR / "README.md").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "requirement",
    [
        "Proposed",
        "cross-engine parity",
        "whole-body dynamics, contact and locomotion",
        "trajectory optimisation and MPC",
        "screw theory and Lie groups",
        "small PRs to `main`",
        "default-off feature flags",
        "research-only branches are never shipped",
        "Dieter's approval is the phase-0 exit gate",
        "AffineDrift is presentation-only",
        "heavy dynamics remain in UpstreamDrift",
        "0001-markerless-mocap-publication-boundary.md",
        "D-sorganization/UpstreamDrift#13789",
        "MJX benchmark work",
    ],
)
def test_humanoid_expansion_scope_contract(requirement: str) -> None:
    assert requirement.casefold() in (ADR_DIR / ADR_NAME).read_text(encoding="utf-8").casefold()
