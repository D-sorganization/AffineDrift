"""Generate search-maturity.json: a page href -> maturity badge lookup.

Quarto's local search index (search.json) is built from rendered page text
and carries no custom front matter fields, so it cannot show the maturity
badge that scripts/filters/page-header-card.lua renders on the page itself.
This script scans the same `status`/`maturity` front matter and writes a
small JSON map that js/search-maturity-badge.js fetches client-side to
annotate matching search results with the same badge.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from src.tools.utils import setup_logging
from src.tools.utils.content_utils import collect_qmd_files, read_qmd_with_frontmatter

logger = setup_logging(__name__)

# Mirrors generate_sitemap.py's SITEMAP_CONTENT_DIRS: any rendered content
# page can carry a maturity badge.
SEARCH_MATURITY_CONTENT_DIRS = [
    ".",
    "articles",
    "books",
    "critiques",
    "models",
    "pages",
    "repositories",
    "resources",
]


def variant_from_status(status: str) -> str:
    """Derive a `.badge--<variant>` CSS class suffix from a status string.

    Must match scripts/filters/page-header-card.lua's derivation
    (`status_str:lower():gsub("%s+", "-"):gsub("[^%w%-]", "")`) so a page's
    header badge and its search-result badge always agree.
    """
    dashed = re.sub(r"\s+", "-", status.strip().lower())
    return re.sub(r"[^a-z0-9-]", "", dashed)


def qmd_path_to_url_path(filepath: Path) -> str:
    """Convert a QMD path to its rendered site URL path (mirrors generate_sitemap.py)."""
    url_path = filepath.with_suffix(".html").as_posix()
    if url_path == "index.html":
        return ""
    return url_path


DEFAULT_OUTPUT = "data/search-maturity.json"


def build_index(content_dirs: list[str]) -> dict[str, dict[str, str]]:
    """Map each page's URL path to its maturity badge label and CSS variant."""
    index: dict[str, dict[str, str]] = {}
    for filepath in collect_qmd_files(content_dirs):
        _content, frontmatter = read_qmd_with_frontmatter(filepath)
        status = frontmatter.get("status") or frontmatter.get("maturity")
        if not status:
            continue
        status_str = str(status).strip()
        if not status_str:
            continue
        index[qmd_path_to_url_path(filepath)] = {
            "label": status_str,
            "variant": variant_from_status(status_str),
        }
    return index


def main() -> None:
    """Generate search-maturity.json."""
    parser = argparse.ArgumentParser(
        description="Generate search-maturity.json for search result maturity badges"
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output path for the generated index (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the committed index differs from a fresh generation",
    )
    args = parser.parse_args()

    rendered = render_index(build_index(SEARCH_MATURITY_CONTENT_DIRS))
    output_path = Path(args.output)
    if args.check:
        current = output_path.read_text(encoding="utf-8") if output_path.is_file() else None
        if current != rendered:
            raise SystemExit(
                f"{output_path} is stale; run python -m scripts.generate_search_maturity_index"
            )
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(rendered.encode("utf-8"))
    logger.info("Wrote %s", output_path)


def render_index(index: dict[str, dict[str, str]]) -> str:
    """Serialize the index deterministically (sorted keys, LF, trailing newline)."""
    return json.dumps(index, indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    main()
