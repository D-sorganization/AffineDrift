"""Structural guards for the development log and handoff.

Line-hunk "union" merge resolution aligns concurrent edits on shared lines
(`## Next Steps`, `- **State:** in_review`), so one pull request's heading lands
directly on top of another's entry and the fields of both get spliced together.
These tests catch the visible symptom: a heading with no body of its own, or the
same handoff section appearing twice.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_LOG = REPO_ROOT / "docs" / "development" / "DEVELOPMENT_LOG.md"
HANDOFF = REPO_ROOT / "docs" / "development" / "HANDOFF.md"
# Deliberate group dividers (#4437) that introduce the H1 checkpoints below them.
HANDOFF_DIVIDERS = frozenset({"# Previous Checkpoints"})


def _prose_lines(path: Path) -> list[tuple[int, str]]:
    """Return (line number, text) pairs outside fenced code blocks."""
    lines: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append((number, line))
    return lines


def _heading_level(text: str) -> int:
    """Markdown ATX heading level of `text`, or 0 when it is not a heading."""
    hashes = len(text) - len(text.lstrip("#"))
    return hashes if 0 < hashes <= 6 and text[hashes : hashes + 1] == " " else 0


def _headings_without_body(
    path: Path, prefix: str, exempt: frozenset[str] = frozenset()
) -> list[str]:
    """Headings starting with `prefix` followed directly by a same-or-higher-level heading."""
    lines = [(n, text) for n, text in _prose_lines(path) if text.strip()]
    stacked = []
    for (number, text), (_, following) in zip(lines, lines[1:], strict=False):
        level = _heading_level(following)
        if text.startswith(prefix) and text not in exempt and 0 < level <= _heading_level(text):
            stacked.append(f"line {number}: {text!r} is followed by {following!r}")
    return stacked


def test_development_log_entries_have_bodies() -> None:
    assert _headings_without_body(DEVELOPMENT_LOG, "### DL-#") == []


def test_handoff_h1_sections_have_bodies() -> None:
    assert _headings_without_body(HANDOFF, "# ", HANDOFF_DIVIDERS) == []


def test_handoff_h1_titles_are_unique() -> None:
    titles = Counter(text for _, text in _prose_lines(HANDOFF) if text.startswith("# "))
    assert [title for title, count in titles.items() if count > 1] == []
