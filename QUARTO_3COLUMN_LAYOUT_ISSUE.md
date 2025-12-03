# Quarto 3-Column Layout Rendering Issue

## Problem

The `.qmd` source files contain the correct 3-column layout structure with:
- `.standard-page-layout` container
- `.left-sidebar` with `.toc-nav` (Table of Contents)
- `.main-content-area` (main content)
- `.right-sidebar` with `.history-nav` (History)

However, when Quarto renders these files, the HTML output in `docs/*.html` is missing the sidebar structure entirely. The rendered HTML only contains the main content without the 3-column layout.

## Root Cause

When Quarto processes `.qmd` files with `page-layout: full` and `{=html}` blocks:

1. **Quarto wraps content**: Even with `{=html}` blocks, Quarto wraps the content in its own page structure (`<div class="quarto-title-meta column-page">`, etc.)

2. **Content extraction**: Quarto may be extracting only the inner content from HTML blocks and discarding the wrapper structure

3. **Layout processing**: The `page-layout: full` setting might be interfering with custom HTML layouts

## Evidence

**Source (`articles.qmd`):**
```html
```{=html}
<section class="article-section">
  <div class="container">
    <div class="standard-page-layout">
      <aside class="left-sidebar">...</aside>
      <main class="main-content-area">...</main>
      <aside class="right-sidebar">...</aside>
    </div>
  </div>
</section>
```
```

**Rendered (`docs/articles.html`):**
```html
<section class="article-section">
  <div class="container">
    <div class="articles-list">
      <!-- Sidebars are missing! -->
    </div>
  </div>
</section>
```

## Potential Solutions

### Option 1: Use Custom Template (Recommended)
Create a custom Quarto template that preserves the HTML structure:
- Modify `_templates/partials/header.html` or create a custom layout template
- Ensure the template doesn't strip custom HTML blocks

### Option 2: Post-Processing Script
Create a post-render script that:
- Runs after `quarto render`
- Injects the sidebar structure into rendered HTML files
- Uses the source `.qmd` files as reference

### Option 3: Use Quarto's Layout System
Instead of custom HTML, use Quarto's built-in layout features:
- Use `::: {.columns}` syntax
- Configure layout in `_quarto.yml`
- May require restructuring the HTML

### Option 4: Raw HTML Files
For pages that need custom layouts:
- Keep them as pure HTML files in `docs/`
- Don't use Quarto rendering for these pages
- Manually maintain them

## Immediate Workaround

The current workaround (from previous investigation) was to manually extract HTML from `.qmd` files using a Python script. This bypasses Quarto entirely but:
- ✅ Preserves the 3-column layout
- ❌ Doesn't use Quarto's templating system
- ❌ Requires manual regeneration
- ❌ Doesn't benefit from Quarto's other features

## Next Steps

1. **Test Quarto rendering**: Run `quarto render articles.qmd` and inspect the output
2. **Check Quarto version**: Ensure using a version that supports `{=html}` blocks properly
3. **Review Quarto documentation**: Check if there's a setting to preserve raw HTML
4. **Consider custom template**: Create a template that preserves the layout structure
5. **Document the solution**: Once fixed, document the approach for future pages

## Related Files

- Source files: `articles.qmd`, `models*.qmd`, `resources-*.qmd`
- Rendered files: `docs/articles.html`, `docs/models*.html`, `docs/resources-*.html`
- Configuration: `_quarto.yml`
- Templates: `_templates/partials/header.html`

