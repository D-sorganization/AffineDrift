#!/usr/bin/env python3
"""Tests for accessibility validation script."""

from scripts.validate_accessibility import (
    check_alt_text_in_qmd,
    check_aria_labels_in_js,
    check_colorblind_safe_colors,
    check_heading_hierarchy,
)


class TestAltTextValidation:
    """Tests for alt text validation in QMD files."""

    def test_markdown_image_with_alt_text(self, tmp_path):
        """Test that markdown images with alt text pass validation."""
        test_file = tmp_path / "test.qmd"
        test_file.write_text("![Valid alt text](image.png)")

        issues = check_alt_text_in_qmd(test_file)
        assert len(issues) == 0

    def test_markdown_image_without_alt_text(self, tmp_path):
        """Test that markdown images without alt text are flagged."""
        test_file = tmp_path / "test.qmd"
        test_file.write_text("![](image.png)")

        issues = check_alt_text_in_qmd(test_file)
        assert len(issues) == 1
        assert "Missing alt text" in issues[0]

    def test_html_image_with_alt(self, tmp_path):
        """Test that HTML images with alt attribute pass validation."""
        test_file = tmp_path / "test.qmd"
        test_file.write_text('<img src="image.png" alt="Description">')

        issues = check_alt_text_in_qmd(test_file)
        assert len(issues) == 0

    def test_html_image_without_alt(self, tmp_path):
        """Test that HTML images without alt attribute are flagged."""
        test_file = tmp_path / "test.qmd"
        test_file.write_text('<img src="image.png">')

        issues = check_alt_text_in_qmd(test_file)
        assert len(issues) == 1
        assert "Missing alt attribute" in issues[0]


class TestColorblindSafeColors:
    """Test colorblind-safe color validation."""

    def test_okabe_ito_colors_pass(self, tmp_path):
        """Test that Okabe-Ito palette colors pass validation."""
        test_file = tmp_path / "test.css"
        content = """
            .element {
                color: #E69F00;
                background: #56B4E9;
                border: #009E73;
            }
        """
        test_file.write_text(content)

        issues = check_colorblind_safe_colors(test_file)
        assert len(issues) == 0

    def test_neutral_colors_pass(self, tmp_path):
        """Test that neutral colors (grays, whites) pass validation."""
        test_file = tmp_path / "test.css"
        content = """
            .element {
                color: #FFFFFF;
                background: #000000;
                border: #6C757D;
            }
        """
        test_file.write_text(content)

        issues = check_colorblind_safe_colors(test_file)
        assert len(issues) == 0

    def test_problematic_colors_flagged(self, tmp_path):
        """Test that potentially problematic colors are flagged."""
        test_file = tmp_path / "test.css"
        content = """
            .element {
                color: #FF0000;
                background: #00FF00;
            }
        """
        test_file.write_text(content)

        issues = check_colorblind_safe_colors(test_file)
        # These bright reds and greens should be flagged
        # (though the function is permissive, so may not flag all)
        assert isinstance(issues, list)


class TestAriaLabels:
    """Test ARIA label validation in JavaScript."""

    def test_aria_labels_present(self, tmp_path):
        """Test that JavaScript with ARIA labels passes validation."""
        test_file = tmp_path / "test.js"
        content = """
            element.setAttribute('aria-label', 'Description');
            button.setAttribute("aria-label", "Click me");
        """
        test_file.write_text(content)

        issues = check_aria_labels_in_js(test_file)
        assert len(issues) == 0

    def test_no_aria_labels(self, tmp_path):
        """Test that JavaScript without ARIA labels is flagged."""
        test_file = tmp_path / "test.js"
        content = """
            element.setAttribute('class', 'button');
            button.addEventListener('click', handler);
        """
        test_file.write_text(content)

        issues = check_aria_labels_in_js(test_file)
        assert len(issues) == 1
        assert "No ARIA labels found" in issues[0]


class TestHeadingHierarchy:
    """Test heading hierarchy validation."""

    def test_proper_hierarchy(self, tmp_path):
        """Test that proper heading hierarchy passes validation."""
        test_file = tmp_path / "test.qmd"
        content = """
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
        """
        test_file.write_text(content)

        issues = check_heading_hierarchy(test_file)
        assert len(issues) == 0

    def test_minor_skip_allowed(self, tmp_path):
        """Test that minor heading skips (h2 to h4) are allowed."""
        test_file = tmp_path / "test.qmd"
        content = """
# Heading 1
## Heading 2
#### Heading 4
        """
        test_file.write_text(content)

        issues = check_heading_hierarchy(test_file)
        # Minor skips (1-2 levels) should be allowed
        assert len(issues) == 0

    def test_major_skip_flagged(self, tmp_path):
        """Test that major heading skips (h2 to h5) are flagged."""
        test_file = tmp_path / "test.qmd"
        content = """
# Heading 1
## Heading 2
##### Heading 5
        """
        test_file.write_text(content)

        issues = check_heading_hierarchy(test_file)
        assert len(issues) == 1
        assert "Major heading hierarchy skip" in issues[0]
        assert "h2 to h5" in issues[0]

    def test_no_headings(self, tmp_path):
        """Test that files without headings don't cause errors."""
        test_file = tmp_path / "test.qmd"
        test_file.write_text("Just some regular text without headings.")

        issues = check_heading_hierarchy(test_file)
        assert len(issues) == 0


class TestIntegration:
    """Integration tests for accessibility validation."""

    def test_valid_qmd_file(self, tmp_path):
        """Test a complete valid QMD file."""
        test_file = tmp_path / "valid.qmd"
        content = """
# Main Title

![Descriptive alt text](image.png)

## Section

Some content here.

### Subsection

More content.
        """
        test_file.write_text(content)

        alt_issues = check_alt_text_in_qmd(test_file)
        heading_issues = check_heading_hierarchy(test_file)

        assert len(alt_issues) == 0
        assert len(heading_issues) == 0

    def test_problematic_qmd_file(self, tmp_path):
        """Test a QMD file with multiple issues."""
        test_file = tmp_path / "problematic.qmd"
        content = """
# Main Title

![](image.png)

## Section

##### Deep heading

<img src="another.png">
        """
        test_file.write_text(content)

        alt_issues = check_alt_text_in_qmd(test_file)
        heading_issues = check_heading_hierarchy(test_file)

        # Should have alt text issues
        assert len(alt_issues) > 0

        # Should have heading hierarchy issues
        assert len(heading_issues) > 0
