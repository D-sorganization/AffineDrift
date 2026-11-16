"""Regression coverage for code fences shared by Quarto prose lints."""

from pathlib import Path

import pytest

from scripts.check_citation_resolution import collect_citation_keys
from scripts.check_qmd_citation_keys import extract_citation_keys
from scripts.scan_quarto_syntax import _find_raw_theorem_environments


@pytest.mark.parametrize("extract", [collect_citation_keys, extract_citation_keys])
@pytest.mark.parametrize(
    "block",
    [
        "~~~python\n@decorator\n~~~\n",
        "````markdown\n```python\n@decorator\n```\n````\n",
        "~~~~latex\n~~~\n@decorator\n~~~~~\n",
        "~~~latex\n```\n@decorator\n~~~\n",
        "~~~python\n~~~not-a-close\n@decorator\n~~~\n",
        "~~~python\n@decorator\n",
    ],
)
def test_citation_lints_ignore_complete_fenced_region(extract, block: str) -> None:
    assert extract("Cite @before.\n" + block + "\n") == {"before"}


@pytest.mark.parametrize("marker", ["~~~", "````"])
def test_raw_theorem_lint_ignores_fences_preserving_line_numbers(marker: str) -> None:
    text = f"{marker}latex\n\\begin{{theorem}}\n```\n{marker}\n\\begin{{theorem}}\n"
    issues = _find_raw_theorem_environments(Path("example.qmd"), text)
    assert [issue[0] for issue in issues] == [5]


@pytest.mark.parametrize("marker", ["~~~", "````"])
@pytest.mark.parametrize("extract", [collect_citation_keys, extract_citation_keys])
def test_citations_resume_after_matching_longer_closer(extract, marker: str) -> None:
    text = f"{marker}python\n@hidden\n{marker[0] * (len(marker) + 1)}\nCite @visible."
    assert extract(text) == {"visible"}


def test_fence_stripping_preserves_crlf_and_prose_boundaries() -> None:
    from scripts.quarto_fences import strip_fenced_code

    text = "before\r\n~~~python\r\n@hidden\r\n~~~~\r\nafter"
    assert strip_fenced_code(text) == "before\r\n\r\n\r\n\r\nafter"


def test_fence_stripping_rejects_non_text() -> None:
    from scripts.quarto_fences import strip_fenced_code

    with pytest.raises(TypeError, match="text must be a string"):
        strip_fenced_code(None)
