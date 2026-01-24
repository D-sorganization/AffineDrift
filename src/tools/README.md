# AffineDrift Tools Directory

This directory contains utility tools and interactive simulators for the AffineDrift project.

## Quick Reference

| Tool                       | Purpose                                      | Usage                                           |
| -------------------------- | -------------------------------------------- | ----------------------------------------------- |
| `check_links.py`           | Extract and validate links from HTML files   | `python check_links.py file.html`               |
| `check_site_health.py`     | Verify internal links and generate sitemap   | `python check_site_health.py`                   |
| `clean_latex_comments.py`  | Remove LaTeX comments from QMD files         | `python clean_latex_comments.py file.qmd`       |
| `code_quality_check.py`    | Run code quality checks                      | `python code_quality_check.py`                  |
| `convert_all_latex.py`     | Batch convert LaTeX to HTML                  | `python convert_all_latex.py input_dir/`        |
| `convert_all_to_quarto.py` | Batch convert LaTeX to Quarto                | `python convert_all_to_quarto.py`               |
| `fix_quarto_syntax.py`     | Fix common Quarto syntax issues              | `python fix_quarto_syntax.py file.qmd`          |
| `latex_to_html.py`         | Convert LaTeX document to HTML               | `python latex_to_html.py input.tex output.html` |
| `latex_to_qmd.py`          | Convert LaTeX to Quarto markdown             | `python latex_to_qmd.py input.tex`              |
| `latex_to_quarto.py`       | Alternative LaTeX converter                  | `python latex_to_quarto.py input.tex`           |
| `publish_manual_article.py`| Convert Markdown to HTML with templates      | `python publish_manual_article.py`              |
| `update_navigation.py`     | Update navigation across HTML files          | `python update_navigation.py`                   |
| `verify_images.py`         | Validate image URLs in HTML                  | `python verify_images.py file.html`             |
| `wrap_sidebars.py`         | Wrap sidebar content in sticky divs          | `python wrap_sidebars.py`                       |

## Tool Categories

### Content Conversion Tools

Tools for converting between document formats:

#### `latex_to_qmd.py`

Convert LaTeX documents to Quarto markdown format.

```bash
python latex_to_qmd.py input.tex
# Creates: input.qmd
```

**Features:**

- Preserves math equations
- Converts LaTeX environments to Quarto equivalents
- Handles bibliography references

#### `latex_to_html.py`

Convert LaTeX documents directly to HTML.

```bash
python latex_to_html.py input.tex output.html
```

#### `convert_all_latex.py` / `convert_all_to_quarto.py`

Batch conversion for multiple files.

```bash
# Convert all .tex files in a directory
python convert_all_latex.py articles/latex/
```

See [CONVERSION_GUIDE.md](CONVERSION_GUIDE.md) for detailed conversion documentation.

### Quality Assurance Tools

Tools for checking and fixing content quality:

#### `check_links.py`

Extract and validate links from HTML files.

```bash
python check_links.py docs/articles/my-article.html
# Outputs: List of all links and their status
```

#### `check_site_health.py`

Comprehensive site health check - validates internal links and generates sitemap.

```bash
python check_site_health.py
# Checks all HTML files in docs/ directory
```

#### `verify_images.py`

Validate that all image URLs in HTML files resolve correctly.

```bash
python verify_images.py docs/index.html
# Reports: broken images, missing alt text
```

#### `code_quality_check.py`

Run code quality checks on Python files.

```bash
python code_quality_check.py
# Checks: style, type hints, docstrings
```

### Content Processing Tools

Tools for processing and fixing content:

#### `clean_latex_comments.py`

Remove LaTeX-style comments from Quarto files.

```bash
python clean_latex_comments.py article.qmd
# Removes: % comments and \comment{} blocks
```

#### `fix_quarto_syntax.py`

Fix common Quarto markdown syntax issues.

```bash
python fix_quarto_syntax.py article.qmd
# Fixes: callout syntax, code block formatting
```

#### `wrap_sidebars.py`

Wrap sidebar content in sticky div containers for improved scroll behavior.

```bash
cd articles/
python ../src/tools/wrap_sidebars.py
# Processes all .qmd files in current directory
```

### Build & Navigation Tools

#### `update_navigation.py`

Update navigation elements across all HTML files for consistency.

```bash
python update_navigation.py
# Updates: navbar, sidebar links, breadcrumbs
```

#### `publish_manual_article.py`

Convert Markdown articles to HTML using project templates.

```bash
python publish_manual_article.py --input article.md --output docs/articles/
```

## Interactive Tools

### `wrist_universal_joint/`

**Grip Angle Torque Transmission Simulator**

Interactive tool for analyzing how grip angle affects torque transmission in golf swing biomechanics.

**Files:**

- `grip_angle_simulator.html` - Standalone JavaScript/HTML5 version
- `Grip_Angle_Torque_Transmission_Streamlit.py` - Streamlit web app
- `requirements.txt` - Python dependencies
- `EMBEDDING_GUIDE.md` - Embedding instructions
- `README.md` - Tool documentation

**Related Article:** [Wrists Behave as Universal Joints](../../articles/wrist-universal-joint.qmd)

### `matlab_code_analyzer_gui/`

Interactive MATLAB GUI for code analysis and quality checks.

See [matlab_code_analyzer_gui/README.md](matlab_code_analyzer_gui/README.md).

### `matlab_utilities/`

Collection of MATLAB utility functions for quality checking and testing.

See [matlab_utilities/README.md](matlab_utilities/README.md).

## Adding New Tools

When adding a new tool:

1. **Create the tool** with proper structure:

   ```python
   """Tool description and usage.

   Usage:
       python my_tool.py [options]

   Example:
       python my_tool.py --input file.txt
   """

   import logging
   from pathlib import Path

   logger = logging.getLogger(__name__)

   def main() -> None:
       """Main entry point."""
       # Implementation

   if __name__ == "__main__":
       main()
   ```

2. **Add docstrings** following Google style:

   ```python
   def process_file(path: Path, options: dict) -> bool:
       """Process a single file.

       Args:
           path: Path to the file to process.
           options: Processing options dictionary.

       Returns:
           True if processing succeeded, False otherwise.

       Raises:
           FileNotFoundError: If path doesn't exist.
       """
   ```

3. **Update this README** with:
   - Entry in Quick Reference table
   - Usage examples
   - Category placement

4. **Add tests** in `tests/test_<tool_name>.py`

## Development Guidelines

- **NO `print()` statements** - Use `logging` module
- **Type hints required** for all functions
- **Docstrings required** (Google style)
- **Test coverage** for new tools
- Run `ruff check` and `ruff format` before committing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for full guidelines.

## CI/CD Integration

Tools are validated as part of the repository CI/CD pipeline:

- Python syntax and linting checks
- Type checking with mypy
- HTML validation for interactive tools
- Unit tests execution

See `.github/workflows/ci-standard.yml` for details.
