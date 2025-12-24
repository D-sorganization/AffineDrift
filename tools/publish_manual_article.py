#!/usr/bin/env python3
"""
Script to manually publish an article by converting simple Markdown to HTML
and wrapping it in the standard template.
"""

import html
import re
import sys
from pathlib import Path


def simple_markdown_to_html(md_text: str) -> str:
    """
    Very basic Markdown to HTML converter for specific article structure.
    """
    lines = md_text.split("\n")
    html_lines = []

    in_list = False

    for line in lines:
        line = line.strip()

        # Skip YAML frontmatter (handled separately)
        if line == "---":
            continue

        # Headers
        if line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            title = line[3:]
            # Extract section number if present
            anchor = title.lower().replace(" ", "-").replace(".", "")
            html_lines.append(
                f'<h2 id="{anchor}" class="anchored" data-anchor-id="{anchor}">{title}</h2>'
            )
            continue

        # Lists
        if line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = line[2:]
            # Bold
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
            # Italics
            content = re.sub(r"\*(.*?)\*", r"<em>\1</em>", content)
            html_lines.append(f"<li>{content}</li>")
            continue

        if in_list and not line.startswith("- ") and line:
            # Assume end of list
            html_lines.append("</ul>")
            in_list = False

        if not line:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        # Paragraphs
        # Wrap in <p> if not empty and not header

        # Bold
        line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
        # Italics
        line = re.sub(r"\*(.*?)\*", r"<em>\1</em>", line)

        # Math (MathJax handles \( \) and \[ \], we just pass them through)

        html_lines.append(f"<p>{line}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def create_html_page(
    title: str,
    description: str,
    body_html: str,
    output_file: Path,
    page_type: str = "articles",
    template_path: Path = Path("docs/articles.html"),
) -> bool:
    """Create a complete HTML page from a template"""
    if template_path.exists():
        template = template_path.read_text()

        title_escaped = html.escape(title)
        description_escaped = html.escape(description)

        # Update metadata
        template = re.sub(
            r"<title>.*?</title>", f"<title>{title_escaped} – AffineDrift</title>", template
        )

        template = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{description_escaped}">',
            template,
        )

        # FIX PATHS for subdirectory
        # 1. ./ prefixes
        template = template.replace('href="./', 'href="../')
        template = template.replace('src="./', 'src="../')

        # 2. site_libs (usually no prefix)
        template = template.replace('src="site_libs/', 'src="../site_libs/')
        template = template.replace('href="site_libs/', 'href="../site_libs/')

        # 3. specific assets
        template = template.replace('src="script.js"', 'src="../script.js"')
        template = template.replace('href="styles.css"', 'href="../styles.css"')
        template = template.replace('src="logo/', 'src="../logo/')

        # 4. other root links that might be bare
        template = template.replace('href="index.html"', 'href="../index.html"')
        template = template.replace('href="about.html"', 'href="../about.html"')
        template = template.replace('href="feed.xml"', 'href="../feed.xml"')
        template = template.replace('href="favicon.ico"', 'href="../favicon.ico"')

        # 5. Fix the self-reference to articles.html (which became ../articles.html)
        # Ensure the 'Articles' nav link is active
        # The template has <a class="nav-link active" ...> or similar.
        # We just need to make sure links to other pages are correct.

        # Replace title block
        template = re.sub(
            r'<h1 class="title">.*?</h1>', f'<h1 class="title">{title_escaped}</h1>', template
        )

        # Replace description in page
        template = re.sub(
            r'<div class="description">\s*.*?\s*</div>',
            f'<div class="description">\n    {description_escaped}\n  </div>',
            template,
            flags=re.DOTALL,
        )

        # Wrap body in the container structure
        full_body = f"""
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
        content_pattern = r'<section class="article-section">.*?</section>'
        template = re.sub(content_pattern, lambda _: full_body, template, flags=re.DOTALL)

        if page_type != "articles":
            template = re.sub(
                r"\s*function updateArticlesHistory\(\) \{.*?\}\s*", "", template, flags=re.DOTALL
            )
            template = re.sub(r"\s*updateArticlesHistory\(\);?\s*", "", template)

        output_file.write_text(template)
        return True
    return False


def main() -> None:
    """Main execution function to publish the article."""
    qmd_path = Path("articles/intentional-constraint-collapse.qmd")
    output_path = Path("docs/articles/intentional-constraint-collapse.html")

    if not qmd_path.exists():
        print(f"Error: {qmd_path} not found")
        sys.exit(1)

    content = qmd_path.read_text()

    # Extract frontmatter
    yaml_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    title = "Intentional Constraint Collapse at Impact"
    description = "How Golfers Generate High Force with Stable Club Motion"

    if yaml_match:
        yaml_content = yaml_match.group(1)
        t_match = re.search(r'^title:\s*"([^"]+)"', yaml_content, re.MULTILINE)
        if t_match:
            title = t_match.group(1)

        body_md = content[yaml_match.end():]
    else:
        body_md = content

    body_html = simple_markdown_to_html(body_md)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    success = create_html_page(title, description, body_html, output_path)
    if success:
        print(f"Successfully created {output_path}")
    else:
        print("Failed to create HTML page")


if __name__ == "__main__":
    main()
