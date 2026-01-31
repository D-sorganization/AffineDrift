#!/usr/bin/env python3
"""
Deploy Assets Script
Copies critical assets (startup-launcher.js/css) to the docs/ directory.
This ensures the frontend works correctly even if Quarto build steps miss these files.
"""

import shutil
import sys
from pathlib import Path


def main():
    # Robust root detection
    root = Path(__file__).resolve().parent.parent

    src_js = root / "src/js/startup-launcher.js"
    src_css = root / "src/css/startup-launcher.css"

    docs_js_dir = root / "docs/js"
    docs_css_dir = root / "docs/css"

    # Ensure source files exist
    if not src_js.exists():
        print(f"Error: Source file {src_js} not found.")
        sys.exit(1)
    if not src_css.exists():
        print(f"Error: Source file {src_css} not found.")
        sys.exit(1)

    # Create destination directories
    docs_js_dir.mkdir(parents=True, exist_ok=True)
    docs_css_dir.mkdir(parents=True, exist_ok=True)

    dest_js = docs_js_dir / "startup-launcher.js"
    dest_css = docs_css_dir / "startup-launcher.css"

    try:
        shutil.copy2(src_js, dest_js)
        print(f"Copied {src_js} -> {dest_js}")

        shutil.copy2(src_css, dest_css)
        print(f"Copied {src_css} -> {dest_css}")

        print("Asset deployment complete.")
    except Exception as e:
        print(f"Error deploying assets: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
