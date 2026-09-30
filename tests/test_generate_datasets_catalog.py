"""Tests for the datasets catalog generator (WEB-07.7, #4549).

Covers the acceptance criteria from issue #4549: no truncated text, no
third-party thumbnail host, every entry carries licence and access fields,
and AffineDrift's own artefacts are listed with real SHA-256 checksums.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.datasets_catalog import (
    AFFINEDRIFT_REQUIRED_FIELDS,
    THIRD_PARTY_REQUIRED_FIELDS,
    DatasetCatalogError,
    compute_directory_checksums,
    load_catalog,
    render_updated_qmd,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_CATALOG_PATH = REPO_ROOT / "data" / "datasets.yml"
REAL_QMD_PATH = REPO_ROOT / "resources" / "resources-datasets.qmd"


def _write_catalog(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "datasets.yml"
    path.write_text(content, encoding="utf-8")
    return path


@pytest.mark.unit
def test_load_catalog_rejects_third_party_entry_missing_required_field(tmp_path: Path) -> None:
    """A third-party entry missing a required field fails loudly (DbC boundary check)."""
    path = _write_catalog(
        tmp_path,
        "third_party:\n  - id: golfdb\n    name: GolfDB\n",
    )
    with pytest.raises(DatasetCatalogError) as exc_info:
        load_catalog(path)
    assert "golfdb" in str(exc_info.value)
    for field in THIRD_PARTY_REQUIRED_FIELDS:
        if field not in {"id", "name"}:
            assert field in str(exc_info.value)


@pytest.mark.unit
def test_load_catalog_rejects_affinedrift_entry_missing_required_field(tmp_path: Path) -> None:
    """An AffineDrift artefact entry missing a required field fails loudly."""
    path = _write_catalog(
        tmp_path,
        "affinedrift:\n  - id: ztcf-fixtures\n    name: ZTCF\n",
    )
    with pytest.raises(DatasetCatalogError) as exc_info:
        load_catalog(path)
    assert "ztcf-fixtures" in str(exc_info.value)
    for field in AFFINEDRIFT_REQUIRED_FIELDS:
        if field not in {"id", "name"}:
            assert field in str(exc_info.value)


@pytest.mark.unit
def test_load_catalog_parses_real_data_file() -> None:
    """The committed data/datasets.yml parses into non-empty third-party and affinedrift lists."""
    catalog = load_catalog(REAL_CATALOG_PATH)
    assert len(catalog.third_party) == 4
    assert len(catalog.affinedrift) == 3


@pytest.mark.unit
def test_compute_directory_checksums_matches_real_sha256(tmp_path: Path) -> None:
    """Checksums are real SHA-256 digests of the actual file bytes, not fabricated."""
    (tmp_path / "a.json").write_bytes(b'{"x": 1}')
    (tmp_path / "b.json").write_bytes(b'{"y": 2}')

    checksums = compute_directory_checksums(tmp_path, ".")

    assert [c.filename for c in checksums] == ["a.json", "b.json"]
    import hashlib

    assert checksums[0].sha256 == hashlib.sha256(b'{"x": 1}').hexdigest()
    assert checksums[1].sha256 == hashlib.sha256(b'{"y": 2}').hexdigest()


@pytest.mark.unit
def test_compute_directory_checksums_raises_for_missing_directory(tmp_path: Path) -> None:
    """A dataset entry pointing at a nonexistent directory fails loudly, not silently."""
    with pytest.raises(DatasetCatalogError, match="not found"):
        compute_directory_checksums(tmp_path, "does-not-exist")


@pytest.mark.unit
def test_compute_directory_checksums_raises_for_empty_directory(tmp_path: Path) -> None:
    """A directory with no JSON files fails loudly rather than rendering an empty table."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(DatasetCatalogError, match="no JSON files"):
        compute_directory_checksums(tmp_path, "empty")


