"""Scientific-trust contracts for induced-acceleration attribution."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.content_lint

REPO_ROOT = Path(__file__).resolve().parent.parent
QMD_CONTRACT = REPO_ROOT / "_includes" / "induced-acceleration-attribution-contract.qmd"
QMD_SOURCES = (
    REPO_ROOT / "articles" / "The_Physics_of_Golf" / "quarto" / "ch30b_induced_acceleration.qmd",
    REPO_ROOT
    / "articles"
    / "The_Geometry_of_Motion"
    / "quarto"
    / "ch03b_induced_acceleration_biomechanics.qmd",
    REPO_ROOT / "resources" / "research-review-induced-acceleration-analysis.qmd",
)
TEX_SOURCES = (
    REPO_ROOT / "articles" / "The_Physics_of_Golf" / "chapters" / "ch30b_induced_acceleration.tex",
    REPO_ROOT
    / "articles"
    / "The_Geometry_of_Motion"
    / "Volume_I"
    / "chapters"
    / "ch03b_induced_acceleration_biomechanics.tex",
)


def test_coordinate_change_preserves_dynamics_but_changes_reported_components() -> None:
    """Generalized-acceleration components are coordinate representations."""
    mass_q = np.array([[2.0, 0.5], [0.5, 1.0]])
    force_q = np.array([1.0, 2.0])
    q_from_z = np.array([[1.0, 1.0], [0.0, 1.0]])

    acceleration_q = np.linalg.solve(mass_q, force_q)
    mass_z = q_from_z.T @ mass_q @ q_from_z
    force_z = q_from_z.T @ force_q
    acceleration_z = np.linalg.solve(mass_z, force_z)

    assert q_from_z @ acceleration_z == pytest.approx(acceleration_q)
    assert acceleration_z != pytest.approx(acceleration_q)


def test_force_repartition_preserves_total_but_changes_term_attribution() -> None:
    """A compensating residual allocation changes terms without changing motion."""
    inverse_mass = np.linalg.inv(np.array([[2.0, 0.5], [0.5, 1.0]]))
    force_a = np.array([1.0, 0.0])
    force_b = np.array([0.0, 2.0])
    reassigned_residual = np.array([0.25, -0.5])

    original_terms = (inverse_mass @ force_a, inverse_mass @ force_b)
    repartitioned_terms = (
        inverse_mass @ (force_a + reassigned_residual),
        inverse_mass @ (force_b - reassigned_residual),
    )

    assert sum(original_terms) == pytest.approx(sum(repartitioned_terms))
    assert repartitioned_terms[0] != pytest.approx(original_terms[0])
    assert repartitioned_terms[1] != pytest.approx(original_terms[1])


def test_normative_attribution_record_is_complete_and_fail_closed() -> None:
    contract = QMD_CONTRACT.read_text(encoding="utf-8")
    required_fields = (
        "Normative Attribution Record",
        "model and revision",
        "engine, solver, and revision",
        "generalized coordinates",
        "reference frame",
        "mass matrix",
        "constraint handling",
        "contact model",
        "force partition",
        "residual treatment",
        "numerical tolerance",
        "identifiability contract",
        "unsupported or unqualified",
        "anatomical source",
        "neural intent",
        "necessity",
        "sufficiency",
        "intervention effect",
    )

    normalized_contract = re.sub(r"\s+", " ", contract).lower()
    for field in required_fields:
        assert field.lower() in normalized_contract


def test_quarto_and_latex_sources_publish_the_same_attribution_boundary() -> None:
    for path in QMD_SOURCES:
        source = path.read_text(encoding="utf-8")
        assert "induced-acceleration-attribution-contract.qmd" in source

    for path in TEX_SOURCES:
        source = path.read_text(encoding="utf-8")
        assert "Normative Attribution Record" in source
        assert "engine, solver, and revision" in source
        assert "unsupported or unqualified" in source
        assert "anatomical source" in source
        assert "intervention effect" in source


def test_unique_cause_language_requires_an_identifiability_qualifier() -> None:
    unique_cause_pattern = re.compile(
        r"\b(?:caused by|cause of|causal contribution|causal relationship|"
        r"primary contributor|primarily responsible)\b",
        re.IGNORECASE,
    )
    qualifier_pattern = re.compile(
        r"\b(?:model-bounded|model-reported|not (?:a )?unique cause|"
        r"does not identify|identifiability contract)\b",
        re.IGNORECASE,
    )

    for path in (*QMD_SOURCES, *TEX_SOURCES):
        paragraphs = re.split(r"\n\s*\n", path.read_text(encoding="utf-8"))
        for paragraph in paragraphs:
            if unique_cause_pattern.search(paragraph):
                assert qualifier_pattern.search(paragraph), (
                    f"{path.name} has unique-cause language without an "
                    f"identifiability qualifier: {paragraph[:180]}"
                )


@pytest.mark.parametrize("path", (*QMD_SOURCES, *TEX_SOURCES), ids=lambda path: path.name)
def test_sources_remove_unqualified_equivalence_effort_and_parity_claims(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    forbidden_claims = (
        "provides the missing causal information",
        "Only induced acceleration and power analysis",
        "the answers are mathematically identical",
        "system is effectively on autopilot",
        "Voluntary effort",
        "Physics takes over late",
        "proper sequencing and posture optimize",
        "Both frameworks are saying the same thing",
        "the control term equals the muscle-induced acceleration",
        "equivalent to saying that the drift field dominates",
    )

    for claim in forbidden_claims:
        assert claim.lower() not in source.lower(), f"{path.name} retains overclaim: {claim}"
