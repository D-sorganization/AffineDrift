"""Regression checks for Rodrigues derivation in Volume 0 Chapter 6."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CH06_RODRIGUES = (
    REPO_ROOT
    / "articles"
    / "The_Geometry_of_Motion"
    / "Volume_0"
    / "chapters"
    / "ch06_exponential_coordinates.tex"
)


def test_rodrigues_power_pattern_captures_alternating_signs() -> None:
    """Odd powers of the skew matrix in the derivation should alternate sign."""
    text = CH06_RODRIGUES.read_text(encoding="utf-8")
    odd_sign_pattern = re.compile(
        r"\[\\hat\{\\boldsymbol\{\\omega\}\}\]\^\{2k\+1\}\s*=\s*\(-1\)\^k\s*"
        r"\[\\hat\{\\boldsymbol\{\\omega\}\}\]"
    )
    assert odd_sign_pattern.search(text), (
        "Expected derivation to state [ω]^(2k+1) = (-1)^k [ω]"
    )
    bad_pattern = re.compile(
        r"\[\\hat\{\\boldsymbol\{\\omega\}\}\]\^\{2k\+1\}\s*=\s*"
        r"\[\\hat\{\\boldsymbol\{\\omega\}\}\]"
    )
    assert not bad_pattern.search(text), (
        "Found non-alternating odd-power pattern for [\\hat{\\boldsymbol{\\omega}}]^{2k+1}"
    )
