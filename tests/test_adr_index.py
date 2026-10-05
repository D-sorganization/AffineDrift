"""Contract for the Architecture Decision Record directory (issue #4531).

Every ``docs/adr/NNNN-*.md`` record must be reachable from the index in
``docs/adr/README.md`` and must declare its status, so a reader can always
tell which decisions are in force.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
ADR_DIR = REPO_ROOT / "docs" / "adr"
README = ADR_DIR / "README.md"
ADR_NAME = re.compile(r"^\d{4}-[a-z0-9][a-z0-9-]*\.md$")
INDEX_HEADING = "## Index"


def _adr_files() -> list[Path]:
    """Return every numbered ADR file, sorted by name.

    Postcondition: each returned path matches ``NNNN-<slug>.md``.
    """
    files = sorted(p for p in ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md"))
    assert all(ADR_NAME.match(p.name) for p in files), files
    return files


def _index_section(readme_text: str) -> str:
    """Return the text of the README's ``## Index`` section.

    Precondition: the README contains an ``## Index`` heading.
    """
    if INDEX_HEADING not in readme_text:
        raise ValueError(f"{README} has no '{INDEX_HEADING}' section")
    after = readme_text.split(INDEX_HEADING, 1)[1]
    return re.split(r"^## ", after, maxsplit=1, flags=re.MULTILINE)[0]


def test_adr_directory_has_records() -> None:
    assert _adr_files(), "docs/adr/ must contain at least one NNNN-*.md record"


def test_numbered_adr_names_are_well_formed() -> None:
    stray = [
        p.name for p in ADR_DIR.glob("*.md") if p.name != "README.md" and not ADR_NAME.match(p.name)
    ]
    assert not stray, f"ADR files must be named NNNN-<slug>.md: {stray}"


def test_adr_numbers_are_unique() -> None:
    numbers = [p.name[:4] for p in _adr_files()]
    assert len(numbers) == len(set(numbers)), numbers


@pytest.mark.parametrize("adr", _adr_files(), ids=lambda p: p.name)
def test_adr_is_listed_in_readme_index(adr: Path) -> None:
    index = _index_section(README.read_text(encoding="utf-8"))
    assert f"]({adr.name})" in index, f"{adr.name} is missing from the README index"


@pytest.mark.parametrize("adr", _adr_files(), ids=lambda p: p.name)
def test_adr_has_status_section(adr: Path) -> None:
    text = adr.read_text(encoding="utf-8")
    match = re.search(r"^## Status\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, f"{adr.name} has no '## Status' section"
    assert match.group(1).strip(), f"{adr.name} has an empty '## Status' section"


def test_readme_index_links_resolve() -> None:
    index = _index_section(README.read_text(encoding="utf-8"))
    targets = re.findall(r"\]\(([^)]+\.md)\)", index)
    missing = [t for t in targets if not (ADR_DIR / t).is_file()]
    assert not missing, f"README index links to missing ADRs: {missing}"
