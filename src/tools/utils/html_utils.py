"""HTML template manipulation utilities.

This module provides functions for manipulating HTML templates,
specifically for the AffineDrift site generation workflow.

Example:
    from src.tools.utils import create_html_page

    success = create_html_page(
        title="My Article",
        description="Article description",
        body_html="<p>Content here</p>",
        output_file=Path("docs/my-article.html"),
        template_content=template,
    )
"""

from __future__ import annotations

import html
import logging
import re
from pathlib import Path

from src.core.contracts import require

from .constants import PATH_REPLACEMENT_PATTERNS

logger = logging.getLogger(__name__)


def escape_html(text: str) -> str:
    """Escape HTML special characters in text.

    Args:
        text: The text to escape.

    Returns:
        HTML-escaped text.
    """
    return html.escape(text)


def update_metadata(template: str, title: str, description: str) -> str:
    """Update HTML metadata (title tag and meta description).

    Args:
        template: The HTML template string.
        title: The page title.
        description: The page description.

    Returns:
        Template with updated metadata.
    """
    title_escaped = escape_html(title)
    description_escaped = escape_html(description)

    # Replace title tag
    template = re.sub(
        r"<title>.*?</title>",
        f"<title>{title_escaped} – AffineDrift</title>",
        template,
    )

    # Replace meta description
    template = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{description_escaped}">',
        template,
    )

    return template


def update_title_block(template: str, title: str, description: str) -> str:
    """Update the visible title and description blocks in the page.

    Args:
        template: The HTML template string.
        title: The page title.
        description: The page description.

    Returns:
        Template with updated title blocks.
    """
    title_escaped = escape_html(title)
    description_escaped = escape_html(description)

    # Replace h1 title
    template = re.sub(
        r'<h1 class="title">.*?</h1>',
        f'<h1 class="title">{title_escaped}</h1>',
        template,
    )

    # Replace description div
    template = re.sub(
        r'<div class="description">\s*.*?\s*</div>',
        f'<div class="description">\n    {description_escaped}\n  </div>',
        template,
        flags=re.DOTALL,
    )

    return template


def replace_content_section(template: str, body_html: str) -> str:
    """Replace the main content section with new HTML content.

    Args:
        template: The HTML template string.
        body_html: The new HTML content for the main section.

    Returns:
        Template with replaced content section.
    """
    content_pattern = r'<section class="article-section.*?">.*?</section>'
    # Use lambda to avoid backslash escaping issues in body_html
    template = re.sub(
        content_pattern,
        lambda _: body_html,
        template,
        flags=re.DOTALL,
    )
    return template


def remove_articles_scripts(template: str) -> str:
    """Remove articles-specific JavaScript from template.

    Used when generating non-articles pages that don't need
    the updateArticlesHistory function.

    Args:
        template: The HTML template string.

    Returns:
        Template with articles scripts removed.
    """
    # Remove updateArticlesHistory function
    template = re.sub(
        r"\s*function updateArticlesHistory\(\) \{.*?\}\s*",
        "",
        template,
        flags=re.DOTALL,
    )
    # Remove function calls
    template = re.sub(r"\s*updateArticlesHistory\(\);?\s*", "", template)
    return template


def fix_relative_paths(template: str, depth: int = 1) -> str:
    """Fix relative paths for pages in subdirectories.

    Args:
        template: The HTML template string.
        depth: Number of directory levels deep (1 = articles/, 2 = articles/sub/).

    Returns:
        Template with corrected relative paths.
    """
    prefix = "../" * depth

    # Apply all path replacements from centralized patterns
    for old_pattern, new_pattern in PATH_REPLACEMENT_PATTERNS:
        template = template.replace(old_pattern, new_pattern.format(prefix=prefix))

    return template


def _apply_template_transforms(
    template: str,
    title: str,
    description: str,
    body_html: str,
    page_type: str,
    fix_paths: bool,
    path_depth: int,
) -> str:
    """Apply all template transformation steps in sequence.

    Returns the fully transformed template string.
    """
    template = update_metadata(template, title, description)
    if fix_paths:
        template = fix_relative_paths(template, path_depth)
    template = update_title_block(template, title, description)
    template = replace_content_section(template, body_html)
    if page_type != "articles":
        template = remove_articles_scripts(template)
    return template


def create_html_page(
    title: str,
    description: str,
    body_html: str,
    output_file: Path,
    template_content: str,
    page_type: str = "articles",
    fix_paths: bool = False,
    path_depth: int = 1,
) -> bool:
    """Create a complete HTML page from a template.

    Handles metadata updates, content replacement, and path fixes.

    Args:
        title: Page title.
        description: Page description.
        body_html: HTML content for the main body.
        output_file: Path where the HTML file should be written.
        template_content: The HTML template string.
        page_type: Type of page ('articles', 'models', 'resources').
        fix_paths: Whether to fix relative paths for subdirectories.
        path_depth: Directory depth for path fixes.

    Returns:
        True if successful, False otherwise.
    """
    require(len(title) > 0, "page title must not be empty")
    require(output_file is not None, "output_file must not be None")
    if not template_content:
        return False
    rendered = _apply_template_transforms(
        template_content, title, description, body_html, page_type, fix_paths, path_depth
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(rendered)
    return True
