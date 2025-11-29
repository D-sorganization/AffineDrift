# Main Branch vs Current State Comparison

## Overview

This document compares the current state of the `merge-quarto-branch` with the `main` branch to identify all differences.

## Key Changes Summary

### Files Added (New in Current Branch)
- **Quarto Configuration**: `_quarto.yml`, `.quartoignore`
- **Quarto Articles**: `articles/wrist-universal-joint.qmd`, `articles/inverse-dynamics.qmd`
- **Quarto Workflow**: `.github/workflows/quarto-publish.yml`
- **Documentation**: `QUARTO_GUIDE.md`, `BRANCH_REVIEW_SUMMARY.md`, `WEBSITE_ANALYSIS.md`, etc.
- **Conversion Tools**: `tools/latex_to_qmd.py`, `tools/convert_all_to_quarto.py`, etc.
- **Custom Styling**: `custom.scss`
- **New HTML Page**: `reading-list.html`

### Files Modified
- **Navigation**: All HTML files have navigation updates (removed "About" tab)
- **Contact Page**: `contact.html` - Added About section above contact form
- **Index**: `index.html` - Navigation updated
- **Articles**: `articles.html` - Updated to include Quarto articles
- **Content Files**: Various HTML files in `content/` directory

### Files Moved/Archived
- Several LaTeX files moved to `Archive/` subdirectory:
  - `Wrist_Universal_ChatGPT.tex`
  - `Wrist_Universal_Gemini.tex`
  - `Wrist_Universal_GeminiCombined.tex`
  - `Wrist_Universal_GrokCombined.tex`
  - `Wrist_Universal_GrokCombined_2.tex`

### Files Preserved (Critical)
- ✅ **Calculator**: `content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` - PRESERVED
- ✅ **All HTML pages**: All existing HTML pages maintained
- ✅ **Styles and Scripts**: `styles.css`, `script.js` - Preserved

## Website Structure Comparison

### Main Branch Structure
```
AffineDrift/
├── index.html (Homepage)
├── articles.html
├── contact.html
├── about.html (separate page)
├── resources.html
├── theory*.html (multiple theory pages)
├── styles.css
├── script.js
└── content/ (LaTeX and source files)
```

### Current Branch Structure
```
AffineDrift/
├── index.html (Homepage - navigation updated)
├── articles.html (updated with Quarto articles)
├── contact.html (About section + Contact form)
├── about.html (still exists but not linked)
├── resources.html
├── theory*.html (navigation updated)
├── styles.css
├── script.js
├── _quarto.yml (Quarto config)
├── articles/ (NEW - Quarto articles)
│   ├── wrist-universal-joint.qmd
│   └── inverse-dynamics.qmd
├── _site/ (Quarto output)
│   └── articles/ (rendered HTML)
└── content/ (preserved, some files archived)
```

## Navigation Changes

### Main Branch Navigation
```
- Affine Drift
- Articles
- Reviews
- Resources
- Contact
- About
```

### Current Branch Navigation
```
- Affine Drift
- Articles
- Reviews
- Resources
- Contact (contains About content)
```

## Content Changes

### Contact Page
- **Main**: Just contact form
- **Current**: About section (from about.html) + Contact form

### Articles Page
- **Main**: Links to HTML articles
- **Current**: Links to HTML articles + Quarto articles

## Quarto Integration

### What Quarto Adds
1. **New Article Format**: `.qmd` files that render to HTML
2. **Math Rendering**: MathJax configured in Quarto
3. **Publishing Workflow**: Automated Quarto rendering in CI/CD
4. **Better Math Support**: Native LaTeX math in articles

### What's Preserved
1. **All existing HTML pages**: No changes to structure
2. **Calculator**: `Universal_Joint_Model_Enhanced.py` intact
3. **Styling**: Custom CSS preserved
4. **JavaScript**: All scripts preserved

## Issues to Address

1. **Preview Server**: Currently showing directory listing instead of index.html
2. **Equation Rendering**: Need to verify MathJax works in Quarto articles
3. **Navigation Consistency**: Some pages may still have "About" link
4. **File Organization**: `_site/` directory contains Quarto output

## Next Steps

1. Fix preview server to serve index.html by default
2. Verify all navigation links are consistent
3. Test equation rendering in Quarto articles
4. Ensure calculator still works
5. Test full website functionality






