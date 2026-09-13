"""Exercise the companion's chapter boundaries in Pandoc's actual document tree."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts/filters/companion-hierarchy.lua"
WRAPPER = ROOT / "articles/proximal-distal-a-journey-through-the-swing.qmd"


def _pandoc(source: str, *, filtered: bool) -> dict[str, Any]:
    """Parse real Markdown and optionally apply the production Lua filter."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto/Pandoc is required for the document-tree integration check")
    command = [quarto, "pandoc", "--from=markdown", "--to=json"]
    if filtered:
        command.extend(["--lua-filter", str(FILTER)])
    result = subprocess.run(
        command, input=source, text=True, encoding="utf-8", capture_output=True, check=True
    )
    return json.loads(result.stdout)


def _headers(document: dict[str, Any]) -> list[list[Any]]:
    """Read top-level headers while preserving Pandoc's identifiers and text."""
    return [block["c"] for block in document["blocks"] if block["t"] == "Header"]


@pytest.mark.integration
def test_real_companion_has_thirty_chapters_and_preserves_content_and_ids() -> None:
    source = WRAPPER.read_text(encoding="utf-8")
    for included in re.findall(r"\{\{< include ([^>]+) >\}\}", source):
        source = source.replace(
            "{{< include " + included + " >}}",
            (WRAPPER.parent / included).read_text(encoding="utf-8"),
        )
    before = _pandoc(source, filtered=False)
    after = _pandoc(source, filtered=True)
    originals, headings = _headers(before), _headers(after)
    assert len(originals) == len(headings)
    chapters = [header for header in headings if re.fullmatch(r"sec-lay-ch\d{2}", header[1][0])]
    assert [header[1][0] for header in chapters] == [f"sec-lay-ch{i:02d}" for i in range(1, 31)]
    assert all(header[0] == 2 for header in chapters)
    inside_chapter = False
    for original, heading in zip(originals, headings, strict=True):
        identifier = original[1][0]
        if re.fullmatch(r"sec-lay-ch\d{2}", identifier):
            inside_chapter = True
            assert heading == original
        elif identifier in {"glossary", "references"}:
            inside_chapter = False
            assert heading == original
        else:
            assert heading[0] == original[0] + int(inside_chapter)
            assert heading[1:] == original[1:]
    # The filter must not rewrite scientific prose, links, math, or other blocks.
    for original, changed in zip(before["blocks"], after["blocks"], strict=True):
        if original["t"] != "Header":
            assert changed == original


@pytest.mark.integration
def test_unrelated_headings_and_back_matter_are_not_demoted() -> None:
    source = """## Introduction {.unnumbered}
## Chapter {#sec-lay-ch01}
## Picture {#old-picture-anchor}
### Detail {#old-detail-anchor}
## Glossary {.unnumbered}
### Term
"""
    headings = _headers(_pandoc(source, filtered=True))
    assert [header[0] for header in headings] == [2, 2, 3, 4, 2, 3]
    assert headings[2][1][0] == "old-picture-anchor"
