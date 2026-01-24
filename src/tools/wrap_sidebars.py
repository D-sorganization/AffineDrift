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
import sys
from pathlib import Path

# Add repo root to sys.path to allow imports from src
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

from src.tools.utils import setup_logging  # noqa: E402

logger = setup_logging(__name__, format_string="%(message)s")


def wrap_file(path: Path) -> None:
    """Wrap sidebar content in a sticky div for the given file.

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

    # Wrap left-sidebar
    if '<aside class="left-sidebar">' in content:
        # Check if already wrapped to avoid double wrapping
        if "sidebar-sticky-content" not in content:
            parts = content.split('<aside class="left-sidebar">')
            if len(parts) > 1:
                # parts[1] starts with content inside aside.
                # Find the closing tag.
                subparts = parts[1].split(aside_close, 1)
                if len(subparts) > 1:
                    content = (
                        parts[0]
                        + '<aside class="left-sidebar">\n        '
                        + sticky_div_start
                        + subparts[0]
                        + sticky_div_end
                        + "\n      "
                        + aside_close
                        + subparts[1]
                    )

    # Re-process for right sidebar on the modified content
    if '<aside class="right-sidebar">' in content:
        parts = content.split('<aside class="right-sidebar">')
        if len(parts) > 1:
            # Check if immediate child is div
            if not parts[1].strip().startswith(sticky_div_start):
                subparts = parts[1].split(aside_close, 1)
                if len(subparts) > 1:
                    content = (
                        parts[0]
                        + '<aside class="right-sidebar">\n        '
                        + sticky_div_start
                        + subparts[0]
                        + sticky_div_end
                        + "\n      "
                        + aside_close
                        + subparts[1]
                    )

    # Re-process for resources-sidebar
    if '<aside class="resources-sidebar">' in content:
        parts = content.split('<aside class="resources-sidebar">')
        if len(parts) > 1 and not parts[1].strip().startswith(sticky_div_start):
            subparts = parts[1].split(aside_close, 1)
            if len(subparts) > 1:
                content = (
                    parts[0]
                    + '<aside class="resources-sidebar">\n        '
                    + sticky_div_start
                    + subparts[0]
                    + sticky_div_end
                    + "\n      "
                    + aside_close
                    + subparts[1]
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
