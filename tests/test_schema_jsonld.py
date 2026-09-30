"""Exercise the Schema.org JSON-LD Lua filter against Quarto's real HTML render.

The filter (`scripts/filters/schema-jsonld.lua`) uses `quarto.doc.include_text`,
a Quarto-specific Lua API unavailable under bare `quarto pandoc`, so these
tests render through `quarto render` (see `tests/test_companion_hierarchy.py`
for the sibling pattern that uses `quarto pandoc` for filters that do not need
that API).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts/filters/schema-jsonld.lua"

JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def _render(frontmatter_extra: str) -> dict[str, object] | None:
    """Render a synthetic page through the production filter; return its JSON-LD."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the JSON-LD filter integration check")
    with tempfile.TemporaryDirectory() as tmp_dir:
        qmd = Path(tmp_dir) / "test.qmd"
        qmd.write_text(
            "---\n"
            "title: Test Title\n"
            "description: Test description\n"
            "author: Jane Doe\n"
            f"{frontmatter_extra}\n"
            f"filters:\n  - {FILTER.resolve().as_posix()}\n"
            "format: html\n"
            "---\n\nBody text.\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [quarto, "render", str(qmd), "--to", "html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        assert result.returncode == 0
        html = qmd.with_suffix(".html").read_text(encoding="utf-8")
    match = JSONLD_RE.search(html)
    return json.loads(match.group(1)) if match else None


@pytest.mark.integration
def test_page_without_schema_type_gets_no_jsonld() -> None:
    assert _render("categories: [test]") is None


@pytest.mark.integration
def test_unsupported_schema_type_is_ignored() -> None:
    assert _render("schema-type: Person") is None


@pytest.mark.integration
def test_scholarly_article_emits_valid_jsonld_with_iso_date() -> None:
    data = _render("date: 2026-01-15\ndate-format: iso\nschema-type: ScholarlyArticle")
    assert data == {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": "Test Title",
        "description": "Test description",
        "publisher": {
            "@type": "Organization",
            "name": "AffineDrift",
            "logo": {"@type": "ImageObject", "url": "https://affinedrift.com/logo/og-card.png"},
        },
        "author": {"@type": "Person", "name": "Jane Doe"},
        "datePublished": "2026-01-15",
        "isAccessibleForFree": True,
    }


@pytest.mark.integration
def test_scholarly_article_omits_non_iso_date_rather_than_emit_wrong_format() -> None:
    # Quarto's default html date-format reformats `date` into a display
    # string (e.g. "January 15, 2026") before Lua filters run.
    data = _render("date: 2026-01-15\nschema-type: ScholarlyArticle")
    assert data is not None
    assert "datePublished" not in data


@pytest.mark.integration
def test_book_includes_isbn() -> None:
    data = _render("isbn: '978-0-000-00000-0'\nschema-type: Book")
    assert data["@type"] == "Book"
    assert data["name"] == "Test Title"
    assert data["isbn"] == "978-0-000-00000-0"


@pytest.mark.integration
def test_chapter_includes_is_part_of_and_position() -> None:
    data = _render('part-of-title: "Parent Work"\nchapter-number: "3"\nschema-type: Chapter')
    assert data["@type"] == "Chapter"
    assert data["headline"] == "Test Title"
    assert data["isPartOf"] == {"@type": "CreativeWork", "name": "Parent Work"}
    assert data["position"] == "3"


@pytest.mark.integration
def test_dataset_uses_creator_not_author() -> None:
    data = _render("license: CC-BY-4.0\nschema-type: Dataset")
    assert data["@type"] == "Dataset"
    assert data["creator"] == {"@type": "Person", "name": "Jane Doe"}
    assert "author" not in data
    assert data["license"] == "CC-BY-4.0"


@pytest.mark.integration
def test_software_source_code_defaults_repository_and_keeps_language() -> None:
    data = _render("programming-language: Python\nschema-type: SoftwareSourceCode")
    assert data["@type"] == "SoftwareSourceCode"
    assert data["codeRepository"] == "https://github.com/D-sorganization/AffineDrift"
    assert data["programmingLanguage"] == "Python"
