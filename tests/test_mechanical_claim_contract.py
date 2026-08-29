"""Regression contracts for mechanical-quantity and attribution claims."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT_DIR = Path(__file__).resolve().parent.parent

FORBIDDEN_CLAIMS_BY_SOURCE = {
    "articles/theory-part2.qmd": (
        "85% of the mechanical load",
        "The golfer's muscles are not driving the downswing",
    ),
    "articles/drifter-manifesto.qmd": (
        "85% of the mechanical load",
        "The golfer's muscles are not driving the downswing",
        "deterministic map from observed forces to their mechanical causes",
    ),
    "articles/appendix-applications.qmd": (
        "reveal exactly how much force the golfer is adding with their muscles",
        "player's true effort hidden inside the motion",
        "## Estimating Active Effort",
        "isolation of the golfer's actual contribution",
        "active muscular effort",
        "drift-free input data",
        "supports: - torque estimation",
    ),
    "articles/affine-nature-golf-swing.qmd": (
        "deterministic map from observed forces to their mechanical causes",
        "attributing every newton of force in the swing to its specific causal origin",
        "golfer's immediate intent (Input)",
    ),
}


@pytest.mark.parametrize(
    ("relative_path", "forbidden_claims"),
    FORBIDDEN_CLAIMS_BY_SOURCE.items(),
    ids=FORBIDDEN_CLAIMS_BY_SOURCE,
)
def test_governed_sources_do_not_conflate_torque_with_load_or_muscle_cause(
    relative_path: str,
    forbidden_claims: tuple[str, ...],
) -> None:
    path = ROOT_DIR / relative_path
    source = path.read_text(encoding="utf-8")

    for claim in forbidden_claims:
        assert claim not in source, f"{path.name} retains overclaim: {claim}"


@pytest.mark.parametrize(
    "relative_path",
    ("articles/theory-part2.qmd", "articles/drifter-manifesto.qmd"),
)
def test_torque_example_states_the_power_work_and_identifiability_boundary(
    relative_path: str,
) -> None:
    source = (ROOT_DIR / relative_path).read_text(encoding="utf-8")

    assert r"P = \tau^\mathsf{T}\dot{q}" in source
    assert r"W = \int" in source
    assert "pointwise generalized-torque decomposition" in source
    assert "does not identify individual muscle forces" in source
