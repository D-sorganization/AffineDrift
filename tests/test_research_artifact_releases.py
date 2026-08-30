"""Comprehensive test suite for governed research artifact releases (Issue #4042)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from src.affine_control.research_releases.generator import (
    build_authoritative_releases,
    generate_research_releases,
)
from src.affine_control.research_releases.validator import (
    ReleaseIntegrityError,
    compute_file_sha256,
    validate_release_package,
)
from src.affine_control.research_releases.vocabulary import (
    RELEASE_AUTHORITY_BOUNDARY,
    ExecutionReport,
    IndependentReviewRecord,
    ReleaseArtifact,
    ReleaseLevel,
    ResearchReleasePackage,
    UncertaintyBreakdown,
)


def test_release_artifact_invariants() -> None:
    """Verify ReleaseArtifact adheres to DbC preconditions."""
    art = ReleaseArtifact(
        path="data/trust/example.json",
        sha256="a" * 64,
        byte_size=1024,
        kind="dataset",
        description="Example dataset",
    )
    assert art.byte_size == 1024
    assert art.to_dict()["kind"] == "dataset"

    with pytest.raises(ValueError, match="Invalid SHA-256 digest"):
        ReleaseArtifact(
            path="path.json",
            sha256="short_hash",
            byte_size=10,
            kind="dataset",
            description="Desc",
        )

    with pytest.raises(ValueError, match="byte_size must be non-negative"):
        ReleaseArtifact(
            path="path.json",
            sha256="a" * 64,
            byte_size=-10,
            kind="dataset",
            description="Desc",
        )


def test_independent_review_record_dbc() -> None:
    """Verify IndependentReviewRecord contract invariants."""
    rev = IndependentReviewRecord(
        reviewer_id="reviewer-01",
        review_scope="Mathematical proof check",
        conflict_of_interest_statement="None declared",
        disposition="approved",
        findings=("Proof holds",),
        verification_commit="f" * 40,
    )
    assert rev.disposition == "approved"

    with pytest.raises(ValueError, match="Invalid disposition"):
        IndependentReviewRecord(
            reviewer_id="reviewer-01",
            review_scope="Scope",
            conflict_of_interest_statement="None",
            disposition="invalid_disposition",
            findings=(),
            verification_commit="f" * 40,
        )

    with pytest.raises(ValueError, match="Invalid verification git commit"):
        IndependentReviewRecord(
            reviewer_id="reviewer-01",
            review_scope="Scope",
            conflict_of_interest_statement="None",
            disposition="approved",
            findings=(),
            verification_commit="not_40_hex",
        )


def test_release_validator_detects_digest_mismatch(tmp_path: Path) -> None:
    """Verify validator catches modified or corrupted release artifacts."""
    test_file = tmp_path / "test_artifact.json"
    test_file.write_text('{"status": "valid"}', encoding="utf-8")
    correct_hash = compute_file_sha256(test_file)
    size = test_file.stat().st_size

    pkg = ResearchReleasePackage(
        release_id="rel-test-001",
        release_level=ReleaseLevel.INTERNALLY_REVIEWED.value,
        title="Test Release Package",
        protocol_id="ad-protocol-test-001",
        git_commit="e" * 40,
        repository_url="https://github.com/D-sorganization/AffineDrift",
        environment_pins={"python": "3.12.14"},
        license="MIT",
        artifacts=(
            ReleaseArtifact(
                path="test_artifact.json",
                sha256=correct_hash,
                byte_size=size,
                kind="data",
                description="Test data",
            ),
        ),
        analysis_execution=ExecutionReport(
            command="python -m test",
            exit_code=0,
            runtime_seconds=1.0,
            outputs_produced=("test_artifact.json",),
        ),
        uncertainty_and_limitations=UncertaintyBreakdown(
            measured_quantities=("Measured",),
            modeled_quantities=("Modeled",),
            assumed_quantities=("Assumed",),
            unavailable_quantities=("Unavailable",),
            known_limitations=("Limitations",),
        ),
        independent_review=IndependentReviewRecord(
            reviewer_id="rev-01",
            review_scope="Scope",
            conflict_of_interest_statement="None",
            disposition="approved",
            findings=("Passed",),
            verification_commit="e" * 40,
        ),
        authority_boundary=RELEASE_AUTHORITY_BOUNDARY,
        released_on="2026-08-30",
    )

    # Valid run passes
    errors = validate_release_package(pkg, tmp_path)
    assert errors == []

    # Corrupted file throws ReleaseIntegrityError
    test_file.write_text('{"status": "corrupted"}', encoding="utf-8")
    with pytest.raises(ReleaseIntegrityError, match="digest mismatch"):
        validate_release_package(pkg, tmp_path)


def test_full_release_generation_and_schema_validation() -> None:
    """Verify live release package generation and schema conformance."""
    repo_root = Path(__file__).resolve().parent.parent
    releases = build_authoritative_releases(repo_root)
    assert len(releases) >= 1

    schema_file = repo_root / "schemas/research-artifact-release-v1.schema.json"
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    for rel in releases:
        jsonschema.validate(instance=rel.to_dict(), schema=schema)

    reg_path, part_path = generate_research_releases(check=False, repo_root=repo_root)
    assert reg_path.is_file()
    assert part_path.is_file()

    # Verify check mode passes
    generate_research_releases(check=True, repo_root=repo_root)
