#!/usr/bin/env python3
"""Check Quarto render rules and sitemap/source coverage."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import yaml
from defusedxml import ElementTree as ET

logger = logging.getLogger(__name__)
SITEMAP_NAMESPACE = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def load_render_rules(quarto_config: Path) -> list[str]:
    """Load the configured Quarto render rules."""
    data = yaml.safe_load(quarto_config.read_text(encoding="utf-8"))
    render_rules = data.get("project", {}).get("render", [])
    if not isinstance(render_rules, list):
        raise ValueError("project.render is not a list")
    return render_rules


def sitemap_loc_to_source_path(loc: str, repo_root: Path) -> Path:
    """Map a sitemap URL to the expected Quarto source path."""
    prefix = "https://affinedrift.com"
    if not loc.startswith(prefix):
        raise ValueError(f"Unexpected sitemap host: {loc}")

    relative = loc.removeprefix(prefix).lstrip("/")
    if not relative:
        return repo_root / "index.qmd"

    if relative.endswith("/"):
        return repo_root / relative.rstrip("/") / "index.qmd"

    source = Path(relative)
    if source.suffix == ".html":
        qmd_cand = repo_root / source.with_suffix(".qmd")
        if qmd_cand.exists():
            return qmd_cand
        md_cand = repo_root / source.with_suffix(".md")
        if md_cand.exists():
            return md_cand
        return qmd_cand
    return repo_root / source / "index.qmd"


def load_sitemap_paths(sitemap_path: Path) -> list[str]:
    """Return all sitemap <loc> URLs."""
    root = ET.fromstring(sitemap_path.read_text(encoding="utf-8"))
    return [
        loc.text.strip()
        for loc in root.findall("sm:url/sm:loc", SITEMAP_NAMESPACE)
        if loc.text and loc.text.strip()
    ]


def find_missing_sitemap_sources(
    sitemap_locs: list[str], repo_root: Path
) -> list[tuple[str, Path]]:
    """Return sitemap URLs whose expected source files do not exist."""
    missing: list[tuple[str, Path]] = []
    for loc in sitemap_locs:
        source_path = sitemap_loc_to_source_path(loc, repo_root)
        if not source_path.exists():
            missing.append((loc, source_path))
    return missing


def find_unindexed_sources(sitemap_locs: list[str], repo_root: Path) -> list[Path]:
    """Return published source files that are missing from the sitemap."""
    indexed_paths = {sitemap_loc_to_source_path(loc, repo_root).resolve() for loc in sitemap_locs}
    from src.tools.utils.content_utils import collect_qmd_files

    dirs = [
        ".",
        "articles",
        "books",
        "critiques",
        "models",
        "pages",
        "repositories",
        "resources",
    ]
    content_files = collect_qmd_files(dirs)
    unindexed: list[Path] = []
    for rel_path in content_files:
        full_path = (repo_root / rel_path).resolve()
        if full_path.name in ["404.qmd", "offline.qmd"]:
            continue
        if full_path not in indexed_paths:
            unindexed.append(rel_path)
    return unindexed


def main() -> int:
    """Verify Quarto render rules cover all required patterns."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    repo_root = Path(__file__).resolve().parent.parent
    quarto_config = repo_root / "_quarto.yml"
    render_rules = load_render_rules(quarto_config)

    required_rules = {"*.qmd", "articles/**/*.qmd", "pages/**/*.qmd", "resources/**/*.qmd"}
    missing = [rule for rule in required_rules if rule not in render_rules]
    if missing:
        logger.error("Missing required render rules:")
        for rule in missing:
            logger.error("- %s", rule)
        return 1

    logger.info("Quarto render coverage check passed.")
    logger.info("Render rules:")
    for rule in render_rules:
        logger.info("- %s", rule)

    sitemap_path = repo_root / "sitemap.xml"
    sitemap_locs = load_sitemap_paths(sitemap_path)
    missing_sources = find_missing_sitemap_sources(sitemap_locs, repo_root)
    if missing_sources:
        logger.error("Sitemap URLs missing source pages:")
        for loc, source_path in missing_sources:
            logger.error("- %s -> %s", loc, source_path.relative_to(repo_root))
        return 1

    unindexed_sources = find_unindexed_sources(sitemap_locs, repo_root)
    if unindexed_sources:
        logger.error("Published source pages missing from sitemap:")
        for source_path in unindexed_sources:
            logger.error("- %s", source_path)
        return 1

    logger.info(
        "Bidirectional sitemap/source coverage check passed for %d URLs.", len(sitemap_locs)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
