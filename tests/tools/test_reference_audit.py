"""Tests for reference_audit in AffineDrift."""

from src.tools.reference_audit import (
    collect_citation_keys_from_tex,
    load_text,
    parse_bibtex_entry_keys,
    validate_bibtex_identifier_fields,
)


def test_parse_bibtex_entry_keys():
    bib = """
    @article{smith2020,
        author = "Smith",
    }
    @book{ jones_2021 ,
        author = "Jones",
    }
    """
    keys = parse_bibtex_entry_keys(bib)
    assert keys == {"smith2020", "jones_2021"}


def test_collect_citation_keys_from_tex():
    tex = r"Here is a cite \cite{smith2020} and \cite{jones_2021, adams2022}"
    keys = collect_citation_keys_from_tex(tex)
    assert keys == {"smith2020", "jones_2021", "adams2022"}


def test_validate_bibtex_identifier_fields():
    bib = """
    @article{has_doi,
        doi = {10.1234/5678},
}
    @article{missing_id,
        author = {Unknown},
}
    @book{has_isbn,
        ISBN={123-456},
}
    @misc{has_url,
        Url = {https://example.com},
}
    """
    errors = validate_bibtex_identifier_fields(bib)
    assert len(errors) == 1
    assert "missing_id: missing DOI/URL/ISBN identifier" in errors[0]


def test_load_text(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Hello", encoding="utf-8")
    assert load_text(f) == "Hello"