@pytest.mark.unit
def test_render_updated_qmd_preserves_content_outside_markers(tmp_path: Path) -> None:
    """Regeneration only touches the marked block; sidebar/script content is untouched."""
    catalog_path = _write_catalog(
        tmp_path,
        "\n".join(
            [
                "third_party:",
                "  - id: golfdb",
                "    name: GolfDB",
                "    description: A golf video database.",
                "    paper_url: https://arxiv.org/abs/1903.06528",
                "    licence: CC BY-NC 4.0",
                "    size: 1400 videos",
                "    modality: Video",
                "    access: Public",
                "    citation: McNally et al.",
                "affinedrift: []",
            ]
        ),
    )
    qmd_path = tmp_path / "page.qmd"
    qmd_path.write_text(
        "before\n"
        "<!-- GENERATED:BEGIN datasets-catalog -->\n"
        "stale content\n"
        "<!-- GENERATED:END datasets-catalog -->\n"
        "after",
        encoding="utf-8",
    )
    catalog = load_catalog(catalog_path)

    updated = render_updated_qmd(qmd_path, catalog, tmp_path)

    assert updated.startswith("before\n<!-- GENERATED:BEGIN datasets-catalog -->")
    assert updated.endswith("<!-- GENERATED:END datasets-catalog -->\nafter")
    assert "stale content" not in updated
    assert "GolfDB" in updated


@pytest.mark.unit
def test_render_updated_qmd_raises_without_markers(tmp_path: Path) -> None:
    """A page missing the generated-block markers fails loudly instead of silently no-op-ing."""
    catalog_path = _write_catalog(tmp_path, "third_party: []\naffinedrift: []\n")
    qmd_path = tmp_path / "page.qmd"
    qmd_path.write_text("no markers here", encoding="utf-8")
    catalog = load_catalog(catalog_path)

    with pytest.raises(DatasetCatalogError, match="no .* block"):
        render_updated_qmd(qmd_path, catalog, tmp_path)


@pytest.mark.unit
def test_render_third_party_entries_have_no_truncated_description() -> None:
    """Every third-party description ends with sentence punctuation, not a mid-word cutoff."""
    catalog = load_catalog(REAL_CATALOG_PATH)
    for entry in catalog.third_party:
        assert entry.description.strip()[-1] in ".!?"
        assert len(entry.description) > 100


@pytest.mark.unit
def test_every_third_party_entry_has_licence_and_access() -> None:
    """Acceptance criterion: every third-party entry carries licence and access fields."""
    catalog = load_catalog(REAL_CATALOG_PATH)
    for entry in catalog.third_party:
        assert entry.licence.strip()
        assert entry.access.strip()


@pytest.mark.unit
def test_every_affinedrift_entry_has_licence_and_access() -> None:
    """Acceptance criterion: every AffineDrift artefact entry carries licence and access fields."""
    catalog = load_catalog(REAL_CATALOG_PATH)
    for entry in catalog.affinedrift:
        assert entry.licence.strip()
        assert entry.access.strip()


@pytest.mark.integration
def test_generated_page_has_no_third_party_thumbnail_host() -> None:
    """Acceptance criterion: no third-party thumbnail host appears on the rendered page."""
    content = REAL_QMD_PATH.read_text(encoding="utf-8")
    assert "mini.s-shot.ru" not in content


@pytest.mark.integration
def test_generated_page_lists_affinedrift_artifacts_with_checksums() -> None:
    """Acceptance criterion: the site's own artefacts are listed with SHA-256 checksums."""
    content = REAL_QMD_PATH.read_text(encoding="utf-8")
    assert "AffineDrift Data Artefacts" in content
    assert "resource-checksums" in content
    assert "SHA-256 checksums" in content


@pytest.mark.integration
def test_real_page_is_up_to_date_with_real_catalog() -> None:
    """The committed page matches what the generator produces from data/datasets.yml (--check)."""
    catalog = load_catalog(REAL_CATALOG_PATH)
    updated = render_updated_qmd(REAL_QMD_PATH, catalog, REPO_ROOT)
    current = REAL_QMD_PATH.read_text(encoding="utf-8")
    assert updated == current
