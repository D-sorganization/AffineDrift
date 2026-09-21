#!/usr/bin/env python3
"""Insert On this site bridge callouts into Physics of Golf chapters."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

CONFIG = Path("config/physics_of_golf_chapter_bridges.yml")
CHAPTER_DIR = Path("articles/The_Physics_of_Golf/quarto")
EXERCISE_PATTERN = re.compile(r"^## Chapter Exercises", re.MULTILINE)
RELATED_PATTERN = re.compile(r"^## Related Articles\s*\n(?:Continue with .+\n)?", re.MULTILINE)


def render_block(links: list[dict[str, str]]) -> str:
    """Render the canonical On this site callout for a chapter."""
    lines = ["::: {.callout-note}", "## On This Site", ""]
    for link in links:
        lines.append(f'- **[{link["title"]}]({link["href"]})** — {link["blurb"]}')
    lines.append(":::")
    return "\n".join(lines) + "\n\n"


def main() -> None:
    """Apply bridge callouts from the curated config."""
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    for fname, links in config.items():
        path = CHAPTER_DIR / fname
        text = path.read_text(encoding="utf-8")
        if "## On This Site" in text:
            continue
        block = render_block(links)
        text = RELATED_PATTERN.sub("", text)
        match = EXERCISE_PATTERN.search(text)
        if match:
            text = text[: match.start()] + block + text[match.start() :]
        else:
            text = text.rstrip() + "\n\n" + block
        path.write_text(text, encoding="utf-8")
        print(f"updated {fname}")


if __name__ == "__main__":
    main()
