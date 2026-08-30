#!/usr/bin/env python3
"""CLI entrypoint to generate or verify reader comprehension and findability study artifacts."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.affine_control.reader_validation.generator import (
    generate_reader_validation_study,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    """CLI main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that generated study artifacts are up to date without writing changes.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    try:
        data_path, part_path = generate_reader_validation_study(
            check=args.check, repo_root=repo_root
        )
        if args.check:
            logger.info(
                "Reader validation artifacts are up to date: %s, %s",
                data_path,
                part_path,
            )
        else:
            logger.info(
                "Generated reader validation artifacts: %s, %s",
                data_path,
                part_path,
            )
        return 0
    except Exception as exc:
        logger.error("Reader validation study generation failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
