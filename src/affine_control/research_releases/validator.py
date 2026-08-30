"""Validation logic for governed research releases and checksum integrity."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from src.affine_control.research_releases.vocabulary import (
    ResearchReleasePackage,
)

logger = logging.getLogger(__name__)


class ReleaseIntegrityError(ValueError):
    """Raised when a research release fails checksum or provenance verification."""


def compute_file_sha256(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_release_package(package: ResearchReleasePackage, repo_root: Path) -> list[str]:
    """Validate release artifact files, checksums, and provenance boundaries."""
    errors: list[str] = []

    for artifact in package.artifacts:
        file_path = repo_root / artifact.path
        if not file_path.is_file():
            errors.append(f"Artifact file missing: {artifact.path}")
            continue

        actual_hash = compute_file_sha256(file_path)
        if actual_hash != artifact.sha256:
            errors.append(
                f"Artifact digest mismatch for {artifact.path}: "
                f"expected {artifact.sha256}, got {actual_hash}"
            )

        actual_size = file_path.stat().st_size
        if actual_size != artifact.byte_size:
            errors.append(
                f"Artifact size mismatch for {artifact.path}: "
                f"expected {artifact.byte_size}, got {actual_size}"
            )

    if not package.independent_review.conflict_of_interest_statement.strip():
        errors.append("Independent review lacks required conflict of interest disclosure")

    if errors:
        msg = f"Release package {package.release_id} failed integrity verification: {errors}"
        logger.error(msg)
        raise ReleaseIntegrityError(msg)

    return errors
