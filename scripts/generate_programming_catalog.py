"""CLI script to generate the Programming Companion catalog pages (ISSUE-4023).

Usage:
    python -m scripts.generate_programming_catalog [--check] [--output-dir models/programming]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.affine_control.programming_companion.catalog_generator import (
    CatalogGenerator,
    CatalogGeneratorError,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST_PATH = ROOT / "tests/fixtures/companion/manifest_v1_0_0_authoritative.json"
DEFAULT_OUTPUT_DIR = ROOT / "models/programming"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or verify Programming Companion catalog QMD pages."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help=f"Path to companion manifest JSON (default: {DEFAULT_MANIFEST_PATH})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Target output directory for QMD pages (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether existing files are up-to-date without writing changes",
    )

    args = parser.parse_args()

    if not args.manifest.exists():
        logger.error("Manifest file not found: %s", args.manifest)
        return 1

    try:
        manifest_data = json.loads(args.manifest.read_text(encoding="utf-8"))
        generator = CatalogGenerator(manifest_data)

        if args.check:
            is_clean, drifts = generator.check(args.output_dir)
            if not is_clean:
                logger.error(
                    "Programming Companion catalog is stale (%d drift(s) detected):", len(drifts)
                )
                for d in drifts:
                    logger.error("  - %s (%s)", d.path, d.reason)
                return 1
            logger.info("Programming Companion catalog is up to date in %s", args.output_dir)
            return 0

        files = generator.generate_all(args.output_dir)
        logger.info("Generated %d Programming Companion pages in %s", len(files), args.output_dir)
        return 0

    except CatalogGeneratorError as exc:
        logger.error("Catalog generation error: %s", exc)
        return 1
    except Exception as exc:
        logger.exception("Unexpected error during catalog generation: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
