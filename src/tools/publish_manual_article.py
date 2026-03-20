#!/usr/bin/env python3
"""Script to manually publish an article by converting simple Markdown to HTML.

This tool converts a simple Markdown article to HTML and wraps it in the
standard AffineDrift template. It's useful for publishing articles that
don't need full Quarto processing.

Usage:
    python publish_manual_article.py

Note:
    This script is configured for a specific article. Modify the paths
    in main() to publish different articles.
"""

import re
import sys
from pathlib import Path

# Add project root to path for imports
from src.tools.utils import (
import logging

logger = logging.getLogger(__name__)
    create_html_page,
    extract_frontmatter,
    extract_title_description,
    setup_logging,
)

logger = setup_logging(__name__)


def simple_markdown_to_html(md_text: str) -> str:
    """Convert simple Markdown to HTML.

    This is a basic converter that handles headers, lists, bold, and italics.
    For more complex Markdown, use a full parser like markdown or mistune.

    Args:
        md_text: The Markdown text to convert.

    Returns:
        HTML string.
    """
    lines = md_text.split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        line = line.strip()

        # Skip YAML frontmatter markers
        if line == "---":
            continue

        # Headers
        if line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            title = line[3:]
            anchor = title.lower().replace(" ", "-").replace(".", "")
            html_lines.append(
                f'<h2 id="{anchor}" class="anchored" data-anchor-id="{anchor}">{title}</h2>',
            )
            continue

        # Lists
        if line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = line[2:]
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
            content = re.sub(r"\*(.*?)\*", r"<em>\1</em>", content)
            html_lines.append(f"<li>{content}</li>")
            continue

        if in_list and not line.startswith("- ") and line:
            html_lines.append("</ul>")
            in_list = False

        if not line:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        # Paragraphs with inline formatting
        line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"\*(.*?)\*", r"<em>\1</em>", line)
        html_lines.append(f"<p>{line}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def wrap_in_article_section(body_html: str) -> str:
    """Wrap body HTML in the standard article section structure.

    Args:
        body_html: The article body HTML content.

    Returns:
        HTML string with the article section wrapper.
    """
    return f"""
<section class="article-section">
  <div class="container">
    <div class="standard-page-layout">
      <main class="main-content-area" style="grid-column: 2 / 4;">
        <div class="article-content">
          {body_html}
        </div>
      </main>
      <aside class="right-sidebar">
        <div class="sidebar-sticky-content">
            <nav id="TOC" role="doc-toc">
                <h3 class="sidebar-heading">On this page</h3>
                <ul>
                <!-- Manual TOC placeholder -->
                </ul>
            </nav>
        </div>
      </aside>
    </div>
  </div>
</section>
"""


def main() -> None:
    """Publish a manually-authored article."""
    qmd_path = Path("articles/intentional-constraint-collapse.qmd")
    output_path = Path("docs/articles/intentional-constraint-collapse.html")
    template_path = Path("docs/articles.html")

    if not qmd_path.exists():
        logger.error("Source file not found: %s", qmd_path)
        sys.exit(1)

    if not template_path.exists():
        logger.error("Template file not found: %s", template_path)
        sys.exit(1)

    content = qmd_path.read_text()
    template_content = template_path.read_text()

    # Extract frontmatter using shared utility
    yaml_content, body_md = extract_frontmatter(content)

    # Extract title and description using shared utility
    title, description = extract_title_description(
        yaml_content,
        default_title="Intentional Constraint Collapse at Impact",
        default_description="How Golfers Generate High Force with Stable Club Motion",
    )

    # Convert markdown to HTML and wrap in article section
    body_html = simple_markdown_to_html(body_md)
    wrapped_body = wrap_in_article_section(body_html)

    # Create HTML page using shared utility
    success = create_html_page(
        title=title,
        description=description,
        body_html=wrapped_body,
        output_file=output_path,
        template_content=template_content,
        page_type="articles",
        fix_paths=True,
        path_depth=1,
    )

    if success:
        logger.info("Published article: %s", output_path)
    else:
        logger.error("Failed to publish article: %s", output_path)
        sys.exit(1)


if __name__ == "__main__":
    main()
