"""Regenerate resources/resources-datasets.qmd from data/datasets.yml (WEB-07.7, #4549).

Usage:
    python3 -m scripts.generate_datasets_catalog [--check]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.tools.datasets_catalog import DatasetCatalogError, load_catalog, render_updated_qmd

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "data/datasets.yml"
QMD_PATH = ROOT / "resources/resources-datasets.qmd"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """Regenerate or check the datasets catalog page; return a process exit code."""
    parser = argparse.ArgumentParser(description="Regenerate the datasets catalog page.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if regeneration would change the page, without writing it",
    )
    args = parser.parse_args(argv)

    try:
        catalog = load_catalog(CATALOG_PATH)
        updated = render_updated_qmd(QMD_PATH, catalog, ROOT)
    except DatasetCatalogError as exc:
        logger.error("Dataset catalog error: %s", exc)
        return 1

    current = QMD_PATH.read_text(encoding="utf-8")
    if updated == current:
        logger.info("Datasets catalog is up to date in %s", QMD_PATH)
        return 0
    if args.check:
        logger.error(
            "Datasets catalog is stale; run `python3 -m scripts.generate_datasets_catalog`."
        )
        return 1
    QMD_PATH.write_text(updated, encoding="utf-8")
    logger.info("Regenerated %s", QMD_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
