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


def _split_aside_content(
    content: str,
    aside_open_tag: str,
    aside_close: str,
) -> tuple[list[str], list[str]] | None:
    """Split content on aside open/close tags.

    Returns:
        Tuple of (parts, subparts) if splitting succeeds, None if not splittable.
    """
    parts = content.split(aside_open_tag)
    if len(parts) <= 1:
        return None
    subparts = parts[1].split(aside_close, 1)
    if len(subparts) <= 1:
        return None
    return parts, subparts


def _reassemble_wrapped(
    parts: list[str],
    subparts: list[str],
    aside_open_tag: str,
    aside_close: str,
    sticky_div_start: str,
    sticky_div_end: str,
) -> str:
    """Reassemble content with the aside inner content wrapped in a sticky div."""
    return (
        parts[0] + aside_open_tag + "\n        "
        + sticky_div_start + subparts[0] + sticky_div_end
        + "\n      " + aside_close + subparts[1]
    )


def _wrap_aside(
    content: str,
    aside_open_tag: str,
    sticky_div_start: str,
    sticky_div_end: str,
    aside_close: str,
    *,
    check_already_wrapped: bool = True,
) -> str:
    """Wrap the first occurrence of an aside tag with a sticky div container.

    Args:
        content: Full HTML/QMD content string to process.
        aside_open_tag: The opening aside tag to search for.
        sticky_div_start: Opening sticky div tag string.
        sticky_div_end: Closing sticky div tag string.
        aside_close: Closing aside tag string.
        check_already_wrapped: Skip wrapping if already wrapped. Defaults to True.

    Returns:
        Updated content string, or original if tag not found or already wrapped.
    """
    if aside_open_tag not in content:
        return content
    split_result = _split_aside_content(content, aside_open_tag, aside_close)
    if split_result is None:
        return content
    parts, subparts = split_result
    if check_already_wrapped and parts[1].strip().startswith(sticky_div_start):
        return content
    return _reassemble_wrapped(
        parts, subparts, aside_open_tag, aside_close, sticky_div_start, sticky_div_end
    )


def wrap_file(path: Path) -> None:
    """Wrap sidebar content in a sticky div for the given file.

    Processes left-sidebar, right-sidebar, and resources-sidebar aside tags,
    wrapping each in a ``sidebar-sticky-content`` div container.

    Args:
        path: Path to the .qmd file to process.
    """
    content = path.read_text()
    original_content = content

    # Define tag parts to avoid lint "Angle bracket placeholder" errors
    lt = chr(60)
    gt = chr(62)
    aside_close = f"{lt}/aside{gt}"
    sticky_div_start = f'{lt}div class="sidebar-sticky-content"{gt}'
    sticky_div_end = f"{lt}/div{gt}"

    # Wrap left-sidebar (only when not already wrapped anywhere in the file)
    if "sidebar-sticky-content" not in content:
        content = _wrap_aside(
            content,
            '<aside class="left-sidebar">',
            sticky_div_start,
            sticky_div_end,
            aside_close,
            check_already_wrapped=False,
        )

    # Wrap right-sidebar and resources-sidebar on the (possibly modified) content
    content = _wrap_aside(
        content,
        '<aside class="right-sidebar">',
        sticky_div_start,
        sticky_div_end,
        aside_close,
    )
    content = _wrap_aside(
        content,
        '<aside class="resources-sidebar">',
        sticky_div_start,
        sticky_div_end,
        aside_close,
    )

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
