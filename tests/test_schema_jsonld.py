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
import yaml

ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts/filters/schema-jsonld.lua"

JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def _render(frontmatter_extra: str, body: str = "Body text.") -> dict[str, object] | None:
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
            f"---\n\n{body}\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [quarto, "render", str(qmd), "--to", "html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        assert result.returncode == 0, result.stderr
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


@pytest.mark.integration
def test_technical_reference_cites_equations_and_pinned_code() -> None:
    citations = [
        "https://affinedrift.com/pages/notation.html#drift-and-control",
        "https://github.com/D-sorganization/UpstreamDrift/blob/" + "a" * 40 + "/engine.py",
    ]
    metadata = "schema-type: TechArticle\nschema-citations:\n" + "".join(
        f"  - {url}\n" for url in citations
    )
    data = _render(metadata)
    assert data is not None
    assert data["@type"] == "TechArticle"
    assert data["headline"] == "Test Title"
    assert data["author"] == {"@type": "Person", "name": "Jane Doe"}
    assert data["citation"] == citations


@pytest.mark.integration
def test_glossary_exports_its_actual_definitions_without_script_breakout() -> None:
    body = """### Gravity

::: {.glossary-entry #def-gravity}
**Technical Definition:** Acceleration in a declared frame. Literal `</script>` stays text.
:::
"""
    data = _render(
        "schema-type: DefinedTermSet\nschema-url: https://affinedrift.com/pages/glossary.html",
        body,
    )
    assert data is not None
    assert data["@type"] == "DefinedTermSet"
    terms = data["hasDefinedTerm"]
    assert len(terms) == 1
    term = terms[0]
    assert term["@type"] == "DefinedTerm"
    assert term["name"] == "Gravity"
    assert term["termCode"] == "def-gravity"
    assert term["url"] == "https://affinedrift.com/pages/glossary.html#def-gravity"
    assert "Acceleration in a declared frame" in term["description"]
    assert "</script>" in term["description"]


@pytest.mark.integration
def test_every_real_glossary_entry_is_exported() -> None:
    source = (ROOT / "pages/glossary.qmd").read_text(encoding="utf-8")
    expected = re.findall(r'\.glossary-entry[^\n]*\bid="(def-[^"]+)"', source)
    assert expected
    data = _render(
        "schema-type: DefinedTermSet\nschema-url: https://affinedrift.com/pages/glossary.html",
        source.split("---", 2)[2],
    )
    assert data is not None
    terms = data["hasDefinedTerm"]
    assert len(terms) == len(expected)
    assert {term["termCode"] for term in terms} == set(expected)
    assert terms[0]["name"] == "Acceleration"
    description = " ".join(terms[0]["description"].split()).replace("’", "'")
    assert "rate at which an object's speed or direction changes" in description
    assert "\n\nTechnical Definition:" in terms[0]["description"]


@pytest.mark.integration
@pytest.mark.parametrize(
    ("metadata", "message"),
    [
        (
            "schema-type: TechArticle\nschema-citations: ['javascript:alert(1)']",
            "schema-citations must contain absolute HTTPS references",
        ),
        (
            "schema-type: DefinedTermSet\nschema-url: https://affinedrift.com/pages/glossary.html",
            "DefinedTermSet requires glossary-entry definitions",
        ),
    ],
)
def test_invalid_reference_metadata_fails_the_render(metadata: str, message: str) -> None:
    with pytest.raises(AssertionError, match=message):
        _render(metadata)


@pytest.mark.parametrize(
    ("source", "schema_type"),
    [
        ("pages/notation.qmd", "TechArticle"),
        ("pages/upstreamdrift-engine-protocol.qmd", "TechArticle"),
        ("pages/glossary.qmd", "DefinedTermSet"),
    ],
)
def test_canonical_reference_pages_enable_structured_metadata(
    source: str, schema_type: str
) -> None:
    text = (ROOT / source).read_text(encoding="utf-8")
    metadata = yaml.safe_load(text.split("---", 2)[1])
    assert metadata.get("schema-type") == schema_type
    assert metadata["schema-url"] == "https://affinedrift.com/" + source.replace(".qmd", ".html")
    if schema_type == "TechArticle":
        assert metadata["schema-citations"]
