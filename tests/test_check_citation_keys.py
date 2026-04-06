"""Tests for the citation-key resolution checker (scripts/check_citation_keys.py).

Verifies parser behaviour, cross-reference exclusions, and false-positive prevention.
Closes issue #2224.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

import pytest

from scripts.check_citation_keys import extract_citation_keys, parse_bib_keys

# ─── parse_bib_keys ──────────────────────────────────────────────────────────

_BIB_KEY_PATTERN = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)


def _keys_from_text(bib_text: str) -> set[str]:
    """Parse BibTeX keys from raw text (used only inside this test module)."""
    return {m.group(1).strip() for m in _BIB_KEY_PATTERN.finditer(bib_text)}


def test_parse_bib_keys_extracts_article_keys(tmp_path: Path) -> None:
    """parse_bib_keys should return the key from an @article entry."""
    bib = tmp_path / "test.bib"
    bib.write_text("@article{smith2020, title={A Title}, year={2020}}\n")
    assert parse_bib_keys(bib) == {"smith2020"}


def test_parse_bib_keys_extracts_book_keys(tmp_path: Path) -> None:
    """parse_bib_keys should return the key from an @book entry."""
    bib = tmp_path / "test.bib"
    bib.write_text("@book{jones1995intro, author={Jones}, year={1995}}\n")
    assert parse_bib_keys(bib) == {"jones1995intro"}


def test_parse_bib_keys_handles_multiple_entries(tmp_path: Path) -> None:
    """parse_bib_keys should handle multiple BibTeX entries in one file."""
    bib = tmp_path / "test.bib"
    bib.write_text(
        "@article{alpha2000, title={A}}\n"
        "@book{beta1999, author={B}}\n"
        "@inproceedings{gamma2010, title={C}}\n"
    )
    assert parse_bib_keys(bib) == {"alpha2000", "beta1999", "gamma2010"}


def test_parse_bib_keys_is_case_insensitive_for_entry_type(tmp_path: Path) -> None:
    """parse_bib_keys should be case-insensitive for the @TYPE prefix."""
    bib = tmp_path / "test.bib"
    bib.write_text("@Article{Mixed2020, title={Mixed case type}}\n")
    assert "Mixed2020" in parse_bib_keys(bib)


def test_parse_bib_keys_returns_empty_for_missing_file(tmp_path: Path) -> None:
    """parse_bib_keys should return an empty set when the file does not exist."""
    missing = tmp_path / "nonexistent.bib"
    assert parse_bib_keys(missing) == set()


# ─── extract_citation_keys ───────────────────────────────────────────────────


def test_extract_citation_keys_finds_simple_key() -> None:
    """extract_citation_keys should find a plain [@key] citation."""
    text = "As shown in [@smith2020]."
    assert extract_citation_keys(text) == {"smith2020"}


def test_extract_citation_keys_finds_multiple_keys_in_group() -> None:
    """extract_citation_keys should handle [@key1; @key2] multi-key groups."""
    text = "See [@alpha2000; @beta1999]."
    keys = extract_citation_keys(text)
    assert "alpha2000" in keys
    assert "beta1999" in keys


def test_extract_citation_keys_excludes_sec_prefix() -> None:
    """extract_citation_keys must exclude @sec- internal cross-references."""
    text = "Refer to @sec-introduction for details."
    assert not any(k.startswith("sec-") for k in extract_citation_keys(text))


def test_extract_citation_keys_excludes_eq_prefix() -> None:
    """extract_citation_keys must exclude @eq- equation cross-references."""
    text = "Equation [@eq-euler] shows this."
    assert not any(k.startswith("eq-") for k in extract_citation_keys(text))


def test_extract_citation_keys_excludes_fig_prefix() -> None:
    """extract_citation_keys must exclude @fig- figure cross-references."""
    text = "As seen in [@fig-diagram]."
    assert not any(k.startswith("fig-") for k in extract_citation_keys(text))


def test_extract_citation_keys_excludes_tbl_prefix() -> None:
    """extract_citation_keys must exclude @tbl- table cross-references."""
    text = "Values in [@tbl-results]."
    assert not any(k.startswith("tbl-") for k in extract_citation_keys(text))


def test_extract_citation_keys_excludes_ch_prefix() -> None:
    """extract_citation_keys must exclude @ch- chapter cross-references."""
    text = "See [@ch-introduction] and [@smith2020]."
    keys = extract_citation_keys(text)
    assert not any(k.startswith("ch-") for k in keys)
    assert "smith2020" in keys


def test_extract_citation_keys_excludes_colon_prefixes() -> None:
    """extract_citation_keys must exclude colon-form cross-refs like @eq:label."""
    text = "See [@eq:euler] and [@fig:diagram] but cite [@jones1999]."
    keys = extract_citation_keys(text)
    assert not any(k.startswith("eq:") for k in keys)
    assert not any(k.startswith("fig:") for k in keys)
    assert "jones1999" in keys


def test_extract_citation_keys_skips_code_blocks() -> None:
    """extract_citation_keys must not match citation-like text inside code fences."""
    text = "Text.\n\n```\n[@fake2000]\n```\n\nReal [@real2020]."
    keys = extract_citation_keys(text)
    assert "fake2000" not in keys
    assert "real2020" in keys


def test_extract_citation_keys_skips_yaml_frontmatter() -> None:
    """extract_citation_keys must ignore bibliography declarations in front-matter."""
    text = "---\ntitle: Test\nbibliography: refs.bib\n---\n\nCite [@jones1995]."
    assert extract_citation_keys(text) == {"jones1995"}


def test_extract_citation_keys_returns_empty_when_no_citations() -> None:
    """extract_citation_keys should return an empty set for plain prose."""
    text = "This paragraph has no citations at all."
    assert extract_citation_keys(text) == set()


def test_extract_citation_keys_handles_suppress_author_form() -> None:
    """extract_citation_keys should capture keys in [-@key] form."""
    text = "As noted [-@jones1995]."
    keys = extract_citation_keys(text)
    # [-@key] blocks are matched by _CITE_BLOCK_RE because it looks for [<any>@<key>]
    assert "jones1995" in keys


# ─── false-positive prevention ───────────────────────────────────────────────


def test_extract_citation_keys_no_false_positive_in_email() -> None:
    """Email addresses should not produce spurious citation keys."""
    text = "Contact user@example.com for details."
    # email is not in [...] brackets so our regex should not match it
    keys = extract_citation_keys(text)
    assert "example.com" not in keys


@pytest.mark.parametrize(
    "prefix",
    ["sec-", "eq-", "fig-", "tbl-", "ch-", "lst-", "thm-", "cor-", "def-", "exm-", "exr-"],
)
def test_all_internal_prefixes_excluded(prefix: str) -> None:
    """Every documented internal cross-reference prefix must be excluded."""
    key = f"{prefix}some-label"
    text = f"See [@{key}] for reference."
    keys = extract_citation_keys(text)
    assert not any(k.startswith(prefix) for k in keys), f"prefix {prefix!r} not excluded"


def test_extract_citation_keys_multiline_document() -> None:
    """extract_citation_keys handles a realistic multi-paragraph document."""
    text = textwrap.dedent("""\
        ---
        title: Example
        bibliography: refs.bib
        ---

        Introduction [@intro2020].

        ## Methods

        See [@methodA1999; @methodB2005] for approaches.

        ```python
        x = 1  # not a citation [@fake]
        ```

        Conclusion [@summary2021].
        """)
    keys = extract_citation_keys(text)
    assert keys == {"intro2020", "methodA1999", "methodB2005", "summary2021"}
    assert "fake" not in keys
