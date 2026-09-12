"""Keep review evidence aligned with the public manifest's source precedence."""

from pathlib import Path

import pytest

from scripts.claim_audit_evidence import (
    ReviewEvidenceError,
    evidence_digests,
    validate_review_evidence,
)


def review_record(root: Path, source: str) -> dict[str, object]:
    """Bind a minimal route review to the actual fixture bytes."""
    return {
        "route": "/critiques/example.html",
        "review": {
            "source_path": source,
            "evidence_paths": [source],
            "evidence_sha256": evidence_digests(root, [source]),
        },
    }


def test_markdown_review_binds_existing_published_source(tmp_path: Path) -> None:
    (tmp_path / "critiques").mkdir()
    source = "critiques/example.md"
    (tmp_path / source).write_text("# Critique\n", encoding="utf-8")
    validate_review_evidence(review_record(tmp_path, source), tmp_path)


def test_quarto_source_takes_precedence_over_markdown(tmp_path: Path) -> None:
    (tmp_path / "critiques").mkdir()
    for source in ["critiques/example.md", "critiques/example.qmd"]:
        (tmp_path / source).write_text("# Critique\n", encoding="utf-8")
    with pytest.raises(ReviewEvidenceError, match="does not match its public route"):
        validate_review_evidence(review_record(tmp_path, "critiques/example.md"), tmp_path)
    validate_review_evidence(review_record(tmp_path, "critiques/example.qmd"), tmp_path)


def test_markdown_source_cannot_bind_a_different_route(tmp_path: Path) -> None:
    (tmp_path / "critiques").mkdir()
    source = "critiques/unrelated.md"
    (tmp_path / source).write_text("# Another Critique\n", encoding="utf-8")
    with pytest.raises(ReviewEvidenceError, match="does not match its public route"):
        validate_review_evidence(review_record(tmp_path, source), tmp_path)
