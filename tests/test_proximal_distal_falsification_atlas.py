"""Contracts for the governed proximal-distal falsification atlas (#4087)."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from src.affine_control.falsification_atlas import (
    AtlasPaths,
    AtlasValidationError,
    load_atlas,
    render_atlas,
)

ROOT = Path(__file__).parents[1]
MAPPING = ROOT / "data/trust/proximal_distal_falsification_atlas.json"
SCHEMA = ROOT / "schemas/proximal-distal-falsification-atlas-v1.schema.json"
CLAIMS = ROOT / "articles/proximal_distal_energy_transfer/data/claim_adjudication_summary.json"
CRITIQUES = ROOT / "data/trust/claim_critique_ledger.json"
SOURCE_MANIFEST = ROOT / "articles/proximal_distal_energy_transfer/source_manifest.json"
READINESS = ROOT / "data/research_protocols/library.json"
OUTPUT = ROOT / "articles/_generated/proximal-distal-falsification-atlas.qmd"
ARTICLE = ROOT / "articles/proximal-distal-falsification-atlas.qmd"
MONOGRAPH = ROOT / "articles/proximal_distal_energy_transfer/index.qmd"
QUARTO = ROOT / "_quarto.yml"
ATLAS_STYLES = ROOT / "css/components/falsification-atlas.css"

REQUIRED_THEMES = {
    "endpoint-equifinality",
    "timing-without-benefit",
    "coordinate-dependent-attribution",
    "bilateral-hand-ambiguity",
    "prescribed-base-artifacts",
    "shaft-contact-confounding",
}


def _paths(mapping: Path = MAPPING, output: Path = OUTPUT) -> AtlasPaths:
    """Return the canonical atlas path contract with optional test overrides."""
    return AtlasPaths(
        root=ROOT,
        mapping=mapping,
        schema=SCHEMA,
        claims=CLAIMS,
        critiques=CRITIQUES,
        source_manifest=SOURCE_MANIFEST,
        readiness=READINESS,
        output=output,
    )


def _write_mapping(tmp_path: Path, mutate: object) -> Path:
    """Write a deliberately mutated mapping for a failing-closed test."""
    payload = json.loads(MAPPING.read_text(encoding="utf-8"))
    assert callable(mutate)
    mutate(payload)
    target = tmp_path / "atlas.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def test_schema_is_valid_draft_2020_12_and_mapping_conforms() -> None:
    """The editorial mapping must have one strict machine-readable contract."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(json.loads(MAPPING.read_text(encoding="utf-8")))


def test_atlas_covers_each_required_falsification_theme_exactly_once() -> None:
    """The six issue-mandated alternative mechanisms must not disappear."""
    atlas = load_atlas(_paths())
    themes = [record.theme for record in atlas.records]
    assert set(themes) == REQUIRED_THEMES
    assert len(themes) == len(set(themes)) == 6


def test_claim_and_critique_states_are_derived_from_authorities() -> None:
    """Editorial mappings cannot rewrite governed claim or critique states."""
    atlas = load_atlas(_paths())
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))["claims"]
    critiques = json.loads(CRITIQUES.read_text(encoding="utf-8"))["critiques"]
    claim_by_id = {item["claim_id"]: item for item in claims}
    critique_by_id = {item["critique_id"]: item for item in critiques}
    for record in atlas.records:
        claim = claim_by_id[record.claim_id]
        critique = critique_by_id[record.critique_id]
        assert record.claim == claim["statement"]
        assert record.evidence_state == claim["adjudication_outcome"]
        assert record.uncertainty == claim["uncertainty_boundary"]
        assert record.falsifier == claim["falsifier"]
        assert record.critique_state == critique["disposition"]


def test_readiness_and_release_states_are_derived_from_authority() -> None:
    """Editorial mappings cannot promote research readiness or publication."""
    atlas = load_atlas(_paths())
    protocols = json.loads(READINESS.read_text(encoding="utf-8"))["protocols"]
    protocol_by_id = {item["protocol_id"]: item for item in protocols}
    for record in atlas.records:
        protocol = protocol_by_id[record.readiness_protocol_id]
        release = protocol["links"]["validation_release"]
        assert record.readiness_state == protocol["state"]
        assert record.readiness_evidence_origin == protocol["evidence_origin"]
        assert record.validation_release_state == release["status"]
        assert record.validation_release_next_gate == release["next_gate"]


def test_mapping_rejects_manually_amplified_claim_fields(tmp_path: Path) -> None:
    """The schema must forbid hand-authored claim summaries or statuses."""
    path = _write_mapping(
        tmp_path,
        lambda payload: payload["records"][0].update({"evidence_state": "validated"}),
    )
    with pytest.raises(AtlasValidationError, match="schema"):
        load_atlas(replace(_paths(), mapping=path))


def test_atlas_rejects_stale_claim_authority_digest(tmp_path: Path) -> None:
    """A changed monograph claim projection requires explicit reconciliation."""
    path = _write_mapping(
        tmp_path,
        lambda payload: payload["authorities"]["claims"].update({"sha256": "0" * 64}),
    )
    with pytest.raises(AtlasValidationError, match="claims SHA-256"):
        load_atlas(replace(_paths(), mapping=path))


def test_atlas_rejects_misdeclared_authority_path(tmp_path: Path) -> None:
    """A correct digest cannot excuse misleading provenance metadata."""
    path = _write_mapping(
        tmp_path,
        lambda payload: payload["authorities"]["claims"].update(
            {"path": "data/trust/claim_registry.json"}
        ),
    )
    with pytest.raises(AtlasValidationError, match="claims authority path"):
        load_atlas(replace(_paths(), mapping=path))


