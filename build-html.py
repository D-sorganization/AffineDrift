#!/usr/bin/env python3
"""
Simple script to extract HTML from .qmd files and create proper HTML files.
This is a workaround for when Quarto is not available.
"""

import html
import re
from pathlib import Path


def extract_html_from_qmd(qmd_file: Path) -> tuple[str | None, str | None, str | None]:
    """Extract HTML content from a .qmd file

    Args:
        qmd_file: Path to the .qmd file to process

    Returns:
        Tuple of (title, description, html_content). Any can be None if not found.
    """
    content = qmd_file.read_text()

    # Extract YAML frontmatter
    yaml_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not yaml_match:
        return None, None, None

    yaml_content = yaml_match.group(1)

    # Extract title and description
    title_match = re.search(r'^title:\s*"([^"]+)"', yaml_content, re.MULTILINE)
    desc_match = re.search(r'^description:\s*"([^"]+)"', yaml_content, re.MULTILINE)

    title = title_match.group(1) if title_match else qmd_file.stem
    description = desc_match.group(1) if desc_match else ""

    # Extract HTML block
    html_match = re.search(r'```{=html}\s*\n(.*?)\n\s*```', content, re.DOTALL)
    if not html_match:
        return title, description, None

    html_content = html_match.group(1)
    return title, description, html_content

def create_html_page(title: str, description: str, body_html: str, output_file: Path, page_type: str = "articles", template_path: Path = Path('docs/articles.html')) -> bool:
    """Create a complete HTML page from a template

    Args:
        title: Page title
        description: Page description
        body_html: HTML content for the main body
        output_file: Path where the HTML file should be written
        page_type: Type of page ('articles', 'models', 'resources') to set correct nav active state
        template_path: Path to the HTML template file

    Returns:
        True if successful, False otherwise
    """
    # Read template from existing articles.html (but don't modify it)
    if template_path.exists():
        template = template_path.read_text()

        # Escape inputs for security
        title_escaped = html.escape(title)
        description_escaped = html.escape(description)

        # Replace title
        template = re.sub(
            r'<title>.*?</title>',
            f'<title>{title_escaped} – AffineDrift</title>',
            template
        )

        # Replace meta description
        template = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{description_escaped}">',
            template
        )

        # Fix navigation active state based on page type
        if page_type == "models":
            # Remove active state from Articles link
            template = re.sub(
                r'<a class="nav-link active" href="./articles.html" aria-current="page">',
                '<a class="nav-link" href="./articles.html">',
                template
            )
        elif page_type == "resources":
            # Remove active state from Articles link, add to Resources
            template = re.sub(
                r'<a class="nav-link active" href="./articles.html" aria-current="page">',
                '<a class="nav-link" href="./articles.html">',
                template
            )
            template = re.sub(
                r'<a class="nav-link" href="./resources.html">',
                '<a class="nav-link active" href="./resources.html" aria-current="page">',
                template
            )
        # For articles type, keep Articles as active (default)

        # Replace title block
        template = re.sub(
            r'<h1 class="title">.*?</h1>',
            f'<h1 class="title">{title_escaped}</h1>',
            template
        )

        # Replace description in page
        template = re.sub(
            r'<div class="description">\s*.*?\s*</div>',
            f'<div class="description">\n    {description_escaped}\n  </div>',
            template,
            flags=re.DOTALL
        )

        # Replace the main content
        content_pattern = r'<section class="article-section">.*?</section>'
        template = re.sub(
            content_pattern,
            body_html,
            template,
            flags=re.DOTALL
        )

        # Remove articles-specific JavaScript for non-articles pages
        if page_type != "articles":
            # Remove updateArticlesHistory function and calls
            template = re.sub(
                r'\s*function updateArticlesHistory\(\) \{.*?\}\s*',
                '',
                template,
                flags=re.DOTALL
            )
            template = re.sub(
                r'\s*updateArticlesHistory\(\);?\s*',
                '',
                template
            )

        output_file.write_text(template)
        return True

    return False

def main() -> None:
    """Main function to process all .qmd files and generate HTML pages."""
    # Find all .qmd files that need to be built
    # Note: Process articles.qmd LAST to avoid corrupting the template
    qmd_files = [
        'models.qmd',
        'models-drake.qmd',
        'models-mujoco.qmd',
        'models-myosim.qmd',
        'models-opensim.qmd',
        'models-pendulum.qmd',
        'models-pinocchio.qmd',
        'models-simulink.qmd',
        'resources-books.qmd',
        'resources-datasets.qmd',
        'resources-papers.qmd',
        'resources-researchers.qmd',
        'resources-software.qmd',
        'resources-videos.qmd',
        'resources-websites.qmd',
        'resources.qmd',
    ]

    # Process articles.qmd LAST to avoid corrupting the template
    # (articles.html is used as the template for all other pages)
    qmd_files.append('articles.qmd')

    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)

    for qmd_name in qmd_files:
        qmd_file = Path(qmd_name)
        if not qmd_file.exists():
            print(f"Warning: {qmd_name} not found")
            continue

        print(f"Processing {qmd_name}...")

        title, description, html_content = extract_html_from_qmd(qmd_file)

        if html_content is None:
            print(f"  No HTML content found in {qmd_name}")
            continue

        # Ensure title and description are strings (for mypy)
        if title is None:
            title = qmd_file.stem
        if description is None:
            description = ""

        output_file = docs_dir / qmd_file.with_suffix('.html').name

        # Determine page type for navigation active state
        if qmd_name.startswith('models'):
            page_type = "models"
        elif qmd_name.startswith('resources'):
            page_type = "resources"
        else:
            page_type = "articles"

        if create_html_page(title, description, html_content, output_file, page_type):
            print(f"  Created {output_file}")
        else:
            print(f"  Failed to create {output_file}")

if __name__ == '__main__':
    main()
