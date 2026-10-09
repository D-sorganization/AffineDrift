"""Protect site-wide glossary data, generator, tooltip filter, and usage integrity.

Implements acceptance criteria for [WEB-01.5] (#4490):
1. data/glossary.yml contains at least 60 terms with plain and technical definitions.
2. Every term has a valid canonical_page reference.
3. Every {{< term ... >}} shortcode used across the repository references a declared key.
4. pages/glossary.qmd is generated from data/glossary.yml and stays fresh.
5. Tooltips provide accessible WAI-ARIA markup.
6. The book glossary links to the site glossary without duplication.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from scripts.generate_site_glossary import generate_glossary_qmd
from src.tools.site_glossary import (
    MINIMUM_TERMS,
    get_glossary_path,
    load_glossary,
    validate_glossary_entry,
)

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY_YAML = ROOT / "data" / "glossary.yml"
GLOSSARY_QMD = ROOT / "pages" / "glossary.qmd"
GLOSSARY_FILTER = ROOT / "scripts" / "filters" / "term-tooltip.lua"
BOOK_GLOSSARY_QMD = ROOT / "articles" / "The_Physics_of_Golf" / "quarto" / "glossary.qmd"


def test_glossary_data_minimum_count_and_schema() -> None:
    """Ensure data/glossary.yml exists, has >= 60 terms, and matches required schema."""
    glossary = load_glossary()
    assert (
        len(glossary) >= MINIMUM_TERMS
    ), f"Glossary must have at least {MINIMUM_TERMS} terms at launch; found {len(glossary)}"

    for key, entry in glossary.items():
        assert (
            isinstance(key, str) and key == key.strip() and key == key.lower()
        ), f"Term key '{key}' must be lowercase and stripped"
        assert re.match(
            r"^[a-z0-9-]+$", key
        ), f"Term key '{key}' must use only lowercase alphanumeric characters and hyphens"
        assert isinstance(entry, dict), f"Entry for '{key}' must be a mapping"
        validate_glossary_entry(key, entry)
        if "symbols" in entry and entry["symbols"] is not None:
            assert isinstance(entry["symbols"], list), f"Term '{key}' symbols must be a list"


def test_glossary_loader_and_validator_error_cases(tmp_path: Path) -> None:
    """Verify error contracts of load_glossary and validate_glossary_entry."""
    assert get_glossary_path().exists()

    with pytest.raises(FileNotFoundError, match="Missing glossary data file"):
        load_glossary(tmp_path / "nonexistent.yml")

    invalid_file = tmp_path / "invalid.yml"
    invalid_file.write_text("- item1\n- item2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        load_glossary(invalid_file)

    valid_entry = {
        "name": "Drift",
        "plain": "The model's change at zero declared input.",
        "technical": "The complete zero-declared-input vector field.",
        "canonical_page": "articles/affine-nature-golf-swing.qmd",
    }
    validate_glossary_entry("drift", valid_entry)

    bad_entry_missing = dict(valid_entry)
    del bad_entry_missing["plain"]
    with pytest.raises(ValueError, match="missing required field 'plain'"):
        validate_glossary_entry("drift", bad_entry_missing)

    bad_entry_empty = dict(valid_entry, plain="")
    with pytest.raises(ValueError, match="missing required field 'plain'"):
        validate_glossary_entry("drift", bad_entry_empty)

    bad_entry_non_str = dict(valid_entry, name=123)
    with pytest.raises(ValueError, match="name must be a string"):
        validate_glossary_entry("drift", bad_entry_non_str)


def test_glossary_canonical_pages_resolve() -> None:
    """Ensure every canonical_page in data/glossary.yml resolves to a valid file in the project."""
    glossary = load_glossary()
    for key, entry in glossary.items():
        page = entry["canonical_page"]
        # Normalise .html to .qmd or check raw source
        src_path = page.replace(".html", ".qmd")
        if src_path.startswith("/"):
            src_path = src_path[1:]
        resolved = ROOT / src_path
        alt_resolved = ROOT / page
        assert (
            resolved.exists() or alt_resolved.exists()
        ), f"Term '{key}' specifies canonical_page '{page}' which does not exist in repo ({resolved})"


def test_pages_glossary_qmd_exists_and_covers_all_terms() -> None:
    """Ensure pages/glossary.qmd exists, is up to date, and renders all terms from data/glossary.yml."""
    glossary = load_glossary()
    assert GLOSSARY_QMD.exists(), f"pages/glossary.qmd must exist: {GLOSSARY_QMD}"
    qmd_content = GLOSSARY_QMD.read_text(encoding="utf-8")
    assert qmd_content == generate_glossary_qmd(
        glossary
    ), "Generated glossary is stale; run python scripts/generate_site_glossary.py"

    # Frontmatter verification
    assert (
        'title: "Site Glossary"' in qmd_content
        or "title: Site Glossary" in qmd_content
        or 'title: "Glossary"' in qmd_content
        or "title: Glossary" in qmd_content
    )
    # Each term must have an anchor/heading or entry
    for key, entry in glossary.items():
        term_name = entry["name"]
        assert term_name in qmd_content, f"Term name '{term_name}' not found in pages/glossary.qmd"
        assert (
            f"#{key}" in qmd_content or f'id="{key}"' in qmd_content or f"{{#{key}}}" in qmd_content
        ), f"Anchor or ID for term '{key}' not found in pages/glossary.qmd"


def test_every_term_shortcode_references_valid_key() -> None:
    """Scan all qmd and md files for {{< term ... >}} shortcodes and verify key exists in YAML."""
    glossary = load_glossary()
    term_pattern = re.compile(
        r"\{\{<\s*term\s+[\"']?([a-z0-9-]+)[\"']?(?:\s+[\"'](.*?)[\"'])?\s*>\}\}"
    )

    all_files = list(ROOT.glob("**/*.qmd")) + list(ROOT.glob("**/*.md"))
    for file_path in all_files:
        if (
            ".git" in file_path.parts
            or "docs" in file_path.parts
            or file_path.name in ("CONTRIBUTING.md", "README.md")
        ):
            continue
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        for match in term_pattern.finditer(content):
            key = match.group(1)
            if key in ("key", "term-key"):
                continue
            assert (
                key in glossary
            ), f"Unknown glossary term key '{key}' referenced in {file_path.relative_to(ROOT)}"


@pytest.mark.integration
def test_glossary_alphabet_renders_as_links() -> None:
    """Catch indentation turning the alphabetical navigation into visible HTML code."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required to verify rendered glossary navigation")
    glossary = load_glossary()
    result = subprocess.run(
        [quarto, "pandoc", "--from=markdown", "--to=html", "--mathjax"],
        input=generate_glossary_qmd(glossary),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    letters = {term["name"][0].lower() for term in glossary.values()}
    for letter in letters:
        assert f'<a href="#{letter}" class="glossary-nav__letter">' in result.stdout
    assert result.stdout.count('class="glossary-nav__letter"') == len(letters)


def test_book_glossary_links_to_site_glossary() -> None:
    """Ensure the book appendix glossary links to the site glossary without duplication."""
    assert BOOK_GLOSSARY_QMD.exists()
    content = BOOK_GLOSSARY_QMD.read_text(encoding="utf-8")
    assert (
        "pages/glossary.html" in content
        or "pages/glossary.qmd" in content
        or "site glossary" in content.lower()
    ), "Book glossary must link to the site-wide glossary in pages/glossary.qmd"


@pytest.mark.integration
def test_term_tooltip_lua_filter_accessible_markup() -> None:
    """Render a test snippet using term-tooltip.lua and check WAI-ARIA accessibility."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the term-tooltip filter integration check")
    assert GLOSSARY_FILTER.exists(), f"Filter must exist at {GLOSSARY_FILTER}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        qmd = Path(tmp_dir) / "test.qmd"
        content = (
            "---\n"
            "title: Test Glossary Tooltip\n"
            f"filters:\n  - {GLOSSARY_FILTER.resolve().as_posix()}\n"
            "format: html\n"
            "---\n\n"
            'Compare {{< term drift >}} with {{< term control-input "declared input" >}}.\n'
        )
        qmd.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [quarto, "render", str(qmd), "--to", "html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0, f"quarto render failed:\n{result.stderr}\n{result.stdout}"
        html_file = qmd.with_suffix(".html")
        assert html_file.exists()
        html = html_file.read_text(encoding="utf-8")

        # Verify accessible tooltip structure
        assert "glossary-term" in html
        assert "glossary-tooltip" in html
        assert 'role="tooltip"' in html or "aria-describedby" in html
        assert "pages/glossary.html#drift" in html
        assert "declared input" in html
        assert load_glossary()["drift"]["plain"] in html
        assert load_glossary()["control-input"]["plain"] in html
