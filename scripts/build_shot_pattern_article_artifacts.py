"""Regenerate shot-pattern article tables from vendored upstream summary data."""

from __future__ import annotations

import logging
from pathlib import Path

from src.tools.shot_pattern_article.summary import build_article_summary

LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "articles/shot_pattern_analysis/data"
TABLE_MD = DATA_DIR / "scoring_table.md"
EXCLUSION_MD = DATA_DIR / "exclusion_rates.md"


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not (DATA_DIR / "headline_paired_sg.csv").is_file():
        raise SystemExit(f"missing dataset: {DATA_DIR / 'headline_paired_sg.csv'}")
    summary = build_article_summary(DATA_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_MD.write_text(summary["markdown_table"], encoding="utf-8")
    EXCLUSION_MD.write_text(summary["exclusion_markdown"], encoding="utf-8")
    LOGGER.info(
        "Wrote %s and %s",
        TABLE_MD.relative_to(ROOT),
        EXCLUSION_MD.relative_to(ROOT),
    )


if __name__ == "__main__":
    main()
