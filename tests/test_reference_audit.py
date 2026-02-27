"""Tests for bibliography and citation traceability checks."""

from __future__ import annotations

from src.tools.reference_audit import (
    collect_citation_keys_from_tex,
    parse_bibtex_entry_keys,
    validate_bibtex_identifier_fields,
)


def test_parse_bibtex_entry_keys_extracts_ids() -> None:
    """BibTeX parser should extract citation keys from entry headers."""
    bib_text = """
@article{slotine1987,
  title = {On Slotine},
}
@book{lynch2017,
  title = {Modern Robotics},
}
"""
    assert parse_bibtex_entry_keys(bib_text) == {"slotine1987", "lynch2017"}


def test_collect_citation_keys_from_tex_handles_multi_key_cites() -> None:
    """TeX citation parser should expand comma-delimited key groups."""
    tex = r"""
As shown in \cite{slotine1987,lynch2017} and \citep{astolfi2009}.
"""
    assert collect_citation_keys_from_tex(tex) == {"slotine1987", "lynch2017", "astolfi2009"}


def test_validate_bibtex_identifier_fields_requires_doi_or_url_or_isbn() -> None:
    """Each BibTeX entry should include a stable external identifier."""
    bib_text = """
@article{valid_ref,
  title = {A Valid Ref},
  doi = {10.1109/9.12345}
}
@book{missing_ids,
  title = {No Identifiers Here}
}
"""
    errors = validate_bibtex_identifier_fields(bib_text)
    assert errors == ["missing_ids: missing DOI/URL/ISBN identifier"]