def test_atlas_rejects_unknown_claim_or_critique_ids(tmp_path: Path) -> None:
    """Every atlas row must resolve both governed authority identifiers."""
    claim_path = _write_mapping(
        tmp_path,
        lambda payload: payload["records"][0].update({"claim_id": "PD-CLAIM-999"}),
    )
    with pytest.raises(AtlasValidationError, match="unknown claim"):
        load_atlas(replace(_paths(), mapping=claim_path))

    critique_path = _write_mapping(
        tmp_path,
        lambda payload: payload["records"][0].update({"critique_id": "crit-missing"}),
    )
    with pytest.raises(AtlasValidationError, match="unknown critique"):
        load_atlas(replace(_paths(), mapping=critique_path))

    readiness_path = _write_mapping(
        tmp_path,
        lambda payload: payload["records"][0].update(
            {"readiness_protocol_id": "ad-protocol-missing-001"}
        ),
    )
    with pytest.raises(AtlasValidationError, match="unknown readiness protocol"):
        load_atlas(replace(_paths(), mapping=readiness_path))


def test_atlas_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    """Ambiguous duplicate editorial keys must fail before schema validation."""
    target = tmp_path / "duplicate.json"
    target.write_text('{"schema_version":"1.0.0","schema_version":"1.0.0"}', encoding="utf-8")
    with pytest.raises(AtlasValidationError, match="duplicate JSON key"):
        load_atlas(replace(_paths(), mapping=target))


def test_atlas_rejects_duplicate_record_ids_and_themes(tmp_path: Path) -> None:
    """A row cannot silently replace a required falsification theme."""
    duplicate_id = _write_mapping(
        tmp_path,
        lambda payload: payload["records"][1].update(
            {"atlas_id": payload["records"][0]["atlas_id"]}
        ),
    )
    with pytest.raises(AtlasValidationError, match="duplicate atlas identifier"):
        load_atlas(replace(_paths(), mapping=duplicate_id))

    duplicate_theme = _write_mapping(
        tmp_path,
        lambda payload: payload["records"][1].update({"theme": payload["records"][0]["theme"]}),
    )
    with pytest.raises(AtlasValidationError, match="duplicate atlas theme"):
        load_atlas(replace(_paths(), mapping=duplicate_theme))


def test_unavailable_provider_workflows_have_explicit_reasons() -> None:
    """Missing Upstream publication must remain visible on every atlas row."""
    atlas = load_atlas(_paths())
    assert atlas.provider_state == "unavailable"
    assert atlas.provider_reason
    assert all(record.workflow_state == "unavailable" for record in atlas.records)
    assert all(record.workflow_reason for record in atlas.records)
    assert all(record.provider_record_url is None for record in atlas.records)


def test_chapter_paths_and_anchors_resolve_in_canonical_sources() -> None:
    """Atlas links must target actual monograph sections, not guessed routes."""
    for record in load_atlas(_paths()).records:
        chapter = ROOT / record.chapter_path
        assert chapter.is_file()
        assert f"{{#{record.chapter_anchor}}}" in chapter.read_text(encoding="utf-8")


def test_render_is_deterministic_static_and_complete() -> None:
    """The accessible print/no-JS representation must contain every record."""
    atlas = load_atlas(_paths())
    first = render_atlas(atlas)
    second = render_atlas(atlas)
    assert first == second
    assert '<section class="falsification-atlas-record"' in first
    assert "This establishes" in first
    assert "This does not establish" in first
    assert "Workflow unavailable" in first
    assert "Research readiness" in first
    assert "Validation release" in first
    assert "research-protocol-readiness.html#ad-protocol-" in first
    assert "<script" not in first
    for record in atlas.records:
        assert record.atlas_id in first
        assert record.claim_id in first
        assert record.critique_id in first


def test_committed_projection_matches_generator() -> None:
    """Generated public atlas content must never drift from its authorities."""
    expected = render_atlas(load_atlas(_paths()))
    assert OUTPUT.read_text(encoding="utf-8") == expected


def test_public_article_links_exact_monograph_authority() -> None:
    """Readers must move from synthesis to exact immutable monograph authority."""
    article = ARTICLE.read_text(encoding="utf-8")
    assert "_generated/proximal-distal-falsification-atlas.qmd" in article
    assert "proximal_distal_energy_transfer/index.html" in article


def test_public_article_is_registered_for_rendering() -> None:
    """The atlas cannot be silently omitted from the deployed site."""
    quarto = QUARTO.read_text(encoding="utf-8")
    assert "articles/**/*.qmd" in quarto
    assert "articles/proximal-distal-falsification-atlas.html" in quarto
    assert "schemas/proximal-distal-falsification-atlas-v1.schema.json" in quarto


def test_atlas_has_a_dedicated_responsive_print_safe_component() -> None:
    """The long-form evidence records need a deliberate, reusable reading surface."""
    article = ARTICLE.read_text(encoding="utf-8")
    component = ATLAS_STYLES.read_text(encoding="utf-8")
    assert "../css/components/falsification-atlas.css" in article
    assert ".falsification-atlas-record" in component
    assert ".falsification-atlas-record dt" in component
    assert "overflow-wrap: anywhere" in component
    assert "@media print" in component
