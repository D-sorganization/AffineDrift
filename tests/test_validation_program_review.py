"""Independent manufactured checks for validation-program review #4847.

These identities test the chapter's examples, not any physical device or the
private campaign implementation. The provenance check uses inspected metadata.
"""

import math
import re
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pytest

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/Launch_Monitor_Technology_Review/sections/11-validation-program.tex"
)
QUALIFICATION_SHA256 = "679856edb290111a0106c0cbcbd2b673f581fd6b0026409c4d643565b330709a"


def test_qualification_digest_matches_inspected_pinned_manifest() -> None:
    """Catch the published dropped character without requiring private rows."""
    source = CHAPTER.read_text(encoding="utf-8").replace(r"\allowbreak{}", "")
    source = source.replace(r"\\", " ")
    match = re.search(r"qualification:\s*([a-f0-9]+)", source)
    assert match is not None
    assert match[1] == QUALIFICATION_SHA256


def test_normal_approximation_distinguishes_pairs_from_attempts() -> None:
    """Recompute one-endpoint planning, not multiplicity-adjusted power."""
    normal = NormalDist()
    approximation = ((normal.inv_cdf(0.975) + normal.inv_cdf(0.8)) * 3.0) ** 2
    assert approximation == pytest.approx(70.6399176)
    complete_pairs = math.ceil(approximation)
    attempts = math.ceil(complete_pairs / 0.85)
    assert complete_pairs == 71
    assert attempts == 84
    # Inflating expected yield is not a guarantee of meeting either quota.
    assert attempts * 0.85 < 84


def test_shared_bias_can_hide_absolute_error() -> None:
    """Perfect same-shot agreement does not imply accuracy."""
    truth = np.array([90.0, 130.0, 190.0, 230.0])
    device = truth + 5.0
    reference = truth + 5.0
    np.testing.assert_array_equal(device - reference, np.zeros(4))
    assert np.sqrt(np.mean((device - truth) ** 2)) == 5.0


@pytest.mark.parametrize("correlation", [-0.7, 0.0, 0.7])
def test_paired_error_variance_retains_reference_covariance(correlation: float) -> None:
    """Independent linear covariance propagation checks the subtraction sign."""
    covariance = np.array([[9.0, correlation * 6.0], [correlation * 6.0, 4.0]])
    difference = np.array([1.0, -1.0])
    propagated = difference @ covariance @ difference
    assert propagated == pytest.approx(9.0 + 4.0 - 2.0 * correlation * 6.0)


@pytest.mark.parametrize(
    "blocks,replicates,block_variance", [(3, 4, 2.0), (5, 1, 2.0), (3, 4, 0.0), (2, 10, 9.0)]
)
def test_block_mean_variance_from_full_covariance(
    blocks: int, replicates: int, block_variance: float
) -> None:
    """Verify averaging all covariance entries, including within-block terms."""
    count, residual_variance = blocks * replicates, 4.0
    covariance = block_variance * np.kron(np.eye(blocks), np.ones((replicates, replicates)))
    covariance += residual_variance * np.eye(count)
    weights = np.full(count, 1.0 / count)
    actual = weights @ covariance @ weights
    expected = block_variance / blocks + residual_variance / count
    assert actual == pytest.approx(expected)
    naive = (block_variance + residual_variance) / count
    if replicates > 1 and block_variance > 0:
        assert actual > naive
    else:
        assert actual == pytest.approx(naive)


def test_repeatability_requires_a_separate_variance_component() -> None:
    """Several instrument/reference variances yield identical paired variance."""
    decompositions = np.array([[1.0, 8.0], [4.0, 5.0], [8.0, 1.0]])
    np.testing.assert_array_equal(decompositions.sum(axis=1), np.full(3, 9.0))
    within_thresholds = 1.96 * np.sqrt(2.0 * decompositions[:, 0])
    assert len(np.unique(within_thresholds)) == 3
    assert np.all(within_thresholds != 1.96 * 3.0)


def test_mean_uncertainty_and_individual_agreement_have_different_scales() -> None:
    """A fixed distribution does not narrow when more pairs are collected."""
    paired_sd = 3.0
    agreement_half_width = 1.96 * paired_sd
    mean_half_widths = 1.96 * paired_sd / np.sqrt([25.0, 100.0])
    assert mean_half_widths[0] == pytest.approx(2.0 * mean_half_widths[1])
    assert agreement_half_width > max(mean_half_widths)
