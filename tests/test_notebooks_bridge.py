"""Tests for the Tangent-Space Methods notebook bridge feature."""

from __future__ import annotations

import json
from pathlib import Path

from src.tools.notebooks_bridge import (
    ChapterRef,
    discover_book_chapters,
    extract_chapters_from_text,
    sync_notebook_bridge,
    validate_notebook_bridge,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "notebooks" / "geometry_of_motion" / "manifest.json"


def test_extract_chapters_from_text_parses_anchor_contract() -> None:
    """Chapter parser should extract ids/titles/anchors from headings."""
    sample = "## Chapter 2: Variational Dynamics {#book1-ch2}\n"
    chapters = extract_chapters_from_text(
        sample, source_file=Path("books/tangent-space-methods.qmd")
    )
    assert chapters == [
        ChapterRef(
            volume=1,
            chapter=2,
            anchor="book1-ch2",
            title="Variational Dynamics",
            source_file=Path("books/tangent-space-methods.qmd"),
        )
    ]


def test_discover_book_chapters_matches_expected_count() -> None:
    """Volumes I-IV should expose 40 chapter anchors in total."""
    chapters = discover_book_chapters(repo_root=REPO_ROOT)
    assert len(chapters) == 40


def test_sync_notebook_bridge_is_idempotent(tmp_path: Path) -> None:
    """Repeated sync runs should not change manifest output."""
    books_dir = tmp_path / "books"
    books_dir.mkdir()
    (books_dir / "tangent-space-methods.qmd").write_text(
        "## Chapter 1: Foundations {#book1-ch1}\n",
        encoding="utf-8",
    )
    (books_dir / "control-is-motion.qmd").write_text(
        "## Chapter 1: Throwing Away the Target {#book2-ch1}\n",
        encoding="utf-8",
    )
    (books_dir / "biomechanics-biology-to-systems.qmd").write_text(
        "## Chapter 1: Biology vs Engineering {#book3-ch1}\n",
        encoding="utf-8",
    )
    (books_dir / "human-motor-control.qmd").write_text(
        "## Chapter 1: Degrees-of-Freedom Problem {#book4-ch1}\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "notebooks" / "geometry_of_motion"
    manifest_path = output_dir / "manifest.json"
    sync_notebook_bridge(repo_root=tmp_path, output_dir=output_dir, manifest_path=manifest_path)
    first = json.loads(manifest_path.read_text(encoding="utf-8"))
    sync_notebook_bridge(repo_root=tmp_path, output_dir=output_dir, manifest_path=manifest_path)
    second = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert first == second


def test_sync_notebook_bridge_prunes_unmanaged_notebooks(tmp_path: Path) -> None:
    """Sync should remove stale notebooks not represented in the manifest."""
    books_dir = tmp_path / "books"
    books_dir.mkdir()
    (books_dir / "tangent-space-methods.qmd").write_text(
        "## Chapter 1: Foundations {#book1-ch1}\n",
        encoding="utf-8",
    )
    (books_dir / "control-is-motion.qmd").write_text(
        "## Chapter 1: Throwing Away the Target {#book2-ch1}\n",
        encoding="utf-8",
    )
    (books_dir / "biomechanics-biology-to-systems.qmd").write_text(
        "## Chapter 1: Biology vs Engineering {#book3-ch1}\n",
        encoding="utf-8",
    )
    (books_dir / "human-motor-control.qmd").write_text(
        "## Chapter 1: Degrees-of-Freedom Problem {#book4-ch1}\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "notebooks" / "geometry_of_motion"
    output_dir.mkdir(parents=True)
    stale = output_dir / "obsolete.ipynb"
    stale.write_text("{}", encoding="utf-8")
    manifest_path = output_dir / "manifest.json"

    sync_notebook_bridge(repo_root=tmp_path, output_dir=output_dir, manifest_path=manifest_path)
    assert not stale.exists()


def test_notebook_bridge_manifest_is_valid() -> None:
    """Notebook bridge manifest should be internally consistent."""
    errors = validate_notebook_bridge(manifest_path=MANIFEST_PATH, repo_root=REPO_ROOT)
    assert errors == []


def test_manifest_covers_all_book_chapters() -> None:
    """Manifest should map every discovered chapter anchor exactly once."""
    chapters = discover_book_chapters(repo_root=REPO_ROOT)
    chapter_anchors = {chapter.anchor for chapter in chapters}
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_anchors = {
        entry["source_ref"].split("#", maxsplit=1)[1] for entry in manifest["entries"]
    }
    assert manifest_anchors == chapter_anchors
