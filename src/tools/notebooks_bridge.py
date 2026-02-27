"""Notebook bridge generation and validation for The Geometry of Motion."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from src.core.contracts import ensure, require

ALLOWED_STATUS = {"scaffolded", "planned"}
CHAPTER_HEADING_PATTERN = re.compile(
    r"^## Chapter (\d+): (.+?) \{#(book\d+-ch\d+)\}\s*$",
    re.MULTILINE,
)
BOOK_VOLUME_FILES: tuple[tuple[int, Path], ...] = (
    (1, Path("books/tangent-space-methods.qmd")),
    (2, Path("books/control-is-motion.qmd")),
    (3, Path("books/biomechanics-biology-to-systems.qmd")),
    (4, Path("books/human-motor-control.qmd")),
)


@dataclass(frozen=True)
class ChapterRef:
    """Reference to a chapter anchor in the books workspace."""

    volume: int
    chapter: int
    anchor: str
    title: str
    source_file: Path


def _load_json(path: Path) -> dict[str, Any]:
    require(path.exists(), f"Missing file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    require(isinstance(data, dict), f"Expected JSON object in {path}")
    return cast("dict[str, Any]", data)


def _slug(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return normalized or "chapter"


def _notebook_rel_path(chapter: ChapterRef) -> Path:
    filename = f"vol{chapter.volume}_ch{chapter.chapter}_{_slug(chapter.title)}.ipynb"
    return Path("notebooks/geometry_of_motion") / filename


def _build_notebook(chapter: ChapterRef) -> dict[str, Any]:
    title = f"# Tutorial: Volume {chapter.volume} Chapter {chapter.chapter} {chapter.title}\n"
    chapter_label = f"Volume {chapter.volume} Chapter {chapter.chapter}"
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [title, "\n", f"Source: `{chapter_label}`\n"],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from __future__ import annotations\n",
                    "\n",
                    f"CHAPTER = '{chapter_label}'\n",
                    "CHAPTER\n",
                ],
            },
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def extract_chapters_from_text(text: str, *, source_file: Path) -> list[ChapterRef]:
    """Extract chapter references from a books page."""
    require(len(text) > 0, "text must not be empty")
    require(source_file is not None, "source_file must be provided")

    volume_match = re.search(r"book(\d+)-", text)
    inferred_volume = int(volume_match.group(1)) if volume_match is not None else 0
    chapters: list[ChapterRef] = []
    for match in CHAPTER_HEADING_PATTERN.finditer(text):
        chapter_num = int(match.group(1))
        title = match.group(2).strip()
        anchor = match.group(3).strip()
        volume_match = re.match(r"book(\d+)-ch\d+", anchor)
        volume = int(volume_match.group(1)) if volume_match is not None else inferred_volume
        chapters.append(
            ChapterRef(
                volume=volume,
                chapter=chapter_num,
                anchor=anchor,
                title=title,
                source_file=source_file,
            )
        )
    return chapters


def discover_book_chapters(*, repo_root: Path) -> list[ChapterRef]:
    """Discover chapter anchors across Volumes I-IV books pages."""
    require(repo_root.exists(), "repo_root must exist")
    chapters: list[ChapterRef] = []
    for expected_volume, relative_file in BOOK_VOLUME_FILES:
        file_path = repo_root / relative_file
        require(file_path.exists(), f"Missing books file: {relative_file}")
        text = file_path.read_text(encoding="utf-8")
        file_chapters = extract_chapters_from_text(text, source_file=relative_file)
        chapters.extend(file_chapters)
        for chapter in file_chapters:
            ensure(chapter.volume == expected_volume, f"Volume mismatch for {chapter.anchor}")
    return chapters


def _entry_from_chapter(chapter: ChapterRef) -> dict[str, Any]:
    notebook_rel = _notebook_rel_path(chapter)
    return {
        "id": f"vol{chapter.volume}-ch{chapter.chapter}-{_slug(chapter.title)}",
        "title": f"Volume {chapter.volume} Chapter {chapter.chapter} {chapter.title} Notebook",
        "source_ref": f"{chapter.source_file.as_posix()}#{chapter.anchor}",
        "notebook_path": notebook_rel.as_posix(),
        "status": "scaffolded",
    }


def _write_notebook(path: Path, notebook_data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(notebook_data, handle, indent=2)
        handle.write("\n")


def _write_manifest(*, manifest_path: Path, entries: list[dict[str, Any]]) -> None:
    manifest = {
        "series": "The Geometry of Motion",
        "description": "Executable chapter bridge between textbook pages and Jupyter notebooks.",
        "entries": entries,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")


def _prune_stale_notebooks(*, output_dir: Path, expected_files: set[Path]) -> None:
    if not output_dir.exists():
        return
    for notebook_file in output_dir.glob("*.ipynb"):
        if notebook_file not in expected_files:
            notebook_file.unlink()


def sync_notebook_bridge(*, repo_root: Path, output_dir: Path, manifest_path: Path) -> None:
    """Generate a complete chapter-to-notebook bridge from books pages."""
    require(repo_root.exists(), "repo_root must exist")
    chapters = discover_book_chapters(repo_root=repo_root)
    entries = [_entry_from_chapter(chapter) for chapter in chapters]
    expected_files: set[Path] = set()
    for chapter in chapters:
        notebook_path = repo_root / _notebook_rel_path(chapter)
        _write_notebook(notebook_path, _build_notebook(chapter))
        expected_files.add(notebook_path)
    _prune_stale_notebooks(output_dir=output_dir, expected_files=expected_files)
    _write_manifest(manifest_path=manifest_path, entries=entries)
    ensure(manifest_path.exists(), "Manifest generation failed")
    ensure(output_dir.exists(), "Notebook output directory must exist after sync")


def _parse_source_ref(source_ref: str) -> tuple[Path, str | None]:
    if "#" not in source_ref:
        return Path(source_ref), None
    file_part, anchor = source_ref.split("#", maxsplit=1)
    return Path(file_part), anchor


def _has_tutorial_title(notebook_data: dict[str, Any]) -> bool:
    cells = notebook_data.get("cells")
    if not isinstance(cells, list) or not cells:
        return False
    first = cells[0]
    if not isinstance(first, dict) or first.get("cell_type") != "markdown":
        return False
    source = first.get("source")
    if isinstance(source, list):
        return bool(source and str(source[0]).startswith("# Tutorial:"))
    if isinstance(source, str):
        return source.startswith("# Tutorial:")
    return False


def _validate_entry(entry: dict[str, Any], repo_root: Path) -> list[str]:
    errors: list[str] = []
    entry_id = str(entry.get("id", "<missing-id>"))
    for field in ("id", "title", "source_ref", "notebook_path", "status"):
        if field not in entry:
            errors.append(f"{entry_id}: missing field '{field}'")
    status = str(entry.get("status", ""))
    if status not in ALLOWED_STATUS:
        errors.append(f"{entry_id}: invalid status '{status}'")

    source_file, anchor = _parse_source_ref(str(entry.get("source_ref", "")))
    source_path = repo_root / source_file
    if not source_path.exists():
        errors.append(f"{entry_id}: missing source file '{source_file}'")
    elif anchor is not None and f"{{#{anchor}}}" not in source_path.read_text(encoding="utf-8"):
        errors.append(f"{entry_id}: missing anchor '{anchor}' in '{source_file}'")

    notebook_path = repo_root / Path(str(entry.get("notebook_path", "")))
    if status == "scaffolded":
        if not notebook_path.exists():
            errors.append(f"{entry_id}: missing notebook '{notebook_path}'")
        else:
            notebook_data = _load_json(notebook_path)
            if not _has_tutorial_title(notebook_data):
                errors.append(f"{entry_id}: notebook title cell must start with '# Tutorial:'")
    return errors


def validate_notebook_bridge(*, manifest_path: Path, repo_root: Path) -> list[str]:
    """Validate notebook bridge manifest and scaffolds."""
    require(manifest_path.exists(), "manifest_path must exist")
    require(repo_root.exists(), "repo_root must exist")
    manifest = _load_json(manifest_path)
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        return ["Manifest must contain an 'entries' list"]
    errors: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("Manifest entries must be objects")
            continue
        errors.extend(_validate_entry(entry, repo_root))
    return errors
