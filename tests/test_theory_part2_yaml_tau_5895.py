"""Theory Part 2 key-takeaways must keep the LaTeX command \\tau (#5895).

A double-quoted YAML scalar treats ``\\t`` as a tab. The ZVCF takeaway then
renders a tab plus ``au`` instead of ``$M(q)^{-1}\\tau$``.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "articles" / "theory-part2.qmd"
LATEX_CONTROL = "$M(q)^{-1}\\tau$"


def _parsed_front_matter(page: Path) -> dict[str, object]:
    """Load the YAML front matter of ``page``.

    Preconditions: ``page`` exists and its leading ``---`` block is closed
    and loads as a mapping.
    Postcondition: the return value is that mapping.
    """
    text = page.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{page} has no YAML front matter"
    end = text.find("\n---\n", 4)
    assert end != -1, f"{page} front matter is unclosed"
    loaded = yaml.safe_load(text[4:end])
    assert isinstance(loaded, dict), "front matter must be a mapping"
    return loaded


def test_zvcf_key_takeaway_preserves_latex_tau() -> None:
    """The parsed ZVCF takeaway contains ``\\tau`` and no tab escape."""
    takeaways = _parsed_front_matter(PAGE).get("key-takeaways")
    assert isinstance(takeaways, list) and takeaways, "key-takeaways must be a list"
    zvcf_items = [item for item in takeaways if isinstance(item, str) and "ZVCF" in item]
    assert len(zvcf_items) == 1
    zvcf = zvcf_items[0]
    assert LATEX_CONTROL in zvcf
    assert "\t" not in zvcf
