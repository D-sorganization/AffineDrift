"""Independent covariance checks for the manufactured repeated-swing example."""

from pathlib import Path

import numpy as np
import pytest

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/proximal_distal_companion/chapters/ch24_measured_golfers.qmd"
)


@pytest.mark.parametrize("repeats,between", [(10, 1.0), (10, 0.0), (1, 1.0)])
def test_population_mean_variance_from_full_covariance(repeats: int, between: float) -> None:
    """Compare the analytic mean variance with the full nested covariance matrix."""
    participants, residual = 15, 1.0
    observations = participants * repeats
    within_person = between * np.ones((repeats, repeats)) + residual * np.eye(repeats)
    covariance = np.kron(np.eye(participants), within_person)
    weights = np.full(observations, 1.0 / observations)
    variance = float(weights @ covariance @ weights)
    expected = between / participants + residual / observations
    assert variance == pytest.approx(expected)
    naive = (between + residual) / observations
    if repeats == 10 and between == 1.0:
        assert variance == pytest.approx(11 / 150)
        assert naive == pytest.approx(2 / 150)
        assert variance / naive == pytest.approx(5.5)
        assert (between + residual) / variance == pytest.approx(300 / 11)
    else:
        assert variance == pytest.approx(naive)


def test_systematic_review_attribution() -> None:
    """Keep the 92-study review distinct from the narrative measurement review."""
    paragraphs = CHAPTER.read_text(encoding="utf-8").split("\n\n")
    passages = [paragraph for paragraph in paragraphs if "92" in paragraph]
    assert passages
    assert all("@bourgain2022" in paragraph for paragraph in passages)


def test_wrist_emg_scope_names_the_measured_muscle() -> None:
    """Prevent the ECU study from being generalized to all wrist muscles."""
    assert "extensor carpi ulnaris" in CHAPTER.read_text(encoding="utf-8").lower()
