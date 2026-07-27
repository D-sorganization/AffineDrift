"""Content hygiene checks for public Quarto pages."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.content_lint

ROOT_DIR = Path(__file__).resolve().parent.parent
CRITIQUES_DIR = ROOT_DIR / "critiques"
QUARTO_CONFIG = ROOT_DIR / "_quarto.yml"
EDITORIAL_ONLY = {"INLINE_SUGGESTIONS.md"}


def _frontmatter(path: Path) -> dict[str, object]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    data = yaml.safe_load(parts[1])
    return data if isinstance(data, dict) else {}


def test_editorial_only_critique_notes_are_excluded_from_quarto_render() -> None:
    config = QUARTO_CONFIG.read_text(encoding="utf-8")

    assert '"critiques/*.md"' in config
    assert '"!critiques/INLINE_SUGGESTIONS.md"' in config


def test_public_critique_markdown_has_unique_descriptions() -> None:
    public_files = [
        path for path in sorted(CRITIQUES_DIR.glob("*.md")) if path.name not in EDITORIAL_ONLY
    ]
    descriptions: list[str] = []

    for path in public_files:
        metadata = _frontmatter(path)
        description = str(metadata.get("description", "")).strip()
        descriptions.append(description)

        assert metadata.get("title"), f"{path.name} needs a public title"
        assert description, f"{path.name} needs a meta description"
        assert 50 <= len(description) <= 160, f"{path.name} description length is off"

    assert len(descriptions) == len(set(descriptions)), "critique descriptions must be unique"


def test_about_source_uses_explicit_em_dash_in_raw_html_copy() -> None:
    about = (ROOT_DIR / "pages" / "about.qmd").read_text(encoding="utf-8")

    assert "active control—the namesake" in about
    assert "active control---the namesake" not in about
