#!/usr/bin/env python3
"""Generate PDFs from Tangent Hyperplane articles for NotebookLM."""

import re
from pathlib import Path

import markdown
from weasyprint import CSS, HTML

# Custom CSS for beautiful PDFs
PDF_CSS = """
@page {
    size: letter;
    margin: 1in;
    @bottom-center {
        content: counter(page);
        font-family: 'Georgia', serif;
        font-size: 10pt;
        color: #666;
    }
}

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    font-size: 24pt;
    color: #1a1a2e;
    border-bottom: 2px solid #1a1a2e;
    padding-bottom: 10px;
    margin-top: 0;
}

h2 {
    font-size: 18pt;
    color: #16213e;
    margin-top: 30px;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
}

h3 {
    font-size: 14pt;
    color: #0f3460;
    margin-top: 25px;
}

h4 {
    font-size: 12pt;
    color: #333;
    margin-top: 20px;
}

pre, code {
    font-family: 'Courier New', monospace;
    background-color: #f5f5f5;
    border-radius: 4px;
}

pre {
    padding: 15px;
    border: 1px solid #ddd;
    overflow-x: auto;
    font-size: 9pt;
}

code {
    padding: 2px 5px;
    font-size: 10pt;
}

blockquote {
    border-left: 4px solid #0f3460;
    margin-left: 0;
    padding-left: 20px;
    color: #555;
    font-style: italic;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #1a1a2e;
    color: white;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

a {
    color: #0f3460;
    text-decoration: none;
}

/* Math styling (for inline TeX that markdown might convert) */
.math {
    font-family: 'Computer Modern', serif;
}

/* Title page styling */
.title-page {
    text-align: center;
    padding-top: 200px;
}

/* Keep equations together */
.equation {
    page-break-inside: avoid;
}

/* Prevent widows/orphans */
p {
    orphans: 3;
    widows: 3;
}

/* Image styling */
img {
    max-width: 100%;
    height: auto;
}

/* Definition lists */
dt {
    font-weight: bold;
    color: #16213e;
}

dd {
    margin-left: 20px;
    margin-bottom: 10px;
}
"""


from typing import Any

def extract_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from quarto/markdown file."""
    frontmatter = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_content = parts[1]
            body = parts[2]
            # Simple YAML parsing for title/author
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter, body


def clean_qmd_to_md(content: str) -> str:
    """Clean QMD (Quarto) specific syntax to standard markdown."""
    # Remove quarto code block options like {python} #| fig-cap: "..."
    content = re.sub(r'\{[a-z]+\}.*?\n', '\n', content)
    content = re.sub(r'#\|.*?\n', '', content)

    # Convert callout blocks to blockquotes
    content = re.sub(r'::: \{\.callout-(\w+)\}', r'> **\1:**', content)
    content = re.sub(r':::', '', content)

    # Keep LaTeX math as-is for display (WeasyPrint won't render it but it's readable)
    # Wrap display math in code blocks for readability
    content = re.sub(r'\$\$(.+?)\$\$', r'```\n\1\n```', content, flags=re.DOTALL)

    return content


def md_to_html(md_content: str, title: str = "") -> str:
    """Convert markdown to HTML with proper structure."""
    md = markdown.Markdown(
        extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'toc',
            'meta',
        ]
    )

    html_body = md.convert(md_content)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
</head>
<body>
{html_body}
</body>
</html>"""

    return html


def generate_pdf(input_path: Path, output_path: Path) -> Path:
    """Generate PDF from a .qmd or .md file."""
    print(f"Processing: {input_path.name}")

    content = input_path.read_text(encoding='utf-8')

    # Extract frontmatter
    frontmatter, body = extract_frontmatter(content)
    title = frontmatter.get('title', input_path.stem)

    # Clean QMD syntax
    if input_path.suffix == '.qmd':
        body = clean_qmd_to_md(body)

    # Convert to HTML
    html_content = md_to_html(body, title)

    # Generate PDF
    html = HTML(string=html_content)
    css = CSS(string=PDF_CSS)
    html.write_pdf(output_path, stylesheets=[css])

    print(f"  ✓ Generated: {output_path.name}")
    return output_path


def main() -> list[Path]:
    """Generate PDFs for the 4-part Tangent Hyperplane series."""
    base_dir = Path(__file__).parent
    output_dir = base_dir / "PDFs_for_NotebookLM"
    output_dir.mkdir(exist_ok=True)

    # Define the 4-part series
    articles = [
        # Part 1: Core Document (Main Thesis)
        (
            base_dir / "Tangent_Hyperplanes_Unified_Thesis.qmd",
            "Part1_Tangent_Hyperplanes_Unified_Thesis.pdf",
        ),
        # Part 2: Residual-Aware Control
        (
            base_dir / "Advanced" / "Residual-Aware_Control.qmd",
            "Part2_Residual-Aware_Control.pdf",
        ),
        # Part 3: Contraction Theory Unification
        (
            base_dir / "Advanced" / "Contraction_Tangent_Unification.qmd",
            "Part3_Contraction_Theory_Unification.pdf",
        ),
        # Part 4: Hybrid Systems
        (
            base_dir / "Advanced" / "Hybrid_Tangent_Spaces.qmd",
            "Part4_Hybrid_Systems.pdf",
        ),
    ]

    # Also include supplementary materials
    supplements = [
        (base_dir / "LAYMANS_TERMS_SUMMARY.md", "Supplement_Laymans_Terms.pdf"),
        (base_dir / "TABLE_OF_CONTENTS.md", "Supplement_Table_of_Contents.pdf"),
    ]

    print("=" * 60)
    print("Generating PDFs for Tangent Hyperplane Framework")
    print("=" * 60)
    print()

    generated = []

    print("Main 4-Part Series:")
    print("-" * 40)
    for input_file, output_name in articles:
        if input_file.exists():
            output_path = output_dir / output_name
            generate_pdf(input_file, output_path)
            generated.append(output_path)
        else:
            print(f"  ⚠ Missing: {input_file.name}")

    print()
    print("Supplementary Materials:")
    print("-" * 40)
    for input_file, output_name in supplements:
        if input_file.exists():
            output_path = output_dir / output_name
            generate_pdf(input_file, output_path)
            generated.append(output_path)
        else:
            print(f"  ⚠ Missing: {input_file.name}")

    print()
    print("=" * 60)
    print(f"Generated {len(generated)} PDFs in: {output_dir}")
    print("=" * 60)

    return generated


if __name__ == "__main__":
    main()
