#!/usr/bin/env python3
"""
Simple script to extract HTML from .qmd files and create proper HTML files.
This is a workaround for when Quarto is not available.
"""

import re
import sys
from pathlib import Path

def extract_html_from_qmd(qmd_file):
    """Extract HTML content from a .qmd file"""
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
    html_match = re.search(r'```{=html}\n(.*?)\n```', content, re.DOTALL)
    if not html_match:
        return title, description, None

    html_content = html_match.group(1)
    return title, description, html_content

def create_html_page(title, description, body_html, output_file):
    """Create a complete HTML page"""

    # Read template from existing articles.html
    template_file = Path('docs/articles.html')
    if template_file.exists():
        template = template_file.read_text()

        # Replace title
        template = re.sub(
            r'<title>.*?</title>',
            f'<title>{title} – AffineDrift</title>',
            template
        )

        # Replace meta description
        template = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{description}">',
            template
        )

        # Replace title block
        template = re.sub(
            r'<h1 class="title">.*?</h1>',
            f'<h1 class="title">{title}</h1>',
            template
        )

        # Replace description in page
        template = re.sub(
            r'<div class="description">\s*.*?\s*</div>',
            f'<div class="description">\n    {description}\n  </div>',
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

        output_file.write_text(template)
        return True

    return False

def main():
    # Find all .qmd files that need to be built
    qmd_files = [
        'models.qmd',
        'models-drake.qmd',
        'models-mujoco.qmd',
        'models-myosim.qmd',
        'models-opensim.qmd',
        'models-pendulum.qmd',
        'models-pinnochio.qmd',
        'models-simulink.qmd',
        'resources-books.qmd',
        'resources-datasets.qmd',
        'resources-papers.qmd',
        'resources-researchers.qmd',
        'resources-software.qmd',
        'resources-videos.qmd',
        'resources-websites.qmd',
    ]

    # Also rebuild articles.html
    qmd_files.insert(0, 'articles.qmd')

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

        output_file = docs_dir / qmd_file.with_suffix('.html').name

        if create_html_page(title, description, html_content, output_file):
            print(f"  Created {output_file}")
        else:
            print(f"  Failed to create {output_file}")

if __name__ == '__main__':
    main()
