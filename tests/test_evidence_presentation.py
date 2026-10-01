"""Comprehensive TDD test suite for reader-facing evidence presentation vocabulary, projector, and renderer."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import jsonschema
import pytest

from src.affine_control.evidence_presentation import generator as evidence_presentation_generator
from src.affine_control.evidence_presentation.generator import (
    build_evidence_presentation_registry,
    generate_evidence_presentation,
)
from src.affine_control.evidence_presentation.projector import (
    project_claim,
    project_companion_entity,
    project_protocol,
)
from src.affine_control.evidence_presentation.renderer import (
    render_evidence_badge,
    render_evidence_card,
    render_evidence_table,
)
from src.affine_control.evidence_presentation.vocabulary import (
    AUTHORITY_BOUNDARY_STATEMENT,
    EvidencePresentationViewModel,
    EvidenceTier,
)


def test_view_model_invariants_and_dbc() -> None:
    """Verify that view model constructor enforces Design by Contract preconditions."""
    valid_args = {
        "entity_id": "test-entity-001",
        "title": "Test Entity",
        "kind": "claim",
        "tier": EvidenceTier.QUALIFIED_SIMULATION.value,
        "state_label": "Simulation Ready",
        "state_badge_class": "badge-qualified-simulation",
        "establishes": ("Establishes A",),
        "does_not_establish": ("Does not establish B",),
        "limitations": ("Limitation C",),
        "next_gate": "Gate D",
        "source_revision": "2eb6e9a7852c00223594806a127a3c3c78d46db1",
        "evidence_origin": "computational",
        "authority_boundary": AUTHORITY_BOUNDARY_STATEMENT,
        "accessible_label": "Accessible summary",
    }

    vm = EvidencePresentationViewModel(**valid_args)
    assert vm.entity_id == "test-entity-001"
    assert vm.to_dict()["tier"] == "qualified_simulation"

    # Reject empty entity_id
    with pytest.raises(ValueError, match="entity_id must not be empty"):
        EvidencePresentationViewModel(**{**valid_args, "entity_id": ""})

    # Reject empty establishes
    with pytest.raises(ValueError, match="establishes must contain at least one item"):
        EvidencePresentationViewModel(**{**valid_args, "establishes": ()})

    # Reject empty does_not_establish
    with pytest.raises(ValueError, match="does_not_establish must contain at least one item"):
        EvidencePresentationViewModel(**{**valid_args, "does_not_establish": ()})

    # Reject empty limitations
    with pytest.raises(ValueError, match="limitations must contain at least one item"):
        EvidencePresentationViewModel(**{**valid_args, "limitations": ()})


def test_project_claim_analytical() -> None:
    """Verify projection of analytical counterexample claims."""
    claim_dict = {
        "claim_id": "ad-claim-distal-lag-001",
        "title": "Distal Lag Non-Invariance",
        "evidence_class": "analytical_counterexample",
        "critique_status": "adjudicated",
        "accessible_summary": "Distal joint deceleration is not an invariant requirement.",
        "technical_claim": "The induced acceleration equation shows distal acceleration without proximal braking.",
        "limitations": ["Planar three-link model dynamics only"],
        "next_validation_gate": "Peer-reviewed publication",
        "review_commit": "2eb6e9a7852c00223594806a127a3c3c78d46db1",
    }
    vm = project_claim(claim_dict)
    assert vm.tier == EvidenceTier.MATHEMATICAL_IDENTITY.value
    assert "Distal joint deceleration" in vm.establishes[0]
    assert any("universal human execution invariance" in x for x in vm.does_not_establish)
    assert vm.authority_boundary == AUTHORITY_BOUNDARY_STATEMENT


def test_project_protocol_manufactured() -> None:
    """Verify projection of manufactured research protocol."""
    proto_dict = {
        "protocol_id": "ad-protocol-active-impedance-001",
        "title": "Active Impedance Identification",
        "state": "simulation-ready",
        "evidence_origin": "manufactured-synthetic",
        "next_gate": "pilot-ready",
        "companion_issue": 4036,
        "record_revision": "2eb6e9a7852c00223594806a127a3c3c78d46db1",
    }
    vm = project_protocol(proto_dict)
    assert vm.tier == EvidenceTier.MANUFACTURED_SYNTHETIC.value
    assert "Simulation Ready [manufactured-synthetic]" in vm.state_label
    assert vm.source_url == "https://github.com/D-sorganization/AffineDrift/issues/4036"


def test_project_companion_entity() -> None:
    """Verify projection of programming companion entities."""
    vm = project_companion_entity(
        entity_id="engine-differentiable-forward-dynamics",
        title="Differentiable Forward Dynamics Engine",
        kind="engine",
        description="Core physics integrator",
        commit_sha="2eb6e9a7852c00223594806a127a3c3c78d46db1",
        provenance_hash="a" * 64,
    )
    assert vm.tier == EvidenceTier.QUALIFIED_SIMULATION.value
    assert vm.kind == "engine"
    assert vm.source_revision == "2eb6e9a7852c00223594806a127a3c3c78d46db1"


def test_rendering_components() -> None:
    """Verify accessible rendering of badges, cards, and tables."""
    vm = EvidencePresentationViewModel(
        entity_id="test-001",
        title="Test Heading",
        kind="claim",
        tier=EvidenceTier.QUALIFIED_SIMULATION.value,
        state_label="Qualified Simulation",
        state_badge_class="badge-qualified-simulation",
        establishes=("Establishes property X",),
        does_not_establish=("Does not establish property Y",),
        limitations=("Limited to planar test rigs",),
        next_gate="Validation Gate Alpha",
        source_revision="2eb6e9a7852c00223594806a127a3c3c78d46db1",
        evidence_origin="computational",
        authority_boundary=AUTHORITY_BOUNDARY_STATEMENT,
        accessible_label="Evidence state for Test Heading: Qualified Simulation.",
    )

    badge = render_evidence_badge(vm)
    assert 'role="status"' in badge
    assert 'aria-label="Evidence state for Test Heading: Qualified Simulation."' in badge
    assert "badge-qualified-simulation" in badge

    card = render_evidence_card(vm)
    assert ".evidence-state-card" in card
    assert 'role="region"' in card
    assert "This establishes:" in card
    assert "This does not establish:" in card
    assert "Governed limitations:" in card
    assert AUTHORITY_BOUNDARY_STATEMENT in card

    table = render_evidence_table([vm])
    assert "| Entity / Claim | Tier | Reader-Facing State |" in table
    assert "Test Heading" in table


def test_full_registry_generation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    trust_generation_root: Path,
) -> None:
    """Verify live repository generation and schema validation."""
    source_root = Path(__file__).resolve().parent.parent
    registry, vms = build_evidence_presentation_registry(source_root)

    assert len(vms) > 0
    assert registry["schema_version"] == "affinedrift.evidence-presentation/v1"

    schema_file = source_root / "schemas/evidence-presentation-v1.schema.json"
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    jsonschema.validate(instance=registry, schema=schema)

    registry_path = source_root / "data/trust/generated/evidence_presentation_registry.json"
    partial_path = source_root / "_includes/generated/evidence-presentation-summary.qmd"
    reviewed_registry_bytes = registry_path.read_bytes()
    reviewed_partial_bytes = partial_path.read_bytes()
    next_day = date.fromisoformat(registry["generated_on"]) + timedelta(days=1)

    class NextDayDate(date):
        @classmethod
        def today(cls) -> date:
            return next_day

    monkeypatch.setattr(evidence_presentation_generator, "date", NextDayDate)

    assert trust_generation_root.resolve() == tmp_path.resolve()
    assert trust_generation_root.resolve() != source_root.resolve()

    # Test file generation
    reg_path, part_path = generate_evidence_presentation(
        check=False, repo_root=trust_generation_root
    )
    assert reg_path.is_file()
    assert part_path.is_file()
    assert reg_path.resolve().is_relative_to(tmp_path.resolve())
    assert part_path.resolve().is_relative_to(tmp_path.resolve())
    assert json.loads(reg_path.read_text(encoding="utf-8"))["generated_on"] == next_day.isoformat()

    # Test check mode passes
    checked_reg_path, checked_part_path = generate_evidence_presentation(
        check=True, repo_root=trust_generation_root
    )
    assert checked_reg_path == reg_path
    assert checked_part_path == part_path
    assert registry_path.read_bytes() == reviewed_registry_bytes
    assert partial_path.read_bytes() == reviewed_partial_bytes
