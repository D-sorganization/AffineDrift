"""Scientific-trust contracts for the canonical control-affine articles."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_INCLUDE = ROOT / "_includes" / "control-affine-attribution-boundary.qmd"
CANONICAL_SOURCES = (
    ROOT / "articles" / "theory-part1.qmd",
    ROOT / "articles" / "theory-part2.qmd",
    ROOT / "articles" / "affine-nature-golf-swing.qmd",
    ROOT / "articles" / "drifter-manifesto.qmd",
)
PART1_SOURCES = (
    ROOT / "articles" / "theory-part1.qmd",
    ROOT / "articles" / "affine-nature-golf-swing.qmd",
    ROOT / "articles" / "drifter-manifesto.qmd",
)

FALSE_FORMULATIONS = (
    "control-non-affine due to the multiplicative state dependency",
    "Hill model introduces multiplicative state-dependency",
    "these forces enter nonlinearly and do not preserve the affine structure",
    "they are **mechanically orthogonal**",
    "This orthogonality is structural",
    "By isolating the input $u$ in a separate linear term, we have created a causal map",
    "a deterministic map from observed forces to their mechanical causes",
    "attribute specific features of the swing trajectory to either the golfer's intent",
    "what would the club do if the golfer's muscles went silent",
    "what additional motion does muscular effort create",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_canonical_sources_reject_false_affinity_orthogonality_and_causality() -> None:
    """Known P0 formulations must not survive in any maintained edition."""
    corpus = "\n".join(_read(path) for path in CANONICAL_SOURCES)

    for formulation in FALSE_FORMULATIONS:
        assert formulation not in corpus


def test_part1_editions_define_affinity_at_fixed_state_and_declared_input() -> None:
    """State-dependent gain is compatible with affinity in the declared input."""
    required = (
        "linear in the declared input at fixed state",
        "state-dependent input map $G(x)$",
        "do not by themselves break control-affinity",
    )

    for source in PART1_SOURCES:
        text = _read(source)
        for phrase in required:
            assert phrase in text, f"{source.name} is missing: {phrase}"


def test_all_canonical_editions_include_one_attribution_boundary() -> None:
    """Every maintained edition must render the shared authority boundary."""
    directive = "{{< include ../_includes/control-affine-attribution-boundary.qmd >}}"

    assert BOUNDARY_INCLUDE.is_file()
    for source in CANONICAL_SOURCES:
        assert _read(source).count(directive) == 1, source.name


def test_attribution_boundary_declares_every_condition_and_identifiability_limit() -> None:
    """The shared boundary must state the full model-conditioned contract."""
    boundary = _read(BOUNDARY_INCLUDE)
    required = (
        "model",
        "coordinates",
        "declared input",
        "parameters",
        "intervention",
        "identifiability",
        "does not identify neural intent",
        "individual-muscle forces",
        "unique real-world cause",
        "additivity does not imply orthogonality",
    )

    for phrase in required:
        assert phrase in boundary


def test_accessible_summaries_describe_a_declared_channel_not_muscle_silence() -> None:
    """Lay explanations must remain no stronger than the technical contract."""
    affine = _read(ROOT / "articles" / "affine-nature-golf-swing.qmd")
    manifesto = _read(ROOT / "articles" / "drifter-manifesto.qmd")

    assert "declared input channel" in affine[:8_000]
    assert "declared input channel" in manifesto[:12_000]
    assert "turning off a golfer's muscles" not in manifesto
    assert "cut the power to the virtual golfer's muscles" not in manifesto
