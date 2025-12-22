# Quarto Local Testing Guide

## Prerequisites

- Quarto is installed (version 1.8.26 or later)
- Python environment (if using Python code chunks)
- All dependencies installed

## Quick Start

### 1. Preview the Entire Site

To preview the entire Quarto website locally:

```bash
quarto preview
```

This will:
- Start a local web server (usually at `http://localhost:4200`)
- Automatically rebuild when you make changes
- Show the rendered site in your browser

### 2. Render the Entire Site

To build the complete site without preview:

```bash
quarto render
```

This generates all HTML files in the `_site` directory.

### 3. Render Individual Articles

To render a specific article:

```bash
quarto render articles/wrist-universal-joint.qmd
quarto render articles/inverse-dynamics.qmd
```

### 4. Check for Errors

To check for rendering errors without building:

```bash
quarto check
```

## Testing Checklist

Before pushing to main, verify:

- [ ] **Site renders without errors**: `quarto render` completes successfully
- [ ] **Navigation works**: All links in navbar and sidebar function correctly
- [ ] **Articles display correctly**:
  - [ ] `articles/wrist-universal-joint.qmd` renders properly
  - [ ] `articles/inverse-dynamics.qmd` renders properly
  - [ ] Math equations display correctly (MathJax)
  - [ ] Code blocks render with syntax highlighting
- [ ] **Calculator still works**:
  - [ ] `content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` is present
  - [ ] Calculator can be run independently
- [ ] **Links are correct**:
  - [ ] Internal links work
  - [ ] External links are valid
  - [ ] Images load correctly
- [ ] **Mobile responsive**: Test on different screen sizes
- [ ] **Search functionality**: If implemented, test search

## Common Issues

### Math Equations Not Rendering

If MathJax equations don't render:
1. Check that `html-math-method: mathjax` is in `_quarto.yml`
2. Verify MathJax CDN is accessible
3. Check browser console for errors

### Code Blocks Not Highlighting

If syntax highlighting doesn't work:
1. Ensure code blocks use proper language tags (e.g., ````python`)
2. Check that `code-fold: true` is set in format options

### Missing Files

If files are missing:
1. Check `.gitignore` - some files may be ignored
2. Verify all source files are in the repository
3. Check that `output-dir: _site` matches your build directory

## Preview vs Render

- **`quarto preview`**: Interactive preview with live reload (for development)
- **`quarto render`**: Full build to `_site/` directory (for production)

## Production Build

When ready to deploy:

```bash
# Clean previous build
rm -rf _site

# Render complete site
quarto render

# Verify output
ls -la _site/
```

The `_site/` directory contains the complete static website ready for deployment.

## Integration with CI/CD

The GitHub Actions workflow (`.github/workflows/quarto-publish.yml`) will:
1. Install Quarto
2. Render the site
3. Deploy to GitHub Pages

Test locally first to catch issues before they reach CI/CD.
