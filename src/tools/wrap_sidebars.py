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
import logging
from pathlib import Path

from src.tools.utils import setup_logging

logger = logging.getLogger(__name__)

logger = setup_logging(__name__, format_string="%(message)s")

# Build tag strings from character codes to avoid lint "Angle bracket placeholder" errors
_LT = chr(60)
_GT = chr(62)
_ASIDE_CLOSE = f"{_LT}/aside{_GT}"
_STICKY_DIV_START = f'{_LT}div class="sidebar-sticky-content"{_GT}'
_STICKY_DIV_END = f"{_LT}/div{_GT}"


def _wrap_aside(content: str, aside_class: str, *, check_already_wrapped: bool = True) -> str:
    """Wrap a single named aside element with a sticky-content div.

    Args:
        content: Full file content string.
        aside_class: CSS class of the aside tag to wrap (e.g. 'left-sidebar').
        check_already_wrapped: If True, skip when sticky div already present.

    Returns:
        Updated content string, or original if tag not found / already wrapped.
    """
    aside_open = f'<aside class="{aside_class}">'
    if aside_open not in content:
        return content
    parts = content.split(aside_open)
    if len(parts) < 2:
        return content
    if check_already_wrapped and parts[1].strip().startswith(_STICKY_DIV_START):
        return content
    subparts = parts[1].split(_ASIDE_CLOSE, 1)
    if len(subparts) < 2:
        return content
    return (
        parts[0]
        + aside_open
        + "\n        "
        + _STICKY_DIV_START
        + subparts[0]
        + _STICKY_DIV_END
        + "\n      "
        + _ASIDE_CLOSE
        + subparts[1]
    )


def wrap_file(path: Path) -> None:
    """Wrap sidebar content in a sticky div for the given file.

    Args:
        path: Path to the .qmd file to process.

    """
    content = path.read_text()
    original_content = content

    # Left-sidebar: only wrap if no sticky content present anywhere in file yet
    if "sidebar-sticky-content" not in content:
        content = _wrap_aside(content, "left-sidebar", check_already_wrapped=False)

    # Right and resources sidebars: check per-aside whether already wrapped
    content = _wrap_aside(content, "right-sidebar")
    content = _wrap_aside(content, "resources-sidebar")

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
