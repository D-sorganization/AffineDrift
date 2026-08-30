"""Tests for the Programming Companion catalog generator (ISSUE-4023).

Verifies deterministic generation of authoritative Quarto markdown pages from
the pinned UpstreamDrift companion manifest under strict TDD, DbC, LoD, and DRY standards.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.affine_control.programming_companion.catalog_generator import (
    CatalogGenerator,
    CatalogGeneratorError,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "companion"
AUTHORITATIVE_MANIFEST = FIXTURES_DIR / "manifest_v1_0_0_authoritative.json"


@pytest.fixture
def manifest_data() -> dict[str, object]:
    return json.loads(AUTHORITATIVE_MANIFEST.read_text(encoding="utf-8"))


@pytest.mark.unit
def test_generate_catalog_creates_all_expected_qmd_files(
    manifest_data: dict[str, object], tmp_path: Path
) -> None:
    """Generator builds index, engines, programs, features, workflows, and provenance pages."""
    generator = CatalogGenerator(manifest_data)
    files = generator.generate_all(tmp_path)

    expected_names = {
        "index.qmd",
        "engines.qmd",
        "programs.qmd",
        "features.qmd",
        "workflows.qmd",
        "provenance.qmd",
    }
    assert {f.relative_path.name for f in files} == expected_names
    for f in files:
        target = tmp_path / f.relative_path
        assert target.exists()
        assert target.stat().st_size > 0
        assert target.read_text(encoding="utf-8") == f.content


@pytest.mark.unit
def test_generate_catalog_is_strictly_deterministic(
    manifest_data: dict[str, object], tmp_path: Path
) -> None:
    """Generator is purely deterministic and idempotent across multiple runs."""
    generator = CatalogGenerator(manifest_data)
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"

    files_a = generator.generate_all(dir_a)
    files_b = generator.generate_all(dir_b)

    assert len(files_a) == len(files_b)
    for fa, fb in zip(files_a, files_b, strict=True):
        assert fa.relative_path == fb.relative_path
        assert fa.content == fb.content


@pytest.mark.unit
def test_generate_catalog_check_mode_detects_drift(
    manifest_data: dict[str, object], tmp_path: Path
) -> None:
    """Check mode returns clean status when in sync and detects drift/stale files."""
    generator = CatalogGenerator(manifest_data)
    generator.generate_all(tmp_path)

    is_clean, drift = generator.check(tmp_path)
    assert is_clean is True
    assert drift == []

    # Mutate one file to introduce drift
    mutated_file = tmp_path / "engines.qmd"
    mutated_file.write_text("MUTATED CONTENT", encoding="utf-8")

    is_clean, drift = generator.check(tmp_path)
    assert is_clean is False
    assert len(drift) == 1
    assert drift[0].path == Path("engines.qmd")
    assert drift[0].reason == "content_mismatch"


@pytest.mark.unit
def test_generated_pages_author_single_visible_h1(
    manifest_data: dict[str, object], tmp_path: Path
) -> None:
    """Every generated QMD page contains exactly one title/H1 and valid frontmatter."""
    generator = CatalogGenerator(manifest_data)
    files = generator.generate_all(tmp_path)

    for f in files:
        content = f.content
        lines = content.splitlines()
        # Must have valid YAML frontmatter
        assert lines[0] == "---"
        second_dash = lines.index("---", 1)
        assert second_dash > 1
        frontmatter = "\n".join(lines[1:second_dash])
        assert "title:" in frontmatter
        assert "description:" in frontmatter

        # Must not contain unrendered raw markdown body H1 outside title frontmatter
        body = "\n".join(lines[second_dash + 1 :])
        assert "\n# " not in body, f"Page {f.relative_path} has extra markdown H1 in body"


@pytest.mark.unit
def test_semantic_separation_of_support_tiers_and_validation(
    manifest_data: dict[str, object], tmp_path: Path
) -> None:
    """Generated pages clearly separate software support tiers from scientific qualification."""
    generator = CatalogGenerator(manifest_data)
    files = generator.generate_all(tmp_path)
    file_map = {f.relative_path.name: f.content for f in files}

    # Engines page mentions all 5 engines and their exact tiers
    engines_qmd = file_map["engines.qmd"]
    assert "MuJoCo" in engines_qmd
    assert "Drake" in engines_qmd
    assert "Pinocchio" in engines_qmd
    assert "OpenSim" in engines_qmd
    assert "MyoSuite" in engines_qmd
    assert "Supported" in engines_qmd
    assert "Extended" in engines_qmd
    assert "Experimental" in engines_qmd

    # Authority boundary callouts must explicitly distinguish software from human validation
    for qmd in file_map.values():
        assert (
            "This establishes" in qmd
            or "Authority Boundary" in qmd
            or "This does not establish" in qmd
        )


@pytest.mark.unit
def test_generator_fails_closed_on_invalid_manifest() -> None:
    """Generator refuses malformed manifests or missing required summary sections."""
    with pytest.raises(CatalogGeneratorError, match="invalid manifest structure"):
        CatalogGenerator({"manifest_id": "incomplete"})
