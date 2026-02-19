"""Wrap sidebar content in sticky divs for better scroll behavior.

This tool processes Quarto markdown (.qmd) files to wrap sidebar content
(left-sidebar, right-sidebar, resources-sidebar) in sticky div containers.
This enables CSS-based sticky positioning for sidebar navigation.

Usage:
    python wrap_sidebars.py

The script processes all .qmd files in the current directory.

Example:
    $ cd articles/
    $ python ../src/tools/wrap_sidebars.py

Note:
    - Files are modified in-place
    - Already-wrapped sidebars are skipped to avoid double-wrapping
    - Backup files before running if unsure
"""

import glob
from pathlib import Path

from src.tools.utils import setup_logging

logger = setup_logging(__name__, format_string="%(message)s")


def _wrap_aside_block(content: str, aside_class: str) -> str:
    """Wrap a single aside block's content in a sticky div.

    Args:
        content: Full file content.
        aside_class: CSS class of the aside element (e.g. 'left-sidebar').

    Returns:
        Modified content with the aside block wrapped.
    """
    lt = chr(60)
    gt = chr(62)
    aside_close = f"{lt}/aside{gt}"
    sticky_div_start = f'{lt}div class="sidebar-sticky-content"{gt}'
    sticky_div_end = f"{lt}/div{gt}"

    tag = f'<aside class="{aside_class}">'
    if tag not in content:
        return content

    parts = content.split(tag)
    if len(parts) <= 1:
        return content

    # Skip if already wrapped
    if parts[1].strip().startswith(sticky_div_start):
        return content
    if aside_class == "left-sidebar" and "sidebar-sticky-content" in content:
        return content

    subparts = parts[1].split(aside_close, 1)
    if len(subparts) <= 1:
        return content

    return (
        parts[0]
        + tag
        + "\n        "
        + sticky_div_start
        + subparts[0]
        + sticky_div_end
        + "\n      "
        + aside_close
        + subparts[1]
    )


def wrap_file(path: Path) -> None:
    """Wrap sidebar content in a sticky div for the given file.

    Args:
        path: Path to the .qmd file to process.

    """
    content = path.read_text()
    original_content = content

    for sidebar_class in ("left-sidebar", "right-sidebar", "resources-sidebar"):
        content = _wrap_aside_block(content, sidebar_class)

    if content != original_content:
        path.write_text(content)
        logger.info("Wrapped sidebars in %s", path)


def main() -> None:
    """Process all .qmd files in the current directory.

    Finds all Quarto markdown files and wraps their sidebar content
    in sticky div containers for improved scroll behavior.
    """
    files = glob.glob("*.qmd")
    logger.info("Found %d .qmd files to process", len(files))

    for f in files:
        wrap_file(Path(f))

    logger.info("Sidebar wrapping complete")


if __name__ == "__main__":
    main()
