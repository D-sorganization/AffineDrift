"""Tests for scripts/check_bibliography_quality.py.

TDD: RED tests written first, then the implementation.
Tests DbC preconditions (file parses) and postconditions (rules pass).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# The module under test — will be implemented to make these pass
from scripts.check_bibliography_quality import (
    BibliographyError,
    check_no_duplicate_ids,
    check_no_et_al_authors,
    check_papers_have_doi_or_url,
    check_required_fields,
    load_and_validate,
)

# ─── fixtures ──────────────────────────────────────────────────────────────

VALID_PAPER = {
    "id": "smith2020example",
    "title": "An Example Paper",
    "authors": ["Jane Smith", "John Doe"],
    "year": 2020,
    "type": "paper",
    "venue": "Journal of Examples",
    "doi": "10.1000/example",
}

VALID_BOOK = {
    "id": "doe2019book",
    "title": "Example Book",
    "authors": ["John Doe"],
    "year": 2019,
    "type": "book",
    "venue": "Example Publisher",
}


@pytest.fixture
def tmp_bib(tmp_path: Path):
    """Write a bibliography JSON file to a temp dir and return its path."""

    def _write(entries: list[dict]) -> Path:
        p = tmp_path / "bibliography.json"
        p.write_text(json.dumps(entries), encoding="utf-8")
        return p

    return _write


# ─── load_and_validate ─────────────────────────────────────────────────────


class TestLoadAndValidate:
    def test_loads_valid_file(self, tmp_bib):
        path = tmp_bib([VALID_PAPER])
        entries = load_and_validate(path)
        assert len(entries) == 1

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(BibliographyError, match="not found"):
            load_and_validate(tmp_path / "missing.json")

    def test_raises_on_invalid_json(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("not valid json", encoding="utf-8")
        with pytest.raises(BibliographyError, match="JSON"):
            load_and_validate(bad)

    def test_raises_when_not_a_list(self, tmp_bib):
        path = tmp_bib({"not": "a list"})  # type: ignore[arg-type]
        with pytest.raises(BibliographyError, match="list"):
            load_and_validate(path)


# ─── check_required_fields ─────────────────────────────────────────────────


class TestCheckRequiredFields:
    def test_passes_complete_entry(self):
        violations = check_required_fields([VALID_PAPER])
        assert violations == []

    def test_detects_missing_id(self):
        entry = {**VALID_PAPER, "id": ""}
        violations = check_required_fields([entry])
        assert any("id" in v for v in violations)

    def test_detects_missing_title(self):
        entry = {k: v for k, v in VALID_PAPER.items() if k != "title"}
        violations = check_required_fields([entry])
        assert any("title" in v for v in violations)

    def test_detects_missing_authors(self):
        entry = {**VALID_PAPER, "authors": []}
        violations = check_required_fields([entry])
        assert any("authors" in v for v in violations)

    def test_detects_missing_year(self):
        entry = {k: v for k, v in VALID_PAPER.items() if k != "year"}
        violations = check_required_fields([entry])
        assert any("year" in v for v in violations)

    def test_detects_missing_type(self):
        entry = {k: v for k, v in VALID_PAPER.items() if k != "type"}
        violations = check_required_fields([entry])
        assert any("type" in v for v in violations)

    def test_multiple_violations_reported(self):
        entry = {"id": "x"}  # missing title, authors, year, type
        violations = check_required_fields([entry])
        assert len(violations) >= 3


# ─── check_no_et_al_authors ────────────────────────────────────────────────


class TestCheckNoEtAlAuthors:
    def test_passes_clean_entry(self):
        violations = check_no_et_al_authors([VALID_PAPER])
        assert violations == []

    def test_detects_et_al_as_sole_author(self):
        entry = {**VALID_PAPER, "authors": ["et al."]}
        violations = check_no_et_al_authors([entry])
        assert len(violations) == 1
        assert "et al." in violations[0]
        assert VALID_PAPER["id"] in violations[0]

    def test_detects_et_al_in_author_list(self):
        entry = {**VALID_PAPER, "authors": ["Jane Smith", "et al."]}
        violations = check_no_et_al_authors([entry])
        assert len(violations) == 1

    def test_case_insensitive_detection(self):
        entry = {**VALID_PAPER, "authors": ["Et Al.", "John Doe"]}
        violations = check_no_et_al_authors([entry])
        assert len(violations) == 1

    def test_multiple_bad_entries_all_reported(self):
        e1 = {**VALID_PAPER, "id": "a", "authors": ["et al."]}
        e2 = {**VALID_PAPER, "id": "b", "authors": ["et al."]}
        violations = check_no_et_al_authors([e1, e2])
        assert len(violations) == 2

    def test_budget_allows_known_et_al_entries(self, tmp_path):
        """Entries listed in the budget under et_al_exempt_ids are exempt."""
        entry = {**VALID_PAPER, "id": "exempt1", "authors": ["Jane Smith", "et al."]}
        budget = tmp_path / "bib_budget.json"
        budget.write_text(json.dumps({"et_al_exempt_ids": ["exempt1"]}), encoding="utf-8")
        violations = check_no_et_al_authors([entry], budget_path=budget)
        assert violations == []

    def test_budget_does_not_exempt_unlisted_entries(self, tmp_path):
        """Unlisted entries are still checked even if a budget file exists."""
        entry = {**VALID_PAPER, "id": "not_exempt", "authors": ["Jane Smith", "et al."]}
        budget = tmp_path / "bib_budget.json"
        budget.write_text(json.dumps({"et_al_exempt_ids": ["some_other_id"]}), encoding="utf-8")
        violations = check_no_et_al_authors([entry], budget_path=budget)
        assert len(violations) == 1


# ─── check_no_duplicate_ids ────────────────────────────────────────────────


class TestCheckNoDuplicateIds:
    def test_passes_unique_ids(self):
        e1 = {**VALID_PAPER, "id": "alpha"}
        e2 = {**VALID_PAPER, "id": "beta"}
        violations = check_no_duplicate_ids([e1, e2])
        assert violations == []

    def test_detects_duplicate_id(self):
        e1 = {**VALID_PAPER, "id": "same"}
        e2 = {**VALID_PAPER, "id": "same"}
        violations = check_no_duplicate_ids([e1, e2])
        assert len(violations) == 1
        assert "same" in violations[0]

    def test_detects_multiple_duplicate_pairs(self):
        entries = [
            {**VALID_PAPER, "id": "x"},
            {**VALID_PAPER, "id": "x"},
            {**VALID_PAPER, "id": "y"},
            {**VALID_PAPER, "id": "y"},
        ]
        violations = check_no_duplicate_ids(entries)
        assert len(violations) == 2


# ─── check_papers_have_doi_or_url ─────────────────────────────────────────


class TestCheckPapersHaveDoiOrUrl:
    def test_passes_paper_with_doi(self):
        violations = check_papers_have_doi_or_url([VALID_PAPER])
        assert violations == []

    def test_passes_paper_with_url(self):
        entry = {**VALID_PAPER}
        del entry["doi"]
        entry["url"] = "https://example.com/paper"
        violations = check_papers_have_doi_or_url([entry])
        assert violations == []

    def test_fails_paper_with_neither(self):
        entry = {k: v for k, v in VALID_PAPER.items() if k != "doi"}
        violations = check_papers_have_doi_or_url([entry])
        assert len(violations) == 1
        assert VALID_PAPER["id"] in violations[0]

    def test_books_not_required_to_have_doi(self):
        book = {**VALID_BOOK}  # no doi or url
        violations = check_papers_have_doi_or_url([book])
        assert violations == []

    def test_software_not_required_to_have_doi(self):
        sw = {**VALID_PAPER, "type": "software", "id": "sw1"}
        del sw["doi"]
        violations = check_papers_have_doi_or_url([sw])
        assert violations == []

    def test_budget_allows_known_missing_dois(self, tmp_bib, tmp_path):
        """Entries listed in the budget file are exempt from the DOI check."""
        entry = {k: v for k, v in VALID_PAPER.items() if k != "doi"}
        budget = tmp_path / "bib_budget.json"
        budget.write_text(json.dumps({"exempt_ids": [entry["id"]]}), encoding="utf-8")
        violations = check_papers_have_doi_or_url([entry], budget_path=budget)
        assert violations == []
