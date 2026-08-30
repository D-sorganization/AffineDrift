#!/usr/bin/env python3
"""CLI entrypoint to generate or verify reader-facing evidence presentation registry and partials."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.affine_control.evidence_presentation.generator import generate_evidence_presentation

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    """CLI main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that generated artifacts are up to date without writing changes.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    try:
        reg_path, part_path = generate_evidence_presentation(check=args.check, repo_root=repo_root)
        if args.check:
            logger.info(
                "Evidence presentation artifacts are up to date: %s, %s", reg_path, part_path
            )
        else:
            logger.info("Generated evidence presentation artifacts: %s, %s", reg_path, part_path)
        return 0
    except Exception as exc:
        logger.error("Evidence presentation generation failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
