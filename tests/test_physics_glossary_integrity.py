"""Protect the paired glossary's term coverage and resolvable definitions."""

import re
from collections import Counter
from pathlib import Path

import pytest

BOOK = Path(__file__).resolve().parents[1] / "articles" / "The_Physics_of_Golf"
WEB = BOOK / "quarto" / "glossary.qmd"
PRINT = BOOK / "chapters" / "glossary.tex"
MINIMUM_TERMS = 422  # Original unique terms plus the missing Facet Joint target.


def _entries(path: Path) -> list[tuple[str, str]]:
    """Read each canonical definition, retaining duplicates for validation."""
    pattern = (
        r"^\*\*([^*\n]+)\*\*: (.+)$" if path.suffix == ".qmd" else r"^\\item\[([^\n]+?)\] (.+)$"
    )
    return re.findall(pattern, path.read_text(encoding="utf-8"), re.MULTILINE)


@pytest.mark.parametrize("path", [WEB, PRINT])
def test_glossary_definitions_are_unique_and_aliases_resolve(path: Path) -> None:
    """Duplicate labels and circular or missing aliases defeat lookup."""
    entries = _entries(path)
    counts = Counter(term.casefold() for term, _ in entries)
    assert all(count == 1 for count in counts.values())
    assert len(counts) >= MINIMUM_TERMS
    for term, definition in entries:
        alias = re.fullmatch(r"See ([^.]+)\.", definition)
        if alias:
            target = alias[1].casefold()
            assert target in counts, (term, target)
            assert target != term.casefold(), term


def test_glossary_editions_preserve_terms_equations_and_citations() -> None:
    """Format conversion must not silently drop technical content."""
    web, printed = dict(_entries(WEB)), dict(_entries(PRINT))
    assert web.keys() == printed.keys()
    for term, definition in web.items():
        assert re.findall(r"\$(.+?)\$", definition) == re.findall(r"\$(.+?)\$", printed[term]), term
        web_keys = set(re.findall(r"@([A-Za-z0-9_-]+)", definition))
        print_keys = {
            key
            for group in re.findall(r"\\cite[pt]?\{([^}]+)\}", printed[term])
            for key in group.split(",")
        }
        assert web_keys == print_keys, term
        normalized = re.sub(
            r"\\cite[pt]?\{([^}]+)\}",
            lambda match: "[" + "; ".join("@" + key for key in match[1].split(",")) + "]",
            printed[term],
        )
        assert definition == normalized, term
