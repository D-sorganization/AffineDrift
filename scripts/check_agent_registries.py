#!/usr/bin/env python3
"""Validate agent convention and canonical-parameter JSON registries (#5596).

python3 -m scripts.check_agent_registries
python3 -m scripts.check_agent_registries --check
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.tools.agent_registries import (
    CONVENTIONS_PATH,
    PARAMETERS_PATH,
    validate_registry_documents,
)

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    """Run schema and semantic validation; ``--check`` is the CI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail on validation errors (default behavior; explicit for CI)",
    )
    parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        validate_registry_documents(
            conventions_payload=_load(CONVENTIONS_PATH),
            parameters_payload=_load(PARAMETERS_PATH),
            root=REPO_ROOT,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        logger.error("%s", exc)
        return 1
    logger.info(
        "agent registries valid: %s and %s",
        CONVENTIONS_PATH.relative_to(REPO_ROOT),
        PARAMETERS_PATH.relative_to(REPO_ROOT),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
