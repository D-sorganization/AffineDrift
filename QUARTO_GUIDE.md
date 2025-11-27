# Quarto Setup and Usage Guide for AffineDrift

This guide explains how to use Quarto for building and publishing the AffineDrift website.

## What is Quarto?

Quarto is an open-source scientific and technical publishing system built on Pandoc. It's perfect for AffineDrift because:

- **Native LaTeX support**: Write equations directly in LaTeX syntax
- **Multiple output formats**: HTML, PDF, DOCX from the same source
- **Cross-references**: Automatic numbering and linking for equations, figures, sections
- **Code integration**: Can include Python/R/Julia code and outputs
- **Professional publishing**: Industry-standard tool with active development

## Installation

### Linux (Debian/Ubuntu)
```bash
wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.4.549/quarto-1.4.549-linux-amd64.deb
sudo dpkg -i quarto-1.4.549-linux-amd64.deb
```

### macOS
```bash
brew install quarto
```

### Windows
Download and run the installer from: https://quarto.org/docs/get-started/

### Verify Installation
```bash
quarto --version
```

## Project Structure

```
AffineDrift/
├── _quarto.yml              # Main configuration
├── custom.scss              # Custom styling
├── articles/                # Quarto article files (.qmd)
│   ├── _metadata.yml        # Shared article settings
│   ├── wrist-universal-joint.qmd
│   └── inverse-dynamics.qmd
├── index.html               # Existing pages (can be kept or converted)
├── styles.css               # Existing styles
└── _site/                   # Generated output (gitignored)
```

## Quarto Document Format (.qmd)

Quarto documents use Markdown with LaTeX equations:

```markdown
---
title: "Article Title"
author: "AffineDrift"
date: "2025-01-26"
format:
  html:
    toc: true
---

## Introduction

Regular markdown text with **bold** and *italic*.

Inline equation: $E = mc^2$

Display equation:
$$
F = ma
$$ {#eq-force}

Reference equation: See @eq-force for details.
```

## Common Commands

### Preview with Live Reload
```bash
quarto preview
# Opens browser at http://localhost:4200
# Auto-reloads when files change
```

### Render Entire Site
```bash
quarto render
# Generates all HTML files in _site/
```

### Render Single Document
```bash
quarto render articles/wrist-universal-joint.qmd
```

### Publish to GitHub Pages
```bash
quarto publish gh-pages
# Automatically builds and deploys to gh-pages branch
```

## Quarto Features for Technical Content

### Equations

**Inline:**
```markdown
The equation $E = mc^2$ is famous.
```

