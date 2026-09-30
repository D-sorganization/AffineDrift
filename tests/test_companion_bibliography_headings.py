"""The rendered companion bibliographies keep a single H1 (#4548).

Quarto renders the front-matter ``title`` as the page's H1, so a body ``#``
heading gives the page a second visible H1, which the public-site
verification's axe pass rejects.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BIBLIOGRAPHIES = sorted((ROOT / "articles").glob("*-bibliography.md"))
FENCE = re.compile(r"^(```|~~~)")


def body_h1_lines(text: str) -> list[str]:
    """Return the level-one ATX headings outside fenced code blocks."""
    in_fence = False
    headings = []
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence and re.match(r"^# ", line):
            headings.append(line)
    return headings


@pytest.mark.unit
def test_bibliographies_exist() -> None:
    assert len(BIBLIOGRAPHIES) >= 22


@pytest.mark.unit
@pytest.mark.parametrize("path", BIBLIOGRAPHIES, ids=lambda p: p.name)
def test_bibliography_has_no_body_h1(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n") and "\ntitle:" in text.split("\n---\n", 1)[0]
    assert body_h1_lines(text) == []
