# AffineDrift Articles

This directory contains Quarto articles converted from LaTeX source files.

## Files

- **wrist-universal-joint.qmd**: Constraint Torques at the Wrist article
- **inverse-dynamics.qmd**: Interpretation of Inverse Dynamics article
- **_metadata.yml**: Shared configuration for all articles

## Editing Articles

Quarto uses Markdown with LaTeX equations:

```markdown
## Section Heading

Regular text with **bold** and *italic*.

Inline equation: $E = mc^2$

Display equation:
$$
F = ma
$$ {#eq-force}

Reference: See @eq-force
```

## Preview Changes

```bash
# Preview entire site with live reload
quarto preview

# Preview single article
quarto preview articles/wrist-universal-joint.qmd
```

## Build

```bash
# Build entire site
quarto render

# Build single article
quarto render articles/wrist-universal-joint.qmd
```

## Adding New Articles

1. Create new `.qmd` file in this directory
2. Add YAML frontmatter:
```yaml
---
title: "Article Title"
author: "AffineDrift"
date: "2025-01-26"
---
```
3. Write content in Markdown with LaTeX equations
4. Render to preview

## Converting from LaTeX

```bash
# Single file
python3 ../tools/latex_to_qmd.py path/to/file.tex articles/output.qmd

# Batch conversion
python3 ../tools/convert_all_to_quarto.py
```

## Documentation

See [QUARTO_GUIDE.md](../QUARTO_GUIDE.md) for complete documentation.
