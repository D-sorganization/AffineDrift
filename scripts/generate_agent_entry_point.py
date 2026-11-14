#!/usr/bin/env python3
"""Generate or verify llms.txt and llms-full.txt from data/agent/canonical_pages.json (#5596).

python -m scripts.generate_agent_entry_point
python -m scripts.generate_agent_entry_point --check
"""

from __future__ import annotations

import argparse
import logging
import sys

from src.tools.agent_entry_point import (
    LLMS_FULL_PATH,
    LLMS_PATH,
    MANIFEST_PATH,
    load_manifest,
    render_both,
)

logger = logging.getLogger(__name__)


def _write_if_needed(path, expected: str, check: bool) -> bool:
    """Return True when content is already fresh; False when stale under --check."""
    current = path.read_text(encoding="utf-8") if path.is_file() else None
    if current == expected:
        return True
    if check:
        logger.error("%s is stale; run: python -m scripts.generate_agent_entry_point", path.name)
        return False
    path.write_text(expected, encoding="utf-8", newline="\n")
    logger.info("wrote %s", path.name)
    return True


def main(argv: list[str] | None = None) -> int:
    """Write the agent entry files, or with ``--check`` fail if any is stale."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if outputs are stale")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    llms, llms_full = render_both(manifest)
    ok = _write_if_needed(LLMS_PATH, llms, args.check)
    ok = _write_if_needed(LLMS_FULL_PATH, llms_full, args.check) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
