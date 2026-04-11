"""Compatibility entrypoint for the packaged mypy autofix agent.

The GitHub autofix workflow and older local callers invoke this script path
directly. Keep it as a thin wrapper while the implementation lives in
``scripts.mypy_autofix``.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _main() -> int:
    """Run the packaged entrypoint after making the repo root importable."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.mypy_autofix.__main__ import main

    return main()


if __name__ == "__main__":
    sys.exit(_main())
