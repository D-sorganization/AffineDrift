"""Generate or verify the Tools repository catalog page (repositories/tools.qmd).

Consumes data/tools/tools.json (Tools repository registry) and generates
repositories/tools.qmd with governed capability tables and authority boundaries.

Usage::

    python -m scripts.generate_tools_catalog          # rewrite repositories/tools.qmd
    python -m scripts.generate_tools_catalog --check  # fail if stale
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.affine_control.programming_companion import (
    load_tools_registry,
    render_tools_qmd,
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "data" / "tools" / "tools.json"
FALLBACK_REGISTRY_PATH = REPO_ROOT.parent / "Tools" / "tools.json"
OUTPUT_PATH = REPO_ROOT / "repositories" / "tools.qmd"


def resolve_registry_path(path: Path | None = None) -> Path:
    """Resolve tools registry path."""
    target = path or (
        DEFAULT_REGISTRY_PATH if DEFAULT_REGISTRY_PATH.is_file() else FALLBACK_REGISTRY_PATH
    )
    if not target.is_file():
        raise FileNotFoundError(f"Tools registry not found at {target}")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if output differs from generated",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=None,
        help="path to tools.json",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    reg_path = resolve_registry_path(args.registry)
    registry = load_tools_registry(reg_path)
    rendered = render_tools_qmd(registry)

    if args.check:
        if not OUTPUT_PATH.is_file():
            logger.error(
                "%s does not exist; run python -m scripts.generate_tools_catalog",
                OUTPUT_PATH,
            )
            return 1
        current = OUTPUT_PATH.read_text(encoding="utf-8")
        if current != rendered:
            logger.error(
                "%s is stale; run python -m scripts.generate_tools_catalog",
                OUTPUT_PATH,
            )
            return 1
        logger.info("%s is current.", OUTPUT_PATH.relative_to(REPO_ROOT))
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    logger.info("Wrote %s", OUTPUT_PATH.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
