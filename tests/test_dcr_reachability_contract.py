"""Executable and publication contracts for the DCR reachability correction."""

from pathlib import Path

import pytest

from src.affine_control.reachability import constant_additive_drift_interval

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLE = REPO_ROOT / "articles" / "controllability-drift-ratio.qmd"


def test_constant_additive_drift_translates_without_shrinking_reachable_interval() -> None:
    """Arbitrarily large constant drift changes the center, not control-effect width."""
    zero_drift = constant_additive_drift_interval(0.0, 0.0, 1.0, 1.0)
    large_drift = constant_additive_drift_interval(0.0, 100.0, 1.0, 1.0)

    assert zero_drift == pytest.approx((-1.0, 1.0))
    assert large_drift == pytest.approx((99.0, 101.0))
    assert zero_drift[1] - zero_drift[0] == pytest.approx(large_drift[1] - large_drift[0])


@pytest.mark.parametrize(
    ("initial_state", "drift", "control_bound", "horizon"),
    [
        (0.0, 0.0, -1.0, 1.0),
        (0.0, 0.0, 1.0, -1.0),
        (float("nan"), 0.0, 1.0, 1.0),
        (0.0, float("inf"), 1.0, 1.0),
    ],
)
def test_constant_additive_drift_contract_rejects_invalid_inputs(
    initial_state: float,
    drift: float,
    control_bound: float,
    horizon: float,
) -> None:
    """The analytic counterexample fails closed outside its declared domain."""
    with pytest.raises(ValueError):
        constant_additive_drift_interval(initial_state, drift, control_bound, horizon)


def test_dcr_article_distinguishes_velocity_control_effect_and_reachable_sets() -> None:
    """Scalar DCR must not be promoted into an unsupported reachable-set theorem."""
    article = ARTICLE.read_text(encoding="utf-8")

    required_contracts = (
        "DCR alone does not determine finite-horizon reachability",
        "f(x) + G(x)\\mathcal{U}(x)",
        "G(x)\\mathcal{U}(x)",
        "\\mathcal{R}(T;x_0)",
        "admissible control set",
        "task metric",
        "uncertainty",
        "impact-event outcome",
        "unvalidated hypotheses",
    )
    for contract in required_contracts:
        assert contract in article

    forbidden_claims = (
        "no amount of paddling will steer you",
        "locked into the path",
        "perfect setup",
        "Elite golfers don't try to steer",
        "When drift dominates, it collapses",
        "\\dim(\\mathcal{V}(x))",
        "\\mathcal{O}(1/\\text{DCR}^2)",
        "High DCR implies large $A_f$",
        "Only the ballistic trajectory remains reachable",
    )
    for claim in forbidden_claims:
        assert claim not in article
