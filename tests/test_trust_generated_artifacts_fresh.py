"""Committed trust-generator artifacts must match what their generators produce.

Each generator's ``check=True`` mode reads the committed files and raises if they are
stale, so these tests fail whenever an input (claim registry, falsification atlas, ...)
changes without regenerating the outputs. Regenerate with::

    PYTHONPATH=. python scripts/generate_evidence_presentation.py
    PYTHONPATH=. python scripts/generate_reader_comprehension_study.py
    PYTHONPATH=. python scripts/generate_research_releases.py
"""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from src.affine_control.evidence_presentation import generator as evidence_generator
from src.affine_control.reader_validation import generator as reader_generator
from src.affine_control.research_releases.generator import generate_research_releases

REPO_ROOT = Path(__file__).resolve().parent.parent

EVIDENCE_REGISTRY = "data/trust/generated/evidence_presentation_registry.json"
EVIDENCE_PARTIAL = "_includes/generated/evidence-presentation-summary.qmd"
READER_STUDY = "data/trust/generated/reader_validation_study.json"
READER_PARTIAL = "_includes/generated/reader-validation-summary.qmd"


class _OtherDay(date):
    """A ``date`` whose ``today()`` is never the day the artifacts were committed."""

    @classmethod
    def today(cls) -> _OtherDay:
        return cls(2000, 1, 1)


def _copy_into(tmp_root: Path, *relative_paths: str) -> None:
    for relative in relative_paths:
        target = tmp_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative, target)


def test_evidence_presentation_artifacts_are_fresh() -> None:
    evidence_generator.generate_evidence_presentation(check=True, repo_root=REPO_ROOT)


def test_reader_validation_artifacts_are_fresh() -> None:
    reader_generator.generate_reader_validation_study(check=True, repo_root=REPO_ROOT)


def test_research_release_artifacts_are_fresh() -> None:
    generate_research_releases(check=True, repo_root=REPO_ROOT)


def test_evidence_presentation_check_ignores_generated_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(evidence_generator, "date", _OtherDay)
    evidence_generator.generate_evidence_presentation(check=True, repo_root=REPO_ROOT)


def test_reader_validation_check_ignores_generated_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(reader_generator, "date", _OtherDay)
    reader_generator.generate_reader_validation_study(check=True, repo_root=REPO_ROOT)


def test_evidence_presentation_check_still_detects_content_drift(tmp_path: Path) -> None:
    _copy_into(
        tmp_path,
        "data/trust/claim_registry.json",
        "data/research_protocols/public_summary.json",
        "tests/fixtures/companion/manifest_v1_0_0_authoritative.json",
        "schemas/evidence-presentation-v1.schema.json",
        EVIDENCE_REGISTRY,
        EVIDENCE_PARTIAL,
    )
    registry_path = tmp_path / EVIDENCE_REGISTRY
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["entities"][0]["source_revision"] = "0" * 64
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(ValueError, match="stale"):
        evidence_generator.generate_evidence_presentation(check=True, repo_root=tmp_path)


def test_reader_validation_check_still_detects_content_drift(tmp_path: Path) -> None:
    _copy_into(
        tmp_path,
        "schemas/reader-comprehension-study-v1.schema.json",
        READER_STUDY,
        READER_PARTIAL,
    )
    study_path = tmp_path / READER_STUDY
    study = json.loads(study_path.read_text(encoding="utf-8"))
    study["cohorts"] = list(reversed(study["cohorts"]))
    study_path.write_text(json.dumps(study), encoding="utf-8")

    with pytest.raises(ValueError, match="stale"):
        reader_generator.generate_reader_validation_study(check=True, repo_root=tmp_path)
