"""Common styling constants and utilities for Core Theory figures."""

from __future__ import annotations

from pathlib import Path

# Common styling palette
PRIMARY_BLUE = "#17608a"
ACCENT_ORANGE = "#a34716"
SAGE_GREEN = "#2a7f62"
SLATE_GRAY = "#5c6773"
LIGHT_BG = "#f4f7f9"
GRID_COLOR = "#d8e1e8"
TEXT_COLOR = "#22252a"


def _clean_svg(path: Path) -> None:
    """Normalize line endings and strip trailing whitespace for deterministic diffs."""
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(cleaned, encoding="utf-8", newline="\n")
