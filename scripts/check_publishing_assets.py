#!/usr/bin/env python3
"""CLI wrapper for publishing assets verification."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.tools.check_publishing_assets import main  # noqa: E402 -- reason: sys.path modified above

if __name__ == "__main__":
    sys.exit(main())