**Display:**
```markdown
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

**Numbered with label:**
```markdown
$$
F = ma
$$ {#eq-newton}

See @eq-newton for Newton's second law.
```

### Cross-References

**Equations:**
```markdown
$$
E = mc^2
$$ {#eq-einstein}

As shown in @eq-einstein...
```

**Sections:**
```markdown
## Introduction {#sec-intro}

As discussed in @sec-intro...
```

**Figures:**
```markdown
![Caption](image.png){#fig-myplot}

See @fig-myplot for details.
```

### Callout Boxes

```markdown
::: {.callout-note}
This is a note callout.
:::

::: {.callout-warning}
This is a warning.
:::

::: {.callout-important}
This is important.
:::
```

### Custom CSS Classes

```markdown
::: {.abstract-section}
This content gets the abstract-section CSS class.
:::

::: {.keypoint-box}
**Key Point:** This is styled as a key point.
:::
```

### Code Blocks

````markdown
```python
#| echo: true
#| eval: false
import numpy as np
x = np.linspace(0, 10, 100)
```
````

### Tables

```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

: Table caption {#tbl-mytable}
```

## Configuration Files

### `_quarto.yml` (Main Config)

Key settings:
- `project.type: website` - Specifies website project
- `project.output-dir: _site` - Where output goes
- `website.navbar` - Navigation bar configuration
- `format.html` - HTML output settings
- `format.html.html-math-method: mathjax` - Equation rendering

### `custom.scss` (Styling)

SCSS variables and custom CSS rules for AffineDrift branding.

### `articles/_metadata.yml` (Shared Article Settings)

Settings applied to all articles in the directory.

## Conversion Tools

### Convert Single LaTeX File
```bash
python3 tools/latex_to_qmd.py "content/path/to/article.tex" "articles/output.qmd"
```

### Convert All LaTeX Files
```bash
python3 tools/convert_all_to_quarto.py
```

### Add New Conversion
Edit `tools/convert_all_to_quarto.py` and add to `CONVERSIONS` list:
```python
{
    "source": "content/path/to/new-article.tex",
    "target": "articles/new-article.qmd",
    "description": "New Article"
}
```

## GitHub Actions Workflow

Create `.github/workflows/quarto-publish.yml`:

```yaml
name: Quarto Publish

on:
  push:
    branches: [main]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Quarto
        uses: quarto-dev/quarto-actions/setup@v2

      - name: Render Quarto Project
        run: quarto render

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./_site
```

## Migration Strategy

### Option 1: Full Migration (Recommended)
1. Convert all existing HTML pages to Quarto
2. Use Quarto for entire site
3. Single build system

### Option 2: Hybrid Approach
1. Keep existing HTML pages as-is
2. Use Quarto only for new technical articles
3. Quarto renders to `_site/`, copy other files there

### Option 3: Gradual Migration
1. Start with articles directory
2. Gradually convert other pages
3. Eventually full Quarto site

## Tips and Best Practices

### Equations
- Use `$$...$$` for display equations (on their own line)
- Use `$...$` for inline equations
- Add `{#eq-label}` for numbered equations
- Reference with `@eq-label`

### File Organization
- Keep `.qmd` files in `articles/` directory
- Use kebab-case for filenames: `wrist-universal-joint.qmd`
- One article per file

### Styling
- Customize in `custom.scss`
- Use existing `styles.css` via `css: styles.css` in frontmatter
- Define custom divs for special formatting

### Performance
- Quarto caching speeds up rebuilds
- Preview mode only rebuilds changed files
- Use `quarto render --no-execute` to skip code execution

### Version Control
- Add `_site/` to `.gitignore`
- Commit `.qmd` source files
- Let CI/CD build and deploy

## Troubleshooting

### Equations Not Rendering
- Check MathJax is configured in `_quarto.yml`
- Verify equation delimiters: `$$...$$` or `$...$`
- Look for LaTeX syntax errors

### Preview Not Working
- Check port 4200 isn't in use
- Try `quarto preview --port 4300`
- Check firewall settings

### Build Errors
- Run `quarto check` to verify installation
- Check YAML frontmatter syntax
- Look for unclosed code blocks or divs

### Styling Issues
- Verify `custom.scss` syntax
- Check CSS class names match
- Use browser dev tools to debug

## Resources

### Official Documentation
- [Quarto Website](https://quarto.org)
- [Get Started Guide](https://quarto.org/docs/get-started/)
- [Authoring Guide](https://quarto.org/docs/authoring/)
- [Reference](https://quarto.org/docs/reference/)

### Equation Syntax
- [LaTeX Math Symbols](https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols)
- [MathJax Documentation](https://docs.mathjax.org/)

### Publishing
- [GitHub Pages](https://quarto.org/docs/publishing/github-pages.html)
- [Netlify](https://quarto.org/docs/publishing/netlify.html)
- [Other Platforms](https://quarto.org/docs/publishing/)

### Examples
- [Quarto Gallery](https://quarto.org/docs/gallery/)
- [Example Websites](https://quarto.org/docs/websites/)

## Support

For questions or issues:
1. Check [Quarto Discussions](https://github.com/quarto-dev/quarto-cli/discussions)
2. Review [GitHub Issues](https://github.com/quarto-dev/quarto-cli/issues)
3. Consult [Stack Overflow](https://stackoverflow.com/questions/tagged/quarto)

## Next Steps

1. **Install Quarto** following instructions above
2. **Test preview**: `quarto preview` in project root
3. **Review converted articles** in `articles/` directory
4. **Customize styling** in `custom.scss` as needed
5. **Set up CI/CD** for automatic deployment
6. **Migrate remaining pages** gradually

Happy publishing! 🚀
