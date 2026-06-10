"""Tests for bibliography JSON data generation helpers."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import generate_bibliography_data


def test_extract_yaml_from_markdown_returns_only_bibliography_items(tmp_path: Path) -> None:
    """Only YAML list entries containing an id should be extracted."""
    source = tmp_path / "refs.md"
    source.write_text(
        """Intro
```yaml
- id: Smith2020
  title: A Paper
- title: Missing ID
```
```yaml
not: a-list
```
""",
        encoding="utf-8",
    )

    items = generate_bibliography_data.extract_yaml_from_markdown(source)

    assert items == [{"id": "Smith2020", "title": "A Paper"}]


def test_normalize_item_renames_scholar_link_and_wraps_strings() -> None:
    """Frontend bibliography fields should be normalized in-place."""
    item = {
        "id": "A",
        "authors": "One Author",
        "concepts": "control",
        "scholar_link": "https://example.test",
    }

    normalized = generate_bibliography_data.normalize_item(item)

    assert normalized["authors"] == ["One Author"]
    assert normalized["concepts"] == ["control"]
    assert normalized["scholar_url"] == "https://example.test"
    assert "scholar_link" not in normalized


def test_merge_reference_preserves_existing_values() -> None:
    """Merging should fill blanks without overwriting populated fields."""
    existing = {"id": "A", "title": "Original", "doi": ""}
    new = {"id": "A", "title": "Replacement", "doi": "10/example"}

    generate_bibliography_data._merge_reference(existing, new)

    assert existing == {"id": "A", "title": "Original", "doi": "10/example"}


def test_process_reading_paths_writes_json(tmp_path: Path, monkeypatch) -> None:
    """reading_paths.yaml should be copied to JSON when present."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "reading_paths.yaml").write_text(
        "- id: path-a\n  title: Path A\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "docs" / "data"
    output_dir.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    generate_bibliography_data._process_reading_paths(output_dir)

    assert json.loads((output_dir / "reading_paths.json").read_text(encoding="utf-8")) == [
        {"id": "path-a", "title": "Path A"}
    ]
