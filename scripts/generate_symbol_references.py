#!/usr/bin/env python3
"""Generate or verify data/symbol_references.json from NOTATION.md (#4584).

python -m scripts.generate_symbol_references
python -m scripts.generate_symbol_references --check
"""

from __future__ import annotations

import argparse
import logging
import sys

from src.tools.symbol_references import (
    NOTATION_PATH,
    REGISTRY_PATH,
    parse_symbol_table,
    render_registry,
)

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """Write the registry, or with ``--check`` fail if it is stale."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the registry is stale")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    expected = render_registry(parse_symbol_table(NOTATION_PATH.read_text(encoding="utf-8")))
    current = REGISTRY_PATH.read_text(encoding="utf-8") if REGISTRY_PATH.exists() else None
    if args.check:
        if current != expected:
            logger.error(
                "%s is stale; run: python -m scripts.generate_symbol_references", REGISTRY_PATH.name
            )
            return 1
        return 0
    REGISTRY_PATH.write_text(expected, encoding="utf-8", newline="\n")
    logger.info("wrote %s", REGISTRY_PATH.relative_to(NOTATION_PATH.parent).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
