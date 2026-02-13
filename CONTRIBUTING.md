# Contributing to AffineDrift

Thank you for your interest in contributing to AffineDrift! This document provides guidelines for contributing to the project.

## Ways to Contribute

1. **Report Issues**: Found a typo, broken link, or bug? [Open an issue](https://github.com/D-sorganization/AffineDrift/issues)

2. **Suggest Resources**: Know a great video, paper, or tool related to affine control theory or golf biomechanics? Let us know!

3. **Improve Documentation**: Help make guides clearer for beginners

4. **Fix Bugs**: Submit pull requests for any issues you find

5. **Enhance Content**: Suggest improvements to explanations or add new sections

## Getting Started

### Prerequisites

- **Git** - Version control
- **Python 3.8+** - For build scripts and tools
- **Quarto** - Static site generator ([Install Quarto](https://quarto.org/docs/get-started/))
- **Node.js** (optional) - For JavaScript linting and testing

### Initial Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/AffineDrift.git
   cd AffineDrift
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Quarto installation**:
   ```bash
   quarto check
   ```

5. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Workflow

1. **Make your changes** to `.qmd` files (Quarto markdown)
2. **Preview locally**:
   ```bash
   quarto preview
   ```
3. **Run quality checks**:
   ```bash
   # Python linting
   ruff check .
   ruff format .
   
   # Type checking
   mypy .
   
   # Run tests
   pytest
   ```
4. **Build the site**:
   ```bash
   quarto render
   ```
5. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   git push origin feature/your-feature-name
   ```
6. **Open a pull request** on GitHub

## Code Guidelines

### Quarto Markdown (.qmd)

Quarto files are the source for all content pages.

**Structure:**
```yaml
---
title: "Your Article Title"
author: "Your Name"
date: "2026-01-22"
description: "Brief description for SEO"
categories: [category1, category2]
---

## Introduction

Your content here...
```

**Best Practices:**
- Use YAML frontmatter for metadata
- Include `description` for SEO
- Add `categories` for organization
- Use proper heading hierarchy (h2, h3, h4)
- Include alt text for images: `![Description](image.png)`
- Cite sources using bibliography references

**Math Equations:**
- Inline: `$E = mc^2$`
- Display: `$$\frac{a}{b}$$`
- Use LaTeX syntax for equations

**Code Blocks:**
````markdown
```python
def example():
    return "Hello"
```
````

### Python

Follow PEP 8 and project-specific standards in [AGENTS.md](AGENTS.md):

- **NO `print()` statements** - Use `logging` module
- **Type hints** for all functions
- **Docstrings** (Google or NumPy style)
- **No wildcard imports** (`from module import *`)
- **Specific exception handling** (no bare `except:`)

**Example:**
```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def process_file(file_path: Path) -> dict[str, str]:
    """
    Process a file and return results.
    
    Args:
        file_path: Path to the file to process
        
    Returns:
        Dictionary containing processing results
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    logger.info(f"Processing {file_path}")
    # Implementation
    return {"status": "success"}
```

### HTML

- Use semantic HTML5 elements (`<article>`, `<section>`, `<nav>`)
- Maintain consistent indentation (2 spaces)
- Add comments for complex sections
- Ensure accessibility (alt text, ARIA labels, semantic markup)
- Validate with `html-validate` (configured in `.htmlvalidate.json`)

### CSS

- Use existing CSS variables for colors (defined in `custom.scss`)
- Follow BEM naming convention for new classes
- Keep specificity low (avoid `!important`)
- Add comments for non-obvious styles
- Test responsive behavior (mobile-first approach)
- Use `stylelint` for linting

**Example:**
```css
/* Component: Article Card */
.article-card {
  /* Block */
}

.article-card__title {
  /* Element */
}

.article-card--featured {
  /* Modifier */
}
```

### JavaScript

- Use ES6+ features (arrow functions, `const`/`let`, template literals)
- **NO `var`** - Use `const` by default, `let` if reassignment needed
- Add JSDoc comments for functions
- Avoid global variables
- Use strict equality (`===`, `!==`)
- Test in multiple browsers
- Follow patterns in existing `script.js`

**Example:**
```javascript
/**
 * Scrolls to a specific element with offset
 * @param {string} elementId - ID of target element
 * @param {number} offset - Scroll offset in pixels
 */
const scrollToElement = (elementId, offset = 140) => {
  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`Element ${elementId} not found`);
    return;
  }
  
  const position = element.getBoundingClientRect().top + window.scrollY - offset;
  window.scrollTo({ top: position, behavior: 'smooth' });
};
```

### Content Writing

- Use clear, accessible language
- Explain technical terms on first use
- Maintain consistent tone (professional but approachable)
- Check spelling and grammar
- Cite sources appropriately
- Include "Layman's Terms" sections for complex topics
- Add "Critics Corner" for addressing potential objections

## Pull Request Process

### Architecture Decision Records (ADR)

For architecture-impacting changes, add or update an ADR in `docs/adr/`.

- Use `docs/adr/ADR_TEMPLATE.md`
- Include context, decision, alternatives, and consequences
- Link the ADR in the pull request description

Examples of changes requiring ADRs:
- New boundary/layering rules
- Major testing strategy changes
- Canonical source-of-truth changes for generated/synced assets

### Before Submitting

1. **Run all quality checks locally**:
   ```bash
   # Python linting (REQUIRED - must pass)
   ruff check .
   ruff check --fix .  # Auto-fix issues
   ruff format .       # Format code
   
   # Type checking
   mypy .
   
   # Run tests
   pytest
   
   # HTML validation
   html-validate "docs/**/*.html"
   ```

2. **Build and verify the site**:
   ```bash
   quarto render
   # Check for build errors
   # Verify changes in docs/ directory
   ```

3. **Check for common issues**:
   - No trailing whitespace
   - Imports are sorted
   - All functions have type hints
   - All functions have docstrings
   - No `print()` statements (use `logging`)

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(articles): add new article on drift ratio"
git commit -m "fix(navigation): correct broken link in sidebar"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(scripts): add tests for sitemap generator"
```

### Creating the Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open PR on GitHub** with:
   - **Clear title** following commit message format
   - **Description** including:
     - What changes did you make?
     - Why did you make them?
     - How did you test them?
     - Screenshots (if UI changes)
   - **Link related issues** using `Fixes #123` or `Relates to #456`

3. **Ensure CI passes**:
   - All GitHub Actions workflows must pass
   - Fix any linting or test failures
   - Address any security warnings

4. **Keep PRs focused**:
   - One feature or fix per PR
   - Avoid mixing unrelated changes
   - Keep diffs manageable (< 500 lines preferred)

5. **Respond to feedback**:
   - Address reviewer comments promptly
   - Push additional commits to the same branch
   - Mark conversations as resolved when addressed

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All linting checks pass (`ruff`, `mypy`)
- [ ] Tests added/updated and passing
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow conventional format
- [ ] PR description is clear and complete
- [ ] No merge conflicts with main branch
- [ ] CI/CD pipeline passes

## Reporting Issues

When reporting issues, please include:

- **Description**: What's the problem?
- **Steps to reproduce**: How can we see the issue?
- **Expected behavior**: What should happen?
- **Actual behavior**: What actually happens?
- **Screenshots**: If applicable
- **Browser/OS**: What environment are you using?

## Suggesting Resources

When suggesting resources for the Resources page:

1. **Verify the resource** is high-quality and relevant
2. **Provide complete information**:
   - Title
   - Author/Creator
   - URL
   - Brief description (1-2 sentences)
   - Why it's valuable
   - Publication date (if applicable)
3. **Suggest appropriate category**:
   - Video Lectures
   - Academic Papers/Books
   - Online Courses
   - Computational Tools
   - Helpful Links
4. **Format as Quarto markdown**:
   ```markdown
   ### Resource Title
   
   **Author:** Name
   **Link:** [URL](https://example.com)
   **Description:** Brief description of the resource.
   
   Why it's valuable: Explanation of relevance to affine control theory or golf biomechanics.
   ```

## Project Structure

Understanding the project layout:

```
AffineDrift/
├── articles/              # Article source files (.qmd)
├── docs/                  # Generated site (DO NOT edit directly)
├── scripts/               # Build and maintenance scripts
├── tools/                 # Utility tools
├── tests/                 # Test suites
├── src/                   # Source assets (CSS, JS)
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript modules
│   └── tools/            # Tool-specific assets
├── _quarto.yml           # Quarto configuration
├── custom.scss           # Custom styles
├── script.js             # Main JavaScript
├── styles.css            # Compiled styles
└── requirements.txt      # Python dependencies
```

**Key Files:**
- `_quarto.yml` - Site configuration, navigation, metadata
- `custom.scss` - SCSS variables and custom styles
- `script.js` - Interactive features and navigation
- `requirements.txt` - Python package dependencies

## Common Tasks

### Adding a New Article

1. Create `.qmd` file in `articles/` directory:
   ```bash
   touch articles/my-new-article.qmd
   ```

2. Add frontmatter:
   ```yaml
   ---
   title: "My New Article"
   author: "Your Name"
   date: "2026-01-22"
   description: "Brief description for SEO"
   categories: [theory, applications]
   ---
   ```

3. Write content using Markdown and LaTeX

4. Add to navigation in `_quarto.yml`:
   ```yaml
   website:
     navbar:
       left:
         - text: "Articles"
           menu:
             - text: "My New Article"
               href: articles/my-new-article.qmd
   ```

5. Build and preview:
   ```bash
   quarto preview
   ```

### Updating Styles

1. Edit `custom.scss` (NOT `styles.css` directly)
2. Quarto will compile SCSS to CSS automatically
3. Preview changes:
   ```bash
   quarto preview
   ```

### Adding JavaScript Features

1. Edit `script.js` or create module in `src/js/`
2. Follow existing patterns and conventions
3. Test in multiple browsers
4. Add JSDoc comments

### Running Scripts

```bash
# Generate sitemap
python scripts/generate_sitemap.py

# Generate search index
python scripts/generate_search_index.py

# Run quality checks
python scripts/seo_audit.py

# Check equations
python scripts/check-equations.py
```

### Developing New Tools

When creating a new utility tool for the `src/tools/` directory:

#### Tool Template

```python
"""Brief description of what the tool does.

This tool [longer description of functionality and use cases].

Usage:
    python tool_name.py [options]

Example:
    python tool_name.py --input file.qmd --output result.html
    python tool_name.py --verbose

Note:
    Any important notes about usage or limitations.
"""

import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def process_file(path: Path, options: dict[str, str]) -> bool:
    """Process a single file.

    Args:
        path: Path to the file to process.
        options: Dictionary of processing options.

    Returns:
        True if processing succeeded, False otherwise.

    Raises:
        FileNotFoundError: If the input file doesn't exist.
        ValueError: If the file format is invalid.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    logger.info("Processing %s", path)
    # Implementation here
    return True


def main() -> None:
    """Main entry point for the tool."""
    parser = argparse.ArgumentParser(
        description="Tool description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="Input file path")
    parser.add_argument("--output", "-o", type=Path, help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        process_file(args.input, {"output": args.output})
        logger.info("Processing complete")
    except FileNotFoundError as e:
        logger.error("File error: %s", e)
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
```

#### Tool Development Checklist

1. **Structure**
   - [ ] Module-level docstring with usage examples
   - [ ] `main()` function as entry point
   - [ ] `if __name__ == "__main__":` guard
   - [ ] Argument parsing with `argparse`

2. **Documentation**
   - [ ] Google-style docstrings for all functions
   - [ ] Type hints for parameters and return values
   - [ ] Usage examples in module docstring

3. **Error Handling**
   - [ ] Specific exceptions (not bare `except:`)
   - [ ] Informative error messages
   - [ ] Proper exit codes

4. **Logging**
   - [ ] Use `logging` module (NO `print()`)
   - [ ] Configurable verbosity level
   - [ ] Meaningful log messages

5. **Testing**
   - [ ] Create `tests/test_<tool_name>.py`
   - [ ] Test happy path and error cases
   - [ ] Mock file I/O where appropriate

6. **Integration**
   - [ ] Add to `src/tools/README.md`
   - [ ] Update Quick Reference table
   - [ ] Add usage examples

### Extension Points

The AffineDrift project can be extended in several ways:

#### Custom Quarto Filters

Create custom Lua filters in `_extensions/`:

```lua
-- _extensions/my-filter/my-filter.lua
function Pandoc(doc)
  -- Process the entire document
  return doc
end
```

Register in `_quarto.yml`:

```yaml
filters:
  - _extensions/my-filter/my-filter.lua
```

#### Custom JavaScript Modules

Add interactive features in `src/js/`:

```javascript
// src/js/my-module.js
/**
 * Module description
 * @module my-module
 */

export const myFeature = {
  init() {
    // Initialization code
  },

  /**
   * Process data
   * @param {Object} data - Input data
   * @returns {Object} Processed result
   */
  process(data) {
    return data;
  }
};
```

Import in `script.js`:

```javascript
import { myFeature } from './src/js/my-module.js';
myFeature.init();
```

#### Custom CSS Components

Add styles in `custom.scss`:

```scss
// Use existing variables
.my-component {
  color: var(--text-color);
  background: var(--bg-secondary);

  &__element {
    // BEM naming
  }

  &--modifier {
    // Variant styles
  }
}
```

## Example Pull Requests

### Example: New Article PR

**Title:** `feat(articles): add article on drift ratio analysis`

**Description:**
```markdown
## Summary
- Add new article explaining drift ratio concepts
- Include interactive examples with MathJax
- Add to Articles navigation

## Changes
- `articles/drift-ratio-analysis.qmd` - New article
- `_quarto.yml` - Updated navigation
- `docs/` - Generated HTML

## Testing
- [ ] `quarto preview` shows article correctly
- [ ] Math equations render properly
- [ ] Navigation links work
- [ ] Mobile responsive

Fixes #123
```

### Example: Bug Fix PR

**Title:** `fix(navigation): correct broken sidebar links`

**Description:**
```markdown
## Summary
Fix broken links in the right sidebar that were pointing to old URLs.

## Root Cause
Links were using relative paths that broke after restructuring.

## Solution
Updated to use absolute paths from site root.

## Testing
- Verified all sidebar links in Chrome, Firefox, Safari
- Checked mobile navigation

Fixes #456
```

### Example: Tool Enhancement PR

**Title:** `feat(tools): add batch processing to latex_to_qmd`

**Description:**
```markdown
## Summary
Add ability to process multiple LaTeX files in one command.

## Changes
- Add `--batch` flag for directory processing
- Add progress reporting
- Add summary statistics

## Usage
```bash
python latex_to_qmd.py --batch articles/latex/
```

## Testing
- Added tests in `tests/test_latex_to_qmd.py`
- Tested with 50+ files

Relates to #789
```

## Code of Conduct

### Be Respectful

- Use welcoming and inclusive language
- Respect differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community

### Be Professional

- No harassment, discrimination, or inappropriate content
- Keep discussions relevant and on-topic
- Assume good intentions

### Be Helpful

- Help beginners learn
- Share knowledge generously
- Give credit where it's due

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with the "question" label
- Reach out via the repository discussions
- Check [AGENTS.md](AGENTS.md) for detailed coding standards
- Review existing PRs for examples

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_deployment_integrity.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run with verbose output
pytest -v
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive docstrings
- Follow Arrange-Act-Assert pattern

**Example:**
```python
def test_convert_latex_equation():
    """Test LaTeX to QMD equation conversion."""
    # Arrange
    latex_input = r"\frac{a}{b}"
    
    # Act
    result = convert_latex(latex_input)
    
    # Assert
    assert result == expected_output
    assert result.is_valid()
```

See [tests/README.md](tests/README.md) for detailed testing documentation.

## License

By contributing, you agree that your contributions will be licensed under the same terms as the project.

---

Thank you for helping make AffineDrift better! Your contributions, big or small, are greatly appreciated.
