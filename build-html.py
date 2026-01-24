#!/usr/bin/env python3
"""Simple script to extract HTML from .qmd files and create proper HTML files.

This is a workaround for when Quarto is not available. It processes .qmd files
containing raw HTML blocks and generates proper HTML pages using a template.

Usage:
    python build-html.py

The script reads .qmd files from the current directory and generates
corresponding HTML files in the docs/ directory.
"""

import logging
import re
import subprocess
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.utils import create_html_page, extract_frontmatter, extract_title_description

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def extract_html_from_qmd(qmd_file: Path) -> tuple[str | None, str | None, str | None]:
    """Extract HTML content from a .qmd file.

    Args:
        qmd_file: Path to the .qmd file to process.

    Returns:
        Tuple of (title, description, html_content). Any can be None if not found.
    """
    content = qmd_file.read_text()

    # Extract YAML frontmatter using shared utility
    yaml_content, _ = extract_frontmatter(content)
    if yaml_content is None:
        return None, None, None

    # Extract title and description using shared utility
    title, description = extract_title_description(
        yaml_content,
        default_title=qmd_file.stem,
        default_description="",
    )

    # Extract HTML block
    html_match = re.search(r"```{=html}\s*\n(.*?)\n\s*```", content, re.DOTALL)
    if not html_match:
        return title, description, None

    html_content = html_match.group(1)
    return title, description, html_content


def main() -> None:
    """Process all .qmd files and generate HTML pages."""
    # List of .qmd files to process (articles.qmd processed last as template source)
    qmd_files = [
        "index.qmd",
        "overview.qmd",
        "about.qmd",
        "collaborate.qmd",
        "contact.qmd",
        "drifter-manifesto.qmd",
        "models.qmd",
        "models-drake.qmd",
        "models-mujoco.qmd",
        "models-myosim.qmd",
        "models-opensim.qmd",
        "models-pendulum.qmd",
        "models-pinocchio.qmd",
        "models-simulink.qmd",
        "resources-books.qmd",
        "resources-datasets.qmd",
        "resources-notebooklm.qmd",
        "resources-papers.qmd",
        "resources-researchers.qmd",
        "resources-software.qmd",
        "resources-videos.qmd",
        "resources-websites.qmd",
        "resources.qmd",
        "bibliography.qmd",
        "book-reviews.qmd",
        "research-reviews.qmd",
        "daydreams-doodles.qmd",
        "research-review-baseball-pitching.qmd",
        "research-review-induced-acceleration-analysis.qmd",
        "research-review-interaction-forces.qmd",
        "research-review-shaft-flexibility.qmd",
        "repositories.qmd",
        "repositories-2d-model.qmd",
        "repositories-3d-model.qmd",
        "repositories-drake.qmd",
        "repositories-models.qmd",
        "repositories-pinocchio.qmd",
        "articles.qmd",  # Process last (template source)
    ]

    # Generate bibliography data
    try:
        subprocess.run(
            ["python3", "scripts/generate_bibliography_data.py"],
            check=True,
        )  # noqa: S603, S607
    except subprocess.CalledProcessError as e:
        logger.warning("Failed to generate bibliography data: %s", e)

    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    # Read template once at the start
    template_path = Path("docs/articles.html")
    template_content = ""
    if template_path.exists():
        template_content = template_path.read_text()
    else:
        logger.error("Template file not found: %s", template_path)
        return

    if not template_content:
        logger.error("Template content is empty, cannot proceed")
        return

    for qmd_name in qmd_files:
        qmd_file = Path(qmd_name)
        if not qmd_file.exists():
            continue

        title, description, html_content = extract_html_from_qmd(qmd_file)

        if html_content is None:
            continue

        # Ensure title and description are strings
        title = title or qmd_file.stem
        description = description or ""

        output_file = docs_dir / qmd_file.with_suffix(".html").name

        # Determine page type for navigation active state
        if qmd_name.startswith("models"):
            page_type = "models"
        elif qmd_name.startswith("resources"):
            page_type = "resources"
        else:
            page_type = "articles"

        if create_html_page(
            title=title,
            description=description,
            body_html=html_content,
            output_file=output_file,
            template_content=template_content,
            page_type=page_type,
        ):
            logger.info("Created: %s", output_file)
        else:
            logger.warning("Failed to create: %s", output_file)


if __name__ == "__main__":
    main()
