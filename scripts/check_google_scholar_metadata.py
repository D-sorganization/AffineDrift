#!/usr/bin/env python3
"""Google Scholar citation metadata and BibTeX validator (WEB-07.2 #4544).

Validates that rendered HTML files adhere to Google Scholar indexing requirements
and AffineDrift publication date verification contracts:
1. Every article emits `citation_title` and `citation_author`.
2. `citation_publication_date` is emitted ONLY for owner-verified publication dates
   (date-source: initial-publication-record).
3. Unverified articles (`date-source: unverified` or unverified date) omit
   `citation_publication_date` and contain no `NaN` placeholders.
4. BibTeX download links and `.bib` files are present for citable articles.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

META_TAG_PATTERN = re.compile(
    r'<meta\s+name="([^"]+)"\s+content="([^"]*)"\s*/?>',
    re.IGNORECASE,
)

DATE_REGEX = re.compile(r"^\d{4}(?:-\d{2}-\d{2})?$")


def extract_citation_meta(html_text: str) -> dict[str, list[str]]:
    """Extract all citation_* meta tags from an HTML string into a dictionary."""
    tags: dict[str, list[str]] = {}
    for match in META_TAG_PATTERN.finditer(html_text):
        name = match.group(1).lower()
        if name.startswith("citation_"):
            val = match.group(2)
            tags.setdefault(name, []).append(val)
    return tags


def validate_page_metadata(
    html_path: Path,
    expected_verified_date: str | None = None,
    is_unverified: bool = False,
    require_citation: bool = True,
) -> list[str]:
    """Validate Google Scholar and citation metadata for a single HTML file.

    Parameters
    ----------
    html_path : Path
        Path to the rendered HTML file.
    expected_verified_date : str | None
        Expected verified publication date in YYYY-MM-DD format, or None.
    is_unverified : bool
        True if the page date is unverified and citation_publication_date must be omitted.
    require_citation : bool
        True if citation tags and BibTeX are expected on this page.

    Returns
    -------
    list[str]
        List of error messages describing failed assertions (empty if valid).
    """
    errors: list[str] = []
    if not html_path.is_file():
        return [f"File not found: {html_path}"]

    try:
        content = html_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = html_path.read_text(encoding="utf-8-sig")

    meta = extract_citation_meta(content)

    # Check for forbidden NaN meta values
    for name, vals in meta.items():
        for val in vals:
            if "NaN" in val:
                errors.append(f"{html_path.name}: Meta tag {name} contains NaN value '{val}'")

    if not require_citation:
        return errors

    # 1. citation_title must exist and be non-empty
    titles = meta.get("citation_title", [])
    if not titles or not titles[0].strip():
        errors.append(f"{html_path.name}: Missing or empty citation_title")

    # 2. citation_author must exist
    authors = meta.get("citation_author", [])
    if not authors or not any(a.strip() for a in authors):
        errors.append(f"{html_path.name}: Missing citation_author")

    # 3. Publication date contracts
    pub_dates = meta.get("citation_publication_date", [])
    if is_unverified:
        if pub_dates:
            errors.append(
                f"{html_path.name}: Unverified article must not emit citation_publication_date (got {pub_dates})"
            )
    else:
        if expected_verified_date:
            if not pub_dates:
                errors.append(
                    f"{html_path.name}: Expected verified publication date '{expected_verified_date}' but citation_publication_date is absent"
                )
            elif pub_dates[0] != expected_verified_date:
                errors.append(
                    f"{html_path.name}: citation_publication_date '{pub_dates[0]}' does not match expected '{expected_verified_date}'"
                )
        elif pub_dates:
            for d in pub_dates:
                if not DATE_REGEX.match(d):
                    errors.append(
                        f"{html_path.name}: citation_publication_date '{d}' does not match valid date format (YYYY-MM-DD)"
                    )

    # 4. BibTeX download check
    if "quarto-appendix-bibtex" in content:
        if "quarto-citation-bibtex-download" not in content:
            errors.append(f"{html_path.name}: Missing BibTeX download link in citation appendix")

        bib_file = html_path.with_suffix(".bib")
        if not bib_file.is_file():
            errors.append(f"{html_path.name}: Matching .bib file does not exist ({bib_file.name})")
        else:
            bib_text = bib_file.read_text(encoding="utf-8")
            if not bib_text.strip().startswith("@"):
                errors.append(
                    f"{html_path.name}: Generated .bib file does not start with '@' entry"
                )

    return errors


def main() -> int:
    """CLI runner to validate Google Scholar metadata across sample pages or directory."""
    parser = argparse.ArgumentParser(
        description="Validate Google Scholar metadata on rendered HTML pages."
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Specific HTML files to validate",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("_site"),
        help="Path to directory containing rendered HTML (defaults to _site)",
    )
    args = parser.parse_args()

    files_to_check = args.files
    if not files_to_check:
        if args.docs_dir.is_dir():
            files_to_check = list(args.docs_dir.glob("articles/*.html"))
        else:
            logger.error("No files specified and output directory '%s' not found.", args.docs_dir)
            return 1

    total_errors: list[str] = []
    for f in files_to_check:
        errs = validate_page_metadata(f)
        total_errors.extend(errs)

    if total_errors:
        for err in total_errors:
            logger.error(err)
        return 1

    logger.info(
        "All checked pages (%d) passed Google Scholar metadata verification.", len(files_to_check)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
