#!/usr/bin/env python3
"""Tests for SEO audit script."""

import pytest

from scripts.seo_audit import (
    check_heading_hierarchy,
    check_images,
    extract_first_paragraph,
)
from src.tools.utils import parse_frontmatter_dict


class TestFrontmatterExtraction:
    """Test YAML frontmatter extraction."""

    def test_extract_title_and_description(self):
        """Test extracting title and description from frontmatter."""
        content = (
            '---\ntitle: "Test Page"\ndescription: "A test description"\n---\n\nContent here.\n'
        )
        frontmatter = parse_frontmatter_dict(content)

        assert frontmatter["title"] == "Test Page"
        assert frontmatter["description"] == "A test description"

    @pytest.mark.parametrize(
        "content",
        [
            "Just regular content without frontmatter.",
            "---\n---\n\nContent here.\n",
        ],
        ids=["no-frontmatter", "empty-frontmatter"],
    )
    def test_no_or_empty_frontmatter(self, content: str):
        """Test that content without or with empty frontmatter returns nothing."""
        frontmatter = parse_frontmatter_dict(content)
        assert len(frontmatter) == 0


class TestFirstParagraphExtraction:
    """Test first paragraph extraction for descriptions."""

    def test_extract_simple_paragraph(self):
        """Test extracting a simple first paragraph."""
        content = """---
title: Test
---

This is the first paragraph with enough content to be extracted properly.

This is the second paragraph.
"""
        paragraph = extract_first_paragraph(content)

        assert "first paragraph" in paragraph
        assert len(paragraph) > 0

    def test_skip_headings(self):
        """Test that headings are skipped."""
        content = """# Title

## Subtitle

This is the first real paragraph with sufficient content for extraction.
"""
        paragraph = extract_first_paragraph(content)

        assert "first real paragraph" in paragraph

    def test_no_paragraph(self):
        """Test content without paragraphs."""
        content = "# Just a heading"

        paragraph = extract_first_paragraph(content)

        assert paragraph == ""

    def test_short_paragraph_skipped(self):
        """Test that short paragraphs are skipped."""
        content = """---
title: Test
---

Short.

This is a longer paragraph with enough content to be extracted as a description.
"""
        paragraph = extract_first_paragraph(content)

        assert "longer paragraph" in paragraph
        assert "Short" not in paragraph


class TestHeadingHierarchyCheck:
    """Test heading hierarchy checking."""

    def test_proper_hierarchy(self):
        """Test proper heading hierarchy."""
        content = """# H1
## H2
### H3
"""
        issues = check_heading_hierarchy(content)

        assert len(issues) == 0

    def test_skip_level(self):
        """Test skipped heading level."""
        content = """# H1
### H3
"""
        issues = check_heading_hierarchy(content)

        assert len(issues) == 1
        assert "skip" in issues[0].lower()

    def test_multiple_h1(self):
        """Test multiple H1 headings."""
        content = """# First H1
## H2
# Second H1
"""
        issues = check_heading_hierarchy(content)

        assert len(issues) == 1
        assert "multiple" in issues[0].lower() or "h1" in issues[0].lower()


class TestImageCheck:
    """Test image alt text checking."""

    def test_images_with_alt(self):
        """Test images with alt text."""
        content = """
![Alt text](image.png)
![Another alt](image2.png)
"""
        issues = check_images(content)

        assert len(issues) == 0

    def test_images_without_alt(self):
        """Test images without alt text."""
        content = """
![](image.png)
![](image2.png)
"""
        issues = check_images(content)

        assert len(issues) == 2
        assert all("missing alt text" in issue.lower() for issue in issues)

    def test_mixed_images(self):
        """Test mix of images with and without alt text."""
        content = """
![Good alt](image1.png)
![](image2.png)
![Another good alt](image3.png)
"""
        issues = check_images(content)

        assert len(issues) == 1
        assert "image2.png" in issues[0]


class TestIntegration:
    """Integration tests for SEO audit."""

    def test_complete_valid_file(self):
        """Test a complete valid file."""
        content = """---
title: "Complete Page"
description: "A complete description"
---

# Main Heading

This is the first paragraph with good content.

![Descriptive alt text](image.png)

## Subheading

More content here.
"""
        frontmatter = parse_frontmatter_dict(content)
        heading_issues = check_heading_hierarchy(content)
        image_issues = check_images(content)

        assert frontmatter["title"] == "Complete Page"
        assert len(heading_issues) == 0
        assert len(image_issues) == 0

    def test_file_with_issues(self):
        """Test a file with multiple SEO issues."""
        content = """---
title: "Page Without Description"
---

# First H1

### Skipped H2

![](missing-alt.png)

# Second H1
"""
        frontmatter = parse_frontmatter_dict(content)
        heading_issues = check_heading_hierarchy(content)
        image_issues = check_images(content)

        # Missing description
        assert "description" not in frontmatter

        # Heading hierarchy issues
        assert len(heading_issues) > 0

        # Image alt text issues
        assert len(image_issues) > 0
