"""Offline tests for check_bibliography_metadata.py.

The CrossRef lookups need the network, but everything that decides *what* is
compared -- field extraction, normalisation, citation discovery and the
mismatch rules -- is pure and is pinned here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_bibliography_metadata import (
    cited_keys,
    differences,
    entries,
    field,
    first_page,
    norm,
)

PROCEEDINGS = """@inproceedings{hogan1985impedance,
  booktitle = {Proceedings of the American Control Conference},
  title     = {Impedance Control: An Approach to {Manipulation}},
  author    = {Hogan, Neville},
  year      = 1985,
  pages     = {304--313},
}
"""


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("title", "Impedance Control: An Approach to {Manipulation}"),
        ("booktitle", "Proceedings of the American Control Conference"),
        ("author", "Hogan, Neville"),
        ("year", "1985"),
        ("pages", "304--313"),
        ("volume", ""),
    ],
)
def test_field_reads_the_named_field_not_a_suffix_match(name: str, expected: str) -> None:
    assert field(PROCEEDINGS, name) == expected


def test_field_reads_quoted_values() -> None:
    body = '@article{k,\n  title = "Motor {Cortex} and Direction",\n  journal = "Science",\n}'
    assert field(body, "title") == "Motor {Cortex} and Direction"
    assert field(body, "journal") == "Science"


def test_field_joins_a_value_wrapped_across_lines() -> None:
    body = "@article{k,\n  title = {A long title\n           wrapped twice\n   here},\n}"
    assert field(body, "title") == "A long title wrapped twice here"


def test_field_is_case_insensitive_and_tolerates_unterminated_values() -> None:
    assert field("@article{k, TITLE = {Upper}}", "title") == "Upper"
    assert field("@article{k, title = {never closed", "title") == ""


def test_norm_strips_tex_and_punctuation() -> None:
    assert norm("The {Kinematic}  Chain: Part-II!") == "the kinematic chain part ii"


@pytest.mark.parametrize(
    ("value", "expected"),
    [("187--230", "187"), ("187–230", "187"), ("e1001", "1001"), ("42", "42"), ("", "")],
)
def test_first_page(value: str, expected: str) -> None:
    assert first_page(value) == expected


def test_entries_splits_keys_types_and_bodies() -> None:
    text = PROCEEDINGS + "\n@Article{ Kawato1987 ,\n  title = {Wrong},\n}\n"
    found = list(entries(text))
    assert [(key, kind) for key, kind, _ in found] == [
        ("hogan1985impedance", "inproceedings"),
        ("Kawato1987", "article"),
    ]
    assert field(found[1][2], "title") == "Wrong"


def test_cited_keys_reads_latex_and_pandoc_citations(tmp_path: Path) -> None:
    (tmp_path / "ch1.tex").write_text(
        r"See \citep[p.~3]{alpha, beta} and \textcite{gamma}; \nocite{hidden}.",
        encoding="utf-8",
    )
    sub = tmp_path / "site"
    sub.mkdir()
    (sub / "page.qmd").write_text("As shown [@delta; -@eps.x, p. 4].", encoding="utf-8")
    (sub / "note.md").write_text("Email me@example.com is not [a citation].", encoding="utf-8")
    assert cited_keys(tmp_path) == {"alpha", "beta", "gamma", "delta", "eps.x"}


def _entry(**overrides: str) -> dict[str, str]:
    entry = {"year": "1986", "volume": "233", "pages": "1416--1419", "journal": "Science"}
    entry.update(overrides)
    return entry


RECORD = {
    "issued": {"date-parts": [[1986, 9, 26]]},
    "volume": "233",
    "page": "1416-1419",
    "container-title": ["Science"],
}


def test_differences_empty_when_every_field_agrees() -> None:
    assert differences(_entry(), RECORD) == []


def test_differences_reports_each_mismatch() -> None:
    found = differences(
        _entry(year="1982", volume="2", pages="1527--1537", journal="Journal of Neuroscience"),
        RECORD,
    )
    assert found == [
        "year 1982 vs 1986",
        "volume 2 vs 233",
        "first page 1527 vs 1416",
        "journal 'Journal of Neuroscience' vs 'Science'",
    ]


def test_differences_ignores_fields_missing_on_either_side() -> None:
    assert differences(_entry(year="", volume="", pages="", journal=""), RECORD) == []
    assert differences(_entry(), {}) == []
