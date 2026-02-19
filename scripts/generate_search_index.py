#!/usr/bin/env python3
"""Generate search index for full-text article search.
Extracts content from Quarto markdown files and creates a Fuse.js compatible index.
"""

import json
import re
from datetime import datetime
from pathlib import Path

from src.tools.utils.content_utils import collect_qmd_files, read_qmd_with_frontmatter

# Files to exclude
EXCLUDE_FILES = {
    "404.qmd",
    "_quarto.yml",
}


def extract_body_text(content: str) -> str:
    """Extract plain text from markdown, removing code blocks and HTML."""
    # Remove frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]

    # Remove code blocks
    content = re.sub(r"```[\s\S]*?```", "", content)
    content = re.sub(r"`[^`]+`", "", content)

    # Remove HTML tags
    content = re.sub(r"<[^>]+>", "", content)

    # Remove markdown links but keep text
    content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)

    # Remove images
    content = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", content)

    # Remove LaTeX equations
    content = re.sub(r"\$\$[\s\S]*?\$\$", "", content)
    content = re.sub(r"\$[^$]+\$", "", content)

    # Remove special characters and normalize whitespace
    content = re.sub(r"[#*_~>\-|]", " ", content)
    content = re.sub(r"\s+", " ", content)

    return content.strip()


def extract_headings(content: str) -> list[str]:
    """Extract all headings from markdown content."""
    headings: list[str] = []
    for match in re.finditer(r"^#{1,4}\s+(.+)$", content, re.MULTILINE):
        heading = match.group(1).strip()
        # Clean up heading
        heading = re.sub(r"\{[^}]+\}", "", heading)  # Remove attributes
        heading = heading.strip()
        if heading:
            headings.append(heading)
    return headings


def extract_concepts(content: str, frontmatter: dict[str, str]) -> list[str]:
    """Extract key concepts from content and frontmatter."""
    concepts: list[str] = []

    # From frontmatter keywords/concepts if present
    if "keywords" in frontmatter:
        concepts.extend(frontmatter["keywords"].split(","))

    # Extract emphasized terms
    for match in re.finditer(r"\*\*([^*]+)\*\*", content):
        term = match.group(1).strip()
        if len(term) > 3 and len(term) < 50:
            concepts.append(term)

    # Deduplicate and clean
    concepts = list({c.strip() for c in concepts if c.strip()})
    return concepts[:20]  # Limit to 20 concepts


def process_file(filepath: Path) -> dict[str, object] | None:
    """Process a single Quarto markdown file."""
    try:
        content, frontmatter = read_qmd_with_frontmatter(filepath)
    except (OSError, UnicodeDecodeError, ValueError):
        return None

    # Skip if no title
    title = frontmatter.get("title", "")
    if not title:
        return None

    # Generate URL path
    relative_path = filepath.relative_to(Path())
    url = "/" + str(relative_path).replace(".qmd", ".html")

    # Extract content
    body_text = extract_body_text(content)
    headings = extract_headings(content)
    concepts = extract_concepts(content, frontmatter)

    # Create excerpt (first 200 chars of body)
    excerpt = body_text[:200] + "..." if len(body_text) > 200 else body_text

    return {
        "id": str(relative_path),
        "url": url,
        "title": title,
        "description": frontmatter.get("description", ""),
        "excerpt": excerpt,
        "body": body_text[:5000],  # Limit body size for index
        "headings": headings,
        "concepts": concepts,
        "type": categorize_content(str(relative_path), frontmatter),
    }


def categorize_content(path: str, frontmatter: dict[str, str]) -> str:
    """Categorize content by type."""
    if "articles/" in path:
        if "theory-part" in path:
            return "theory"
        if "bibliography" in path:
            return "reference"
        return "article"
    if "models-" in path:
        return "model"
    if "resources-" in path:
        return "resource"
    if "repositories" in path:
        return "repository"
    return "page"


def main() -> None:
    """Generate the search index."""
    index: list[dict[str, object]] = []
    processed = 0
    skipped = 0

    for filepath in collect_qmd_files():
        if filepath.name in EXCLUDE_FILES:
            continue

        entry = process_file(filepath)

        if entry:
            index.append(entry)
            processed += 1
        else:
            skipped += 1

    # Sort by type, then title
    index.sort(key=lambda x: (x["type"], x["title"]))

    # Write index
    output_path = Path("docs/data/search_index.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated": datetime.now().isoformat(),
                "count": len(index),
                "entries": index,
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    main()
