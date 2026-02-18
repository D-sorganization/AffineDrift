#!/usr/bin/env python3
"""
Deploy Assets Script
Copies critical assets (startup-launcher.js/css) to the docs/ directory.
This ensures the frontend works correctly even if Quarto build steps miss these files.
"""

import logging
import shutil
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def main():
    """Run the deploy assets script."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Robust root detection
    root = Path(__file__).resolve().parent.parent

    src_js = root / "src/js/startup-launcher.js"
    src_css = root / "src/css/startup-launcher.css"

    docs_js_dir = root / "docs/js"
    docs_css_dir = root / "docs/css"

    # Ensure source files exist
    if not src_js.exists():
        logger.error("Error: Source file %s not found.", src_js)
        sys.exit(1)
    if not src_css.exists():
        logger.error("Error: Source file %s not found.", src_css)
        sys.exit(1)

    # Create destination directories
    docs_js_dir.mkdir(parents=True, exist_ok=True)
    docs_css_dir.mkdir(parents=True, exist_ok=True)

    dest_js = docs_js_dir / "startup-launcher.js"
    dest_css = docs_css_dir / "startup-launcher.css"

    try:
        shutil.copy2(src_js, dest_js)
        logger.info("Copied %s -> %s", src_js, dest_js)

        shutil.copy2(src_css, dest_css)
        logger.info("Copied %s -> %s", src_css, dest_css)

        logger.info("Asset deployment complete.")
    except Exception as e:
        logger.error("Error deploying assets: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
