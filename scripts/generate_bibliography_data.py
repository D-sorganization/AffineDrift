#!/usr/bin/env python3
"""Generate bibliography data from markdown YAML blocks.

This script extracts bibliography entries from markdown files containing
YAML code blocks and generates JSON data for the website's bibliography
and citation features.

Usage:
    python generate_bibliography_data.py

Output:
    Creates bibliography.json with extracted citation data.
"""

import json
import re
from pathlib import Path
from typing import Any

import yaml

from src.tools.utils import setup_logging

logger = setup_logging(__name__)


def extract_yaml_from_markdown(file_path: Path) -> list[dict[str, Any]]:
    """Extracts YAML content from a markdown file's code block."""
    try:
        content = file_path.read_text()
        # Look for ```yaml ... ``` blocks
        # We assume the largest yaml block or the one explicitly under Bibliography is what we want.
        # But simply finding all yaml blocks and trying to parse them as list of dicts with 'id' is safer.

        matches = re.findall(r"```yaml\n(.*?)\n```", content, re.DOTALL)

        extracted_items: list[dict[str, Any]] = []
        for match in matches:
            try:
                data = yaml.safe_load(match)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "id" in item:
                            extracted_items.append(item)
            except yaml.YAMLError as e:
                logger.warning("YAML parse error in %s: %s", file_path, e)
                continue

        return extracted_items
    except (OSError, UnicodeDecodeError) as e:
        logger.error("Error extracting YAML from %s: %s", file_path, e)
        return []


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    """Normalizes keys to match what the frontend expects."""
    if "scholar_link" in item and "scholar_url" not in item:
        item["scholar_url"] = item["scholar_link"]
        del item["scholar_link"]

    # Ensure arrays
    if "authors" in item and isinstance(item["authors"], str):
        item["authors"] = [item["authors"]]
    if "concepts" in item and isinstance(item["concepts"], str):
        item["concepts"] = [item["concepts"]]

    return item


def _load_base_bibliography(all_refs: dict[str, dict[str, Any]]) -> None:
    """Load base bibliography.yaml into all_refs."""
    base_bib_path = Path("data/bibliography.yaml")
    if not base_bib_path.exists():
        return
    try:
        with open(base_bib_path) as f:
            base_data = yaml.safe_load(f)
            if base_data:
                for item in base_data:
                    if "id" in item:
                        all_refs[item["id"]] = normalize_item(item)
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as e:
        logger.error("Error loading base bibliography: %s", e)


def _load_article_bibliographies(all_refs: dict[str, dict[str, Any]]) -> None:
    """Load bibliographies from articles/ directory."""
    articles_dir = Path("articles")
    if not articles_dir.exists():
        return
    for md_file in articles_dir.glob("*-bibliography.md"):
        items = extract_yaml_from_markdown(md_file)
        for item in items:
            norm_item = normalize_item(item)
            if norm_item["id"] not in all_refs:
                all_refs[norm_item["id"]] = norm_item
            else:
                _merge_reference(all_refs[norm_item["id"]], norm_item)


def _merge_reference(existing: dict[str, Any], new: dict[str, Any]) -> None:
    """Merge missing fields from new into existing reference."""
    for k, v in new.items():
        if k not in existing or not existing[k]:
            existing[k] = v


def _process_reading_paths(output_dir: Path) -> None:
    """Process reading_paths.yaml into JSON."""
    paths_source = Path("data/reading_paths.yaml")
    paths_output = output_dir / "reading_paths.json"
    if not paths_source.exists():
        return
    try:
        with open(paths_source) as f:
            paths_data = yaml.safe_load(f)
        with open(paths_output, "w") as f:
            json.dump(paths_data, f, indent=2)
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as e:
        logger.error("Error processing reading paths: %s", e)


def main() -> None:
    """Generate JSON data for the interactive bibliography from YAML sources.
    Reads 'data/bibliography.yaml' and 'articles/*-bibliography.md',
    and converts them to JSON in 'docs/data'.
    """
    output_dir = Path("docs/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_refs: dict[str, dict[str, Any]] = {}
    _load_base_bibliography(all_refs)
    _load_article_bibliographies(all_refs)

    # Convert to list and sort
    final_refs = list(all_refs.values())
    final_refs.sort(key=lambda x: (-int(x.get("year", 0)), x.get("title", "")))

    # Write bibliography.json
    bib_output_path = output_dir / "bibliography.json"
    with open(bib_output_path, "w") as f:
        json.dump(final_refs, f, indent=2)

    _process_reading_paths(output_dir)


if __name__ == "__main__":
    main()
