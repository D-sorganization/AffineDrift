"""Tests for Article Front-Matter Schema and Core Page Compliance (WEB-03.1 #4506).

Verifies:
1. schemas/article-front-matter-v1.schema.json exists and is a valid Draft 2020-12 schema.
2. All core pages strictly comply with the schema without allowlist exemptions.
3. Validation fails for core pages missing any required field.
4. Validation fails if summary-plain exceeds 60 words or key-takeaways is outside 3-5 items.
5. Prohibits 'date: today' across all pages.
6. Allowlist entries correspond to existing files and can be burned down over time.
7. CONTRIBUTING.md documents the schema and fields.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import jsonschema

from src.tools.utils.frontmatter import split_frontmatter
from src.tools.utils.frontmatter_schema import (
    ALLOWLIST_PATH,
    SCHEMA_PATH,
    load_article_frontmatter_schema,
    load_frontmatter_allowlist,
    validate_article_frontmatter,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_schema_file_validity() -> None:
    """Verify schemas/article-front-matter-v1.schema.json is valid Draft 2020-12."""
    assert SCHEMA_PATH.is_file(), f"Missing schema file: {SCHEMA_PATH}"
    schema = load_article_frontmatter_schema(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)

    assert schema["$id"] == "https://affinedrift.com/schemas/article-front-matter-v1.schema.json"
    assert "status" in schema["properties"]
    assert "audience-level" in schema["properties"]
    assert "summary-plain" in schema["properties"]
    assert "abstract" in schema["properties"]
    assert "key-takeaways" in schema["properties"]
    assert "date" in schema["properties"]
    assert "evidence-rung" in schema["properties"]


def test_core_pages_fully_satisfy_schema() -> None:
    """All declared core pages must strictly satisfy the schema."""
    cfg = load_frontmatter_allowlist(ALLOWLIST_PATH)
    core_pages = cfg["core_pages"]
    assert len(core_pages) >= 10, "Expected at least 10 core pages"

    schema = load_article_frontmatter_schema(SCHEMA_PATH)
    validator = jsonschema.Draft202012Validator(schema)

    for rel_path in core_pages:
        full_path = REPO_ROOT / rel_path
        assert full_path.is_file(), f"Core page does not exist: {full_path}"
        content = full_path.read_text(encoding="utf-8")
        fm, _body = split_frontmatter(content)
        assert fm, f"Core page {rel_path} has no YAML front matter"

        # Validate with jsonschema
        errors = list(validator.iter_errors(fm))
        assert (
            not errors
        ), f"Core page {rel_path} failed schema validation: {[e.message for e in errors]}"

        # Validate with helper (includes word count and date today checks)
        rule_errors = validate_article_frontmatter(fm, rel_path, allowlist_config=cfg)
        assert not rule_errors, f"Core page {rel_path} failed rule validation: {rule_errors}"


def test_missing_required_field_fails_validation() -> None:
    """A core page missing any required field must fail validation."""
    sample_fm: dict[str, Any] = {
        "title": "Sample Article",
        "status": "available",
        "audience-level": "advanced",
        "summary-plain": "A concise summary of the topic.",
        "abstract": "A detailed technical abstract explaining the mechanics and formulation.",
        "key-takeaways": [
            "First key takeaway point.",
            "Second key takeaway point.",
            "Third key takeaway point.",
        ],
        "date": "2026-01-01",
        "date-modified": "2026-09-01",
        "last-reviewed": "2026-09-01",
        "canonical": "/articles/sample.html",
        "evidence-rung": "mathematical-identity",
    }
    cfg = {"core_pages": ["articles/sample.qmd"], "allowlist": []}

    # Baseline valid
    assert (
        validate_article_frontmatter(sample_fm, "articles/sample.qmd", allowlist_config=cfg) == []
    )

    # Missing status
    corrupt = copy.deepcopy(sample_fm)
    del corrupt["status"]
    errs = validate_article_frontmatter(corrupt, "articles/sample.qmd", allowlist_config=cfg)
    assert any("status" in e for e in errs)

    # Missing audience-level
    corrupt = copy.deepcopy(sample_fm)
    del corrupt["audience-level"]
    errs = validate_article_frontmatter(corrupt, "articles/sample.qmd", allowlist_config=cfg)
    assert any("audience-level" in e for e in errs)

    # Missing key-takeaways
    corrupt = copy.deepcopy(sample_fm)
    del corrupt["key-takeaways"]
    errs = validate_article_frontmatter(corrupt, "articles/sample.qmd", allowlist_config=cfg)
    assert any("key-takeaways" in e for e in errs)


def test_summary_plain_word_budget() -> None:
    """summary-plain exceeding 60 words must fail validation."""
    long_summary = "word " * 65
    sample_fm: dict[str, Any] = {
        "title": "Sample Article",
        "status": "available",
        "audience-level": "intro",
        "summary-plain": long_summary,
        "abstract": "Abstract text.",
        "key-takeaways": ["One", "Two", "Three"],
        "date": "2026-01-01",
        "date-modified": "2026-09-01",
        "last-reviewed": "2026-09-01",
        "canonical": "/articles/sample.html",
        "evidence-rung": "mathematical-identity",
    }
    cfg = {"core_pages": ["articles/sample.qmd"], "allowlist": []}
    errs = validate_article_frontmatter(sample_fm, "articles/sample.qmd", allowlist_config=cfg)
    assert any("exceeds 60 words" in e for e in errs)


def test_key_takeaways_item_count() -> None:
    """key-takeaways must contain between 3 and 5 items."""
    sample_fm: dict[str, Any] = {
        "title": "Sample Article",
        "status": "available",
        "audience-level": "intro",
        "summary-plain": "Brief summary.",
        "abstract": "Abstract text.",
        "key-takeaways": ["Only One", "Only Two"],
        "date": "2026-01-01",
        "date-modified": "2026-09-01",
        "last-reviewed": "2026-09-01",
        "canonical": "/articles/sample.html",
        "evidence-rung": "mathematical-identity",
    }
    cfg = {"core_pages": ["articles/sample.qmd"], "allowlist": []}
    # Too few items (2 < 3)
    errs = validate_article_frontmatter(sample_fm, "articles/sample.qmd", allowlist_config=cfg)
    assert any("key-takeaways" in e for e in errs)

    # Too many items (6 > 5)
    sample_fm["key-takeaways"] = ["1", "2", "3", "4", "5", "6"]
    errs = validate_article_frontmatter(sample_fm, "articles/sample.qmd", allowlist_config=cfg)
    assert any("key-takeaways" in e for e in errs)


def test_prohibits_date_today() -> None:
    """date: today must be rejected even on allowlisted pages."""
    sample_fm = {"title": "Title", "date": "today"}
    cfg = {"core_pages": [], "allowlist": ["articles/some_page.qmd"]}
    errs = validate_article_frontmatter(sample_fm, "articles/some_page.qmd", allowlist_config=cfg)
    assert any("date: today" in e for e in errs)


def test_allowlist_entries_exist() -> None:
    """All allowlist entries must correspond to actual existing files."""
    cfg = load_frontmatter_allowlist(ALLOWLIST_PATH)
    allowlisted = cfg["allowlist"]
    assert len(allowlisted) > 0, "Allowlist should not be empty during migration"
    for rel_path in allowlisted:
        full_path = REPO_ROOT / rel_path
        assert full_path.is_file(), f"Allowlist entry does not exist on disk: {rel_path}"


def test_contributing_docs_schema() -> None:
    """CONTRIBUTING.md must document the article front-matter schema."""
    contrib = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "article-front-matter-v1.schema.json" in contrib
    assert "audience-level" in contrib
    assert "summary-plain" in contrib
    assert "key-takeaways" in contrib
    assert "evidence-rung" in contrib
